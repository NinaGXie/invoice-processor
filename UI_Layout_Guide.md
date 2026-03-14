# UI Layout Guide — Multi-Step App Pattern

This guide documents the layout architecture Dave and Claude built for VideoMuse, a React 19 + Vite + TypeScript + Tailwind CSS v4 application. Use this as a reference when building new projects with a stepped workflow (Steps 1, 2, 3, 4, etc.).

---

## Stack

- **React 19** with functional components + hooks
- **Vite** for bundling
- **TypeScript** (strict)
- **Tailwind CSS v4** via `@tailwindcss/vite` plugin — no PostCSS config needed
- Dark theme throughout

---

## App Shell — The Core Layout

The entire app is a full-viewport vertical flex column. No page-level scrolling — each section either shrinks to fit or scrolls internally.

```
┌─────────────────────────────────────────┐
│  HEADER                          shrink-0 │  ← Pinned, never collapses
├─────────────────────────────────────────┤
│  STEPPER (step nav)              shrink-0 │  ← Pinned, never collapses
├─────────────────────────────────────────┤
│                                           │
│  MAIN CONTENT                    flex-1   │  ← Takes remaining height
│  (renders active step)           min-h-0  │  ← CRITICAL for nested scroll
│                                           │
├─────────────────────────────────────────┤
│  DEBUG PANEL (optional)          shrink-0 │  ← Fixed height, toggleable
└─────────────────────────────────────────┘
```

```tsx
<div className="h-screen flex flex-col bg-gray-950 text-gray-100 overflow-hidden">
  <header className="border-b border-gray-800 px-6 py-3 flex items-center justify-between shrink-0">
    {/* Title left, action buttons right */}
  </header>

  <div className="shrink-0">
    <Stepper />
  </div>

  <main className="flex-1 min-h-0 px-6 py-4 overflow-y-auto">
    <StepContent />  {/* Switch on current_step */}
  </main>

  {showDebugPanel && (
    <div className="shrink-0 border-t border-gray-700 h-72 bg-gray-950">
      <DebugPanel />
    </div>
  )}
</div>
```

### Why this works

- **`h-screen` + `overflow-hidden`** on the root prevents the page itself from scrolling. Everything is contained.
- **`shrink-0`** on header, stepper, and debug panel means they never get compressed when the viewport is small.
- **`flex-1 min-h-0`** on `<main>` is the key trick: `flex-1` fills remaining space, and `min-h-0` overrides the default `min-height: auto` that flex children get. Without `min-h-0`, the main area would grow to fit its content and push the debug panel off-screen instead of scrolling internally.
- **`overflow-y-auto`** on `<main>` enables vertical scrolling only when content overflows.

---

## Stepper — Step Navigation Bar

A horizontal `<nav>` with numbered step buttons connected by lines. Steps have four visual states.

```tsx
<nav className="border-b border-gray-800 px-6 py-3 overflow-x-auto">
  <ol className="flex items-center gap-1 min-w-max">
    {VISIBLE_STEPS.map((step, idx) => (
      <li key={step} className="flex items-center">
        {/* Connector line between steps */}
        {idx > 0 && (
          <div className={`w-8 h-px mx-1 ${
            idx <= currentIdx ? 'bg-primary-500' : 'bg-gray-700'
          }`} />
        )}

        <button
          onClick={() => isAccessible && goToStep(step)}
          disabled={!isAccessible}
          className={`
            flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all
            ${isCurrent  ? 'bg-primary-600/20 text-primary-400 ring-1 ring-primary-500/50' : ''}
            ${isCompleted ? 'text-green-400' : ''}
            ${isStale     ? 'text-amber-400' : ''}
            ${isDefault   ? 'text-gray-500' : ''}
            ${isAccessible ? 'hover:bg-gray-800 cursor-pointer' : 'cursor-not-allowed opacity-50'}
          `}
        >
          <StepIcon /> {STEP_LABELS[step]}
        </button>
      </li>
    ))}
  </ol>
</nav>
```

### Step status colors

| State | Badge | Text | Meaning |
|-------|-------|------|---------|
| **Current** | `bg-primary-600/20 ring-1 ring-primary-500/50` | `text-primary-400` | Active step |
| **Completed** | `bg-green-500/20` with checkmark SVG | `text-green-400` | Done, data is current |
| **Stale** | `bg-amber-500/20` with `!` | `text-amber-400` | Done, but upstream changed |
| **Locked** | `bg-gray-700` with number | `text-gray-500 opacity-50 cursor-not-allowed` | Can't visit yet |

### Step icon component

```tsx
function StepIcon({ completed, stale, index }: { completed: boolean; stale: boolean; index: number }) {
  const base = "w-5 h-5 rounded-full text-xs flex items-center justify-center";
  if (stale)     return <span className={`${base} bg-amber-500/20 text-amber-400`}>!</span>;
  if (completed) return <span className={`${base} bg-green-500/20 text-green-400`}><CheckSVG /></span>;
  return <span className={`${base} bg-gray-700 text-gray-400`}>{index}</span>;
}
```

### Connector lines

The `w-8 h-px` dividers between steps are `bg-primary-500` for visited steps and `bg-gray-700` for future ones, creating a progress-bar effect.

---

## Step Navigation State

### Types

```typescript
type StepId = 'setup' | 'story' | 'storyboard' | 'preview' | 'export' | 'final_export';

interface StepStatus {
  completed: boolean;    // Has the step been finished?
  stale: boolean;        // Has upstream data changed since completion?
  step_state: 'locked' | 'unlocked' | 'active';
}

// In the project state:
current_step: StepId;
step_status: Record<StepId, StepStatus>;
```

### Step gating

```typescript
// Users can only navigate to active or unlocked steps
const canAdvanceTo = (step: StepId) => {
  const state = project.step_status[step]?.step_state;
  return state === 'active' || state === 'unlocked';
};
```

### Initializing defaults

```typescript
const step_status = {} as Record<StepId, StepStatus>;
for (const step of STEP_ORDER) {
  step_status[step] = { completed: false, stale: false, step_state: 'locked' };
}
step_status.setup.step_state = 'active';  // First step is always accessible
```

### Hidden steps

Some internal steps (like `style` or `keyframes`) may share a visible step in the stepper. Map them in the stepper component:

```typescript
function toVisibleStep(step: StepId): StepId {
  if (step === 'style' || step === 'keyframes') return 'storyboard';
  return step;
}
```

### Content switch

```tsx
function StepContent() {
  const { project } = useProject();
  switch (project.current_step) {
    case 'setup':       return <ProjectSetup />;
    case 'story':       return <StoryGeneration />;
    case 'storyboard':  return <Storyboard />;
    case 'preview':     return <Preview />;
    case 'export':      return <Export />;
    case 'final_export': return <FinalExport />;
    default:            return null;
  }
}
```

---

## Step Layout Patterns

Each step's content fills the `<main>` area. Here are the three main layout patterns we used.

### Pattern A: Two-Column Form (Step 1 — Setup)

Responsive grid: single column on mobile, two columns on desktop. Each column is a vertical flex stack.

```tsx
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start flex-1 min-h-0">
  {/* Left: required fields */}
  <div className="flex flex-col gap-3 h-full">
    <InputField />
    <TextArea className="flex-1" />     {/* Grows to fill */}
    <BottomControls />                   {/* Pinned at bottom */}
  </div>

  {/* Right: optional fields */}
  <div className="flex flex-col gap-3 h-full">
    <ImageUpload />
    <AudioUpload />
    <TextArea className="flex-1" />
  </div>
</div>
```

### Pattern B: Three-Panel Resizable (Step 2 — Main Workspace)

Left sidebar + scrollable center content + right sidebar, all with sticky positioning and drag-to-resize handles.

```
┌──────────────┬────────────────────────┬─────────────┐
│  Left Panel  │   Center (scrollable)  │  Right Panel│
│  sticky      │   flex-1               │  sticky     │
│  resizable   │                        │  resizable  │
└──────────────┴────────────────────────┴─────────────┘
```

```tsx
<div className="flex gap-0">
  {/* Left sidebar — sticky, resizable */}
  <div className="shrink-0 flex flex-col h-[calc(100vh-200px)] sticky top-4 self-start"
       style={{ width: leftWidth }}>
    <LeftContent />
  </div>

  <ResizeHandle onResize={handleLeftResize} />

  {/* Center — scrollable, takes remaining width */}
  <div className="flex-1 min-w-0 px-2 space-y-4">
    <CenterContent />
  </div>

  <ResizeHandle onResize={handleRightResize} />

  {/* Right sidebar — sticky, resizable */}
  <div className="shrink-0 sticky top-4 self-start h-[calc(100vh-200px)]"
       style={{ width: rightWidth }}>
    <RightContent />
  </div>
</div>
```

**Why `sticky top-4 self-start`**: Keeps sidebars visible while center content scrolls. `self-start` aligns to the top of the flex row. `h-[calc(100vh-200px)]` gives dynamic height accounting for header + stepper.

**Why `min-w-0`** on center: Prevents flex children from overflowing when content is wider than available space.

#### Resize Handle

```tsx
function ResizeHandle({ onResize }: { onResize: (delta: number) => void }) {
  const onMouseDown = (e: React.MouseEvent) => {
    let lastX = e.clientX;
    const onMouseMove = (ev: MouseEvent) => {
      onResize(ev.clientX - lastX);
      lastX = ev.clientX;
    };
    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  };

  return (
    <div onMouseDown={onMouseDown}
         className="w-2 shrink-0 cursor-col-resize flex items-center justify-center group hover:bg-primary-500/30 transition-colors">
      <div className="w-0.5 h-8 bg-gray-700 group-hover:bg-primary-400 rounded-full" />
    </div>
  );
}
```

### Pattern C: Card List with Accordion (Step 3 — Review/Edit)

Vertical list of collapsible cards. Only one expanded at a time.

```tsx
const [expanded, setExpanded] = useState<string | null>(null);

<div className="space-y-4">
  {/* Controls bar */}
  <div className="flex items-center gap-2 flex-wrap">
    <ToggleButtons />
  </div>

  {/* Card list */}
  {items.map(item => (
    <div key={item.id} className="border border-gray-800 rounded-xl">
      {/* Clickable header */}
      <div onClick={() => setExpanded(expanded === item.id ? null : item.id)}
           className="cursor-pointer hover:bg-gray-800/50 p-4 flex items-center justify-between">
        <span>{item.title}</span>
        <ChevronIcon rotated={expanded === item.id} />
      </div>

      {/* Expanded content */}
      {expanded === item.id && (
        <div className="border-t border-gray-800 p-4 space-y-2">
          <DetailContent />
        </div>
      )}
    </div>
  ))}
</div>
```

---

## Color System

### Theme tokens (Tailwind v4 `@theme`)

```css
@import "tailwindcss";

@theme {
  /* Primary accent (blue) */
  --color-primary-50:  #eff6ff;
  --color-primary-100: #dbeafe;
  --color-primary-200: #bfdbfe;
  --color-primary-300: #93c5fd;
  --color-primary-400: #60a5fa;
  --color-primary-500: #3b82f6;   /* Main accent */
  --color-primary-600: #2563eb;   /* Buttons */
  --color-primary-700: #1d4ed8;
  --color-primary-800: #1e40af;
  --color-primary-900: #1e3a8a;

  /* Surface (optional — we mostly use Tailwind's built-in gray) */
  --color-surface-800: #1e293b;
  --color-surface-900: #0f172a;
  --color-surface-950: #020617;
}
```

This generates `bg-primary-500`, `text-primary-400`, `border-primary-600`, etc. as utility classes.

### Color usage cheat sheet

| Element | Class | Notes |
|---------|-------|-------|
| App background | `bg-gray-950` | Darkest gray |
| Default text | `text-gray-100` | Near-white |
| Muted text | `text-gray-400` | Labels, secondary info |
| Dimmed text | `text-gray-500` | Disabled, hints |
| Borders | `border-gray-800` | Subtle, low contrast |
| Input backgrounds | `bg-gray-800` | One step lighter than app |
| Cards/panels | `bg-gray-900/30 border border-gray-800` | Translucent tint |
| Section headers | `text-gray-400 uppercase tracking-wide text-sm` | All caps, spaced |
| Primary buttons | `bg-primary-600 hover:bg-primary-500 text-white` | |
| Secondary buttons | `bg-gray-800 hover:bg-gray-700 text-gray-400` | |
| Disabled | `opacity-50 cursor-not-allowed` | |
| Success | `text-green-400` / `bg-green-500/20` | Completed states |
| Warning | `text-amber-400` / `bg-amber-500/20` | Stale, needs attention |
| Error | `text-red-400` / `border-red-700/60` | Failures |

---

## Common UI Components

### Buttons

```tsx
{/* Primary action */}
<button className="px-6 py-2.5 bg-primary-600 hover:bg-primary-500 text-white rounded-lg font-medium transition-colors">
  Continue →
</button>

{/* Secondary */}
<button className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-400 rounded-lg transition-colors">
  Cancel
</button>

{/* Disabled */}
<button disabled className="px-6 py-2.5 bg-gray-800 text-gray-500 rounded-lg cursor-not-allowed">
  Not available
</button>
```

### Form inputs

```tsx
<div className="space-y-1">
  <label className="block text-sm text-gray-400">Label</label>
  <input className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:ring-1 focus:ring-primary-500 focus:border-primary-500" />
</div>
```

### Textareas

```tsx
<textarea className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 resize-none"
          rows={6} />
```

### Cards / Panels

```tsx
<div className="bg-gray-900/30 border border-gray-800 rounded-xl p-5">
  <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide">Section Title</h3>
  <p className="text-sm text-gray-300 mt-2">Content goes here.</p>
</div>
```

### Modal overlay

```tsx
{showModal && (
  <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center"
       onClick={() => setShowModal(false)}>
    <div className="bg-gray-900 border border-gray-700 rounded-xl shadow-2xl max-w-sm mx-4 p-6"
         onClick={(e) => e.stopPropagation()}>
      <h2 className="text-lg font-semibold mb-3">Title</h2>
      <p className="text-sm text-gray-400 mb-4">Message</p>
      <div className="flex justify-end gap-2">
        <button className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-400 rounded-lg">Cancel</button>
        <button className="px-4 py-1.5 bg-primary-600 hover:bg-primary-500 text-white rounded-lg">Confirm</button>
      </div>
    </div>
  </div>
)}
```

**Full-screen modal density rule:** When a modal uses a full-screen overlay (`fixed inset-0 z-50`), maximize information density so the user can see everything without scrolling. Techniques:

- Use `text-xs` (not `text-sm`) for data rows and metadata
- Use two-column grids (`grid-cols-2`) for key-value pairs instead of single-column stacks
- Place related sections side-by-side (e.g., Identity + Sequencing in one `grid-cols-2` row)
- Use tight vertical spacing (`gap-y-0.5`, `space-y-0.5`) between data rows
- Add `title` attributes on truncated text so hover reveals the full value
- Reserve `max-h-{N} overflow-y-auto` as a fallback for truly variable-length lists, but set `N` generously (e.g., `max-h-80`) and prefer fitting everything above the fold
- Accept a `className` prop on the Modal component so callers can widen it (e.g., `max-w-3xl` instead of the default `max-w-lg`)

### Loading spinner

```tsx
<div className="animate-spin w-5 h-5 border-2 border-primary-400 border-t-transparent rounded-full" />
```

### Status indicators

```tsx
<span className="text-green-400">✓ Complete</span>
<span className="text-amber-400">! Needs review</span>
<span className="text-red-400">✗ Failed</span>

{/* With background badge */}
<span className="px-2 py-0.5 rounded text-xs bg-green-500/20 text-green-400">Done</span>
```

### Floating action button

```tsx
<div className="fixed bottom-4 right-6 z-40">
  <button className="px-6 py-2.5 bg-primary-600 hover:bg-primary-500 text-white rounded-lg font-medium shadow-lg transition-colors">
    Next Step →
  </button>
</div>
```

---

## Spacing & Sizing Conventions

### Padding

| Class | Where |
|-------|-------|
| `px-3 py-2` | Form inputs (compact) |
| `px-3 py-1.5` | Small buttons, step buttons |
| `px-6 py-2.5` | Primary action buttons |
| `px-6 py-3` | Header, stepper (horizontal sections) |
| `px-6 py-4` | Main content area |
| `p-4` | Card content (medium) |
| `p-5` | Card panels (generous) |

### Gaps

| Class | Where |
|-------|-------|
| `gap-1` | Tight groups (stepper buttons, icon rows) |
| `gap-2` | Form field groups, button rows |
| `gap-3` | Vertical section spacing within a column |
| `gap-6` | Major layout columns (grid-cols-2) |
| `space-y-4` | Stacked cards/sections |

### Border radius

| Class | Where |
|-------|-------|
| `rounded` | Small badges |
| `rounded-lg` | Inputs, buttons (8px) |
| `rounded-xl` | Cards, panels, modals (12px) |
| `rounded-full` | Circular icons, spinners |

### Heights

| Class | Where |
|-------|-------|
| `h-screen` | App container |
| `h-full` | Fill parent |
| `h-[calc(100vh-200px)]` | Sticky sidebar panels (accounts for header + stepper) |
| `h-72` | Debug panel (288px fixed) |
| `min-h-0` | Flex children that need to scroll |

---

## Context Provider Nesting

Wrap the app content in context providers. Order matters — inner providers can consume outer ones.

```tsx
export default function App() {
  return (
    <SettingsProvider>
      <ProjectProvider>
        <FeatureProviderA>
          <FeatureProviderB>
            <AppContent />
          </FeatureProviderB>
        </FeatureProviderA>
      </ProjectProvider>
    </SettingsProvider>
  );
}
```

State management uses `useReducer` inside each provider — not Redux, not Zustand. A single `Project` object holds all data and is modified via dispatched actions.

---

## Critical CSS Gotchas

### 1. `min-h-0` for nested scrolling

Flex children default to `min-height: auto`, which means they grow to fit content instead of scrolling. Always add `min-h-0` to a flex child that should scroll:

```tsx
{/* ✗ Broken — content pushes past viewport */}
<main className="flex-1 overflow-y-auto">

{/* ✓ Works — content scrolls within bounds */}
<main className="flex-1 min-h-0 overflow-y-auto">
```

### 2. `min-w-0` for flex text truncation

Same principle horizontally. Without `min-w-0`, a flex child with long text won't truncate:

```tsx
<div className="flex-1 min-w-0">
  <p className="truncate">Very long text that should ellipsis...</p>
</div>
```

### 3. `overflow-hidden` on the root

The root `h-screen` container must have `overflow-hidden` to prevent the browser from adding a page-level scrollbar. All scrolling happens inside `<main>`.

### 4. `shrink-0` on fixed-size elements

Header, stepper, debug panel — anything that should never collapse — needs `shrink-0`. Without it, the flex algorithm will compress them when space is tight.

### 5. Sticky sidebars need `self-start`

`sticky` alone doesn't work on flex children without `self-start` (or explicit align-self). The sidebar will stretch to the container's full height instead of sticking:

```tsx
{/* ✓ Works */}
<div className="sticky top-4 self-start h-[calc(100vh-200px)]">

{/* ✗ Won't stick — stretches to parent height */}
<div className="sticky top-4 h-[calc(100vh-200px)]">
```

---

## Settings Screen

Settings should be a **full-screen overlay** (`fixed inset-0 z-50`) — not a tiny modal. All settings must be visible at once without scrolling. If content threatens to overflow, restructure into a more compact layout (two-column grid, smaller spacing) rather than adding a scrollbar. The user should never need to scroll to find a setting.

### Layout

```tsx
<div className="fixed inset-0 z-50 flex items-center justify-center">
  <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
  <div className="relative bg-gray-900 border border-gray-700 rounded-xl shadow-2xl
                  max-w-2xl w-full mx-4 p-6">
    {/* All settings visible without scrolling */}
  </div>
</div>
```

### API Key Fields

API keys must have a **visibility toggle** (eye icon). Default to `type="password"` (masked), with a button to toggle to `type="text"`. This lets users verify they pasted the correct key.

```tsx
<div className="relative">
  <input
    type={showKey ? 'text' : 'password'}
    value={value}
    onChange={(e) => onChange(e.target.value)}
    className="w-full px-3 py-2 pr-10 bg-gray-800 border border-gray-700 rounded-lg ..."
  />
  <button
    onClick={() => setShowKey(!showKey)}
    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
    title={showKey ? 'Hide key' : 'Show key'}
  >
    {showKey ? <EyeOffIcon /> : <EyeIcon />}
  </button>
</div>
```

**Rules:**
- Always store API keys in `localStorage` only — never in project state or autosync files
- Show a help text line explaining where the key is stored
- Provide a placeholder hint for the key format (e.g. `sk-ant-...`)

---

## Electron Desktop Considerations

If packaging as an Electron app:

- **Header as drag handle**: `style={{ WebkitAppRegion: 'drag' }}` on the header, with `WebkitAppRegion: 'no-drag'` on interactive elements inside it.
- **Traffic light offset**: When using `titleBarStyle: 'hiddenInset'`, add `paddingLeft: '5rem'` to the header to avoid overlapping the macOS window controls.
- **Settings modal**: Use `fixed inset-0 z-50` overlay pattern — not a separate window.

---

## Flask App UI Reference

This documents the UI pattern built for Flask + Jinja2 apps (no frontend framework).

### Stack

- **Flask** with Jinja2 templates
- **Vanilla CSS** (all styles inline in `<style>` block)
- **Vanilla JS** for interactivity
- Dark theme matching the color system above

### Header with Biosheng Logo

The header has the app title on the left and the Biosheng logo on the right. This is the standard pattern for all Biosheng internal tools.

```html
<header>
    <div class="header-title">
        <!-- SVG icon + App Title text -->
    </div>
    <img src="/static/biosheng_logo_v2.png" alt="Biosheng Logo" style="height: 36px; object-fit: contain;">
</header>
```

```css
header {
    border-bottom: 1px solid #1f2937;
    padding: 20px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
}
.header-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 22px;
    font-weight: 600;
    color: #f3f4f6;
}
```

### Logo setup

1. Place `biosheng_logo_v2.png` in `<project_root>/static/`
2. Use a simple ASCII filename (no spaces, no Chinese characters)
3. Reference as `<img src="/static/biosheng_logo_v2.png">`
4. Flask serves `static/` automatically — no extra config needed

### Color values (CSS hex equivalents of Tailwind tokens)

| Token | Hex |
|-------|-----|
| gray-950 | `#030712` |
| gray-900 | `#111827` |
| gray-800 | `#1f2937` |
| gray-700 | `#374151` |
| gray-500 | `#6b7280` |
| gray-400 | `#9ca3af` |
| gray-300 | `#d1d5db` |
| gray-200 | `#e5e7eb` |
| gray-100 | `#f3f4f6` |
| primary-400 | `#60a5fa` |
| primary-500 | `#3b82f6` |
| primary-600 | `#2563eb` |

---

## Adapting for Your Project

1. **Copy the app shell** (`h-screen flex flex-col overflow-hidden` + header/stepper/main).
2. **Define your steps** as a `StepId` union type and `VISIBLE_STEPS` array.
3. **Set up step_status** with `completed`, `stale`, and `step_state` for gating.
4. **Copy the Stepper component** — it's generic. Just update step labels and colors.
5. **Pick a layout pattern** for each step (two-column form, three-panel resizable, or card accordion).
6. **Copy the @theme tokens** into your `index.css` for consistent primary/surface colors.
7. **Reuse the component patterns** (buttons, inputs, cards, modals) as-is — they're all pure Tailwind utilities.
