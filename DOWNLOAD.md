# Download GameFlow for Blender

## Current public alpha

**GameFlow for Blender v0.5.0-alpha2 — Placement & Stability Update**

Download the Blender-ready ZIP from the GitHub release page:

https://github.com/littlebox84/GameFlow-for-Blender/releases/tag/v0.5.0-alpha2

### Install

1. Download `GameFlow-for-Blender-v0.5.0-alpha2.zip`.
2. Open Blender.
3. Go to **Edit → Preferences → Add-ons**.
4. Choose **Install from Disk**.
5. Select the ZIP **without extracting it**.
6. Enable **GameFlow for Blender**.
7. Open the 3D Viewport and use **N → GameFlow**.
8. Click **Enable GameFlow**.

### What changed in 0.5.0 alpha2

- Ghost-preview placement for Cube, Cylinder, Sphere, Plane, and Cone
- Objects now rest against hit surfaces using their transformed bounding boxes instead of placing their centers inside geometry
- Placement Grid Snap using the GameFlow Build Step
- Continuous Placement mode
- R-to-rotate placement preview
- Orphan preview cleanup on register, unregister, and file-load transitions
- Object Mode safety check for placement
- New GameFlow Health Check
- New Safe Mode that restores normal Blender controls while keeping Creator tools
- Safe Mode now survives project/file loading without GameFlow silently re-enabling its keymap
- Updated dark HUD with SAFE state and placement information
- Expanded v0.5 testing checklist
- Existing Explore, Build, Paint, presets, keymap backup/restore, Repair GameFlow, and Steam Input guidance remain intact

This release is still an alpha. Python syntax is validated automatically, but placement behavior should be tested in real Blender scenes before being considered stable.

The release also includes a SHA-256 checksum file for verifying the download.
