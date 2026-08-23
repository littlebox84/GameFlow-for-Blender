# Changelog

## 0.5.0 — Placement & Stability

- Added **ghost-preview object placement** in Build mode for Cube, Cylinder, Sphere, Plane, and Cone.
- Added scene raycast targeting with world-floor fallback for placement.
- Added optional **Placement Grid Snap** using the existing GameFlow Build Step.
- Added optional **Continuous Placement** so users can keep placing objects until Escape or Right Click.
- Added **R-to-rotate** during placement using the configured Rotation Step.
- Added a dedicated `placement.py` module for the modal preview/placement workflow.
- Added **GameFlow Health Check** covering Blender version, viewport availability, preferences, runtime state, keymap backup, Safe Mode, and HUD state.
- Added **Safe Mode**, which restores normal Blender controls while keeping GameFlow Creator tools available.
- Updated diagnostics to include Safe Mode and placement settings.
- Updated the dark HUD with SAFE state plus placement snap/continuous-placement information.
- Reorganized the Build panel around Placement first, with transform, nudge, rotate, duplicate, floor, and focus tools below it.
- Kept the existing v0.4 Creator Modes, dark HUD, preset guidance, navigation safety, keymap backup/restore, and Steam Input support intact.

## 0.4.1 — Dark HUD update

- Added an optional **dark in-viewport GameFlow HUD** without changing Blender's global theme.
- Added **Full / Minimal / Off** HUD modes.
- Full HUD shows Creator Mode, READY/PAUSED state, selected object, mode-specific information, and navigation hints.
- Build mode HUD shows build step, rotation step, and snapping state.
- Explore mode HUD shows movement speed and look sensitivity.
- Paint mode HUD shows a quick material-workflow hint.
- Added a clear **Control Feel Guide** explaining the difference between GameFlow, Roblox, Minecraft, First-Person, Steam Controller, Accessibility, and Custom presets.
- Clarified that **Steam Input** is the controller-mapping layer, while the **Steam Controller preset** only changes GameFlow movement/look tuning.

## 0.4.0 — Creator update

- Added **Creator Mode** with Explore, Build, and Paint workflows.
- Added beginner-friendly object creation and manipulation tools.
- Added configurable Build Step and Rotation Step.
- Added X/Y/Z nudging, stepped rotation, Duplicate + Offset, Drop to Floor, Focus Selected, snapping, and quick material presets.

## 0.3.0 — UI and core safety

- Redesigned the GameFlow sidebar around a simpler first-use flow.
- Added READY / PAUSED runtime status and Repair GameFlow.
- Fixed modified-key capture so Ctrl/Alt/OS shortcuts pass through normally.
- Added focus-loss protection to prevent stuck movement.

## 0.2.1 — Mouse-look and support polish

- Added Unlimited RMB Look with pointer recentering.
- Added optional Return Cursor After RMB Look.
- Added Copy Diagnostics.

## 0.2.0 — Public alpha

- Consolidated the project as **GameFlow for Blender — From player to creator.**
- Added one-click GameFlow enable workflow, keymap backup/restore, file-load recovery, WASD + Q/E navigation, RMB mouse-look, sprint, wheel zoom, presets, Steam Input guidance, and recovery tools.

## 0.1.0 — Prototype

- Initial branded GameFlow beta based on the Kid Mode navigation prototype.
