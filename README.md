# GameFlow for Blender

> **From player to creator.**

GameFlow is a beginner-friendly control and creation layer for Blender. It makes the 3D viewport feel familiar to people coming from Roblox, Minecraft, Fortnite, first-person games, and controllers — then gives them simple creator tools so they can start building immediately.

## Public alpha

Current version: **0.4.0**  
Target: **Blender 4.2+**

## The idea

**No manual should be required for the basics.**

GameFlow is built around one rule:

> **GameFlow should teach creation, not navigation.**

## Creator Modes

### Explore
Game-style movement and viewport control.

- WASD movement
- Q/E vertical movement
- Hold RMB mouse-look + movement boost
- Shift sprint
- Mouse wheel zoom
- Double RMB context menu
- F frame selected
- F8 pause/resume

### Build
A game-editor-style object workflow layered on top of real Blender tools.

- Quick Select / Move / Rotate / Scale tools
- Add Cube / Cylinder / Sphere / Plane / Cone
- Adjustable build step
- Adjustable rotation step
- Grid snapping toggle
- One-click X/Y/Z nudging
- Step rotation around X/Y/Z
- Duplicate + offset along X/Y/Z
- Drop selected objects to world floor
- Focus selected object

### Paint
Beginner-friendly material presets without requiring shader-node knowledge first.

- Plastic
- Metal
- Matte
- Glass
- Glow

The generated objects and materials are still normal Blender data. GameFlow is a bridge into Blender, not a separate editor.

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

GameFlow currently supports controller workflows through **Steam Input**, mapping common controllers to the same GameFlow navigation system. See [`docs/STEAM_INPUT_SETUP.md`](docs/STEAM_INPUT_SETUP.md).

## Why there is both an add-on and a keymap

GameFlow began as a custom Blender keymap. A keymap alone cannot provide true continuous game-style movement, so the project now uses two cooperating layers:

1. **Runtime add-on** — continuous movement, mouse-look, build tools, materials, lifecycle recovery and UI.
2. **GameFlow keymap layer** — removes or redirects conflicting shortcuts while keeping Blender menus and essential modeling access available.

`GameFlow_Minimal_Keymap.py` remains available as a standalone fallback/manual import.

## Recovery

If GameFlow says it is enabled but navigation is not responding, use **Support & Recovery → Repair GameFlow**.

For bug reports, use **Support & Recovery → Copy Diagnostics** and paste the result into a GitHub issue.

## Contributing

Bug reports, Blender-version testing, controller testing, UX feedback, and code contributions are welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Testing

See [`docs/TESTING_CHECKLIST.md`](docs/TESTING_CHECKLIST.md).

## Roadmap

See [`docs/ROADMAP.md`](docs/ROADMAP.md).

## License

A final public license is still being selected. See `LICENSE.txt` for the current project notice.
