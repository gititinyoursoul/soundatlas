# Media Pipeline Notes

## Goal

The existing media enrichment pipeline should be improved so that musical event seed data produces better, more explainable, and more editorially reviewable media suggestions.

The focus is on:

1. Introducing media intents
2. Structuring event information more clearly
3. Separating query planning from the actual search process
4. Normalizing, filtering, and reviewing provider results more effectively

---

## 1. Analyze the Existing Workflow

Review how the current process works:

- How are events currently structured?
- Which fields are currently used for queries?
- How are YouTube, Spotify, and Qobuz queried?
- How are results currently stored?
- Is there already a review status, deduplication, or ranking mechanism?
- Where do poor or inaccurate search results currently occur?

Goal: Clearly identify the weak points in the current pipeline.

---

## 2. Structure Event Data Conceptually

Event data should not only be treated as a collection of text fields and tags. It should become a structured starting point for search.

Clarify:

- Which artists are primary to the event?
- Which artists are only associated?
- Are there specific songs, works, or albums?
- Are there relevant places, cities, countries, or venues?
- Are there genres, scenes, or historical terms?
- Which terms come from the route?
- Which terms are reliable?
- Which terms are only possible aliases or interpretations?

Goal: Queries should not be generated from unsorted event fields, but from clearly evaluated search components.

---

## 3. Introduce Media Intents

Not every event needs the same types of media. Therefore, suitable search intents should be determined for each event.

Possible media intents:

- Official track
- Official music video
- Live video
- Interview
- Documentary
- Playlist
- Album
- Artist profile
- Venue context
- Historical context

Clarify:

- Which intents are truly relevant for an event?
- Which intents have high priority?
- Which intents are optional?
- Which intents should not be searched for certain events?

Goal: The search becomes more targeted because not all media types are searched using the same queries.

---

## 4. Introduce Query Planning as a Separate Process Step

The pipeline should not generate API queries directly from an event. Instead, it should first create a query plan.

The query plan should define:

- Which provider is searched
- Which media intent is searched
- What priority the search has
- What type of query is used
- What type of result is expected
- Which false positives are likely

Goal: The search becomes easier to plan, test, and debug.

---

## 5. Distinguish Query Types

Queries should be separated by purpose.

Useful query types:

- Precise queries for highly likely matches
- Context queries for interviews, documentaries, or historical context
- Discovery queries for broader exploratory results

Clarify:

- Which query types should be stored automatically?
- Which query types should only be used for expansion?
- Which query types require stronger editorial review?
- Which query types should be assigned lower priority?

Goal: Broad exploratory results are not mixed with high-precision matches.

---

## 6. Treat Providers Separately

YouTube, Spotify, and Qobuz should not be handled with the same logic.

### YouTube

Suitable for:

- Live videos
- Interviews
- Documentaries
- Music videos
- Official audio uploads
- Playlists
- Historical TV or archive recordings

Especially important:

- Detecting the media type
- Evaluating channel quality
- Checking duration
- Checking title and description
- Detecting false positives such as reactions, covers, or tutorials

### Spotify

Suitable for:

- Tracks
- Albums
- Artists
- Playlists

Especially important:

- Artist name
- Track title
- Album title
- Genre or scene terms

Less important:

- Venue
- Route
- Place

### Qobuz

Suitable for:

- Tracks
- Albums
- High-quality music metadata

Especially important:

- Artist
- Work
- Album
- Release context

Less important:

- Broad historical or location-based queries

Goal: Each provider is used according to its strengths.

---

## 7. Define Negative Terms and Error Types

It should be clearly defined which terms often indicate false or less relevant results.

Examples:

- Cover
- Reaction
- Karaoke
- Tutorial
- Lesson
- Remix
- Tribute
- Fan made
- Sped up
- Slowed
- AI cover

Clarify:

- Which terms should lead to a hard rejection?
- Which terms should only create a warning?
- Which terms should be evaluated differently depending on the media intent?
- When can such a term still be relevant?

Goal: False positives are detected earlier without unnecessarily excluding relevant edge cases.

---

## 8. Normalize Results

All provider results should be converted into one shared internal format.

Clarify:

- What minimum information does each result need?
- How are provider IDs stored?
- How are titles, descriptions, artists, channels, or sources stored?
- How is the original search context stored?
- How is the suspected media type stored?
- How are warnings and match reasons stored?

Goal: Results from different providers can be evaluated, compared, and stored consistently.

---

## 9. Evaluate YouTube Results More Precisely

YouTube results need special attention because they are highly heterogeneous.

Check:

- Is the result an official upload?
- Is it a live recording?
- Is it an interview?
- Is it a documentary?
- Is it a cover, reaction, or tutorial?
- Is the video duration plausible?
- Does the channel fit the expected media type?
- Does the publication date fit the context, or is it irrelevant?
- Are there signs of the wrong artist or wrong work?

Goal: YouTube is treated not just as a link source, but as a heterogeneous media source.

---

## 10. Use Match Status Instead of GPT Confidence

Instead of GPT-generated numerical confidence values, simple and explainable status values should be used.

Recommended status values:

- Strong
- Medium
- Weak
- Reject

Clarify:

- When is a result considered strong?
- When is a result considered medium?
- When is a result considered weak?
- When is a result rejected?
- Which rules determine the status?
- Which cases require editorial review?

Goal: Avoid false precision from invented confidence scores.

---

## 11. Introduce Match Reasons and Warnings

Each result should make clear why it was suggested and what risks exist.

Possible match reasons:

- Artist found
- Song or work found
- Album found
- Year found
- Place found
- Matching media type detected
- Official context detected
- Plausible duration
- Result confirmed by another provider

Possible warnings:

- Possible cover
- Possible reaction
- Possible remix
- Possible tutorial
- Year not found
- Place not found
- Unusual duration
- Source not official
- Artist or title is ambiguous
- Poor metadata quality

Goal: Editorial review becomes faster and easier to understand.

---

## 12. Use Ranking Only as Internal Sorting

Ranking can be useful, but it should not be presented as an absolute truth.

Clarify:

- Which signals improve ranking?
- Which signals reduce ranking?
- Which results should appear at the top?
- Which results should only be shown as context?
- Which results should not be suggested at all?

Goal: Ranking helps with sorting but does not replace expert review.

---

## 13. Improve Deduplication

Results should not be stored multiple times if they represent the same media item.

Check:

- Is the URL identical?
- Is the provider ID identical?
- Are the titles very similar?
- Do artist and work match?
- Is the duration similar?
- Is it the same track on different platforms?
- Is it the same video in different uploads?
- Should a result be treated as an alternative or as a duplicate?

Goal: The app stores media items more cleanly and avoids duplicate suggestions.

---

## 14. Introduce Canonical Media Items

Several links can describe the same underlying media item.

Example:

- A track on Spotify
- The same track on Qobuz
- The official audio on YouTube

These should be treated conceptually as one shared media item.

Clarify:

- What is the canonical media item?
- Which provider links belong to it?
- What role does each link have?
- Which link is primary?
- Which links are alternatives?
- Which links are contextual media?

Goal: Seed data becomes less link-centered and more media-centered.

---

## 15. Structure the Review Process

Editorial review should store more than just whether something was checked.

Clarify:

- Was a result accepted?
- Was a result rejected?
- Why was it accepted?
- Why was it rejected?
- Is the result a duplicate?
- Is it technically correct but only secondarily relevant?
- Is it a good contextual result?
- Does it need to be reviewed again later?

Goal: Review data becomes useful quality feedback for future improvements.

---

## 16. Standardize Review Reasons

To make later analysis possible, review reasons should not be free text only. They should be standardized.

Possible review reasons:

- Official source
- Correct artist
- Correct work
- Good context
- Wrong artist
- Wrong work
- Cover version
- Reaction video
- Low quality
- Duplicate
- Not relevant

Goal: The pipeline can learn from editorial decisions.

---

## 17. Improve Dry-Run Mode

Dry run should help understand the pipeline without changing seed data.

The dry run should show:

- Which event is being processed
- Which entities were identified
- Which media intents are used
- Which queries are planned
- Which providers would be queried
- Which results were found
- Which match reasons and warnings were detected
- Which results would be stored
- Which results would be discarded

Goal: Debugging and editorial understanding become much easier.

---

## 18. Build a Test Set for Quality Control

A small manually reviewed test set should help make improvements measurable.

Create:

- Different event types
- Expected good results
- Expected bad results
- Typical false positives
- Difficult edge cases

Check:

- Are good results still found?
- Are bad results reduced?
- Are too many good results accidentally discarded?
- Does the separation by media intent work?
- Does provider-specific search work?

Goal: Changes to queries or filters can be evaluated systematically.

---

## 19. Use GPT in a Focused and Limited Way

GPT should not freely decide every step. It should only help where semantic understanding is useful.

Useful GPT tasks:

- Identifying event entities
- Suggesting possible aliases
- Suggesting media intents
- Describing search risks
- Detecting semantic warnings
- Summarizing review data

Not useful:

- Inventing numerical confidence values
- Making the final ranking decision alone
- Adding unverified facts
- Directly storing results without rules or review

Goal: GPT supports the pipeline but does not replace controlled logic.

---

## 20. Plan the Implementation in Phases

### Phase 1: Build the Foundation

- Introduce media intents
- Structure event information more clearly
- Define query planning as a separate step
- Separate provider-specific search logic
- Define negative terms and warnings

### Phase 2: Improve Quality

- Normalize results
- Classify YouTube results more accurately
- Introduce match status
- Store match reasons and warnings
- Improve dry-run mode

### Phase 3: Strengthen Editorial Workflow and Data Quality

- Structure the review process
- Standardize review reasons
- Improve deduplication
- Introduce canonical media items

### Phase 4: Test Systematically

- Build a test set
- Collect typical error cases
- Test changes against the test set
- Use review data for improvements

---

## Core Guiding Principle

The pipeline should no longer be understood as:

```text
Event → Query → API result → Confidence → Store
```

Instead, it should be understood as:

```text
Event
→ structured search components
→ suitable media intents
→ planned search process
→ provider-specific search
→ normalized results
→ match status, reasons, and warnings
→ deduplication
→ editorial review
→ quality feedback
```

The goal is not to generate more text or more GPT output. The goal is to build a pipeline that is more controlled, easier to review, and easier to improve over time.
