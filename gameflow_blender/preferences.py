import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty
from bpy.types import AddonPreferences

ADDON_ID = __package__

PRESETS = {
    'GAMEFLOW': {'movement_speed': 4.0, 'rmb_speed_multiplier': 2.5, 'sprint_multiplier': 2.0, 'look_sensitivity': 0.0030, 'wheel_zoom_factor': 0.88, 'acceleration': 14.0, 'deceleration': 18.0, 'invert_x': False, 'invert_y': False, 'vertical_mode': 'WORLD'},
    'ROBLOX': {'movement_speed': 5.0, 'rmb_speed_multiplier': 3.0, 'sprint_multiplier': 2.0, 'look_sensitivity': 0.0028, 'wheel_zoom_factor': 0.88, 'acceleration': 16.0, 'deceleration': 20.0, 'invert_x': False, 'invert_y': False, 'vertical_mode': 'WORLD'},
    'MINECRAFT': {'movement_speed': 4.5, 'rmb_speed_multiplier': 2.2, 'sprint_multiplier': 1.8, 'look_sensitivity': 0.0032, 'wheel_zoom_factor': 0.90, 'acceleration': 18.0, 'deceleration': 22.0, 'invert_x': False, 'invert_y': False, 'vertical_mode': 'WORLD'},
    'FPS': {'movement_speed': 6.0, 'rmb_speed_multiplier': 1.8, 'sprint_multiplier': 2.5, 'look_sensitivity': 0.0036, 'wheel_zoom_factor': 0.86, 'acceleration': 22.0, 'deceleration': 24.0, 'invert_x': False, 'invert_y': False, 'vertical_mode': 'WORLD'},
    'STEAM': {'movement_speed': 4.5, 'rmb_speed_multiplier': 2.2, 'sprint_multiplier': 1.8, 'look_sensitivity': 0.0024, 'wheel_zoom_factor': 0.90, 'acceleration': 10.0, 'deceleration': 14.0, 'invert_x': False, 'invert_y': False, 'vertical_mode': 'WORLD'},
    'ACCESSIBLE': {'movement_speed': 2.5, 'rmb_speed_multiplier': 1.6, 'sprint_multiplier': 1.4, 'look_sensitivity': 0.0020, 'wheel_zoom_factor': 0.92, 'acceleration': 7.0, 'deceleration': 9.0, 'invert_x': False, 'invert_y': False, 'vertical_mode': 'WORLD'},
}


def _preset_update(self, _context):
    if self.preset == 'CUSTOM':
        return
    values = PRESETS.get(self.preset)
    if values:
        for name, value in values.items():
            setattr(self, name, value)


class GAMEFLOW_Preferences(AddonPreferences):
    bl_idname = ADDON_ID

    enabled: BoolProperty(name="GameFlow Enabled", default=False)
    creator_mode: EnumProperty(
        name="Creator Mode",
        items=[
            ('NAVIGATE', "Explore", "Move around the scene like a game"),
            ('BUILD', "Build", "Create and arrange objects"),
            ('PAINT', "Paint", "Apply simple material looks"),
        ],
        default='NAVIGATE',
    )
    preset: EnumProperty(
        name="Control Feel",
        items=[
            ('GAMEFLOW', "GameFlow", "Balanced default"),
            ('ROBLOX', "Roblox", "Faster Roblox Studio-like movement"),
            ('MINECRAFT', "Minecraft", "Responsive Minecraft-like movement"),
            ('FPS', "First-Person", "Fast FPS-style response"),
            ('STEAM', "Steam Controller", "Smoother controller-friendly tuning"),
            ('ACCESSIBLE', "Accessibility", "Slower and gentler movement"),
            ('CUSTOM', "Custom", "Use custom advanced values"),
        ],
        default='GAMEFLOW',
        update=_preset_update,
    )
    keymap_mode: EnumProperty(
        name="Keyboard Setup",
        items=[
            ('MINIMAL', "GameFlow Recommended", "Recommended beginner controls"),
            ('CONFLICTS', "GameFlow Conflicts Only", "Only remove direct control conflicts"),
            ('NATIVE', "Standard Blender", "Do not change Blender shortcuts"),
        ],
        default='MINIMAL',
    )
    hud_mode: EnumProperty(
        name="On-screen Helper",
        items=[
            ('FULL', "Helpful", "Readable status bar with contextual control hints"),
            ('MINIMAL', "Simple", "Compact mode and status bar"),
            ('OFF', "Off", "Hide the on-screen helper"),
        ],
        default='FULL',
    )
    hud_corner: EnumProperty(
        name="Helper Position",
        items=[
            ('BOTTOM_CENTER', "Bottom Center", "Readable game-style helper above the bottom of the viewport"),
            ('TOP_RIGHT', "Top Right", "Place the helper in the upper-right"),
            ('BOTTOM_RIGHT', "Bottom Right", "Place the helper in the lower-right"),
            ('BOTTOM_LEFT', "Bottom Left", "Place the helper in the lower-left"),
            ('TOP_LEFT', "Top Left", "Place the helper in the upper-left"),
        ],
        default='BOTTOM_CENTER',
    )

    movement_speed: FloatProperty(name="Move Speed", default=4.0, min=0.05, max=100.0)
    rmb_speed_multiplier: FloatProperty(name="Look Boost", default=2.5, min=1.0, max=10.0)
    sprint_multiplier: FloatProperty(name="Sprint Boost", default=2.0, min=1.0, max=10.0)
    look_sensitivity: FloatProperty(name="Look Speed", default=0.0030, min=0.0002, max=0.02, precision=4)
    wheel_zoom_factor: FloatProperty(name="Scroll Zoom", default=0.88, min=0.50, max=0.98)
    acceleration: FloatProperty(name="Acceleration", default=14.0, min=1.0, max=60.0)
    deceleration: FloatProperty(name="Deceleration", default=18.0, min=1.0, max=60.0)
    smooth_movement: BoolProperty(name="Smooth Movement", default=True)
    invert_x: BoolProperty(name="Invert Horizontal Look", default=False)
    invert_y: BoolProperty(name="Invert Vertical Look", default=False)
    invert_zoom: BoolProperty(name="Invert Scroll Zoom", default=False)
    vertical_mode: EnumProperty(name="Q / E Direction", items=[('WORLD', "World Up/Down", "World vertical"), ('VIEW', "View Relative", "View-relative vertical")], default='WORLD')
    double_click_time: FloatProperty(name="Context Double-Click Time", default=0.32, min=0.15, max=0.60)
    edge_wrap_look: BoolProperty(name="Unlimited RMB Look", default=True)
    edge_wrap_margin: IntProperty(name="Look Edge Margin", default=42, min=10, max=200)
    restore_cursor_after_look: BoolProperty(name="Return Cursor After RMB Look", default=True)

    build_grid_step: FloatProperty(name="Build Step", default=1.0, min=0.01, max=100.0, precision=2)
    build_rotation_step: FloatProperty(name="Rotation Step", default=45.0, min=1.0, max=180.0, precision=1)

    auto_start: BoolProperty(name="Start GameFlow with Blender", default=True)
    restart_after_file_load: BoolProperty(name="Reconnect After Opening a Project", default=True)
    restore_controls_on_disable: BoolProperty(name="Restore Blender Controls When Disabled", default=True)

    show_controls: BoolProperty(name="Help Me", default=False)
    show_build: BoolProperty(name="Build Tools", default=True)
    show_controller: BoolProperty(name="Controller Setup", default=False)
    show_advanced: BoolProperty(name="Advanced", default=False)
    show_support: BoolProperty(name="Recovery Tools", default=False)
    show_preset_help: BoolProperty(name="Preset Help", default=False)

    def draw(self, context):
        layout = self.layout
        layout.label(text="GameFlow for Blender", icon='PLAY')
        layout.label(text="From player to creator.")
        layout.separator()
        layout.prop(self, "preset")
        layout.prop(self, "hud_mode")
        if self.hud_mode != 'OFF':
            layout.prop(self, "hud_corner")
        layout.separator()
        layout.label(text="Advanced")
        layout.prop(self, "keymap_mode")
        layout.prop(self, "movement_speed")
        layout.prop(self, "look_sensitivity")
        layout.prop(self, "auto_start")
        layout.prop(self, "restart_after_file_load")
        layout.prop(self, "restore_controls_on_disable")


def get_prefs(context=None):
    context = context or bpy.context
    addon = context.preferences.addons.get(ADDON_ID)
    return addon.preferences if addon else None


classes = (GAMEFLOW_Preferences,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
