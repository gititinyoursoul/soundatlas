# Spec: Event Inspector

## Status

Draft

## Request

Create a tabbed event inspector for the main SoundAtlas screen so the right-side story surface can scale to richer image previews, media embeds, and citation material.

## Goal

The selected event panel should present story, media, and sources as separate views while keeping the map primary and the timeline compact.

## Non-goals

* NG1: Rework backend endpoints or seed schema.
* NG2: Make the inspector an admin review surface.

## Change type

* Type: frontend-only

## Scope

* Routes/pages: `frontend/src/routes/+page.svelte`
* Components: `frontend/src/lib/components/StoryPanel.svelte`, `frontend/src/lib/components/MediaEmbed.svelte`
* Docs/TODOs: `docs/design/current-frontend-design.md`, `docs/done.md` if the work is completed

## Requirements

* R1: The right-side panel must present `Story`, `Media`, and `Sources` tabs.
* R2: The `Story` tab must remain the default reading view for the selected event.
* R3: The `Media` tab must show image and media previews in fixed-size layouts.
* R4: The `Sources` tab must list source URLs separately from media links.
* R5: Admin review actions must stay out of the public inspector surface.

## Acceptance criteria

* AC1: The right-side panel reads as an event inspector rather than a single scrolling story column.
* AC2: The `Story` tab shows narrative and significance without repeating media-summary boilerplate.
* AC3: The `Media` tab shows previews without stretching the panel vertically.
* AC4: The `Sources` tab shows citations separately from the media gallery.
* AC5: Public browsing does not expose admin review controls.

## Assumptions

* A1: Existing event data already includes `summary`, `significance`, `source_urls`, `media_links`, `image_links`, and `connections`.
* A2: The main page remains the shared selection-state owner.

## Open questions

* Q1: Should the inspector remember the last selected tab per event?
* Q2: Should the media tab prefer image previews or playable embeds when both exist?

