/**
 * Optional OpenWolf hook runner.
 *
 * .wolf/ is gitignored, so hook scripts may be missing on fresh clones.
 * Exit 0 quietly when the target script is absent so Claude Code hooks
 * do not fail or block tool use.
 */
const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const hookName = process.argv[2];
if (!hookName || hookName.includes("..") || path.isAbsolute(hookName)) {
  process.exit(0);
}

const projectDir =
  process.env.CLAUDE_PROJECT_DIR ||
  process.env.CODEX_PROJECT_ROOT ||
  process.env.OPENWOLF_PROJECT_ROOT ||
  process.cwd();

const scriptPath = path.join(projectDir, ".wolf", "hooks", hookName);
if (!fs.existsSync(scriptPath)) {
  process.exit(0);
}

const result = spawnSync(process.execPath, [scriptPath], {
  stdio: "inherit",
  env: process.env,
});
process.exit(result.status === null ? 1 : result.status);
