import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty
from bpy.types import AddonPreferences

ADDON_ID = __package__
ADDON_LEAF_ID = (__package__ or "gameflow_blender").split('.')[-1]

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

    enabled: BoolProperty(name="Full GameFlow Controls Enabled", default=False)
    safe_mode: BoolProperty(name="Safe Mode", description="Use Creator tools while leaving Blender's normal key bindings active", default=False)
    creator_mode: EnumProperty(name="Creator Mode", items=[('NAVIGATE', "Explore", "Game-style viewport navigation"), ('BUILD', "Build", "Create, place, duplicate, snap, rotate, and arrange objects"), ('PAINT', "Paint", "Fast beginner-friendly material presets")], default='NAVIGATE')
    preset: EnumProperty(name="Control Feel", items=[('GAMEFLOW', "GameFlow", "Balanced keyboard/mouse default for most users"), ('ROBLOX', "Roblox", "Faster movement and camera feel inspired by Roblox Studio navigation"), ('MINECRAFT', "Minecraft", "Responsive keyboard/mouse feel inspired by Minecraft movement"), ('FPS', "First-Person", "Fast movement and quick response for experienced FPS players"), ('STEAM', "Steam Controller", "Smoother tuning intended for a controller mapped through Steam Input; this preset does not enable Steam Input by itself"), ('ACCESSIBLE', "Accessibility", "Slower, gentler movement and camera response"), ('CUSTOM', "Custom", "Use the advanced values below")], default='GAMEFLOW', update=_preset_update)
    keymap_mode: EnumProperty(name="Keyboard Simplification", items=[('MINIMAL', "GameFlow Minimal", "Recommended beginner keymap"), ('CONFLICTS', "Conflicts Only", "Only disable direct GameFlow conflicts"), ('NATIVE', "Native Blender", "Do not change Blender's user keymap")], default='MINIMAL')
    hud_mode: EnumProperty(name="Dark Viewport HUD", items=[('FULL', "Full", "Dark GameFlow HUD with mode, status, selection, build data, and control hints"), ('MINIMAL', "Minimal", "Compact dark HUD with mode, status, and selected object"), ('OFF', "Off", "Hide the GameFlow viewport HUD")], default='FULL')

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
    vertical_mode: EnumProperty(name="Q / E Direction", items=[('WORLD', "World Up/Down", "World vertical"), ('VIEW', "View Relative", "View-relative vertical")], default='WORLD')
    double_click_time: FloatProperty(name="Context Double-Click Time", default=0.32, min=0.15, max=0.60)
    edge_wrap_look: BoolProperty(name="Unlimited RMB Look", description="Recenter pointer near viewport edges", default=True)
    edge_wrap_margin: IntProperty(name="Look Edge Margin", default=42, min=10, max=200)
    restore_cursor_after_look: BoolProperty(name="Return Cursor After RMB Look", default=True)

    build_grid_step: FloatProperty(name="Build Step", description="Distance used by GameFlow nudge, duplicate, and placement tools", default=1.0, min=0.01, max=100.0, precision=2)
    build_rotation_step: FloatProperty(name="Rotation Step", description="Degrees used by GameFlow step rotation and placement rotation", default=45.0, min=1.0, max=180.0, precision=1)
    placement_grid_snap: BoolProperty(name="Placement Grid Snap", description="Snap ghost placement to the GameFlow Build Step", default=True)
    placement_continuous: BoolProperty(name="Continuous Placement", description="Keep placing copies until Escape or Right Click", default=True)

    auto_start: BoolProperty(name="Auto-start When Blender Opens", default=True)
    restart_after_file_load: BoolProperty(name="Reconnect After Opening/New Project", default=True)
    restore_controls_on_disable: BoolProperty(name="Restore Saved Controls When Add-on Is Disabled", default=True)

    show_controls: BoolProperty(name="Controls", default=False)
    show_build: BoolProperty(name="Build Tools", default=True)
    show_controller: BoolProperty(name="Controller Setup", default=False)
    show_advanced: BoolProperty(name="Advanced Settings", default=False)
    show_support: BoolProperty(name="Support & Recovery", default=False)
    show_preset_help: BoolProperty(name="What do these presets mean?", default=False)
    show_health: BoolProperty(name="Health & Safety", default=True)

    def draw(self, context):
        layout = self.layout
        layout.label(text="GameFlow for Blender", icon='PLAY')
        layout.label(text="From player to creator.")
        layout.separator()
        layout.prop(self, "creator_mode")
        layout.prop(self, "hud_mode")
        layout.prop(self, "safe_mode")
        col = layout.column(align=True)
        col.prop(self, "preset")
        col.prop(self, "movement_speed")
        col.prop(self, "look_sensitivity")
        build = layout.box()
        build.label(text="Creator Build")
        build.prop(self, "build_grid_step")
        build.prop(self, "build_rotation_step")
        build.prop(self, "placement_grid_snap")
        build.prop(self, "placement_continuous")
        behavior = layout.box()
        behavior.label(text="Behavior")
        behavior.prop(self, "keymap_mode")
        behavior.prop(self, "auto_start")
        behavior.prop(self, "restart_after_file_load")
        behavior.prop(self, "restore_controls_on_disable")
        advanced = layout.box()
        advanced.label(text="Advanced")
        advanced.prop(self, "rmb_speed_multiplier")
        advanced.prop(self, "sprint_multiplier")
        advanced.prop(self, "smooth_movement")
        if self.smooth_movement:
            advanced.prop(self, "acceleration")
            advanced.prop(self, "deceleration")
        advanced.prop(self, "wheel_zoom_factor")
        advanced.prop(self, "invert_x")
        advanced.prop(self, "invert_y")
        advanced.prop(self, "invert_zoom")
        advanced.prop(self, "vertical_mode")
        advanced.prop(self, "double_click_time")
        advanced.prop(self, "edge_wrap_look")
        if self.edge_wrap_look:
            advanced.prop(self, "edge_wrap_margin")
            advanced.prop(self, "restore_cursor_after_look")


def get_prefs(context=None):
    context = context or bpy.context
    preferences = getattr(context, 'preferences', None)
    addons = getattr(preferences, 'addons', None)
    if addons is None:
        return None

    # Normal legacy and extension package IDs first.
    candidates = []
    for key in (ADDON_ID, ADDON_LEAF_ID):
        if key and key not in candidates:
            candidates.append(key)
    try:
        package = str(__package__ or '')
        if package:
            candidates.extend([
                f"bl_ext.user_default.{ADDON_LEAF_ID}",
                f"bl_ext.blender_org.{ADDON_LEAF_ID}",
            ])
    except Exception:
        pass

    for key in candidates:
        try:
            addon = addons.get(key)
            if addon and getattr(addon, 'preferences', None) is not None:
                return addon.preferences
        except Exception:
            continue

    # Blender 5.x may namespace legacy installs differently. Resolve by key
    # suffix and, as a final fallback, by the actual preferences RNA type.
    try:
        for addon in addons:
            module = str(getattr(addon, 'module', '') or '')
            prefs = getattr(addon, 'preferences', None)
            if prefs is None:
                continue
            if module == ADDON_ID or module == ADDON_LEAF_ID or module.endswith('.' + ADDON_LEAF_ID):
                return prefs
            pref_type = type(prefs)
            if pref_type.__name__ == 'GAMEFLOW_Preferences' or 'gameflow' in str(getattr(pref_type, '__module__', '')).lower():
                return prefs
    except Exception:
        pass

    return None


classes = (GAMEFLOW_Preferences,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except (RuntimeError, ValueError, ReferenceError):
            pass
