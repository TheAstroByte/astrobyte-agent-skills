---
name: davinci-resolve-reel-editing
description: Use when asked to plan or edit a reel in DaVinci Resolve. Interview for the purpose and footage first, then drive a reviewed cut through Codex and a verified Resolve connection.
---

# DaVinci Resolve reel editing

This optional skill guides Codex on an Apple Silicon workstation. It is an editorial process, not a bundled MCP server. If another agent receives the request, it may gather the brief and hand it to Codex; Codex owns Resolve editing and render verification. The skill can plan a reel before Resolve or footage exists.

## 1. Find the story

Start by asking what the reel is **for**. Ask who should see it, where it will appear, and what a viewer should understand, feel, or do. If the request already answers these, do not ask again. Continue with only the consequential gaps: available footage/assets and permission to use them, target length and aspect ratio, key moments and exclusions, tone, captions/language, music and rights, branding/safe areas, deadline, and delivery format. Ask in small related batches; suggest defaults for low-stakes details and let the user correct them. Do not invent footage, a campaign objective, a rights grant, or an export specification.

The brief is ready when purpose, audience, source material, and a reviewable output target are clear. If media does not exist yet, return a concise brief, shot list or capture plan, and the inputs needed later. Stop before editing.

## 2. Propose a cut

Inspect authorized source material without changing camera originals. Note frame rate, duration, orientation, audio, usable moments, and any missing assets. Draft a story order with source in/out points in source frames or timecode, intended pacing, vertical framing, captions, music, and a proposed export. Explain any unsupported operation or rights uncertainty. Show the cut plan and obtain approval before making project/timeline changes.

The plan is ready when someone can identify the intended sequence and approve or correct it without opening Resolve.

## 3. Prove the tool path

On the actual workstation, detect the installed Resolve **version and edition**, Codex's available MCP tools, transport, and the project's frame rate and resolution. Check the current Blackmagic release rather than hardcoding a version; use the newest installed, compatible release only after normal update approval. For Studio 21.1 or later, inspect Blackmagic's bundled AI integration first. Its presence does not prove which editing tools it exposes. If insufficient, review and explicitly approve a local-only third-party MCP before configuring Codex. Read [Resolve connection and capability notes](references/resolve-capabilities.md) only at this stage.

The tool path is ready when Codex has listed the actual callable tools, verified read-only project/timeline inspection on a disposable project, and identified a recovery path. If Resolve, media, permissions, or required tools are absent, stop with the exact blocker and retain the brief; never simulate a successful edit.

## 4. Edit with recovery

After approval, duplicate or archive the working project/timeline and record the source identity. Keep original media immutable. Use verified, narrow MCP actions to assemble the approved order on the duplicate; read back each consequential result. Check frame-rate and aspect-ratio settings by reading them back, not by trusting setters. Check captions, linked audio, reframing, transitions, and trims against the actual timeline. Ask before replacing/deleting clips, relinking sources, running arbitrary code, changing global settings, or selecting a render destination. Keep source-to-timeline edits recoverable and avoid unrestricted code or offline project-database writes by default.

Editing is complete when the duplicated timeline matches the approved cut and the original remains available.

## 5. Export and inspect

Approve the destination and format, then render. Inspect the actual output's dimensions, frame rate, duration, audio, captions, cropping, safe areas, opening/ending, and a playback sample at minimum. Compare against the brief and correct failures on the duplicate. Deliver the artifact or path with any remaining manual review items. Publishing or uploading is a separate request.

Completion requires a playable, inspected render, not a successful MCP response alone. If there is no real render, report the work as a plan or unverified draft.
