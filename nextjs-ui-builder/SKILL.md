---
name: nextjs-ui-builder
description: >
  Implements production-ready Next.js interfaces from design images or descriptions,
  following a strict technical stack of Next.js + TypeScript + Tailwind CSS +
  class-variance-authority (CVA). Use when the user provides an image, screenshot,
  or description of a UI and wants it implemented as a Next.js component or page.
  Triggers on "implement this interface", "build this UI from the image",
  "create this component", "implement this screen", "convert this design to code",
  "build this page", "implement this layout". Produces strongly typed, accessible,
  dark/light theme-aware components following the project design system.
---

# Next.js UI Builder

## Overview

Analyze a provided image or description and implement a complete, production-ready Next.js interface following the project's design system and technical standards.

## Workflow

### 1. Analyze the Design

When an image is provided:
- Identify all UI regions: header, sidebar, main content, footer, modals
- List every component visible: buttons, cards, inputs, tables, badges, etc.
- Note layout strategy: grid, flex, responsive breakpoints
- Identify color usage relative to the design system (primary, muted, destructive, etc.)
- Detect interactive states: hover, focus, active, loading, error, disabled

### 2. Plan the File Structure

Map the design to files following Next.js App Router conventions:

```
src/
  app/
    [route]/
      page.tsx          # Page entry point
      layout.tsx        # Layout if needed
  components/
    [feature]/
      [ComponentName]/
        index.tsx       # Component implementation
        types.ts        # Props interfaces and types
        mock-data.ts    # Development mock data
```

### 3. Implement Components

For each identified component, follow this implementation order:
1. Define types in `types.ts`
2. Write mock data in `mock-data.ts` (if data-driven)
3. Implement component in `index.tsx` using CVA for variants

See `references/component-patterns.md` for TypeScript patterns, CVA usage, and code templates.

### 4. Implement the Page

Compose components into the page, ensuring:
- Responsive layout (mobile-first with sm/md/lg/xl breakpoints)
- Dark/light theme via CSS variables (no hardcoded colors)
- Proper semantic HTML and ARIA attributes
- Loading and error states

### 5. Quality Checklist

Before finishing, verify:
- [ ] All props are strictly typed with TypeScript interfaces
- [ ] No hardcoded colors (use design system tokens from references/design-system.md)
- [ ] All interactive elements have keyboard navigation support
- [ ] ARIA labels on icons and non-obvious elements
- [ ] Dark mode works via CSS variable tokens
- [ ] Mobile layout tested (no horizontal overflow)
- [ ] Loading states present for async content
- [ ] Error states handled with user feedback

## Design System Reference

See `references/design-system.md` for:
- Color tokens (CSS variables)
- Component variants (Button, Card, Input, Typography)
- Utility class conventions
- Theme structure

## Component Patterns Reference

See `references/component-patterns.md` for:
- CVA variant setup template
- Props interface conventions
- Mock data patterns
- Lazy loading usage
- Accessibility patterns
