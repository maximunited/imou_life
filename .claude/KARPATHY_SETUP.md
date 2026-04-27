# Karpathy Guidelines Setup

This document explains how the Karpathy Guidelines are installed and how to keep them updated.

## What Was Installed

The Karpathy Guidelines have been integrated into this project as a **git submodule** with the following setup:

### Files and Directories

1. **Git Submodule** (`.claude/skills/karpathy-guidelines/`)
   - Source: https://github.com/forrestchang/andrej-karpathy-skills
   - Location: `.claude/skills/karpathy-guidelines/`
   - Contains the full repository with examples, documentation, and skill definitions

2. **Skill Junction** (`.claude/skills/karpathy/`)
   - Windows junction pointing to: `karpathy-guidelines/skills/karpathy-guidelines/`
   - Makes the skill directly accessible to Claude Code
   - Excluded from git tracking (in `.gitignore`)

3. **Documentation**
   - `.claude/skills/README.md` - Skills directory documentation
   - `CLAUDE.md` - Updated with Karpathy Guidelines reference
   - `.claude/KARPATHY_SETUP.md` - This file

4. **Git Configuration**
   - `.gitmodules` - Submodule configuration
   - `.gitignore` - Excludes the karpathy junction

## How to Use

### In Claude Code

Simply reference the guidelines when asking Claude to write code:

```
Please follow the karpathy guidelines when implementing this feature
```

Or invoke the skill directly:
```
/karpathy-guidelines
```

### Four Core Principles

1. **Think Before Coding**
   - Don't assume, don't hide confusion, surface tradeoffs
   - State assumptions explicitly, ask if uncertain

2. **Simplicity First**
   - Minimum code that solves the problem, nothing speculative
   - No features beyond what was asked

3. **Surgical Changes**
   - Touch only what you must, clean up only your own mess
   - Don't "improve" adjacent code or refactor unrelated things

4. **Goal-Driven Execution**
   - Define success criteria, loop until verified
   - Transform tasks into verifiable goals with tests

## How to Update

The guidelines are maintained as a git submodule, so you can update them independently from your project code.

### Update to Latest Version

```bash
# Navigate to project root
cd /c/Users/Maxim/Projects/imou_life

# Update the karpathy-guidelines submodule
git submodule update --remote .claude/skills/karpathy-guidelines

# Or update all submodules
git submodule update --remote

# Review the changes
cd .claude/skills/karpathy-guidelines
git log --oneline -5

# Return to project root
cd /c/Users/Maxim/Projects/imou_life

# Commit the submodule update
git add .claude/skills/karpathy-guidelines
git commit -m "chore: update karpathy guidelines to latest version"
```

### Pull Updates After Cloning

If you clone this repository on another machine:

```bash
# Clone with submodules
git clone --recurse-submodules <repository-url>

# Or if already cloned, initialize submodules
git submodule update --init --recursive

# Recreate the Windows junction (on Windows)
mklink /J .claude\skills\karpathy .claude\skills\karpathy-guidelines\skills\karpathy-guidelines
```

## Directory Structure

```
imou_life/
├── .claude/
│   ├── skills/
│   │   ├── karpathy-guidelines/     # Git submodule
│   │   │   ├── .claude-plugin/
│   │   │   ├── .cursor/
│   │   │   ├── skills/
│   │   │   │   └── karpathy-guidelines/
│   │   │   │       └── SKILL.md     # Skill definition
│   │   │   ├── CLAUDE.md            # Mergeable guidelines
│   │   │   ├── EXAMPLES.md          # Examples
│   │   │   └── README.md
│   │   ├── karpathy/                # Junction (Windows) → karpathy-guidelines/skills/karpathy-guidelines/
│   │   │   └── SKILL.md             # Accessible via junction
│   │   └── README.md                # Skills directory documentation
│   ├── KARPATHY_SETUP.md            # This file
│   └── settings.local.json
├── CLAUDE.md                         # Project CLAUDE.md (references karpathy)
└── .gitmodules                       # Git submodule configuration
```

## Benefits of This Setup

1. **Always Up-to-Date**: Update with `git submodule update --remote`
2. **Version Controlled**: Submodule commit is tracked in your project
3. **Easy to Share**: Anyone cloning your repo gets the guidelines
4. **Flexible**: Can pin to specific versions or track latest
5. **Maintainable**: Changes in upstream repo can be pulled easily

## Resources

- **Repository**: https://github.com/forrestchang/andrej-karpathy-skills
- **Original Tweet**: https://x.com/karpathy/status/2015883857489522876
- **Examples**: `.claude/skills/karpathy-guidelines/EXAMPLES.md`
- **Full Guidelines**: `.claude/skills/karpathy/SKILL.md`

## Troubleshooting

### Junction Not Working

If the junction breaks, recreate it:

```bash
# Remove old junction
rmdir .claude\skills\karpathy

# Create new junction
mklink /J .claude\skills\karpathy .claude\skills\karpathy-guidelines\skills\karpathy-guidelines
```

### Submodule Not Initialized

```bash
git submodule update --init --recursive
```

### Submodule Out of Sync

```bash
cd .claude/skills/karpathy-guidelines
git checkout main
git pull origin main
cd ../../../
git add .claude/skills/karpathy-guidelines
git commit -m "chore: sync karpathy guidelines"
```
