//! External-writer seam over the real, pinned Craft Anything engine.
//! Reasoning stays with the host; workspace, writes and processes run in Craft.
#![forbid(unsafe_code)]

use craft_anything_engine::inbox::InboxDir;
use craft_anything_engine::workspace::{ActionKind, Approval, CheckResult, Status, TargetRef, Workspace};
use craft_anything_engine::{CallOptions, Caller, Consent, Engine, Session, Settings};
use serde::Deserialize;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::fs::{self, File, OpenOptions};
use std::io::{self, Read};
use std::path::{Component, Path, PathBuf};
use std::sync::Arc;

const UPSTREAM: &str = "8374ad71544f2cc44698ea74ef990aa31600bac6";

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Request {
    op: String,
    #[serde(default)]
    lease: Option<PathBuf>,
    #[serde(default)]
    params: Value,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Lease {
    version: u32,
    project_root: PathBuf,
    receipt: String,
    workspace: String,
    check_commands: Vec<String>,
    command_timeout_seconds: u64,
}

fn error(e: impl std::fmt::Display) -> String { e.to_string() }

fn digest(path: &Path) -> Result<String, String> {
    let mut stream = File::open(path).map_err(error)?;
    let mut hash = Sha256::new();
    let mut block = [0u8; 65536];
    loop {
        let n = stream.read(&mut block).map_err(error)?;
        if n == 0 { break; }
        hash.update(block.get(..n).ok_or("Invalid file read size")?);
    }
    Ok(format!("{:x}", hash.finalize()))
}

fn relative(root: &Path, name: &str) -> Result<PathBuf, String> {
    if name.is_empty() || name.contains(':') || name.contains('\\')
        || Path::new(name).components().any(|c| !matches!(c, Component::Normal(_))) {
        return Err("Expected a portable project-relative path".into());
    }
    let path = root.join(name).canonicalize().map_err(error)?;
    if !path.starts_with(root) { return Err("Referenced input leaves project".into()); }
    Ok(path)
}

fn candidate_digests(root: &Path, allowed: &[Value]) -> Result<Value, String> {
    let mut outputs = serde_json::Map::new();
    for name in allowed.iter().filter_map(Value::as_str).filter(|s| s.starts_with("app/")) {
        let path = root.join(name);
        if path.is_file() {
            outputs.insert(name.into(), Value::String(digest(&relative(root, name)?)?));
        }
    }
    Ok(Value::Object(outputs))
}

fn run(request: Request) -> Result<Value, String> {
    if request.op == "capabilities" {
        return Ok(json!({"backend":"craft-anything-native-engine", "upstream_commit":UPSTREAM,
            "engine_version":"0.6.1", "adapter_version":env!("CARGO_PKG_VERSION"),
            "windows_command_tail_version":craft_anything_engine::tools::build_tools::WINDOWS_COMMAND_TAIL_VERSION,
            "capabilities":["prepare","build","check","refine","return_summary","cleanup","abort"],
            "writer":"current-host via native build tools", "business_acceptance":"not-performed"}));
    }
    let lease_path = request.lease.ok_or("A frozen native lease is required")?.canonicalize().map_err(error)?;
    let lease: Lease = serde_json::from_slice(&fs::read(&lease_path).map_err(error)?).map_err(error)?;
    if lease.version != 1 || !(1..=600).contains(&lease.command_timeout_seconds) {
        return Err("Unsupported lease or command deadline".into());
    }
    let root = lease.project_root.canonicalize().map_err(error)?;
    let receipt_path = relative(&root, &lease.receipt)?;
    let mut receipt: Value = serde_json::from_slice(&fs::read(&receipt_path).map_err(error)?).map_err(error)?;
    let project = receipt.get("project_root").and_then(Value::as_str).ok_or("Unbound session")?;
    if Path::new(project).canonicalize().map_err(error)? != root
        || receipt.get("backend").and_then(Value::as_str) != Some("current-session")
        || receipt.get("workspace").and_then(Value::as_str) != Some(lease.workspace.as_str())
        || matches!(receipt.get("phase").and_then(Value::as_str), Some("finished" | "aborted")) {
        return Err("Session is closed or belongs to a different project/workspace".into());
    }
    let refs = receipt.get("frozen_refs").and_then(Value::as_object).ok_or("Missing frozen inputs")?;
    let mut lease_frozen = false;
    let mut changed = Vec::new();
    for (name, expected) in refs {
        let input = relative(&root, name);
        let same_lease = input.as_ref().is_ok_and(|p| p == &lease_path);
        let unchanged = input.and_then(|p| digest(&p)).is_ok_and(|hash| expected.as_str() == Some(hash.as_str()));
        if !unchanged {
            if request.op != "abort" || same_lease { return Err(format!("Frozen input changed: {name}")); }
            changed.push(name.clone());
        }
        lease_frozen |= same_lease && unchanged;
    }
    if !lease_frozen { return Err("Native lease is not frozen by the session".into()); }
    let workspace_path = relative(&root, &lease.workspace)?;
    // One OS-held writer lock for a workspace, independent of which lease names
    // it. Closing/killing this adapter releases the lock; stale files do not
    // masquerade as live writers.
    let parent = workspace_path.parent().ok_or("Workspace has no parent")?;
    if !parent.starts_with(&root) { return Err("Writer lock leaves project".into()); }
    let lock_name = format!(".craft-{:x}.lock", Sha256::digest(workspace_path.to_string_lossy().as_bytes()));
    let writer_lock = OpenOptions::new().read(true).write(true).create(true).truncate(false)
        .open(parent.join(lock_name)).map_err(error)?;
    writer_lock.try_lock().map_err(|_| "Another native Craft operation owns this workspace".to_string())?;
    let allowed = receipt.get("allowed_outputs").and_then(Value::as_array).ok_or("Missing output scope")?;
    let allowed_path = |name: &str| allowed.iter().any(|a| a.as_str() == Some(name));
    if !allowed_path("craft.json") { return Err("Native Craft manifest must be an observed output".into()); }

    if request.op == "prepare" {
        let mut ws = Workspace::create_at(&workspace_path, "Accepted reconstruction tasks",
            "Implement only the frozen accepted research and Spec tasks; external acceptance required",
            TargetRef::None, None).map_err(error)?;
        fs::create_dir_all(ws.app_dir()).map_err(error)?;
        ws.set_person(|manifest| { manifest.approvals.insert(ActionKind::Commands, Approval::Allow); }).map_err(error)?;
        ws.set_status(Status::Building, "External host writer; accepted research already supplied").map_err(error)?;
        return Ok(json!({"status":"prepared", "native_operation":"Workspace::create_at", "workspace":ws.root,
            "candidate":ws.app_dir(), "business_acceptance":"not-performed"}));
    }
    if request.op == "abort" {
        let reason = request.params.get("reason").and_then(Value::as_str)
            .filter(|s| !s.trim().is_empty()).ok_or("Abort requires a recorded reason")?;
        if workspace_path.join("craft.json").is_file() {
            let mut ws = Workspace::open(&workspace_path).map_err(error)?;
            ws.set_status(Status::Stopped, format!("Aborted, not accepted: {reason}")).map_err(error)?;
        }
        receipt["phase"] = json!("aborted");
        receipt["events"].as_array_mut().ok_or("Missing session events")?.push(
            json!({"phase":"abort", "reason":reason, "changed_frozen_refs":changed,
                "business_acceptance":"not-performed"}));
        let temporary = receipt_path.with_extension("abort.tmp");
        fs::write(&temporary, serde_json::to_vec_pretty(&receipt).map_err(error)?).map_err(error)?;
        fs::rename(&temporary, &receipt_path).map_err(error)?;
        return Ok(json!({"status":"aborted", "outputs":"retained", "changed_frozen_refs":changed,
            "cleanup":"Workspace writer lock acquired; no persistent adapter server; owned commands use Craft Process lifecycle",
            "business_acceptance":"not-performed"}));
    }
    let mut ws = Workspace::open(&workspace_path).map_err(error)?;
    let mut settings = Settings::default();
    settings.auto_mode = false;
    let mut session = Session::new(settings);
    session.ext.insert(Arc::new(InboxDir(ws.inbox_dir())));
    let engine = Engine::new(session);
    let tool = match request.op.as_str() {
        "build" => "build_file_write",
        "refine" => "build_file_edit",
        "check" => "build_command_run",
        "return_summary" => "build_files_list",
        "cleanup" => {
            let snapshot = candidate_digests(&workspace_path, allowed)?;
            let complete = lease.check_commands.iter().all(|command| {
                let id = format!("external-check:{:x}", Sha256::digest(command.as_bytes()));
                ws.manifest.checks.iter().rev().find(|c| c.check == id).is_some_and(|c|
                    c.passed && c.note == snapshot.to_string())
            });
            let has_candidate = allowed.iter().filter_map(Value::as_str)
                .any(|name| name.starts_with("app/") && workspace_path.join(name).is_file());
            if !complete || ws.manifest.awaiting_check || !has_candidate {
                return Err("Candidate needs all frozen native checks after its last write".into());
            }
            ws.set_status(Status::Stopped, "Native calls returned; candidate awaits independent acceptance").map_err(error)?;
            let mut outputs = snapshot;
            outputs["craft.json"] = json!(digest(&workspace_path.join("craft.json"))?);
            return Ok(json!({"status":"candidate", "native_operation":"Workspace::set_status",
                "output_digests":outputs,
                "cleanup":"No persistent server; owned build commands use Craft Process lifecycle",
                "business_acceptance":"not-performed"}));
        }
        _ => return Err("Unsupported native operation".into()),
    };
    if matches!(request.op.as_str(), "build" | "refine") {
        let name = request.params.get("path").and_then(Value::as_str).ok_or("Missing output path")?;
        if !name.starts_with("app/") || !allowed_path(name) { return Err("File is outside frozen candidate outputs".into()); }
    }
    if request.op == "check" {
        let command = request.params.get("command").and_then(Value::as_str).ok_or("Missing check command")?;
        let limit = request.params.get("timeout_secs").and_then(Value::as_u64).ok_or("Missing command deadline")?;
        if !lease.check_commands.iter().any(|c| c == command) || limit == 0 || limit > lease.command_timeout_seconds {
            return Err("Command/deadline differs from frozen check plan".into());
        }
        let id = format!("external-check:{:x}", Sha256::digest(command.as_bytes()));
        ws.manifest.checks.push(CheckResult::new(&id, 0, false, "Native check started; result pending"));
        ws.manifest.awaiting_check = true;
        ws.set_status(Status::Checking, "Running a frozen native check").map_err(error)?;
    } else if matches!(request.op.as_str(), "build" | "refine") {
        // Old results remain in the adapter's event log, but cannot qualify a
        // newly edited candidate. These are Craft check projections, not REA proof.
        ws.manifest.checks.clear();
        ws.manifest.awaiting_check = true;
        ws.set_status(Status::Building, "Candidate changed; native checks need replay").map_err(error)?;
    }
    let params = if request.op == "return_summary" { json!({"path":"app","depth":4}) } else { request.params };
    let output = engine.call(tool, params, CallOptions::new(Caller::Agent).with_consent(Consent::Granted)).map_err(error)?;
    let value = output.to_json();
    if request.op == "check" {
        let command = value.get("result").and_then(|r| r.get("command")).and_then(Value::as_str).ok_or("Native check omitted command identity")?;
        let passed = value.get("result").and_then(|r| r.get("succeeded")).and_then(Value::as_bool).ok_or("Native check omitted execution status")?;
        let id = format!("external-check:{:x}", Sha256::digest(command.as_bytes()));
        let snapshot = candidate_digests(&workspace_path, allowed)?.to_string();
        ws.manifest.checks.push(CheckResult::new(&id, 0, passed, snapshot));
        ws.manifest.awaiting_check = !lease.check_commands.iter().all(|command| {
            let id = format!("external-check:{:x}", Sha256::digest(command.as_bytes()));
            ws.manifest.checks.iter().rev().find(|c| c.check == id).is_some_and(|c| c.passed)
        });
        ws.save().map_err(error)?;
    }
    Ok(json!({"native_tool":tool,"output":value,"business_acceptance":"not-performed"}))
}

fn main() {
    let mut input = String::new();
    let read = io::stdin().take(16 * 1024 * 1024 + 1).read_to_string(&mut input);
    let result = read.map_err(error).and_then(|_| {
        if input.len() > 16 * 1024 * 1024 { return Err("Request exceeds input limit".into()); }
        serde_json::from_str::<Request>(&input).map_err(error).and_then(run)
    });
    match result {
        Ok(value) => println!("{}", json!({"ok":true,"backend":"craft-anything-native-engine","data":value})),
        Err(message) => { println!("{}", json!({"ok":false,"error":message})); std::process::exit(2); }
    }
}
