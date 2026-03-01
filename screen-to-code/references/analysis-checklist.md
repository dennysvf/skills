# Project Analysis Checklist

Use this checklist during Phase 1 to ensure complete project understanding.

## 1. Configuration Files

- [ ] `package.json` — dependencies, scripts, project name
- [ ] `tsconfig.json` — path aliases (@/), strict mode, target
- [ ] `tailwind.config.*` — theme extensions, custom colors, fonts, plugins
- [ ] `postcss.config.*` — plugins
- [ ] `next.config.*` or `vite.config.*` — framework config
- [ ] `.eslintrc.*` / `prettier.*` — code style rules

## 2. Global Styles & Theme

- [ ] `globals.css` / `global.css` — CSS variables, base styles
- [ ] `theme.ts` / `theme.js` — theme object if exists
- [ ] CSS variable naming: `--primary`, `--background`, `--foreground`, etc.
- [ ] Dark mode implementation: `.dark` class, `data-theme`, or media query
- [ ] Base font, font-size scale, line-height patterns
- [ ] Color palette: primary, secondary, accent, destructive, muted
- [ ] Border radius tokens: `--radius` or Tailwind rounded-* usage
- [ ] Shadow patterns: shadow-sm, shadow-md, custom shadows

## 3. Component Patterns

### Naming
- [ ] Files: PascalCase.tsx, kebab-case.tsx, or folder/index.tsx
- [ ] Components: PascalCase function names
- [ ] Props: ComponentNameProps interface
- [ ] Exports: default vs named

### Styling
- [ ] Tailwind utility classes (most common)
- [ ] CSS Modules (*.module.css)
- [ ] Styled-components / Emotion
- [ ] cn() / clsx() / twMerge() utility function
- [ ] class-variance-authority (cva) for variants

### Structure
- [ ] Single file components vs folder-based
- [ ] Colocated styles vs global
- [ ] Colocated types vs /types directory
- [ ] Barrel exports (index.ts re-exports)

## 4. Layout Architecture

- [ ] Root layout: `app/layout.tsx` or `_app.tsx`
- [ ] Nested layouts per route group
- [ ] Shared components: Header, Sidebar, Footer
- [ ] Container/wrapper patterns and max-widths
- [ ] Page padding/margin patterns

## 5. Data Patterns

### Types
- [ ] Location: `/types`, `/lib/types`, colocated
- [ ] Convention: `interface` vs `type`
- [ ] Naming: `IUser`, `UserType`, `User`
- [ ] Shared types vs component-specific

### Mocks / Static Data
- [ ] Location: `/mocks`, `/data`, `/lib/data`, `__mocks__`
- [ ] Export pattern: named exports, default export, const array
- [ ] Type annotations on mock data

### Data Fetching
- [ ] Server Components (RSC) vs Client Components
- [ ] Custom hooks pattern
- [ ] API route structure

## 6. UI Component Library

### Common Components to Identify
- [ ] Button — variants, sizes, loading state
- [ ] Card — structure (header, content, footer)
- [ ] Input / Form — validation, labels, error states
- [ ] Table — headers, rows, pagination
- [ ] Badge / Tag — color variants
- [ ] Avatar — sizes, fallback
- [ ] Dialog / Modal — trigger, content
- [ ] Dropdown / Select — options pattern
- [ ] Tabs — trigger, content
- [ ] Toast / Alert — variants

### Icon Library
- [ ] lucide-react
- [ ] @heroicons/react
- [ ] react-icons
- [ ] Custom SVG components
- [ ] Icon sizing convention

## 7. Responsive Design

- [ ] Mobile-first or desktop-first
- [ ] Breakpoints: sm (640), md (768), lg (1024), xl (1280), 2xl (1536)
- [ ] Custom breakpoints in tailwind config
- [ ] Responsive patterns: hide/show, stack/row, resize

## 8. Accessibility

- [ ] aria-label usage
- [ ] Semantic HTML (nav, main, aside, section)
- [ ] Focus management
- [ ] Color contrast awareness
- [ ] Screen reader considerations

## Quick Reference: Common File Locations

```
src/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   └── (routes)/           # Route groups
├── components/
│   ├── ui/                 # Base UI components (Button, Card, etc.)
│   └── (feature)/          # Feature-specific components
├── lib/
│   ├── utils.ts            # Utility functions (cn, formatDate, etc.)
│   └── constants.ts        # App constants
├── types/                  # TypeScript type definitions
├── mocks/ or data/         # Mock data
├── hooks/                  # Custom React hooks
└── styles/
    └── globals.css         # Global styles & CSS variables
```
