//! Original pinned Craft MCP protocol and tools; no second model or Study loop.
#![forbid(unsafe_code)]
use craft_anything_engine::{Engine, Session, plugins};
use craft_anything_mcp::{ServerOptions, serve_stdio};
use std::path::PathBuf;

fn main() -> std::process::ExitCode {
    let mut args = std::env::args().skip(1);
    let mut state = None;
    let mut all_tools = false;
    let mut deep_mode = false;
    let mut host_consent = false;
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--all-tools" => all_tools = true,
            "--deep-mode" => deep_mode = true,
            // Same semantics as the original MCP's --allow-run: the external
            // host owns permission decisions. Without it, retain upstream refusal.
            "--allow-run" => host_consent = true,
            "--state-dir" => state = args.next().map(PathBuf::from),
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
    if let Some(path) = std::env::var_os("GHIDRA_INSTALL_DIR") {
        session.settings.engines.ghidra.install_dir = Some(PathBuf::from(path));
    }
    if let Some(path) = std::env::var_os("JAVA_HOME") {
        session.settings.engines.ghidra.java_home = Some(PathBuf::from(path));
    }
    let runtime_plugins = plugins::install(&mut session);
    let engine = Engine::shared_with(session, Vec::new(), runtime_plugins);
    let mut options = ServerOptions::from_env();
    options.all_tools = all_tools;
    options.allow_run = host_consent;
    match serve_stdio(engine, options) {
        Ok(()) => std::process::ExitCode::SUCCESS,
        Err(error) => { eprintln!("Craft MCP: {error}"); std::process::ExitCode::FAILURE }
    }
}
