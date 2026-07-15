---
name: record-nexrex-with-loom
description: Use when asked to record a Loom proof of a NexRex UI interaction in Google Chrome, especially when Specific window stalls, selects the wrong app, shows Cropping, or needs a second Start recording click.
---

# Record NexRex with Loom

## Overview

Record one safe NexRex navigation in a Chrome-only Loom video.

## Guardrails

- Use `computer-use` through `node_repl` for all UI actions.
- Keep camera, microphone, and computer audio off.
- Use an already signed-in NexRex page and one safe sidebar click; make no other NexRex changes.
- Dismiss low-disk only; never clean disk.
- No macOS fallback; Loom failure is failure.
- Preserve recordings without explicit deletion approval.
- Refresh state before clicks; never reuse indices.

## Preflight

1. Choose a harmless Chrome destination different from the current NexRex page.
2. Require `Specific window`, `No Camera`, `No Microphone`, and computer sounds off.
3. If `Low on disk space` appears, click `Dismiss` and re-read the settings.

## Select Chrome

1. Click the first `Start recording` and require `Hover over a window to select`.
2. Press `Cmd+Tab` from Loom with `sky.press_key({ app: "Loom", key: "super+Tab" })`.
3. Require a fresh Chrome state titled `NexRex Web Console`.
4. Through `node_repl`, execute `scripts/hover-frontmost-chrome.swift` with `/usr/bin/swift`. It verifies Chrome is frontmost and posts Loom's required mouse-move event.
5. Require button `Select Google Chrome`; reject every other app.
6. Click `Select Google Chrome`.
7. If `Loom Cropping` has focus, choose `Loom Recorder Settings` from Loom's `Window` menu.

## Record and Finish

1. From the restored Recorder Settings, click the second `Start recording`.
2. If `Your mic is muted` appears, click `Continue`; never click `Unmute`.
3. Let the countdown finish. Post-countdown `Loom Cropping` means recording is active.
4. Press `Cmd+Tab`, require NexRex Chrome, and click the chosen destination.
5. Choose `Loom Control Menu` from Loom's `Window` menu; require `Finish recording` and a timer.
6. Click `Finish recording`. A `noWindowsAvailable` response is acceptable only when a fresh Loom state shows Recorder Settings and no Control Menu.

## Reset on Any Mismatch

Never repair a partial picker. From Loom's `Window` menu choose `Loom Recorder Settings`, click `Back`, require initial settings, and restart. Dismiss low-disk first; selection interruptions invalidate the attempt.

## Verification

Open `My Videos`, then verify the newest recording:

- opens and plays;
- shows only the Chrome window;
- contains the NexRex page navigation;
- provides a Loom share URL.

Report duration. Missing evidence means failure.

## Common Mistakes

| Symptom | Cause | Correction |
|---|---|---|
| Picker remains on hover | Semantic Chrome clicks do not create hover | `Cmd+Tab`, run the helper, require `Select Google Chrome` |
| Loom offers ChatGPT | Chrome is not truly frontmost | Reset and switch with `Cmd+Tab` |
| Selection appears complete but recording never starts | Only the first Start was clicked | Return to Recorder Settings and click the second Start |
| Controls are missing | `Loom Cropping` owns focus | Open `Loom Control Menu` from `Window` |
