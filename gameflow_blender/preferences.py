import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty
from bpy.types import AddonPreferences

ADDON_ID = __package__

PRESETS = {
    'GAMEFLOW': {
        'movement_speed': 4.0,
        'rmb_speed_multiplier': 2.5,
        'sprint_multiplier': 2.0,
        'look_sensitivity': 0.0030,
        'wheel_zoom_factor': 0.88,
        'acceleration': 14.0,
        'deceleration': 18.0,
        'invert_x': False,
        'invert_y': False,
        'vertical_mode': 'WORLD',
    },
    'ROBLOX': {
        'movement_speed': 5.0,
        'rmb_speed_multiplier': 3.0,
        'sprint_multiplier': 2.0,
        'look_sensitivity': 0.0028,
        'wheel_zoom_factor': 0.88,
        'acceleration': 16.0,
        'deceleration': 20.0,
        'invert_x': False,
        'invert_y': False,
        'vertical_mode': 'WORLD',
    },
    'MINECRAFT': {
        'movement_speed': 4.5,
        'rmb_speed_multiplier': 2.2,
        'sprint_multiplier': 1.8,
        'look_sensitivity': 0.0032,
        'wheel_zoom_factor': 0.90,
        'acceleration': 18.0,
        'deceleration': 22.0,
        'invert_x': False,
        'invert_y': False,
        'vertical_mode': 'WORLD',
    },
    'FPS': {
        'movement_speed': 6.0,
        'rmb_speed_multiplier': 1.8,
        'sprint_multiplier': 2.5,
        'look_sensitivity': 0.0036,
        'wheel_zoom_factor': 0.86,
        'acceleration': 22.0,
        'deceleration': 24.0,
        'invert_x': False,
        'invert_y': False,
        'vertical_mode': 'WORLD',
    },
    'STEAM': {
        'movement_speed': 4.5,
        'rmb_speed_multiplier': 2.2,
        'sprint_multiplier': 1.8,
        'look_sensitivity': 0.0024,
        'wheel_zoom_factor': 0.90,
        'acceleration': 10.0,
        'deceleration': 14.0,
        'invert_x': False,
        'invert_y': False,
        'vertical_mode': 'WORLD',
    },
    'ACCESSIBLE': {
        'movement_speed': 2.5,
        'rmb_speed_multiplier': 1.6,
        'sprint_multiplier': 1.4,
        'look_sensitivity': 0.0020,
        'wheel_zoom_factor': 0.92,
        'acceleration': 7.0,
        'deceleration': 9.0,
        'invert_x': False,
        'invert_y': False,
        'vertical_mode': 'WORLD',
    },
}


def _preset_update(self, _context):
    if self.preset == 'CUSTOM':
        return
    values = PRESETS.get(self.preset)
    if not values:
        return
    for name, value in values.items():
        setattr(self, name, value)


class GAMEFLOW_Preferences(AddonPreferences):
    bl_idname = ADDON_ID

    enabled: BoolProperty(
        name="Full GameFlow Controls Enabled",
        default=False,
    )
    preset: EnumProperty(
        name="Control Feel",
        items=[
            ('GAMEFLOW', "GameFlow", "Balanced default designed to feel familiar immediately"),
            ('ROBLOX', "Roblox", "Faster game-style movement"),
            ('MINECRAFT', "Minecraft", "Responsive movement with a familiar mouse feel"),
            ('FPS', "First-Person", "Fast movement and quick response"),
            ('STEAM', "Steam Controller", "Smoother values for Steam Input controller use"),
            ('ACCESSIBLE', "Accessibility", "Slower, gentler movement and camera response"),
            ('CUSTOM', "Custom", "Use the advanced values below"),
        ],
        default='GAMEFLOW',
        update=_preset_update,
    )
    keymap_mode: EnumProperty(
        name="Keyboard Simplification",
        items=[
            ('MINIMAL', "GameFlow Minimal", "Recommended: remove most single-key 3D View clutter while keeping menus and core modeling actions"),
            ('CONFLICTS', "Conflicts Only", "Only disable shortcuts that directly conflict with GameFlow movement/navigation"),
            ('NATIVE', "Native Blender", "Do not change Blender's user keymap"),
        ],
        default='MINIMAL',
    )

    movement_speed: FloatProperty(name="Walk Speed", default=4.0, min=0.05, max=100.0)
    rmb_speed_multiplier: FloatProperty(name="RMB Fast Multiplier", default=2.5, min=1.0, max=10.0)
    sprint_multiplier: FloatProperty(name="Shift Sprint Multiplier", default=2.0, min=1.0, max=10.0)
    look_sensitivity: FloatProperty(name="Look Sensitivity", default=0.0030, min=0.0002, max=0.02, precision=4)
    wheel_zoom_factor: FloatProperty(name="Scroll Zoom Strength", default=0.88, min=0.50, max=0.98)
    acceleration: FloatProperty(name="Acceleration", default=14.0, min=1.0, max=60.0)
    deceleration: FloatProperty(name="Deceleration", default=18.0, min=1.0, max=60.0)
    smooth_movement: BoolProperty(name="Smooth Movement", default=True)
    invert_x: BoolProperty(name="Invert Horizontal Look", default=False)
    invert_y: BoolProperty(name="Invert Vertical Look", default=False)
    invert_zoom: BoolProperty(name="Invert Scroll Zoom", default=False)
    vertical_mode: EnumProperty(
        name="Q / E Direction",
        items=[
            ('WORLD', "World Up/Down", "Q/E always move vertically in the scene"),
            ('VIEW', "View Relative", "Q/E move relative to the current view"),
        ],
        default='WORLD',
    )
    double_click_time: FloatProperty(name="Context Double-Click Time", default=0.32, min=0.15, max=0.60)
    auto_start: BoolProperty(name="Auto-start When Blender Opens", default=True)
    restart_after_file_load: BoolProperty(name="Reconnect After Opening/New Project", default=True)
    restore_controls_on_disable: BoolProperty(name="Restore Saved Controls When Add-on Is Disabled", default=True)
    show_advanced: BoolProperty(name="Advanced Settings", default=False)
    show_controller: BoolProperty(name="Controller Setup", default=False)

    def draw(self, context):
        layout = self.layout
        layout.label(text="GameFlow for Blender")
        layout.label(text="From player to creator.")
        layout.separator()
        layout.prop(self, "preset")
        layout.prop(self, "movement_speed")
        layout.prop(self, "look_sensitivity")
        layout.prop(self, "keymap_mode")
        layout.prop(self, "auto_start")
        layout.prop(self, "restart_after_file_load")
        layout.separator()
        layout.label(text="Advanced")
        layout.prop(self, "rmb_speed_multiplier")
        layout.prop(self, "sprint_multiplier")
        layout.prop(self, "smooth_movement")
        layout.prop(self, "acceleration")
        layout.prop(self, "deceleration")
        layout.prop(self, "wheel_zoom_factor")
        layout.prop(self, "invert_x")
        layout.prop(self, "invert_y")
        layout.prop(self, "invert_zoom")
        layout.prop(self, "vertical_mode")
        layout.prop(self, "double_click_time")
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
