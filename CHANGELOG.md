# Changelog

## 0.4.0 — Creator update

- Added **Creator Mode** with Explore, Build, and Paint workflows.
- Added a new `build_tools.py` module for beginner-friendly object creation and manipulation.
- Added quick primitive creation for Cube, Cylinder, Sphere, Plane, and Cone.
- Added one-click Select / Move / Rotate / Scale tool switching.
- Added configurable **Build Step** used by object nudging and duplicate-offset actions.
- Added configurable **Rotation Step** for game-editor-style stepped rotation.
- Added X/Y/Z nudge controls for precise placement without memorizing Blender transform commands.
- Added X/Y/Z step rotation controls.
- Added Duplicate + Offset along X, Y, or Z for fast construction workflows.
- Added **Drop to Floor** to place selected objects on world Z = 0 using their transformed bounding boxes.
- Added **Focus Selected** from the GameFlow Build panel.
- Added a one-click increment snap toggle.
- Added **Paint mode** with beginner material presets: Plastic, Metal, Matte, Glass, and Glow.
- Redesigned the main panel around Creator Mode while preserving the v0.3 navigation/recovery tools.
- Diagnostics now include Creator Mode and build-step settings.

## 0.3.0 — UI and core safety

- Redesigned the GameFlow sidebar around a simpler first-use flow: status, quick feel, controls, controller setup, advanced settings, and support/recovery.
- Added a compact **READY / PAUSED** runtime status with the active preset visible at a glance.
- Added a cleaner two-column control cheat sheet and collapsible sections so beginners are not hit with every option at once.
- Added **Repair GameFlow**, a one-click recovery action that repairs stale runtime state, reapplies the selected GameFlow keymap, and restarts navigation when possible.
- Added a dedicated **Support & Recovery** section containing diagnostics, keymap repair, saved-control restoration, settings reset, and full disable/restore actions.
- Fixed a core input issue where GameFlow could capture modified movement letters such as **Ctrl+S**. Modifier shortcuts using Ctrl, Alt, or OS/Command now pass through to Blender normally.
- Added focus-loss protection: held movement keys and RMB-look state are cleared when Blender loses window focus, preventing stuck movement after Alt-Tab or app switching.
- Pressing Escape while RMB-look is active now safely releases GameFlow look state without changing normal Escape behavior when RMB-look is not active.

## 0.2.1 — Mouse-look and support polish

- Added **Unlimited RMB Look** with pointer recentering near viewport boundaries.
- Added optional **Return Cursor After RMB Look**.
- Added **Copy Diagnostics** for bug reports.

## 0.2.0 — Public alpha

- Consolidated the project as **GameFlow for Blender — From player to creator.**
- Added one-click GameFlow enable workflow, keymap backup/restore, persistent file-load recovery, WASD + Q/E navigation, RMB mouse-look, sprint, wheel zoom, presets, Steam Input guidance, and recovery tools.

## 0.1.0 — Prototype

- Initial branded GameFlow beta based on the Kid Mode navigation prototype.
