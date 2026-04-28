# Claude Code Skills

This directory contains skills for Claude Code.

## Karpathy Guidelines

The Karpathy Guidelines are installed as a git submodule and provide behavioral guidelines to reduce common LLM coding mistakes.

### Installation

Already installed! The guidelines are available at:
- **Submodule**: `.claude/skills/karpathy-guidelines/` (git submodule)
- **Skill**: `.claude/skills/karpathy/` (Windows junction pointing to the skill)

### Usage

Use the skill by invoking:
```
/karpathy-guidelines
```

Or reference the guidelines when asking Claude to write, review, or refactor code.

### Updating

To update the Karpathy Guidelines to the latest version:

```bash
# Update the submodule
git submodule update --remote .claude/skills/karpathy-guidelines

# Or update all submodules
git submodule update --remote

# Commit the update
git add .claude/skills/karpathy-guidelines
git commit -m "chore: update karpathy guidelines"
```

### Core Principles

1. **Think Before Coding** - Don't assume. Don't hide confusion. Surface tradeoffs.
2. **Simplicity First** - Minimum code that solves the problem. Nothing speculative.
3. **Surgical Changes** - Touch only what you must. Clean up only your own mess.
4. **Goal-Driven Execution** - Define success criteria. Loop until verified.

### Documentation

- Full guidelines: `.claude/skills/karpathy/SKILL.md`
- Examples: `.claude/skills/karpathy-guidelines/EXAMPLES.md`
- Cursor integration: `.claude/skills/karpathy-guidelines/CURSOR.md`

### Structure

```
.claude/skills/
├── karpathy-guidelines/         # Git submodule (source repository)
│   ├── CLAUDE.md               # Guidelines for merging
│   ├── EXAMPLES.md             # Practical examples
│   ├── skills/
│   │   └── karpathy-guidelines/
│   │       └── SKILL.md        # Claude Code skill definition
│   └── .cursor/                # Cursor editor rules
│       └── rules/
└── karpathy/                   # Junction → karpathy-guidelines/skills/karpathy-guidelines/
    └── SKILL.md                # Accessible skill file
```

### Notes

- The `karpathy/` directory is a Windows junction (symbolic link) pointing to the skill in the submodule
- Do not edit files in `karpathy/` - edit in `karpathy-guidelines/` instead
- The junction is excluded from git (.gitignore) but will persist locally
