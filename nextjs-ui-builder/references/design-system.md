# Design System Reference

## Color Tokens (CSS Variables)

Use CSS variables exclusively — never hardcode hex or RGB values.

```css
/* globals.css — light theme */
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --card: 0 0% 100%;
  --card-foreground: 222.2 84% 4.9%;
  --popover: 0 0% 100%;
  --popover-foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  --primary-foreground: 210 40% 98%;
  --secondary: 210 40% 96.1%;
  --secondary-foreground: 222.2 47.4% 11.2%;
  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;
  --accent: 210 40% 96.1%;
  --accent-foreground: 222.2 47.4% 11.2%;
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 210 40% 98%;
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 221.2 83.2% 53.3%;
  --radius: 0.5rem;
}

/* Dark theme */
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --card: 222.2 84% 4.9%;
  --card-foreground: 210 40% 98%;
  --primary: 217.2 91.2% 59.8%;
  --primary-foreground: 222.2 47.4% 11.2%;
  --secondary: 217.2 32.6% 17.5%;
  --secondary-foreground: 210 40% 98%;
  --muted: 217.2 32.6% 17.5%;
  --muted-foreground: 215 20.2% 65.1%;
  --accent: 217.2 32.6% 17.5%;
  --accent-foreground: 210 40% 98%;
  --destructive: 0 62.8% 30.6%;
  --destructive-foreground: 210 40% 98%;
  --border: 217.2 32.6% 17.5%;
  --input: 217.2 32.6% 17.5%;
  --ring: 224.3 76.3% 48%;
}
```

### Tailwind Usage

```tsx
// Correct — uses semantic tokens
<div className="bg-background text-foreground border-border">
<p className="text-muted-foreground">

// Wrong — hardcoded colors
<div className="bg-white text-gray-900">
```

## Component Variants

### Button

```
variants: ['default', 'primary', 'destructive', 'outline', 'ghost']
sizes: ['sm', 'md', 'lg', 'icon']
```

Tailwind classes per variant:
- `default`: `bg-secondary text-secondary-foreground hover:bg-secondary/80`
- `primary`: `bg-primary text-primary-foreground hover:bg-primary/90`
- `destructive`: `bg-destructive text-destructive-foreground hover:bg-destructive/90`
- `outline`: `border border-input bg-background hover:bg-accent hover:text-accent-foreground`
- `ghost`: `hover:bg-accent hover:text-accent-foreground`

### Card

```
variants: ['default', 'hover', 'active']
```

- `default`: `bg-card text-card-foreground rounded-lg border border-border shadow-sm`
- `hover`: `... hover:shadow-md hover:scale-[1.01] transition-all duration-200`
- `active`: `... ring-2 ring-primary`

### Input

```
variants: ['default', 'error', 'disabled']
```

- `default`: `border border-input bg-background text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-ring`
- `error`: `border-destructive focus:ring-destructive`
- `disabled`: `opacity-50 cursor-not-allowed`

### Typography

```
variants: ['h1','h2','h3','h4','h5','h6','text','muted']
```

| Variant | Classes |
|---------|---------|
| h1 | `text-4xl font-bold tracking-tight` |
| h2 | `text-3xl font-semibold tracking-tight` |
| h3 | `text-2xl font-semibold` |
| h4 | `text-xl font-semibold` |
| h5 | `text-lg font-medium` |
| h6 | `text-base font-medium` |
| text | `text-base text-foreground` |
| muted | `text-sm text-muted-foreground` |

## Utility Class Conventions

| Category | Classes |
|----------|---------|
| Typography sizes | `text-xs text-sm text-base text-lg text-xl text-2xl` |
| Font weights | `font-normal font-medium font-semibold font-bold` |
| Spacing | `p-4 p-6 gap-4 gap-6` |
| Transitions | `transition-all duration-200` |
| Hover scale | `hover:scale-105` |
| Border radius | `rounded-md rounded-lg rounded-xl` (use `rounded-[--radius]` for system default) |

## Theme Provider Setup

```tsx
// app/layout.tsx
import { ThemeProvider } from '@/components/theme-provider'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```
