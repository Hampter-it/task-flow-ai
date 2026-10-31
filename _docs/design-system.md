# Design system

The UI is one product, not a collection of pages. This document is the
source of truth for visual tokens, components, states, and copy. Read it
before any UI work and update it when the system changes.

The MVP is a single-user task app: one page, one primary action, and a
short flow from "I have something to do" to "it is captured, edited, or
done". The interface should feel calm and predictable, not decorative.

## Principles

- **Calm over clever.** Neutral surfaces, one accent colour, and
  generous spacing. No gradients, glass effects, or competing highlights.
- **One primary action per view.** On the task list that action is
  **New task**. In a form it is **Save changes**.
- **Hierarchy comes from type, spacing, and borders.** Do not use colour
  alone to communicate status or importance.
- **Reuse before adding.** If a component or token already exists, use
  it. A new one needs a real, recurring need.
- **Keyboard and screen reader first.** Every flow must work without a
  mouse and without relying on hover.
- **Consistency beats local optimisation.** A slightly different spacing
  value or colour in one place is a bug in the system, not a feature.

## Colour tokens

The light theme is the MVP default. Dark tokens are defined so a later
theme toggle does not cause a redesign. Do not ship a theme toggle until
it is a scheduled task.

Reference values are below. Encode them as CSS custom properties in the
frontend theme file; components must use the semantic token names, never
raw hex values. The values are chosen to meet WCAG AA contrast for text
and UI boundaries.

### Core surfaces and text

| Token | Light | Dark | Use |
|---|---|---|---|
| `--background` | `#F6F7FB` | `#0B1020` | Page canvas |
| `--foreground` | `#172033` | `#EDF1F8` | Primary text |
| `--card` | `#FFFFFF` | `#121A2E` | Cards, dialogs, header |
| `--card-foreground` | `#172033` | `#EDF1F8` | Text on cards |
| `--muted` | `#F1F3F9` | `#1A2440` | Secondary surfaces, input backgrounds |
| `--muted-foreground` | `#5C667A` | `#A7B1C6` | Secondary text, metadata |
| `--border` | `#DDE2EC` | `#26324D` | Default borders and dividers |
| `--border-strong` | `#C3CAD9` | `#3A4868` | Hover, selected, or emphasised borders |

### Brand and interaction

| Token | Light | Dark | Use |
|---|---|---|---|
| `--primary` | `#4338CA` | `#818CF8` | Primary buttons, checked controls, focus accents |
| `--primary-foreground` | `#FFFFFF` | `#111827` | Text on primary |
| `--primary-hover` | `#3730A3` | `#A5B4FC` | Primary hover |
| `--primary-active` | `#312E81` | `#6366F1` | Primary pressed |
| `--primary-subtle` | `#EEF2FF` | `#1E1B4B` | Selected filter, soft highlight |
| `--primary-subtle-foreground` | `#3730A3` | `#C7D2FE` | Text on soft highlight |
| `--focus` | `#4F46E5` | `#A5B4FC` | Focus ring |
| `--overlay` | `rgb(15 23 42 / 0.45)` | `rgb(0 0 0 / 0.65)` | Dialog backdrop |

### Status

| Token | Light | Dark | Use |
|---|---|---|---|
| `--success` | `#15803D` | `#4ADE80` | Success icons and accents |
| `--success-foreground` | `#FFFFFF` | `#052E16` | Text on success |
| `--success-subtle` | `#ECFDF3` | `#052E16` | Success alert background |
| `--success-subtle-foreground` | `#166534` | `#86EFAC` | Success alert text |
| `--warning` | `#B45309` | `#FBBF24` | Warning icons and accents |
| `--warning-foreground` | `#FFFFFF` | `#451A03` | Text on warning |
| `--warning-subtle` | `#FFFAEB` | `#451A03` | Warning alert background |
| `--warning-subtle-foreground` | `#92400E` | `#FDE68A` | Warning alert text |
| `--danger` | `#B91C1C` | `#F87171` | Destructive actions and errors |
| `--danger-foreground` | `#FFFFFF` | `#450A0A` | Text on danger |
| `--danger-subtle` | `#FEF2F2` | `#450A0A` | Error alert background |
| `--danger-subtle-foreground` | `#991B1B` | `#FECACA` | Error alert text |

Rules:

- Never use a status colour as the only signal. Pair it with text, an
  icon, a checkbox, or a line-through.
- Do not introduce another accent colour. If a new semantic state is
  genuinely needed, add a token here first.
- Do not use `--primary` for success. Completing a task is not a brand
  action.
- Keep disabled text readable but clearly secondary. Use opacity on the
  whole control rather than an unreadable custom grey.

### shadcn/ui mapping

When the frontend is scaffolded with shadcn/ui, map its variables to the
tokens above so generated components inherit the system:

| shadcn variable | Token |
|---|---|
| `--background`, `--foreground` | `--background`, `--foreground` |
| `--card`, `--card-foreground` | `--card`, `--card-foreground` |
| `--popover`, `--popover-foreground` | `--card`, `--card-foreground` |
| `--primary`, `--primary-foreground` | `--primary`, `--primary-foreground` |
| `--secondary`, `--secondary-foreground` | `--muted`, `--foreground` |
| `--muted`, `--muted-foreground` | `--muted`, `--muted-foreground` |
| `--accent`, `--accent-foreground` | `--muted`, `--foreground` |
| `--destructive`, `--destructive-foreground` | `--danger`, `--danger-foreground` |
| `--border`, `--input` | `--border` |
| `--ring` | `--focus` |
| `--radius` | `8px` |

Use `--primary-subtle` and `--primary-subtle-foreground` directly for
selected states such as the active filter. Custom `--success` and
`--warning` variables are allowed in addition to the shadcn set.

## Typography

Use the system sans-serif stack. Do not add a web font without asking;
it is a dependency and a loading decision.

```css
font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
```

Use the system monospace stack for IDs, timestamps, and other literal
values when alignment matters.

| Role | Size / line height | Weight | Notes |
|---|---|---|---|
| Page title | 30 / 36 px | 600 | 24 / 32 px below `md` |
| Section title | 20 / 28 px | 600 | Dialog titles use this role |
| Task title | 16 / 24 px | 600 | Wraps; never truncate to one line |
| Body | 16 / 24 px | 400 | Default reading size |
| Small body | 14 / 20 px | 400 | Descriptions and helper text |
| Label | 14 / 20 px | 500 | Form labels, filter labels |
| Caption | 12 / 16 px | 400 | Metadata, counters |
| Button | 14 / 20 px | 500 | All button sizes |

Rules:

- Limit body text to roughly 65–75 characters per line with a content
  width of `max-w-3xl` (768 px).
- Use weights 400, 500, and 600 only. Do not use 700 or 800.
- Use `font-variant-numeric: tabular-nums` for page numbers, counts, and
  dates in tables.
- Do not use all caps for labels or headings. Brand name **TaskFlow** is
  the only exception to sentence case.
- Keep heading levels semantic: one `h1` per page, then `h2`, `h3`.

## Spacing and layout

Use a 4 px base scale: `4, 8, 12, 16, 20, 24, 32, 40, 48, 64`. Prefer
Tailwind spacing utilities (`gap-2`, `p-4`, `space-y-6`) over arbitrary
values.

| Decision | Value |
|---|---|
| App header height | 64 px |
| Content max width | 768 px (`max-w-3xl`) |
| Page horizontal padding | 16 px mobile, 24 px tablet, 32 px desktop |
| Page top padding | 24 px mobile, 32 px desktop |
| Gap between page sections | 24 px |
| Gap between task rows | 12 px |
| Task card padding | 16 px mobile, 20 px desktop |
| Form field gap | 16 px |
| Dialog padding | 24 px |

Breakpoints: `sm` 640 px, `md` 768 px, `lg` 1024 px. Design mobile-first
and check at 320 px, 768 px, and 1280 px. The layout must never scroll
horizontally at 320 px.

The MVP has a single column. Do not add a sidebar, dashboard grid, or
multi-column card layout. The header is full width; the task content is
centred in the column.

## Shape and elevation

| Token | Value | Use |
|---|---|---|
| Small radius | 6 px (`rounded-md`) | Badges, small controls |
| Default radius | 8 px (`rounded-lg`) | Buttons, inputs, textareas |
| Card radius | 12 px (`rounded-xl`) | Task rows, panels |
| Dialog radius | 16 px (`rounded-2xl`) | Dialogs |
| Full radius | 9999 px | Pills, avatars |

- Borders are 1 px. Use `--border` by default and `--border-strong` on
  hover or selection.
- Cards use a subtle shadow: `0 1px 2px rgb(15 23 42 / 0.05)`.
- Dialogs use `0 12px 32px rgb(15 23 42 / 0.16)`.
- Do not stack heavy shadows. Do not add shadows to inputs or buttons.

## Motion

- Hover, focus, and colour transitions: 150 ms, ease-out.
- Dialog enter/exit: 200 ms, opacity and a small scale or translate.
- Never use bounce, spring, or looping motion.
- Respect `prefers-reduced-motion: reduce`: remove transforms and
  non-essential animation, keep state changes instant.
- Loading feedback is a skeleton or a spinner, not a decorative
  animation.

## Components

### Button

| Variant | Use | Appearance |
|---|---|---|
| Primary | The main action in a view or dialog | `--primary` background, `--primary-foreground` text |
| Secondary / outline | Cancel, Retry, Show all | `--card` background, `--border`, `--foreground` |
| Ghost | Row actions, icon buttons | Transparent, `--foreground`; `--muted` on hover |
| Destructive | Delete confirmation | `--danger` background, `--danger-foreground` text |

- Sizes: small 32 px, default 40 px, large 44 px. Icon-only buttons are
  40 × 40 px. On touch screens, keep the hit area at least 44 × 44 px
  even when the visual button is smaller.
- Show one primary button per view. Secondary actions never compete with
  it.
- Loading state: spinner plus a present-tense label such as "Saving…";
  keep the button width stable and disable it.
- Disabled state: 50% opacity, no hover change, `cursor: not-allowed`.
- Focus: visible ring using `--focus`, 2 px, 2 px offset. Never remove
  the outline without a visible replacement.
- Icon-only buttons need an accessible name, for example
  `aria-label="Edit Learn FastAPI"`.

### Text input and textarea

- Always use a visible label above the field. Placeholder text is not a
  label.
- Input height 40 px; textarea minimum height 96 px (about four rows).
- Label to field gap: 8 px. Field to helper/error gap: 6 px.
- Default border `--border`; focus ring `--focus`; invalid border
  `--danger` plus error text.
- Mark optional fields with "(optional)" after the label. Required fields
  do not need an asterisk if the form is mostly required.
- Show helper text for constraints such as "200 characters or fewer".
- Show a character counter only when the value is near the limit; do not
  clutter every field.
- On error: set `aria-invalid="true"`, link the message with
  `aria-describedby`, and keep the entered value.
- Disable the field only while a request is in flight, and only if
  changing it would be unsafe.

### Checkbox (completion)

- 20 × 20 px, 6 px radius, primary fill when checked.
- The whole label area is clickable.
- Accessible name includes the task: "Mark Learn FastAPI as complete"
  or "Mark Learn FastAPI as active".
- Completed task title: line-through and `--muted-foreground`. The
  checkbox remains checked and focusable.
- Do not remove completed tasks from the list unless the active filter
  excludes them.

### Task row

Each task is a card with this structure:

```text
┌─────────────────────────────────────────────────────────┐
│ [x]  Task title                          [edit] [delete]│
│      Optional description, up to 2 lines                │
│      Created Oct 31, 2026                               │
└─────────────────────────────────────────────────────────┘
```

- Background `--card`, border `--border`, radius 12 px, padding 16/20 px.
- Checkbox aligned to the first line of the title, not vertically
  centred against a tall description.
- Title: 16/24, weight 600, wraps. Never truncate the title.
- Description: 14/20, `--muted-foreground`, clamped to two lines. The
  full text is available in the edit dialog.
- Metadata: 12/16, `--muted-foreground`, for example "Created Oct 31,
  2026". Use `Intl.DateTimeFormat`; do not add a date library.
- Actions: ghost icon buttons on the right, always visible. Do not hide
  them behind hover only; keyboard and touch users must be able to reach
  them.
- Hover: border becomes `--border-strong`; do not lift or scale the card.
- Completed: title line-through and muted; checkbox checked. The card
  stays in place.

### Filter control

- Three options: **All**, **Active**, **Completed**.
- Use a segmented control: a `--muted` container with three buttons.
- Selected option: `--primary-subtle` background and
  `--primary-subtle-foreground` text.
- Use `aria-pressed` on each button and a group label such as "Filter
  tasks". Do not use tab roles; these buttons filter a list, they do not
  switch panels.
- Changing the filter resets pagination to the first page.
- Keep the control on one row. If it cannot fit, allow wrapping with an
  8 px gap rather than horizontal scrolling.

### Pagination

- Show **Previous** and **Next** secondary buttons and a caption such as
  "Page 1".
- Previous is disabled on the first page. Next is disabled when the last
  response contained fewer than `limit` tasks.
- Changing the page keeps the current filter.
- Announce the new page or the updated result count through a polite live
  region when the list changes.
- Do not show a page-size selector in the MVP; the API default is 20 and
  the maximum is 100.

### Dialog

Use a dialog for create, edit, and delete confirmation. Do not use
`window.confirm` or `window.alert`.

- Overlay: `--overlay`.
- Panel: `--card`, radius 16 px, padding 24 px, max width 480 px.
- Mobile: width `calc(100% - 32px)`, with 16 px side margins.
- Title: section title role (20/28, weight 600). Description: 14/20,
  `--muted-foreground`.
- Actions: Cancel on the left, primary/destructive action on the right.
  On narrow screens, stack them full width with Cancel first.
- Open: focus moves into the dialog, usually to the first field or the
  Cancel button for a destructive confirmation.
- Escape closes, focus is trapped while open, and focus returns to the
  control that opened it.
- Do not autofocus a destructive action.
- Clicking the overlay may close a create/edit dialog only if there are
  no unsaved changes; deleting requires an explicit Cancel or Delete.

### Toast

- Use for success and mutation failures: "Task created", "Changes
  saved", "Task deleted", "Couldn't save changes. Try again."
- Position bottom-right on desktop, bottom-centre on mobile.
- Auto-dismiss after 5 seconds; pause while hovered or focused; include a
  close button.
- Success uses `aria-live="polite"`; errors use `aria-live="assertive"`.
- Never use a toast as the only error message for a form. Keep the
  inline error next to the field or in the dialog.

### Empty state

- Centred in the content column, with an icon in a `--muted` circle, a
  title, one sentence of body text, and one action.
- No tasks: "No tasks yet" / "Create your first task to get started." /
  primary **New task**.
- No active tasks: "No active tasks" / "Everything is done." / secondary
  **Show all tasks**.
- No completed tasks: "No completed tasks" / "Complete a task to see it
  here." / secondary **Show all tasks**.
- Do not use a sad-face illustration or joke copy.

### Loading state

- Initial list load: show three skeleton rows that match the final task
  row dimensions. Do not flash a full-page spinner.
- Mutation in progress: keep the current data visible and show a pending
  state on the button or row.
- Set `aria-busy="true"` on the region that is loading.
- Do not shift the layout when the data arrives.

### Error state

- List load failure: inline alert in the content area with a short title,
  one sentence of explanation, and **Retry**. Keep the page header and
  filters visible.
- Mutation failure: keep the dialog open, preserve the entered values,
  and show an inline error. A toast may also appear.
- Do not expose stack traces, raw server messages, or error codes to the
  user. Log technical details to the console.

### Header

- Height 64 px, `--card` background, bottom border.
- Brand **TaskFlow** on the left, 18/24, weight 600.
- Primary **New task** button on the right, with a plus icon.
- On mobile, keep the button visible; do not collapse it into a menu.
- No navigation links in the MVP. There is only one page.

### Badge

- Optional. Use only when a status needs a label in addition to the
  checkbox, for example "Completed".
- Caption size, weight 500, full radius, success-subtle or danger-subtle
  background. Include text; never rely on colour alone.

### Forms

- Single column, 16 px gap between fields.
- Create and edit forms live in a dialog, not inline in the list.
- Title field first, description textarea second.
- Primary action label: **Create task** for create, **Save changes** for
  edit.
- Validate on submit. After the first submit, re-validate the field on
  blur and on change.
- Trim the title before submitting. Do not submit whitespace-only values.
- Disable the submit button while the request is pending, but do not
  clear the form.
- On success: close the dialog, show a toast, and refresh the list.
- On failure: keep the dialog open, show an inline error, and leave the
  values intact.

## Page pattern

The MVP has one page. Keep this composition:

```text
┌─────────────────────────────────────────────────────────────┐
│ TaskFlow                                       [+ New task] │
├─────────────────────────────────────────────────────────────┤
│ Tasks                                                       │
│ [ All ] [ Active ] [ Completed ]                            │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [x]  Task title                           [edit] [del]  │ │
│ │      Description                                        │ │
│ │      Created Oct 31, 2026                               │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [ Previous ]   Page 1   [ Next ]                            │
└─────────────────────────────────────────────────────────────┘
```

- `h1` is "Tasks"; the brand in the header is not the page heading.
- The filter row sits above the list and below the heading.
- Pagination sits below the list, even when there is only one page, so
  the layout does not jump when a second page appears.
- The create/edit dialog opens over the list; it does not navigate to a
  new route.
- There is no task detail page in the MVP. The edit dialog shows the full
  description.

## Interaction rules

- Changing a filter resets the offset to 0.
- Changing a page keeps the current filter.
- Toggling completion either updates after the request succeeds or uses
  an optimistic update with a rollback on failure. Whichever the task
  chooses must be tested. Never leave a checked box after a failed
  request.
- Deleting always asks for confirmation. The confirm button says
  **Delete task**, not "Yes" or "OK".
- Cancel closes without saving. If there are unsaved changes, the create
  and edit dialogs may ask before discarding; do not add this
  confirmation to the delete dialog.
- Do not navigate away from a form with unsaved changes without warning.
- Do not show a success toast before the request has succeeded.
- Refreshing the list after a mutation is the default. Do not build a
  complex client-side cache in the MVP beyond what TanStack Query
  provides.

## Accessibility

Target WCAG 2.2 AA.

- Use semantic HTML: `header`, `main`, `h1`–`h3`, `ul`/`li` where a list
  is a list, `button` for actions, `a` for navigation.
- Every form control has a visible label. Every icon-only button has an
  accessible name.
- Keyboard order follows the visual order. All controls are reachable
  with Tab; checkboxes toggle with Space; dialogs close with Escape.
- Focus is always visible. Use the `--focus` ring with a 2 px offset.
- Do not trap focus outside dialogs. Inside a dialog, trap focus and
  return it to the trigger on close.
- Do not use colour alone for status. Completed tasks keep the checkbox
  and line-through; errors include text.
- Text contrast is at least 4.5:1; large text and UI boundaries are at
  least 3:1. The tokens above are chosen for this.
- Target size is at least 24 × 24 px (WCAG 2.2); aim for 40 × 40 px and
  44 × 44 px on touch.
- Support 200% zoom without loss of content or horizontal scrolling.
- Respect `prefers-reduced-motion`.
- Announce asynchronous results through a polite live region; use
  assertive announcements only for errors that need immediate attention.
- Do not autofocus the destructive action in a confirmation dialog.

## Content and tone

- Sentence case for headings, labels, and buttons.
- Use direct action verbs: **New task**, **Create task**, **Save
  changes**, **Delete task**, **Retry**, **Show all tasks**.
- Use "task", not "to-do", "item", or "ticket".
- Use "Completed" and "Active", not "Done" and "Open".
- Errors say what happened and what to do:
  - "Title is required."
  - "Title must be 200 characters or fewer."
  - "Couldn't save changes. Try again."
  - "Couldn't load tasks. Check your connection and try again."
- Empty states are short and helpful, not cute.
- Dates use `Intl.DateTimeFormat` with a readable format such as
  "Created Oct 31, 2026". Do not show raw ISO strings in the UI.
- Do not use exclamation marks in errors or confirmations.
- No jargon from the API (no "payload", "422", "null") in user-facing
  copy.

## Implementation rules

- The frontend lives in `frontend/` unless an issue says otherwise.
- shadcn/ui primitives live in `frontend/src/components/ui/`. Task
  components live in `frontend/src/components/tasks/`.
- Theme tokens live in one theme file (for example
  `frontend/src/index.css` or `frontend/src/styles/theme.css`). Do not
  scatter CSS variables across components.
- Use Tailwind utilities and semantic tokens. Do not hardcode hex values
  in components. Do not add arbitrary values unless this document
  defines them.
- Use `cn` for conditional classes and class-variance-authority for
  component variants, following the shadcn/ui conventions.
- Use Lucide icons at 16 or 20 px. Decorative icons are `aria-hidden`;
  icon-only buttons carry a label.
- Do not add a new font, icon set, animation library, or UI dependency
  without asking. Update this document in the same change.
- Every component implements default, hover, focus-visible, disabled,
  loading, and error states where they apply. A list also implements
  empty.
- Check every change at 320 px, 768 px, and 1280 px.
- Check every flow with the keyboard before calling the UI done.
- Use semantic tokens for dark mode. Do not add hardcoded `dark:` colour
  overrides that bypass the theme.
- Do not fork a shadcn primitive for a one-off style. Extend it with
  variants or compose it.

## Definition of done for UI work

- The screen uses the tokens and components in this document.
- There is one clear primary action.
- Loading, empty, error, and disabled states are implemented where they
  apply.
- The flow works with the keyboard and has visible focus.
- Controls have accessible names; errors are announced and linked to
  their fields.
- The layout works at 320 px, 768 px, and 1280 px without horizontal
  scrolling.
- Copy follows the content rules and uses sentence case.
- No raw hex values, one-off spacing, or unapproved dependencies were
  added.
- UI behaviour is covered by tests following
  `_docs/testing-guidelines.md`.

## Changing the system

Add a token or component only when a real screen needs it and an
existing one cannot be extended. When the system changes, update this
document in the same task as the implementation, so the next session
starts from the same rules.
