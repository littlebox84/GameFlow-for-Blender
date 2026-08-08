# GameFlow Minimal Blender Keymap — standalone fallback
# Optional fallback: import through Edit > Preferences > Keymap > Import.
#
# This preset intentionally keeps the keyboard light:
# - Mouse interaction and menus remain available.
# - F3 opens Blender's command search for anything not assigned.
# - The GameFlow add-on supplies WASD/QE/RMB game navigation.

keyconfig_version = (5, 0, 119)

keyconfig_data = [
    ("Window", {"space_type": 'EMPTY', "region_type": 'WINDOW'}, {"items": [
        ("wm.search_menu", {"type": 'F3', "value": 'PRESS'}, None),
        ("wm.save_mainfile", {"type": 'S', "value": 'PRESS', "ctrl": True}, None),
        ("ed.undo", {"type": 'Z', "value": 'PRESS', "ctrl": True}, None),
        ("ed.redo", {"type": 'Z', "value": 'PRESS', "ctrl": True, "shift": True}, None),
    ]}),
    ("3D View", {"space_type": 'VIEW_3D', "region_type": 'WINDOW'}, {"items": [
        ("view3d.rotate", {"type": 'MIDDLEMOUSE', "value": 'PRESS'}, None),
        ("view3d.move", {"type": 'MIDDLEMOUSE', "value": 'PRESS', "shift": True}, None),
        ("view3d.zoom", {"type": 'WHEELINMOUSE', "value": 'PRESS'}, {"properties": [("delta", 1)]}),
        ("view3d.zoom", {"type": 'WHEELOUTMOUSE', "value": 'PRESS'}, {"properties": [("delta", -1)]}),
        ("view3d.select", {"type": 'LEFTMOUSE', "value": 'CLICK'}, {"properties": [("deselect_all", True)]}),
        ("view3d.select", {"type": 'LEFTMOUSE', "value": 'CLICK', "shift": True}, {"properties": [("toggle", True)]}),
        ("wm.call_menu", {"type": 'RIGHTMOUSE', "value": 'DOUBLE_CLICK'}, {"properties": [("name", 'VIEW3D_MT_object_context_menu')]}),
        ("view3d.view_selected", {"type": 'F', "value": 'PRESS'}, None),
        ("wm.tool_set_by_id", {"type": 'ONE', "value": 'PRESS', "ctrl": True}, {"properties": [("name", 'builtin.select_box')]}),
        ("wm.tool_set_by_id", {"type": 'TWO', "value": 'PRESS', "ctrl": True}, {"properties": [("name", 'builtin.move')]}),
        ("wm.tool_set_by_id", {"type": 'THREE', "value": 'PRESS', "ctrl": True}, {"properties": [("name", 'builtin.scale')]}),
        ("wm.tool_set_by_id", {"type": 'FOUR', "value": 'PRESS', "ctrl": True}, {"properties": [("name", 'builtin.rotate')]}),
    ]}),
    ("Object Mode", {"space_type": 'EMPTY', "region_type": 'WINDOW'}, {"items": [
        ("object.mode_set", {"type": 'TAB', "value": 'PRESS'}, {"properties": [("mode", 'EDIT')]}),
        ("transform.translate", {"type": 'G', "value": 'PRESS'}, None),
        ("transform.rotate", {"type": 'R', "value": 'PRESS'}, None),
        ("transform.resize", {"type": 'S', "value": 'PRESS'}, None),
        ("object.duplicate_move", {"type": 'D', "value": 'PRESS', "ctrl": True}, None),
        ("object.delete", {"type": 'X', "value": 'PRESS'}, None),
        ("object.delete", {"type": 'DEL', "value": 'PRESS'}, None),
    ]}),
]

if __name__ == "__main__":
    from bpy.app import version as blender_version
    from bl_keymap_utils.io import keyconfig_import_from_data
    import os
    keywords = {}
    if blender_version >= (2, 92, 0):
        keywords["keyconfig_version"] = keyconfig_version
    keyconfig_import_from_data(os.path.splitext(os.path.basename(__file__))[0], keyconfig_data, **keywords)
