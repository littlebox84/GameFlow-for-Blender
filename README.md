# GameFlow for Blender

> **From player to creator.**

GameFlow is a beginner-friendly control layer for Blender that makes the 3D viewport feel familiar to people coming from Roblox, Minecraft, Fortnite, first-person games, and controllers.

Instead of asking a new creator to memorize Blender navigation before they can build anything, GameFlow gives them controls they already understand, while keeping Blender's real modeling tools available underneath.

## Public alpha

Current version: **0.3.0**  
Target: **Blender 4.2+**

GameFlow is currently an early public alpha. The core idea works, but this is still being tested across Blender versions, workspaces, project loading, modeling modes, and different hardware.

## Core controls

| Input | Action |
|---|---|
| W / S | Move forward / backward |
| A / D | Strafe left / right |
| Q / E | Move down / up |
| Hold Right Mouse | Mouse-look + faster movement |
| Shift | Sprint |
| Mouse Wheel | Zoom |
| Double Right Mouse | Context menu |
| Left Mouse | Normal Blender interaction |
| F | Frame selected |
| F8 | Start / stop GameFlow |
| F3 | Blender command search |

## Design philosophy

**No manual should be required for the basics.**

GameFlow is designed around a few principles:

- familiar controls first;
- creation before shortcut memorization;
- keep normal Blender tools accessible;
- advanced settings should stay out of the way until needed;
- GameFlow should be a bridge into Blender, not a replacement for learning it.

The long-term goal is simple:

> **GameFlow should teach creation, not navigation.**

## Features

- Continuous WASD movement
- Q/E vertical movement
- Hold-RMB mouse-look
- Unlimited RMB look with automatic pointer recentering near viewport edges
- Optional cursor return after RMB look
- Sprint movement
- Direct mouse-wheel zoom
- Normal left-click interaction
- Double-right-click context menu
- Persistent navigation across Blender workspaces
- Recovery after opening or creating Blender projects
- Minimal GameFlow keymap to remove conflicting Blender shortcuts
- Modifier-safe runtime input so shortcuts such as Ctrl+S, Ctrl+Shift+S, Ctrl+Z and other modified keys remain Blender controls
- Focus-loss protection to prevent stuck movement after Alt-Tab or switching applications
- Configurable movement and mouse feel
- Beginner and advanced settings
- Steam Input/controller mapping guidance
- Keymap backup and restore workflow
- One-click **Repair GameFlow** recovery
- Copyable diagnostics for easier bug reports
- GitHub Actions Python syntax validation on pushes and pull requests

## UI

The GameFlow sidebar is designed so new users only see what matters first:

1. **Status** — READY or PAUSED, plus pause/resume.
2. **Quick Feel** — preset, movement speed, and look sensitivity.
3. **Controls** — a compact cheat sheet when needed.
4. **Controller / Steam Input** — optional controller setup.
5. **Advanced Settings** — input, motion, look, and startup tuning.
6. **Support & Recovery** — repair, diagnostics, keymap restore, settings reset, and full disable/restore.

## Why there is both an add-on and a keymap

GameFlow began as a custom Blender keymap. That solved part of the problem, but Blender's normal keymap system cannot provide true continuous game-style movement by itself.

The current design therefore has two cooperating layers:

1. **GameFlow runtime add-on** — handles continuous movement, mouse-look, sprinting, zoom, lifecycle recovery, and other behavior that a normal keymap cannot provide.
2. **GameFlow Minimal Keymap** — removes or redirects conflicting Blender shortcuts while preserving the essential modeling commands and menu access.

The add-on is the main product. `GameFlow_Minimal_Keymap.py` remains available as a standalone fallback/manual-import keymap and as part of the project's history.

## Installation

1. Download the latest GameFlow add-on ZIP.
2. Open Blender.
3. Go to **Edit → Preferences → Add-ons**.
4. Choose **Install from Disk**.
5. Select the GameFlow ZIP.
6. Enable **GameFlow for Blender**.
7. Open the 3D Viewport and press **N → GameFlow**.
8. Click **Enable GameFlow**.

If needed, `GameFlow_Minimal_Keymap.py` can also be imported manually from **Edit → Preferences → Keymap → Import**.

## Controller support

GameFlow currently supports controller workflows through **Steam Input**. Steam Input can map common controllers to GameFlow's keyboard and mouse controls, letting the same navigation engine work with Xbox, PlayStation, Steam Deck, and similar devices.

See [`docs/STEAM_INPUT_SETUP.md`](docs/STEAM_INPUT_SETUP.md).

## Advanced controls

GameFlow is meant to work intuitively out of the box, but advanced users can tune:

- movement speed;
- RMB movement boost;
- sprint multiplier;
- mouse sensitivity;
- acceleration/deceleration;
- scroll strength/direction;
- inverted look axes;
- Q/E movement reference;
- double-click timing;
- unlimited RMB-look edge wrapping;
- cursor return behavior;
- auto-start behavior;
- project-load recovery;
- keymap mode and restoration.

## Recovery

If GameFlow ever shows as enabled but navigation is not responding, open **Support & Recovery → Repair GameFlow**. It repairs stale runtime state, reapplies the selected keymap, and restarts navigation when possible.

For bug reports, use **Support & Recovery → Copy Diagnostics** and paste the result into the issue.

## Contributing

Bug reports, Blender-version testing, controller testing, UX feedback, and code contributions are welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Testing

See [`docs/TESTING_CHECKLIST.md`](docs/TESTING_CHECKLIST.md) for the current manual test matrix.

## Roadmap

See [`docs/ROADMAP.md`](docs/ROADMAP.md).

## License

A final public license is still being selected. See `LICENSE.txt` for the current project notice.
