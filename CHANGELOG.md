# Changelog

## 0.2.1 — Mouse-look and support polish

- Added **Unlimited RMB Look** so mouse-look can continue without getting stuck at the viewport edge.
- Added automatic pointer recentering near viewport boundaries during RMB look.
- Added optional **Return Cursor After RMB Look** so the pointer goes back to where the look gesture started.
- Added adjustable edge-wrap margin for users who want to tune the behavior.
- Added a clearer beginner-facing GameFlow panel with version/status information and a simplified control cheat sheet.
- Added **Copy Diagnostics** for bug reports, including GameFlow version, Blender version, operating system, preset, keymap mode, navigation state, and lifecycle settings.
- Updated reset behavior to restore the new mouse-look defaults.

## 0.2.0 — Public alpha

- Rebranded and consolidated the project as **GameFlow for Blender — From player to creator.**
- Added one-click **Enable Full GameFlow Controls** workflow.
- Added safe backup/restore of affected Blender shortcut active states.
- Added three keymap modes: GameFlow Minimal, Conflicts Only, Native Blender.
- Added persistent file-load recovery so GameFlow can reconnect after opening or creating a project.
- Added game-style continuous WASD + Q/E movement.
- Added RMB mouse-look, RMB movement boost, Shift sprint, reliable wheel zoom and double-RMB context menu.
- Preserved left-click Blender interaction and normal non-viewport UI behavior.
- Added movement smoothing with acceleration/deceleration controls.
- Added look/zoom inversion and world-relative vs view-relative vertical movement.
- Added presets: GameFlow, Roblox, Minecraft, First-Person, Steam Controller, Accessibility, Custom.
- Added Steam Input controller mapping documentation and copy-to-clipboard helper.
- Added GameFlow reset, keymap reapply, saved-controls restore and Blender-default restore actions.
- Added F8 pause/resume navigation.

## 0.1.0 — Prototype

- Initial branded GameFlow beta based on the Kid Mode navigation prototype.
- Added workspace-aware runtime movement and early file-load restart handling.

### Reliability fixes included in the 0.2.0 package

- Added a runtime heartbeat so stale "GameFlow is running" flags recover automatically after a destroyed modal operator.
- Mouse-move events now pass through when RMB look is not active, preserving hover, gizmos and left-click dragging.
- Conflicts-only mode no longer disables modified combinations such as Ctrl/Shift shortcuts just because they use W/A/S/D/Q/E.
- Included `GameFlow_Minimal_Keymap.py` as the standalone successor to the original custom keybinding used by the prototype.
