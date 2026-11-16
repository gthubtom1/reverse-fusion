//! Explicit one-call asset generation using original Craft tools and producers.
//! Results stay in case staging; they never write the formal candidate directly.
use craft_anything_engine::{CallOptions, Engine, Session};
use craft_anything_engine::inbox::InboxDir;
use craft_anything_engine::project::write_atomic;
use craft_anything_engine::tool::{Ctx, Effects, Requires, ToolOutput, ToolSpec, Toolset, parse_params, schema_of};
use craft_anything_engine::tools::asset_tools::AssetKeys;
use craft_anything_engine::workspace::{TargetRef, Workspace};
use craft_anything_engines::assets::{AssetProviders, AssetRequest, Catalogue, Shape, fal};
use craft_anything_evidence::{ErrorCode, ToolError, sha256_hex};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::path::{Component, Path, PathBuf};
use std::sync::Arc;

const KEY_ENV: &str = "REVERSE_FUSION_CRAFT_FAL_KEY";

/// Only the maintainer's explicit loopback transport qualifier can set this.
/// It always uses a synthetic key and never reads a real environment credential.
pub struct FixtureBase(pub String);

pub fn fixture_base(value: &str) -> Result<FixtureBase, String> {
    let address = value.strip_prefix("http://").ok_or("Asset fixture base must be an explicit HTTP loopback socket")?;
    let socket: std::net::SocketAddr = address.parse().map_err(|_| "Asset fixture base must contain only a loopback IP and port")?;
    if !socket.ip().is_loopback() || socket.port() == 0 {
        return Err("Asset fixture base must use loopback and a nonzero port".into());
    }
    Ok(FixtureBase(format!("http://{socket}")))
}

#[derive(Deserialize, Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
enum Kind { Image, Model3d }

#[derive(Deserialize, Serialize, JsonSchema)]
#[serde(deny_unknown_fields)]
struct Generate {
    kind: Kind,
    /// Relative PNG or GLB output inside a fresh case staging workspace, never the candidate.
    save_as: String,
    /// Description for an image, or for a 3D model when no reference image is supplied.
    #[serde(default)]
    prompt: String,
    /// For model3d: an HTTP(S) image URL or existing case-relative PNG/JPEG/WebP.
    #[serde(default)]
    image: String,
    /// This invocation's explicit maximum listed cost in USD; not a persistent spending grant.
    budget_usd: f64,
    /// The host confirms this operation is within the user's actual paid-generation permission.
    allow_paid: bool,
    #[serde(default)]
    shape: Option<String>,
    #[serde(default)]
    textured: Option<bool>,
    #[serde(default)]
    faces: Option<u32>,
}

pub fn tools() -> Vec<ToolSpec> {
    vec![ToolSpec { id: "fusion_asset_generate", title: "Generate an explicitly budgeted staged asset",
        summary: "After fusion_case_open, use the original Craft image or 3D tool and fal.ai producer in a fresh case-local staging Workspace. Requires explicit per-call budget, allow_paid and REVERSE_FUSION_CRAFT_FAL_KEY in this server's environment; never reads old keychains. Host owns actual paid-operation permission. Returns original costs, files and digests. Does not edit the candidate; integrate through reviewed Spec/native commands.",
        beginner: "Make a picture or 3D model within an approved budget and save it separately for review.",
        toolset: Toolset::Core,
        effects: Effects::ACCESSES_NETWORK.union(Effects::WRITES_FILESYSTEM).union(Effects::MUTATES_SESSION),
        requires: Requires::Nothing, input_schema: schema_of::<Generate>, run: generate }]
}

fn generate(ctx: &mut Ctx<'_>, params: Value) -> Result<ToolOutput, ToolError> {
    let p: Generate = parse_params(params)?;
    bound_case(ctx.session)?;
    if !p.allow_paid { return Err(ToolError::new(ErrorCode::NoPermission, "Asset generation needs explicit host-confirmed allow_paid for this invocation.")); }
    let fixture = ctx.session.ext.get::<FixtureBase>();
    let key = if fixture.is_some() { "rf-local-fixture-key".to_string() } else {
        std::env::var(KEY_ENV).map_err(|_| ToolError::new(ErrorCode::BadSettings,
            format!("No explicit asset key is available in {KEY_ENV}."))
            .with_remediation("Supply a dedicated fal.ai key to the selected server environment and reconnect; never put it in tool parameters, prompts or receipts."))?
    };
    if key.trim().is_empty() || key.len() > 512 || key.chars().any(char::is_whitespace) {
        return Err(ToolError::new(ErrorCode::BadSettings, "The explicit asset key has an invalid format; its value is not recorded."));
    }
    let mut providers = AssetProviders::built_in();
    if let Some(base) = &fixture { providers.register(Arc::new(fal::Fal::with_base(&base.0))); }
    staged(ctx, p, &key, providers, fixture.is_some())
}

fn clean_value(value: &mut Value, key: &str) {
    match value {
        Value::String(text) => *text = text.replace(key, "[REDACTED]"),
        Value::Array(values) => values.iter_mut().for_each(|v| clean_value(v, key)),
        Value::Object(values) => values.values_mut().for_each(|v| clean_value(v, key)),
        _ => (),
    }
}

fn clean_error(mut error: ToolError, key: &str) -> ToolError {
    error.message = error.message.replace(key, "[REDACTED]");
    error.remediation = error.remediation.map(|text| text.replace(key, "[REDACTED]"));
    if let Some(value) = &mut error.details { clean_value(value, key); }
    error
}

fn bound_case(session: &Session) -> Result<PathBuf, ToolError> {
    let project = session.project.as_ref().ok_or_else(|| ToolError::unavailable("Call fusion_case_open before asset generation."))?;
    let bytes = std::fs::read(project.root.join("fusion-binding.json"))
        .map_err(|_| ToolError::invalid("The selected Project has no owned case binding; call fusion_case_open."))?;
    let binding: super::Binding = serde_json::from_slice(&bytes).map_err(|_| ToolError::invalid("Invalid case binding"))?;
    let case = binding.case_root.canonicalize().map_err(|e| ToolError::io("Bound case", e))?;
    if project.root != case.join("craft-analysis.cany") || !case.starts_with(&binding.project_root) {
        return Err(ToolError::invalid("The selected analysis Project does not match its outcome case"));
    }
    Ok(case)
}

fn output_path(p: &Generate) -> Result<(), ToolError> {
    let path = Path::new(&p.save_as);
    let ext = if matches!(p.kind, Kind::Image) { "png" } else { "glb" };
    if p.save_as.is_empty() || p.save_as.len() > 240 || p.save_as.contains(['\\', ':'])
        || path.is_absolute() || !path.components().all(|c| matches!(c, Component::Normal(_)))
        || !path.extension().is_some_and(|e| e.eq_ignore_ascii_case(ext)) {
        return Err(ToolError::invalid(format!("save_as must be a relative .{ext} file strictly inside the fresh staging app/")));
    }
    Ok(())
}

fn staged(ctx: &mut Ctx<'_>, p: Generate, key: &str, providers: AssetProviders, fixture: bool) -> Result<ToolOutput, ToolError> {
    let case = bound_case(ctx.session)?;
    output_path(&p)?;
    if !p.allow_paid { return Err(ToolError::new(ErrorCode::NoPermission, "Asset generation needs explicit host-confirmed allow_paid for this invocation.")); }
    if !p.budget_usd.is_finite() || p.budget_usd <= 0.0 || p.budget_usd > 1000.0 {
        return Err(ToolError::invalid("budget_usd must be finite, positive and at most 1000 USD for one invocation"));
    }
    let request = serde_json::to_value(&p).map_err(|e| ToolError::internal(e.to_string()))?;
    if request.to_string().contains(key) || [&p.prompt, &p.image, &p.save_as].iter().any(|s| s.contains(key)) {
        return Err(ToolError::invalid("Do not include the asset credential in prompts, image URLs or output paths."));
    }
    let catalogue = Catalogue::built_in();
    let image_model = catalogue.image_model(ctx.session.settings.assets.image_model.as_deref())?;
    let shape = p.shape.as_deref().unwrap_or("square");
    let shape = Shape::parse(shape).ok_or_else(|| ToolError::invalid("shape must be square, wide or tall"))?;
    let picture = AssetRequest::Image { model: image_model, prompt: &p.prompt, shape };
    let model = catalogue.model_3d(None)?;
    let faces = p.faces.unwrap_or(3000);
    if matches!(p.kind, Kind::Model3d) && !model.faces().contains(&faces) {
        return Err(ToolError::invalid("faces is outside the original model's supported range"));
    }
    if matches!(p.kind, Kind::Image) || p.image.trim().is_empty() {
        if p.prompt.trim().is_empty() || p.prompt.len() > 2000 { return Err(ToolError::invalid("prompt must be 1..=2000 characters")); }
    }
    let request_3d = AssetRequest::Model3d { model, image_url: "", textured: p.textured.unwrap_or(true), faces };
    let estimate = match p.kind {
        Kind::Image => providers.for_request(&picture)?.estimate(&picture)?,
        Kind::Model3d => providers.for_request(&request_3d)?.estimate(&request_3d)?
            + if p.image.trim().is_empty() { providers.for_request(&picture)?.estimate(&picture)? } else { 0.0 },
    };
    if estimate > p.budget_usd + 1e-9 {
        return Err(ToolError::new(ErrorCode::OverLimit,
            format!("Original provider's listed estimate ${estimate:.4} exceeds this invocation's ${:.4} budget; no generation started.", p.budget_usd)));
    }
    let local_image = if !p.image.is_empty() && !p.image.starts_with("https://") && !p.image.starts_with("http://") {
        let relative = Path::new(&p.image);
        if relative.is_absolute() || !relative.components().all(|c| matches!(c, Component::Normal(_))) {
            return Err(ToolError::invalid("Local image must be a case-relative path"));
        }
        let source = case.join(relative).canonicalize().map_err(|e| ToolError::io("Asset input image", e))?;
        if !source.starts_with(&case) || !source.is_file() || std::fs::metadata(&source).map_err(|e| ToolError::io("Asset input image", e))?.len() > 20 << 20 {
            return Err(ToolError::invalid("Input image must be an existing file inside the current case, at most 20 MiB"));
        }
        let ext = source.extension().and_then(|v| v.to_str()).unwrap_or("");
        if !["png", "jpg", "jpeg", "webp"].iter().any(|v| ext.eq_ignore_ascii_case(v)) { return Err(ToolError::invalid("Input image must be PNG, JPEG or WebP")); }
        Some(source)
    } else { None };
    if ctx.cancel.is_cancelled() { return Err(ToolError::cancelled()); }
    let directory = case.join("asset-staging");
    std::fs::create_dir_all(&directory).map_err(|e| ToolError::io("Asset staging directory", e))?;
    if directory.canonicalize().map_err(|e| ToolError::io("Asset staging directory", e))?.parent() != Some(case.as_path()) {
        return Err(ToolError::invalid("Asset staging directory must not link outside the current case"));
    }
    let mut workspace = Workspace::create(&directory, "asset", "One explicitly budgeted staged asset; candidate integration requires reviewed Spec/native commands", TargetRef::None)?;
    workspace.set_person(|m| { m.generate_assets = true; m.asset_budget_usd = p.budget_usd; })?;
    let mut image = p.image.clone();
    if let Some(source) = local_image {
        let relative = format!("reference/input.{}", source.extension().and_then(|v| v.to_str()).unwrap_or("png"));
        std::fs::create_dir_all(workspace.root.join("reference")).map_err(|e| ToolError::io("Asset reference directory", e))?;
        std::fs::copy(&source, workspace.root.join(&relative)).map_err(|e| ToolError::io("Asset reference copy", e))?;
        image = relative;
    }
    let mut session = Session::new(ctx.session.settings.clone());
    session.settings.auto_mode = false;
    session.ext.insert(Arc::new(InboxDir(workspace.inbox_dir())));
    session.ext.insert(Arc::new(AssetKeys([("fal".to_string(), key.to_string())].into())));
    session.ext.insert(Arc::new(providers));
    let engine = Engine::new(session);
    let (tool, params) = match p.kind {
        Kind::Image => ("assets_image_generate", json!({"prompt":p.prompt,"save_as":p.save_as,"shape":p.shape})),
        Kind::Model3d => ("assets_model_generate", json!({"prompt":p.prompt,"image":image,"save_as":p.save_as,"textured":p.textured,"faces":p.faces})),
    };
    let receipt = workspace.root.join("fusion-asset-result.json");
    let mut record = json!({"status":"started","original_tool":tool,"transport":if fixture {"loopback-fixture"} else {"fal.ai"},
        "staging_workspace":workspace.root,"request":request,"listed_estimate_usd":estimate,
        "secret_policy":"explicit process environment only; no credential in request or receipt",
        "candidate_modified":false,"integration":"review asset, then integrate using an approved Spec/native command"});
    write_atomic(&receipt, &serde_json::to_vec_pretty(&record).map_err(|e| ToolError::internal(e.to_string()))?)?;
    let result = engine.call(tool, params, CallOptions::new(ctx.caller).with_cancel(ctx.cancel.clone()).with_progress(ctx.progress));
    match result {
        Ok(output) => {
            let mut value = output.to_json(); clean_value(&mut value, key);
            record["status"] = json!("generated"); record["original_result"] = value;
            let app = workspace.app_dir();
            let mut files = Vec::new();
            collect(&app, &app, &mut files)?;
            record["files"] = json!(files);
            write_atomic(&receipt, &serde_json::to_vec_pretty(&record).map_err(|e| ToolError::internal(e.to_string()))?)?;
            record["receipt"] = json!(receipt);
            Ok(ToolOutput::Value(record))
        }
        Err(error) => {
            let mut error = clean_error(error, key);
            record["status"] = json!("failed"); record["original_error"] = serde_json::to_value(&error).map_err(|e| ToolError::internal(e.to_string()))?;
            write_atomic(&receipt, &serde_json::to_vec_pretty(&record).map_err(|e| ToolError::internal(e.to_string()))?)?;
            error.details = Some(json!({"original_details":error.details,"staging_workspace":workspace.root,"receipt":receipt}));
            Err(error)
        }
    }
}

fn collect(root: &Path, path: &Path, files: &mut Vec<Value>) -> Result<(), ToolError> {
    if !path.exists() { return Ok(()); }
    for entry in std::fs::read_dir(path).map_err(|e| ToolError::io("Asset outputs", e))? {
        let entry = entry.map_err(|e| ToolError::io("Asset output", e))?;
        let kind = entry.file_type().map_err(|e| ToolError::io("Asset output", e))?;
        if kind.is_symlink() { return Err(ToolError::invalid("Generated assets must not contain symlinks")); }
        if kind.is_dir() { collect(root, &entry.path(), files)?; }
        else if kind.is_file() {
            let bytes = std::fs::read(entry.path()).map_err(|e| ToolError::io("Asset output", e))?;
            files.push(json!({"path":entry.path().strip_prefix(root).map_err(|e| ToolError::internal(e.to_string()))?.to_string_lossy(),
                "sha256":sha256_hex(&bytes),"bytes":bytes.len()}));
        }
    }
    Ok(())
}
