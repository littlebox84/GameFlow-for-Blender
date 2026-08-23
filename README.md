# GameFlow for Blender

> **From player to creator.**

GameFlow is a beginner-friendly control and creation layer for Blender. It keeps Blender powerful while making navigation, placement, building, and simple material work feel more like a familiar game editor.

## Public alpha

Current version: **0.5.0**  
Target: **Blender 4.2+**

## The idea

**No manual should be required for the basics.**

> **GameFlow should teach creation, not navigation.**

## What is new in 0.5 — Placement & Stability

GameFlow 0.5 adds the first true game-editor-style placement workflow plus a stronger recovery/safety layer.

### Ghost Placement

In **Build** mode, choose Cube, Cylinder, Sphere, Plane, or Cone from the Placement section.

- Move the mouse to move a wireframe preview.
- GameFlow raycasts against scene geometry when possible and falls back to the world floor.
- Left Click places the object.
- Press **R** to rotate the preview by the configured Rotation Step.
- Press **Esc** or Right Click to exit placement.
- **Continuous Placement** can keep creating objects until you exit.
- **Placement Grid Snap** snaps preview positions to the configured Build Step.

Placed objects become normal Blender objects immediately.

### Health Check

GameFlow now includes a one-click health report covering:

- Blender version support
- 3D Viewport availability
- GameFlow preferences
- enabled/runtime status
- navigation status
- keymap backup state
- Safe Mode
- viewport HUD state

The health report is copied to the clipboard so it can be pasted directly into a bug report.

### Safe Mode

**Safe Mode** keeps GameFlow Creator tools available while restoring normal Blender key bindings and pausing GameFlow navigation.

This gives users a fast recovery option if a control conflict appears without requiring them to uninstall the add-on.

## Dark Viewport HUD

GameFlow includes an optional dark in-viewport HUD without changing Blender's global theme.

- **Full** — Creator Mode, READY/PAUSED/SAFE state, selected object, mode-specific data, and hints.
- **Minimal** — compact mode/status/selection display.
- **Off** — no GameFlow HUD.

Build mode now shows placement snap and continuous-placement status in addition to Build Step and Rotation Step.

## Control Feel Presets

These presets change how GameFlow **feels**. They do not change what GameFlow fundamentally does.

| Preset | Best for | What changes |
|---|---|---|
| **GameFlow** | Most keyboard + mouse users | Balanced default movement, mouse-look, acceleration, and zoom. |
| **Roblox** | Roblox / Roblox Studio users | Faster movement and stronger RMB speed boost. |
| **Minecraft** | Minecraft players | Tighter keyboard + mouse movement and response. |
| **First-Person** | Experienced FPS players | Faster, snappier movement and sprint response. |
| **Steam Controller** | Gamepads mapped through Steam Input | Smoother acceleration and lower look sensitivity for analog sticks. |
| **Accessibility** | Users wanting gentler controls | Slower movement, camera response, acceleration, and sprinting. |
| **Custom** | Advanced users | Uses manually tuned values. |

### Steam Controller preset vs Steam Input

These are **not the same thing**.

- **Steam Input** maps a physical controller to GameFlow's keyboard/mouse controls.
- **Steam Controller preset** only changes GameFlow tuning so analog input feels smoother.

For controller use: configure Steam Input first, then try the Steam Controller preset.

## Creator Modes

### Explore

- WASD movement
- Q/E vertical movement
- Hold RMB mouse-look + movement boost
- Shift sprint
- Mouse wheel zoom
- Double RMB context menu
- F frame selected
- F8 pause/resume

### Build

- Ghost-preview primitive placement
- Surface/world-floor targeting
- Placement grid snapping
- Continuous placement
- R-to-rotate preview
- Select / Move / Rotate / Scale tools
- Adjustable Build Step
- Adjustable Rotation Step
- X/Y/Z nudging
- X/Y/Z step rotation
- Duplicate + Offset
- Drop to Floor
- Focus Selected

### Paint

- Plastic
- Metal
- Matte
- Glass
- Glow

The generated objects and materials remain normal Blender data.

## Core reliability

- Persistent navigation across workspaces
- Recovery after opening or creating Blender projects
- Unlimited RMB look with pointer recentering
- Optional cursor return after RMB look
- Modifier-safe input so Ctrl+S, Ctrl+Z and other Blender shortcuts pass through normally
- Focus-loss protection to prevent stuck movement after Alt-Tab
- Minimal / Conflicts Only / Native Blender keymap modes
- Automatic keymap backup and restoration
- One-click **Repair GameFlow**
- **Safe Mode** recovery
- **Health Check** diagnostics
- Copyable diagnostics for bug reports
- Steam Input/controller mapping guidance

## Installation

1. Download the latest GameFlow ZIP from Releases.
2. In Blender open **Edit → Preferences → Add-ons**.
3. Choose **Install from Disk**.
4. Select the ZIP without extracting it.
5. Enable **GameFlow for Blender**.
6. Open the 3D Viewport and press **N → GameFlow**.
7. Click **Enable GameFlow**.

## Controller support

GameFlow currently supports controller workflows through **Steam Input**. See [`docs/STEAM_INPUT_SETUP.md`](docs/STEAM_INPUT_SETUP.md).

## Architecture

GameFlow uses cooperating layers:

1. **Runtime navigation** — continuous game-style movement and mouse-look.
2. **Creator tools** — Build, placement, Paint, and recovery actions.
3. **GameFlow keymap layer** — removes conflicting shortcuts while keeping Blender access available.
4. **HUD/UI layer** — beginner-focused status, controls, and context.

`GameFlow_Minimal_Keymap.py` remains available as a standalone fallback/manual import.

## Testing status

GameFlow is still a public alpha. Python syntax is validated automatically in GitHub Actions, but new placement behavior needs real Blender testing across supported versions and different scenes before it should be considered stable.

See [`docs/TESTING_CHECKLIST.md`](docs/TESTING_CHECKLIST.md).

## Recovery

If GameFlow is enabled but navigation is not responding, use **Support & Recovery → Repair GameFlow**. If controls conflict, use **Health & Safety → Enter Safe Mode**.

For bug reports, run **Health Check** and **Copy Diagnostics** and paste both into a GitHub issue.

## Contributing

Bug reports, Blender-version testing, controller testing, placement testing, UX feedback, and code contributions are welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Roadmap

See [`docs/ROADMAP.md`](docs/ROADMAP.md).

## License

A final public license is still being selected. See `LICENSE.txt` for the current project notice.
