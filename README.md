# Claude Code Skills

Custom skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — extending the CLI with specialized UI implementation workflows.

## Skills

| Skill | Description |
|-------|-------------|
| **screen-to-code** | Implements UI interfaces from screenshots/images with perfect integration into the project's existing design system. Executes 5 mandatory phases: project analysis, image analysis, types & mocks creation, component implementation, and integration. |
| **nextjs-ui-builder** | Implements production-ready Next.js interfaces from images or descriptions using Next.js + TypeScript + Tailwind CSS + CVA. Produces strongly typed, accessible, dark/light theme-aware components following the project's design system. |

## Installation

### Option 1: Clone and install via `.skill` file (recommended)

```bash
git clone https://github.com/dennysvf/skills.git
cd skills
claude skill install ./screen-to-code.skill
claude skill install ./nextjs-ui-builder.skill
```

### Option 2: Symlink

```bash
# Linux / macOS
git clone https://github.com/dennysvf/skills.git
ln -s "$(pwd)/skills/screen-to-code" ~/.claude/skills/screen-to-code
ln -s "$(pwd)/skills/nextjs-ui-builder" ~/.claude/skills/nextjs-ui-builder

# Windows (PowerShell as Admin)
git clone https://github.com/dennysvf/skills.git
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\screen-to-code" -Target "$(Get-Location)\skills\screen-to-code"
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\nextjs-ui-builder" -Target "$(Get-Location)\skills\nextjs-ui-builder"
```

### Verify installation

Start a new Claude Code session and check if the skills appear when you use `/help` or when they auto-trigger.

## Usage

### screen-to-code

Provide a screenshot or image of any UI and ask Claude to implement it:

- "implement this screen"
- "build this interface"
- "code this UI"
- "clone this UI"

The skill will analyze your project's design system first, then implement the UI matching your existing patterns, components, and conventions.

### nextjs-ui-builder

Provide an image or description of a Next.js interface:

- "implement this interface"
- "build this UI from the image"
- "create this component"
- "convert this design to code"

Outputs production-ready components with CVA variants, TypeScript types, mock data, and full dark/light theme support.

## Project Structure

```
├── screen-to-code.skill                        # Packaged skill file
├── screen-to-code/
│   ├── SKILL.md                                # Main skill instructions
│   └── references/
│       └── analysis-checklist.md               # Project analysis checklist
├── nextjs-ui-builder.skill                     # Packaged skill file
└── nextjs-ui-builder/
    ├── SKILL.md                                # Workflow & quality checklist
    └── references/
        ├── design-system.md                    # Color tokens, component variants, theme setup
        └── component-patterns.md               # CVA templates, TypeScript patterns, a11y
```

## Uninstall

```bash
# Linux / macOS
rm -rf ~/.claude/skills/screen-to-code
rm -rf ~/.claude/skills/nextjs-ui-builder

# Windows (PowerShell)
Remove-Item -Recurse "$env:USERPROFILE\.claude\skills\screen-to-code"
Remove-Item -Recurse "$env:USERPROFILE\.claude\skills\nextjs-ui-builder"
```

## License

MIT
