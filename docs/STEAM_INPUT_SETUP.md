# GameFlow Steam Input Controller Layout

GameFlow's controller approach uses Steam Input to emit ordinary keyboard and mouse events. That keeps controller support simple and compatible with GameFlow's existing navigation system.

## Recommended mapping

| Controller input | Steam Input output | GameFlow action |
|---|---|---|
| Left Stick | W / A / S / D | Move |
| Right Stick | Mouse | Look while Left Trigger is held |
| Left Trigger | Right Mouse | Hold to mouse-look; double-tap for context |
| Right Trigger | Left Mouse | Select / interact |
| Left Bumper | Q | Move down |
| Right Bumper | E | Move up |
| Left Stick Click | Shift | Sprint |
| A / Cross | Enter | Confirm |
| B / Circle | Esc | Cancel |
| X / Square | F3 | Blender command search |
| Y / Triangle | F | Frame selected |
| D-pad Up | Ctrl+1 | Select tool |
| D-pad Right | Ctrl+2 | Move tool |
| D-pad Down | Ctrl+3 | Scale tool |
| D-pad Left | Ctrl+4 | Rotate tool |
| Menu / Start | F8 | Pause / Resume GameFlow navigation |

## Setup outline

1. Launch Blender through Steam, or add a non-Steam Blender installation to the Steam library.
2. Open Steam's controller layout for Blender.
3. Map the controls using the table above.
4. In Blender, choose the **Steam Controller** GameFlow preset.
5. Start GameFlow.

Because Steam Input presents these inputs as keyboard/mouse events, GameFlow does not require controller-specific Python libraries.
