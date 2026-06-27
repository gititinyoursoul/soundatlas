# Desktop Navigation Drawer Overlay Design

This document applies `prompts/plan-feature.md` to a planning-only UX concept for a desktop-only overlay navigation drawer.

Related mockup screens:

- `docs/design/navigation-drawer-expanded-overlay.svg`
- `docs/design/navigation-drawer-collapsed-overlay.svg`
- `docs/design/navigation-drawer-routes-subview-overlay.svg`

## Change Classification

Documentation-only design concept for a future frontend UX change.

## Summary

Design a desktop overlay navigation drawer that can switch between expanded and collapsed states without moving the map-first SoundAtlas workspace. The drawer sits above the content, uses a dim overlay when open, keeps navigation visually separate from actions, and defines consistent states for active, disabled, loading, error, and empty navigation groups.

## Assumptions

- Desktop nav-item clicks keep the drawer open. This is assumed because desktop users often move through adjacent routes or sections and benefit from persistent navigation context.
- Clicking the dim overlay closes the drawer.
- `Esc` closes the drawer when the overlay drawer is open.
- Icons use Lucide or the existing frontend icon set, with 20px icons in expanded state and 22px icons in collapsed state.
- The drawer is not part of the mobile layout. Mobile navigation should be designed separately.
- This is a design specification only; no Svelte implementation is included in this pass.

## Open Questions

- Should desktop route switching eventually live in this drawer, or should the drawer only cover app-level navigation?
- Should permission-restricted items be disabled for discoverability or hidden to reduce clutter? Recommendation: disabled for internal/admin tools, hidden for public-only users when the item has no explanatory value.
- Does SoundAtlas need a persistent collapsed rail while the drawer is closed, or should collapsed be an alternate open state only? Recommendation: collapsed is an open state, triggered by a collapse button, not always visible by default.

## User Action

The user opens the navigation drawer from a visible trigger in the compact app header, scans grouped navigation, activates a nav item, optionally collapses to icon-only mode, and closes the overlay by trigger, close button, `Esc`, or clicking the dim overlay.

## (a) Desktop Layout

### Expanded

- Width: `320px`.
- Position: fixed left, top `0`, bottom `0`, `z-index` above app shell and dim overlay.
- Overlay: full viewport dim layer behind drawer, `rgba(23, 32, 42, 0.36)`.
- Header: SoundAtlas wordmark/title, scope label, close button, collapse button.
- Body: scrollable grouped navigation.
- Footer: fixed public access/status section. No logout is shown while the MVP has no public login.
- Item layout: icon, label, optional badge/count, optional permission hint.
- Active item: route-colored left rail, stronger background, high-contrast text, `aria-current="page"`.

### Collapsed

- Width: `72px`.
- Position and overlay behavior match expanded state.
- Header shows icon-only product mark or compact app icon, close button, expand button.
- Nav items are icon-only. No text labels are visible in the drawer.
- Each icon item exposes a tooltip on hover and focus with the text label.
- Active item keeps the left rail, selected background, and `aria-current="page"`.
- Disabled items remain visible only when discoverability is useful; tooltips explain the restriction.

## Navigation Architecture

Recommended group structure for SoundAtlas:

- Explore
  - Routes
- Admin
  - Media Review

Actions are visually separated from navigation:

- Separator before action area.
- Footer status group clarifies that the current surface is admin review mode.
- Research, source browsing, and validation are intentionally out of the drawer until those workflows are concrete.
- Media Review lists draft media links and image links and supports direct review/reject actions.

Future permission patterns:

- Disabled: visible item, reduced opacity, no route transition, tooltip or subtext explains "Admin access required".
- Hidden: item omitted when the user should not know the capability exists or when it has no value in the current product surface.
- Loading permissions: section skeleton rows preserve item height to avoid layout flashes.

## UI Behavior

- Trigger: visible icon button in the compact header, labelled "Open navigation".
- Open: trigger click opens drawer in the last chosen size state, expanded by default.
- Close: close button, trigger toggle, `Esc`, or dim overlay click.
- Collapse: collapse button switches expanded to collapsed without closing the overlay.
- Expand: expand button or tooltip-assisted icon rail control restores text labels.
- Nav-item click on desktop: drawer stays open. Assumed default.
- Route synchronization: active item always follows the current route/path, not merely the last clicked item.
- Animation:
  - Drawer enters with `transform: translateX(-100%)` to `translateX(0)`.
  - Dim overlay fades from `opacity: 0` to `1`.
  - Width transition between expanded and collapsed uses `180ms ease-out`.
  - Open/close uses `220ms cubic-bezier(0.2, 0, 0, 1)`.
  - Content opacity crossfade for labels uses `120ms`, delayed until width transition starts.
  - No layout shift in the app content because drawer overlays content.

## Overlay and Focus

- The drawer overlays the content; the map, timeline, and story panel do not resize.
- Dim overlay covers content and makes background non-interactive while the drawer is open.
- Pointer events on background content are disabled through the overlay.
- Initial focus moves to the drawer container or first useful control after opening.
- Focus is not lost when the drawer closes; it returns to the trigger.
- No permanent focus trap is required if the drawer is treated as a dismissible overlay, but tab order should remain inside the drawer while the dim overlay is active to avoid reaching non-interactive background controls.
- `Esc` closes the drawer.
- Outside click on the dim overlay closes the drawer.

## Scroll and Long Content

- Drawer root uses fixed height: `100vh`.
- Header and footer remain fixed within the drawer.
- Navigation body scrolls independently with `overflow-y: auto`.
- Section headers can remain normal flow; optional sticky section headers are acceptable only if they do not obscure focused items.
- Long lists preserve item height and avoid async height jumps by using skeleton rows with final item dimensions.
- Future virtualization should be possible by keeping nav item height stable, for example `44px` expanded and `48px` collapsed.

## (b) State Gallery

| State | Expanded Pattern | Collapsed Pattern |
| --- | --- | --- |
| Default | Neutral text, transparent or white background, icon at 20px | Icon-only button, tooltip available |
| Hover | Light surface fill `#f3f6f8`, text remains high contrast | Same fill, tooltip opens after short delay |
| Active | Left rail, tinted fill, bold label, `aria-current="page"` | Left rail, tinted icon button, tooltip still says label |
| Disabled | `opacity: 0.48`, no route change, cursor default, reason in tooltip/subtext | Muted icon and tooltip with reason |
| Loading | Skeleton section header and rows with fixed item height | Skeleton icon pills with fixed rail width |
| Error | Inline error panel inside affected section with retry button | Error icon button opens tooltip/popover with retry |
| Empty | Empty state row with icon and concise copy | Empty icon with tooltip: "No entries" |

No permission:

- Public user sees either disabled admin item with "Admin access required" or hidden item based on product policy.
- Disabled is preferred for internal MVP builds because it explains capability boundaries.

Loading failed:

- Keep the drawer open.
- Replace only the failed section with an error block.
- Retry lives inside the section, not as a global app action.

## (c) Components Plan

1. `DrawerTrigger`
   - Header icon button.
   - `aria-haspopup="dialog"` or `aria-controls`.
   - Visible focus ring and tooltip.

2. `NavigationDrawer`
   - Fixed overlay panel.
   - Props/state: `open`, `variant: "expanded" | "collapsed"`, `activeRouteId`, `permissionState`.
   - Owns keyboard close behavior and focus return.

3. `DimOverlay`
   - Full viewport layer behind drawer.
   - Closes on click.
   - Blocks interaction with map/timeline/story content.

4. `DrawerHeader`
   - Product identity, scope, close control, collapse/expand control.

5. `NavSection`
   - Section header and grouped items.
   - Supports loading, empty, error, and permission-filtered states.

6. `NavItem`
   - Icon, label in expanded state, optional badge, active rail.
   - Collapsed state renders icon only and requires tooltip.
   - Disabled state prevents activation and explains why.

7. `Separator`
   - Visual divider between navigation groups and action/footer group.

8. `DrawerFooter`
   - Admin review mode summary.
   - No logout control until authentication exists.

## (d) Styling Guide

Color system:

- Surface: `#ffffff`.
- App dim overlay: `rgba(23, 32, 42, 0.36)`.
- Text primary: `#17202a`.
- Text secondary: `#536170`.
- Border: `#d9e0e7`.
- Hover surface: `#f3f6f8`.
- Active surface: `#fff7f4`.
- Active accent: `#e4572e`.
- Active text: `#7e2d19`.
- Disabled: `#8a96a3` at reduced opacity.
- Error: `#bb3f22` text on `#fff1ed`.
- Focus ring: `2px solid #2454d6`, offset `2px`.

Typography:

- Drawer title: `16px`, weight `800`, line-height `1.2`.
- Scope/meta: `11px`, weight `800`, uppercase, letter spacing `0.08em`.
- Section header: `11px`, weight `800`, uppercase.
- Nav item label: `14px`, weight `700`, line-height `1.3`.
- Footer/action text: `13px`, weight `700`.
- Tooltip: `12px`, weight `700`.

Spacing and sizing:

- Base grid: 8pt.
- Expanded drawer width: `320px`.
- Collapsed drawer width: `72px`.
- Header padding: `16px`.
- Body padding: `8px 12px 12px`.
- Section gap: `16px`.
- Item height: `44px` expanded, `48px` collapsed.
- Item border radius: `8px`.
- Icon size: `20px` expanded, `22px` collapsed.
- Icon-label gap: `12px`.
- Active rail: `4px` wide, flush to item left edge.

Alignment:

- Expanded item grid: `24px icon column`, flexible label, optional badge.
- Collapsed item: centered icon in fixed square button area.
- Text labels never appear in collapsed drawer.
- Badges are hidden in collapsed state unless represented by a small count dot with tooltip text.

## (e) A11y Checklist

- Trigger has accessible name: "Open navigation".
- Drawer has a semantic label, for example `aria-label="Primary navigation"`.
- Active nav item uses `aria-current="page"` or route-appropriate equivalent.
- Disabled items use `aria-disabled="true"` and do not activate.
- Focus moves into drawer on open and returns to trigger on close.
- `Esc` closes the drawer.
- Tab order starts at close/collapse controls, then sections/items, then footer actions.
- Background content is not tabbable while overlay is active.
- Every interactive element has a visible high-contrast focus style.
- Collapsed icon-only items have accessible names and visible tooltips on hover/focus.
- Tooltip content does not replace accessible names; it supplements them.
- Error and retry states are reachable by keyboard.
- Loading state announces progress where necessary without excessive live-region noise.

## Implementation Plan

1. Confirm product scope for drawer entries and permission visibility policy.
2. Add drawer state to the top-level frontend shell: `open`, `variant`, and active-route derived state.
3. Create `DrawerTrigger`, `NavigationDrawer`, `DimOverlay`, `NavSection`, and `NavItem` components.
4. Wire Routes to the existing SoundAtlas route/event selection state.
5. Wire Media Review to draft media/image links from loaded events and backend review actions.
6. Implement expanded and collapsed layouts with stable dimensions and no app-content reflow.
7. Add loading, empty, error, disabled, hover, active, saving, and focus states.
8. Add keyboard handling: trigger, `Esc`, focus return, tab order, and background inert behavior.
9. Validate with desktop screenshots, `npm run check`, `npm run build`, and backend/frontend tests.

## Acceptance Criteria

- Drawer opens from a visible desktop trigger and overlays the existing app without resizing the map.
- Expanded state shows Routes and Media Review nav items.
- Collapsed state shows icons only, with tooltips and accessible names.
- Active item matches the current route consistently.
- Media Review lists draft media and image links and supports direct review/reject actions.
- Disabled, loading, error, and empty states are defined and visually stable.
- Dim overlay blocks background interaction and closes on outside click.
- `Esc` closes the drawer and focus returns to the trigger.
- All interactive controls have visible focus styles.

## Validation Commands

- `npm run check` from `frontend/`.
- `npm run build` from `frontend/` for the implementation pass.
- Screenshot review at desktop widths around `1440px`, `1280px`, and `1024px`.

## Risks

- A modal overlay can interrupt map exploration if it stays open too often; keeping nav clicks open is recommended for desktop, but route changes should visibly update active state immediately.
- Collapsed icon-only navigation depends on excellent tooltips and accessible names; otherwise it becomes hard to learn.
- Permission-hidden items can make troubleshooting harder for internal users; use disabled items during MVP/admin workflows.
- If route switching is moved into the drawer, it must stay synchronized with map, timeline, and story state.

## Suggested File Groups for Review

- Documentation: `docs/design/2026-06-27-navigation-drawer-desktop-overlay-design.md`.
- Mockups: `docs/design/navigation-drawer-expanded-overlay.svg`, `docs/design/navigation-drawer-collapsed-overlay.svg`.
- Future implementation: `frontend/src/lib/components/NavigationDrawer.svelte`, drawer child components, and `frontend/src/routes/+page.svelte`.

## Suggested Commit Grouping

- `docs(design): define desktop overlay drawer concept`
- Future implementation: `feat(frontend): add desktop navigation drawer`
