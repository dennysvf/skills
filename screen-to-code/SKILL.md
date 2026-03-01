---
name: screen-to-code
description: >
  Implements a UI interface from a screenshot/image, perfectly integrated with the project's existing
  design system. Use when the user provides a screenshot, mockup, wireframe, or image of a UI and wants
  it implemented as code. Triggers on: "implement this screen", "build this interface", "code this UI",
  "replicate this design", "implement from image", "screen to code", "clone this UI", or when the user
  attaches an image and asks to implement/build/create it. NOT for creating designs from scratch without
  a reference image.
---

# Screen-to-Code: Pixel-Perfect Implementation with Design System Integration

You are an expert UI engineer. When the user provides a screenshot or image of an interface, you will
implement it with PERFECT integration into their existing project's design system.

## Mandatory Execution Flow

**You MUST execute ALL phases in order. Never skip a phase.**

---

### PHASE 1: PROJECT ANALYSIS (always execute first)

Before writing ANY code, perform a complete audit of the existing project:

#### 1.1 Structure Discovery

```
Scan for and read these critical files (adapt paths to project):
- tailwind.config.* / postcss.config.*
- globals.css / global styles
- theme.ts / theme.js / theme configuration
- layout.tsx / layout.jsx (root and nested)
- next.config.* / vite.config.* / app config
- package.json (dependencies & scripts)
- tsconfig.json
```

#### 1.2 Component Library Mapping

```
Glob for all component files:
- src/components/**/*.{tsx,jsx}
- components/**/*.{tsx,jsx}
- app/**/components/**/*.{tsx,jsx}

For EACH component found, note:
- Props interface pattern
- Styling approach (Tailwind classes, CSS modules, styled-components)
- Naming convention (PascalCase, kebab-case folders, barrel exports)
- Variant patterns (cva, clsx, cn utility)
```

#### 1.3 Design Token Extraction

Extract and memorize:
- **Colors**: CSS variables (--primary, --background, etc.), Tailwind theme extensions
- **Typography**: Font families, sizes, weights used across components
- **Spacing**: Padding/margin patterns, gap values, container widths
- **Borders**: Border radius values, border colors, shadow patterns
- **Breakpoints**: Responsive breakpoints used in the project
- **Dark mode**: How dark mode is implemented (class-based, media query, CSS variables)

#### 1.4 Page Pattern Analysis

Read 2-3 existing pages/routes to understand:
- How pages import and compose layout components
- Data fetching patterns (server components, client components, hooks)
- How mock/static data is structured and consumed
- State management approach
- Common page structure (header, content area, sidebar patterns)

#### 1.5 Existing Conventions Checklist

Identify and document:
- [ ] File naming: kebab-case? PascalCase? index.tsx barrel?
- [ ] Import style: absolute (@/) or relative (../)
- [ ] Export style: default export or named export
- [ ] Type location: colocated, /types folder, or inline
- [ ] Mock location: /mocks, /data, __mocks__, or colocated
- [ ] Component structure: single file or folder with index + styles
- [ ] Utility usage: cn(), clsx(), twMerge()
- [ ] Icon library: lucide-react, heroicons, react-icons, etc.

> **OUTPUT**: Before proceeding, create a mental summary of ALL findings.
> You must be able to answer: "If the original developer wrote this component,
> what patterns would they follow?"

---

### PHASE 2: IMAGE ANALYSIS

#### 2.1 Visual Decomposition

Analyze the provided image and identify:
- **Layout structure**: Grid/flex areas, columns, rows, sections
- **Component hierarchy**: What are the top-level sections? What nests inside what?
- **Data elements**: Every piece of text, number, date, status, metric visible
- **Interactive elements**: Buttons, inputs, dropdowns, tabs, toggles
- **Visual details**: Colors, shadows, borders, spacing, icons, badges, avatars

#### 2.2 Component Mapping

Map each visual element to:
1. An **existing project component** (prefer reuse), OR
2. A **new component to create** (following existing patterns)

#### 2.3 Data Structure Planning

From every dynamic element visible in the image, plan:
- TypeScript interfaces needed
- Mock data structure and values
- Which data feeds which component

---

### PHASE 3: TYPE DEFINITIONS & MOCKS

#### 3.1 Create TypeScript Interfaces

```
Rules:
- Follow the EXACT type definition pattern found in Phase 1
- Place in the location identified in Phase 1 (e.g., /types, colocated)
- Use the project's naming convention for types/interfaces
- Every dynamic value visible in the image MUST have a corresponding type field
```

#### 3.2 Create Mock Data

```
Rules:
- Place mocks in the location identified in Phase 1 (e.g., /mocks, /data)
- Mock data MUST be typed with the interfaces from 3.1
- Values must be realistic and contextually appropriate
- Structure must match how the project typically organizes mock data
- Export pattern must match existing mock files
```

**CRITICAL RULE**: Every text, number, status, date, metric, label, or any
dynamic content visible in the image MUST exist in the mock data. Zero
hardcoded values in components.

---

### PHASE 4: COMPONENT IMPLEMENTATION

#### 4.1 Implementation Rules

1. **Reuse first**: Use existing components (Button, Card, Table, Badge, etc.)
2. **Style consistently**: Use the SAME Tailwind classes, CSS variables, and patterns
3. **Follow structure**: Match the file/folder organization of existing components
4. **Type everything**: All props must be typed; no `any` types
5. **Consume mocks**: Components receive data via typed props, never hardcoded
6. **Responsive**: Use the same breakpoints and responsive patterns
7. **Theme-aware**: Support dark/light mode using the project's approach
8. **Accessible**: Maintain the accessibility level of existing components

#### 4.2 Implementation Order

1. Create type definitions and interfaces
2. Create mock data files
3. Create sub-components (smallest first, bottom-up)
4. Create the main page/view component
5. Wire up data flow (mocks → page → sub-components via props)
6. Add to routing/navigation if applicable

#### 4.3 Code Quality Gates

Before finishing, verify:
- [ ] No hardcoded strings/numbers for dynamic data (ALL from mocks)
- [ ] All components follow project naming convention
- [ ] Import paths match project convention (@ aliases, relative, etc.)
- [ ] Tailwind classes match project's style patterns
- [ ] Dark mode works if project supports it
- [ ] Responsive breakpoints match project's patterns
- [ ] Component props are fully typed
- [ ] File locations follow project structure
- [ ] Existing components are reused where possible

---

### PHASE 5: INTEGRATION & VERIFICATION

#### 5.1 Integration Steps

- Add route/page entry if using file-based routing
- Add navigation link if applicable (sidebar, header menu)
- Ensure all imports resolve correctly
- Verify the component tree compiles without errors

#### 5.2 Final Summary

Provide to the user:
1. List of all files created/modified
2. How to navigate to the new page/component
3. Brief note on which existing components were reused
4. Any components that might need real API data in the future

---

## Anti-Patterns (NEVER do these)

| Anti-Pattern | Correct Approach |
|---|---|
| Hardcoded text in JSX | Import from mock data |
| Hardcoded numbers/metrics | Import from mock data |
| Inline color values (#hex, rgb) | Use CSS variables / Tailwind theme |
| New font-family declarations | Use project's existing fonts |
| Custom breakpoints | Use project's breakpoints |
| Installing new dependencies | Use existing packages first |
| Ignoring dark mode | Support the project's theme system |
| Creating duplicate components | Reuse existing ones |
| Different naming conventions | Match the project exactly |
| Skipping TypeScript types | Type everything |

## Reference Workflow

See `references/analysis-checklist.md` for a detailed checklist you can follow
during the project analysis phase.
