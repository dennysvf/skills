# Component Patterns Reference

## Table of Contents
1. [Types File Pattern](#types-file-pattern)
2. [CVA Variant Pattern](#cva-variant-pattern)
3. [Component Implementation Pattern](#component-implementation-pattern)
4. [Mock Data Pattern](#mock-data-pattern)
5. [Lazy Loading Pattern](#lazy-loading-pattern)
6. [Accessibility Patterns](#accessibility-patterns)
7. [Loading and Error States](#loading-and-error-states)

---

## Types File Pattern

Every component has a `types.ts` that exports all interfaces:

```ts
// components/Dashboard/StatCard/types.ts
export interface StatCardProps {
  title: string
  value: string | number
  description?: string
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  icon?: React.ReactNode
  variant?: 'default' | 'hover' | 'active'
  isLoading?: boolean
  className?: string
}
```

Rules:
- All props interfaces are exported from `types.ts`
- Optional props use `?`
- Union types for constrained string values (not enums)
- `className?: string` always included for composability
- `isLoading?: boolean` for async components
- `children?: React.ReactNode` when slot composition is needed

---

## CVA Variant Pattern

```tsx
// components/Dashboard/StatCard/index.tsx
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'
import type { StatCardProps } from './types'

const statCardVariants = cva(
  // Base classes — always applied
  'rounded-lg border p-6 flex flex-col gap-2 transition-all duration-200',
  {
    variants: {
      variant: {
        default: 'bg-card text-card-foreground border-border shadow-sm',
        hover: 'bg-card text-card-foreground border-border shadow-sm hover:shadow-md hover:scale-[1.02] cursor-pointer',
        active: 'bg-card text-card-foreground border-primary ring-2 ring-primary shadow-md',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export function StatCard({
  title,
  value,
  description,
  trend,
  trendValue,
  icon,
  variant,
  isLoading = false,
  className,
}: StatCardProps) {
  if (isLoading) {
    return <StatCardSkeleton className={className} />
  }

  return (
    <div className={cn(statCardVariants({ variant }), className)}>
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        {icon && <span aria-hidden="true">{icon}</span>}
      </div>
      <p className="text-2xl font-bold">{value}</p>
      {description && (
        <p className="text-xs text-muted-foreground">{description}</p>
      )}
      {trend && trendValue && (
        <TrendBadge trend={trend} value={trendValue} />
      )}
    </div>
  )
}
```

Key rules:
- Import `cn` from `@/lib/utils` (combines clsx + tailwind-merge)
- Base classes encode structure; variant classes encode appearance
- `className` always passed to `cn()` last for overrideability
- Destructure all props; no `props` spreading into DOM elements

---

## Component Implementation Pattern

Full component file structure:

```tsx
'use client' // only if using hooks, events, or browser APIs

import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'
import type { ComponentProps } from './types'

// 1. CVA variants
const componentVariants = cva('base-classes', {
  variants: { variant: { ... } },
  defaultVariants: { variant: 'default' },
})

// 2. Main component
export function ComponentName({ prop1, prop2, variant, className }: ComponentProps) {
  return (
    <div className={cn(componentVariants({ variant }), className)}>
      {/* content */}
    </div>
  )
}

// 3. Skeleton (loading state) — defined in same file
function ComponentNameSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn('animate-pulse rounded-lg bg-muted', className)} />
  )
}

// 4. Named exports only — no default export
export { ComponentName }
```

---

## Mock Data Pattern

```ts
// components/Dashboard/StatCard/mock-data.ts
import type { StatCardProps } from './types'

export const mockStatCards: StatCardProps[] = [
  {
    title: 'Total Revenue',
    value: '$45,231.89',
    description: '+20.1% from last month',
    trend: 'up',
    trendValue: '20.1%',
  },
  {
    title: 'Active Users',
    value: '2,350',
    description: '+180 since last week',
    trend: 'up',
    trendValue: '8.3%',
  },
]
```

Use mock data only during development. Replace with real API calls in production.

---

## Lazy Loading Pattern

Use lazy loading for:
- Heavy components (charts, maps, rich text editors)
- Components only visible after user interaction (modals, drawers)
- Below-the-fold content

```tsx
// page.tsx
import dynamic from 'next/dynamic'

const HeavyChart = dynamic(
  () => import('@/components/Dashboard/HeavyChart').then(m => m.HeavyChart),
  {
    loading: () => <div className="h-64 animate-pulse bg-muted rounded-lg" />,
    ssr: false, // only if component uses browser APIs
  }
)
```

---

## Accessibility Patterns

### Interactive elements

```tsx
// Clickable card (not a button)
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
  aria-label="View project details"
  className="cursor-pointer focus:outline-none focus:ring-2 focus:ring-ring rounded-lg"
>

// Icon-only button
<button aria-label="Close dialog" className="...">
  <XIcon aria-hidden="true" />
</button>

// Status badge
<span role="status" aria-live="polite">{statusMessage}</span>
```

### Form inputs

```tsx
<div className="flex flex-col gap-1.5">
  <label htmlFor="email" className="text-sm font-medium">
    Email
  </label>
  <input
    id="email"
    type="email"
    aria-describedby={error ? 'email-error' : undefined}
    aria-invalid={!!error}
    className={cn(inputVariants({ variant: error ? 'error' : 'default' }))}
  />
  {error && (
    <p id="email-error" role="alert" className="text-xs text-destructive">
      {error}
    </p>
  )}
</div>
```

---

## Loading and Error States

### Loading skeleton

```tsx
function TableSkeleton() {
  return (
    <div className="flex flex-col gap-3" aria-busy="true" aria-label="Loading data">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="h-12 animate-pulse rounded-md bg-muted" />
      ))}
    </div>
  )
}
```

### Error state

```tsx
function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="flex flex-col items-center gap-4 p-8 text-center">
      <p className="text-sm text-destructive">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-sm text-primary underline hover:no-underline"
        >
          Try again
        </button>
      )}
    </div>
  )
}
```

### Empty state

```tsx
function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-3 p-12 text-center">
      <p className="text-base font-medium text-foreground">{title}</p>
      {description && <p className="text-sm text-muted-foreground">{description}</p>}
      {action}
    </div>
  )
}
```
