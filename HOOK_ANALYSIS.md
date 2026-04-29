# Pre-Commit Hook Analysis: Shebang Checks

## Question
Should we remove `check-executables-have-shebangs` and `check-shebang-scripts-are-executable` hooks?

## Initial Analysis (Incorrect)
- ? "We're on Windows, these hooks check Unix shebangs, so remove them"

## Correct Analysis

### Deployment Environment
- **Development**: Windows (current)
- **Deployment**: Linux (Home Assistant in Docker) ?
- **Contributors**: May use Linux/Mac
- **CI/CD**: Runs on Linux (ubuntu-latest)

### Current State
```bash
$ find . -name "*.sh"
# No shell scripts currently
```

### Hook Purpose

**`check-executables-have-shebangs`**
- Prevents files marked executable without a shebang
- Catches mistakes like: `chmod +x script.txt` (forgot to add `#!/bin/bash`)

**`check-shebang-scripts-are-executable`**
- Ensures files with shebangs can actually be executed
- Catches mistakes like: Creating `script.sh` with `#!/bin/bash` but forgetting `chmod +x`

### Arguments FOR Keeping (Winner ?)

1. **Future-Proofing**
   - We might add Linux dev scripts (tests, builds, deploys)
   - Contributors might add shell scripts
   - Docker tooling often uses shell scripts

2. **Defensive Programming**
   - Zero cost when no .sh files exist (hooks skip instantly)
   - Prevents future mistakes
   - Catches accidental `git add --chmod=+x file.py`

3. **Cross-Platform Contributors**
   - Linux/Mac developers might contribute
   - They naturally write .sh scripts
   - Hooks catch permission mistakes

4. **CI/CD on Linux**
   - GitHub Actions runs on `ubuntu-latest`
   - If we add shell scripts for CI, hooks validate them

5. **Home Assistant Context**
   - HA runs on Linux (Docker)
   - Custom components might include helper scripts
   - Better to have hooks and not need them

### Arguments AGAINST (Weak)

1. ~~"No .sh files currently"~~ - But we might add them
2. ~~"Windows development"~~ - But we deploy on Linux
3. ~~"Performance"~~ - Negligible (hooks skip if no files match)

## Conclusion

**KEEP THE HOOKS** ?

The hooks are defensive, cost nothing when unused, and provide value if:
- Contributors add shell scripts
- We add Linux tooling
- Someone accidentally marks a file executable

## Decision

**Keep original `.pre-commit-config.yaml`** with all hooks intact.

The optimization was premature - these hooks serve as guards for future development even if we don't currently have .sh files.
