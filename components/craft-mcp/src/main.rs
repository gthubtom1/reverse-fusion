//! Original pinned Craft MCP protocol and tools; no second model or Study loop.
#![forbid(unsafe_code)]
mod assets;
use craft_anything_engine::{Engine, Session, plugins};
use craft_anything_engine::project::{Project, Purpose, write_atomic};
use craft_anything_engine::tool::{Ctx, Effects, Requires, ToolOutput, ToolSpec, Toolset, parse_params, schema_of};
use craft_anything_evidence::{ErrorCode, ToolError};
use craft_anything_mcp::{ServerOptions, serve_stdio};
use std::path::PathBuf;
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use schemars::JsonSchema;

#[derive(Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
struct CaseOpen {
    /// Absolute existing outcome project directory; never the shared tool checkout.
    project_root: PathBuf,
    /// Absolute existing case directory inside that project (created by the host's case bridge).
    case_root: PathBuf,
}

#[derive(Serialize, Deserialize, PartialEq)]
struct Binding {
    version: u32,
    project_root: PathBuf,
    case_root: PathBuf,
}

fn case_open(ctx: &mut Ctx<'_>, params: Value) -> Result<ToolOutput, ToolError> {
    let p: CaseOpen = parse_params(params)?;
    if !p.project_root.is_absolute() || !p.case_root.is_absolute() {
        return Err(ToolError::invalid("project_root and case_root must be absolute existing directories"));
    }
    let project = p.project_root.canonicalize().map_err(|e| ToolError::io(p.project_root.display(), e))?;
    let case = p.case_root.canonicalize().map_err(|e| ToolError::io(p.case_root.display(), e))?;
    if !project.is_dir() || !case.is_dir() || !case.starts_with(&project) || case == project {
        return Err(ToolError::invalid("case_root must be an existing directory strictly inside project_root"));
    }
    // A globally configured MCP must never turn the shared tool checkout into an outcome case.
    let config = ctx.session.config_dir();
    let tool = if config.file_name().is_some_and(|n| n == "craft-mcp")
        && config.parent().and_then(|p| p.file_name()).is_some_and(|n| n == "state") {
        config.parent().and_then(|p| p.parent()).and_then(|p| p.canonicalize().ok())
    } else { None };
    if tool.as_deref().is_some_and(|root| project == root || case.starts_with(root)) {
        return Err(ToolError::invalid("Use an outcome project outside the shared Reverse Fusion checkout"));
    }
    let root = case.join("craft-analysis.cany");
    if root.exists() && root.canonicalize().map_err(|e| ToolError::io(root.display(), e))?.parent() != Some(case.as_path()) {
        return Err(ToolError::invalid("The analysis store must not link outside the selected case"));
    }
    let identity = Binding { version: 1, project_root: project.clone(), case_root: case.clone() };
    let marker = root.join("fusion-binding.json");
    let current = ctx.session.project.as_ref().map(|p| p.root.clone());
    if current.as_ref() == Some(&root) {
        return Ok(ToolOutput::Value(json!({"bound":root,"reused":true,"project_root":project,"case_root":case})));
    }
    if current.is_none() && (ctx.session.ledger_len() > 0 || ctx.session.unknowns().next().is_some()
        || ctx.session.targets().next().is_some()
        || craft_anything_engine::tools::investigation_tools::load(ctx.session).revision > 0) {
        return Err(ToolError::new(ErrorCode::FeatureMissing,
            "Unbound analysis state exists. Export it explicitly and restart the connection before binding; it cannot be mixed into a case."));
    }
    // Validate the destination before dropping any currently bound session state.
    let native = if root.exists() {
        let bytes = std::fs::read(&marker).map_err(|_| ToolError::invalid("Existing analysis folder is not owned by this case binding"))?;
        let saved: Binding = serde_json::from_slice(&bytes).map_err(|e| ToolError::invalid(format!("Invalid case identity: {e}")))?;
        if saved != identity { return Err(ToolError::invalid("Analysis store belongs to another case/project")); }
        Project::open(&root)?
    } else {
        let native = Project::create(&root, "Reverse Fusion case analysis", Purpose::OwnOrAuthorized)?;
        write_atomic(&marker, &serde_json::to_vec_pretty(&identity).map_err(|e| ToolError::internal(e.to_string()))?)?;
        native
    };
    // Session::open_project merges records. Start a fresh original Session so switching cases
    // never carries the former case's evidence, targets, unknowns or cached investigation.
    if let Some(old) = &ctx.session.project {
        for target in ctx.session.targets() {
            old.save_annotations(&target.target.sha256, &target.annotations)?;
        }
    }
    let mut next = Session::isolated(&ctx.session.config_dir());
    next.settings = ctx.session.settings.clone();
    next.deep_for_run = ctx.session.deep_for_run;
    next.fusion_require_project = true;
    if let Some(engine_ref) = ctx.session.ext.get::<craft_anything_engine::EngineRef>() {
        next.ext.insert(engine_ref);
    }
    if let Some(fixture) = ctx.session.ext.get::<assets::FixtureBase>() { next.ext.insert(fixture); }
    next.open_project(native)?;
    let targets_path = root.join("fusion-targets.json");
    let mut unavailable = Vec::new();
    if targets_path.is_file() {
        let bytes = std::fs::read(&targets_path).map_err(|e| ToolError::io(targets_path.display(), e))?;
        let targets: Vec<craft_anything_engine::target::TargetContext> = serde_json::from_slice(&bytes)
            .map_err(|e| ToolError::invalid(format!("Saved case targets are invalid: {e}")))?;
        if targets.len() > 128 { return Err(ToolError::invalid("Saved target count exceeds 128")); }
        for target in targets {
            if let Err(error) = next.restore_targets(std::slice::from_ref(&target)) {
                unavailable.push(json!({"target":target,"reason":error.message}));
            }
        }
        if !unavailable.is_empty() {
            write_atomic(&root.join("fusion-unrestored-targets.json"),
                &serde_json::to_vec_pretty(&unavailable).map_err(|e| ToolError::internal(e.to_string()))?)?;
        }
    }
    let _ = plugins::install(&mut next); // Restore the same configured original plugin routes.
    *ctx.session = next;
    Ok(ToolOutput::Value(json!({"bound":root,"reused":false,"project_root":project,"case_root":case,
        "restored_targets":ctx.session.targets().count(),"unavailable_targets":unavailable,
        "evidence_records":ctx.session.ledger_len(),
        "memory":"original Project evidence/unknowns/annotations/investigation/journal in this case"})))
}

fn case_tools() -> Vec<ToolSpec> {
    vec![ToolSpec { id:"fusion_case_open",title:"Bind or resume the current case",
        summary:"Before analysis, bind an existing outcome project and case by absolute paths. Creates/reopens its original Craft analysis Project; persisted evidence, target annotations, investigation memory and journal survive restart. Switching uses a fresh Session and never mixes old case records.",
        beginner:"Save analysis in the current project's case and resume it later.",
        toolset:Toolset::Core,effects:Effects::MUTATES_SESSION.union(Effects::WRITES_FILESYSTEM),
        requires:Requires::Nothing,input_schema:schema_of::<CaseOpen>,run:case_open }]
}

fn main() -> std::process::ExitCode {
    let mut args = std::env::args().skip(1);
    let mut state = None;
    let mut all_tools = false;
    let mut deep_mode = false;
    let mut host_consent = false;
    let mut asset_fixture = None;
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--all-tools" => all_tools = true,
            "--deep-mode" => deep_mode = true,
            // Same semantics as the original MCP's --allow-run: the external
            // host owns permission decisions. Without it, retain upstream refusal.
            "--allow-run" => host_consent = true,
            "--state-dir" => state = args.next().map(PathBuf::from),
            "--asset-test-base" => match args.next().ok_or_else(|| "Missing asset test base".to_string()).and_then(|v| assets::fixture_base(&v)) {
                Ok(value) => asset_fixture = Some(value),
                Err(error) => { eprintln!("{error}"); return std::process::ExitCode::FAILURE; }
            },
            "--version" => {
                println!("reverse-fusion-craft-mcp {} / Craft engine 0.6.1 / 8374ad71544f2cc44698ea74ef990aa31600bac6", env!("CARGO_PKG_VERSION"));
                return std::process::ExitCode::SUCCESS;
            }
            _ => { eprintln!("Unsupported argument: {arg}"); return std::process::ExitCode::FAILURE; }
        }
    }
    let Some(state) = state.filter(|p| p.is_absolute()) else {
        eprintln!("An absolute --state-dir for this checkout is required");
        return std::process::ExitCode::FAILURE;
    };
    let mut session = Session::isolated(&state);
    let settings_path = state.join("config.toml");
    if settings_path.is_file() {
        session.settings = craft_anything_engine::Settings::load_from(&settings_path);
    }
    // Persist provider/plugin configuration only in this checkout's MCP state.
    // Cache/project defaults remain owned even when local settings were edited.
    session.settings.engines.store_dir = Some(state.join("engines"));
    session.settings.projects_dir = Some(state.join("projects"));
    session.settings.auto_mode = false;
    session.deep_for_run = Some(deep_mode);
    session.fusion_require_project = true;
    if let Some(value) = asset_fixture { session.ext.insert(std::sync::Arc::new(value)); }
    if let Some(path) = std::env::var_os("GHIDRA_INSTALL_DIR") {
        session.settings.engines.ghidra.install_dir = Some(PathBuf::from(path));
    }
    if let Some(path) = std::env::var_os("JAVA_HOME") {
        session.settings.engines.ghidra.java_home = Some(PathBuf::from(path));
    }
    for (id, slot) in session.settings.engines.tools.entries_mut() {
        if let Some(path) = std::env::var_os(format!("REVERSE_FUSION_CRAFT_TOOL_{}", id.to_ascii_uppercase())) {
            let path = PathBuf::from(path);
            if !path.is_absolute() || !path.is_file() {
                eprintln!("Configured Craft {id} executable must be an existing absolute file");
                return std::process::ExitCode::FAILURE;
            }
            *slot = Some(path);
        }
    }
    let runtime_plugins = plugins::install(&mut session);
    let mut extra = case_tools(); extra.extend(assets::tools());
    let engine = Engine::shared_with(session, extra, runtime_plugins);
    let mut options = ServerOptions::from_env();
    options.all_tools = all_tools;
    options.allow_run = host_consent;
    match serve_stdio(engine, options) {
        Ok(()) => std::process::ExitCode::SUCCESS,
        Err(error) => { eprintln!("Craft MCP: {error}"); std::process::ExitCode::FAILURE }
    }
}
