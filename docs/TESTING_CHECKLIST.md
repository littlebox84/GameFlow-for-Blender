# GameFlow testing checklist

Before a public stable release, test at minimum:

## Installation and recovery

- Fresh Blender profile installation.
- Enable GameFlow and verify the keymap backup file is created.
- Run Health Check before enabling GameFlow, after enabling, and after Safe Mode.
- Enter Safe Mode and confirm normal Blender key bindings are restored.
- Exit Safe Mode and confirm the selected GameFlow keymap is reapplied.
- Repair GameFlow after deliberately pausing navigation.
- Restore Saved Blender Controls.
- Disable add-on with Restore Saved Controls enabled.
- Blender restart with Auto-start enabled.

## Navigation

- WASD forward/back/strafe in Object Mode and Edit Mode.
- Q/E vertical movement.
- RMB look, edge wrapping, and cursor return.
- Shift sprint.
- Mouse wheel zoom in/out while RMB is held and released.
- Double-RMB context menu.
- Left-click select, gizmos, buttons, Outliner and Properties.
- Middle-mouse orbit and Shift+Middle pan.
- F8 pause/resume.
- Ctrl+S, Ctrl+Z, Ctrl+Shift+S, Alt-modified keys, and OS/Command shortcuts pass through normally.
- Alt-Tab while holding movement/RMB and confirm no stuck input when returning.

## Workspaces and file lifecycle

- Workspace changes: Layout, Modeling, Shading, Scripting.
- Open another .blend file while GameFlow is running.
- File → New while GameFlow is running.
- Reconnect After Opening/New Project enabled and disabled.

## Build tools

- Select / Move / Rotate / Scale buttons from the GameFlow sidebar.
- Build Step nudging on X/Y/Z.
- Rotation Step controls on X/Y/Z.
- Duplicate + Offset on X/Y/Z.
- Drop to Floor with unrotated and rotated objects.
- Focus Selected from the sidebar.
- Blender increment snap toggle.

## v0.5 placement workflow

Test each primitive: Cube, Cylinder, Sphere, Plane, Cone.

- Start placement from the GameFlow Build panel.
- Wireframe preview appears and follows the mouse.
- Preview targets existing scene geometry when the mouse is over geometry.
- Preview falls back to world Z=0 when no surface is hit.
- Placement Grid Snap ON snaps all three axes to Build Step.
- Placement Grid Snap OFF allows unsnapped placement.
- Press R repeatedly and confirm the preview rotates by Rotation Step.
- Left Click places an object and converts it from preview to normal Blender geometry.
- Continuous Placement ON creates another preview after placement.
- Continuous Placement OFF exits after one placement.
- Escape cancels the active preview without deleting previously placed objects.
- Right Click cancels the active preview without opening an unwanted context menu.
- Switch workspace while placement is active and confirm Blender remains stable.
- Open/New file while placement is active and confirm no orphan preview object remains.
- Undo after one placement.
- Undo after several continuous placements.
- Save and reopen a file containing GameFlow-placed objects; objects should remain normal Blender data.

## Paint

- Plastic, Metal, Matte, Glass, and Glow on a new mesh.
- Apply a second GameFlow material preset to the same object.
- Undo material changes.

## HUD

- Full / Minimal / Off modes.
- READY / PAUSED state.
- SAFE state while Safe Mode is enabled.
- Selected object name updates.
- Build Step, Rotation Step, Placement Snap, and Continuous Placement values update.
- HUD remains confined to the 3D viewport and does not change Blender's global theme.

## Keymaps and controller

- Switch among Minimal / Conflicts Only / Native keymap modes.
- Steam Input controller mapping on Xbox / PlayStation / Steam Deck if available.
- Confirm the Steam Controller preset changes tuning only and does not claim to enable controller input.

## Blender versions

At minimum, validate the current alpha on:

- Blender 4.2 LTS
- Blender 4.3
- Blender 4.4
- Current Blender 5.x build supported by the tester

Record OS, Blender version, GameFlow version, keymap mode, preset, and Health Check output with every bug report.
