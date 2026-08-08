import bpy
import json
from pathlib import Path

from .preferences import get_prefs

addon_keymaps = []

TARGET_KEYMAP_NAMES = {
    "3D View", "Object Mode", "Mesh", "Curve", "Armature", "Pose",
    "Sculpt", "Vertex Paint", "Weight Paint", "Image Paint", "Grease Pencil",
}

MINIMAL_ALLOWED_UNMODIFIED = {'G', 'R', 'S', 'X', 'DEL', 'TAB', 'B'}
MINIMAL_SIMPLE_TYPES = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ") | {
    'ZERO','ONE','TWO','THREE','FOUR','FIVE','SIX','SEVEN','EIGHT','NINE',
    'RIGHTMOUSE','MIDDLEMOUSE','WHEELINMOUSE','WHEELOUTMOUSE',
}


def backup_path():
    return Path(bpy.utils.user_resource('CONFIG')) / "gameflow_keymap_backup.json"


def _event_dict(kmi):
    return {
        "type": kmi.type, "value": kmi.value,
        "shift": bool(kmi.shift), "ctrl": bool(kmi.ctrl),
        "alt": bool(kmi.alt), "oskey": bool(kmi.oskey),
        "key_modifier": kmi.key_modifier,
    }


def _record_for(km, kmi, ordinal):
    return {
        "keymap": km.name, "space_type": km.space_type,
        "region_type": km.region_type, "ordinal": ordinal,
        "idname": kmi.idname, "event": _event_dict(kmi),
        "active": bool(kmi.active),
    }


def _matches_record(kmi, record):
    e = record["event"]
    return (
        kmi.idname == record["idname"] and kmi.type == e["type"]
        and kmi.value == e["value"] and bool(kmi.shift) == e["shift"]
        and bool(kmi.ctrl) == e["ctrl"] and bool(kmi.alt) == e["alt"]
        and bool(kmi.oskey) == e["oskey"]
        and kmi.key_modifier == e.get("key_modifier", 'NONE')
    )


def _target_keymaps(kc):
    for km in kc.keymaps:
        if km.name in TARGET_KEYMAP_NAMES or km.space_type == 'VIEW_3D':
            yield km


def ensure_backup():
    path = backup_path()
    if path.exists():
        return path
    kc = bpy.context.window_manager.keyconfigs.user
    if kc is None:
        raise RuntimeError("Blender's user key configuration is unavailable")
    records = []
    for km in _target_keymaps(kc):
        for ordinal, kmi in enumerate(km.keymap_items):
            records.append(_record_for(km, kmi, ordinal))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2), encoding='utf-8')
    return path


def restore_saved_controls(delete_backup=False):
    path = backup_path()
    if not path.exists():
        return 0
    kc = bpy.context.window_manager.keyconfigs.user
    if kc is None:
        raise RuntimeError("Blender's user key configuration is unavailable")
    records = json.loads(path.read_text(encoding='utf-8'))
    restored = 0
    for record in records:
        km = kc.keymaps.get(record["keymap"])
        if km is None:
            continue
        candidate = None
        ordinal = record.get("ordinal", -1)
        if 0 <= ordinal < len(km.keymap_items):
            maybe = km.keymap_items[ordinal]
            if _matches_record(maybe, record):
                candidate = maybe
        if candidate is None:
            for maybe in km.keymap_items:
                if _matches_record(maybe, record):
                    candidate = maybe
                    break
        if candidate is not None:
            candidate.active = bool(record["active"])
            restored += 1
    if delete_backup:
        path.unlink(missing_ok=True)
    return restored


def _has_modifier(kmi):
    return bool(kmi.shift or kmi.ctrl or kmi.alt or kmi.oskey)


def _should_disable(kmi, mode):
    if not kmi.active or mode == 'NATIVE':
        return False
    if kmi.type in {'RIGHTMOUSE','WHEELINMOUSE','WHEELOUTMOUSE'}:
        return True
    if mode == 'CONFLICTS':
        return kmi.type in {'W','A','S','D','Q','E'} and not _has_modifier(kmi)
    if mode == 'MINIMAL':
        if kmi.type in {'W','A','S','D','Q','E'} and not _has_modifier(kmi):
            return True
        if kmi.type in MINIMAL_SIMPLE_TYPES and not _has_modifier(kmi):
            return kmi.type not in MINIMAL_ALLOWED_UNMODIFIED
        if kmi.ctrl and not kmi.shift and not kmi.alt and kmi.type in {'ONE','TWO','THREE','FOUR'}:
            return True
    return False


def apply_gameflow_keymap(mode=None):
    prefs = get_prefs()
    mode = mode or (prefs.keymap_mode if prefs else 'MINIMAL')
    ensure_backup()
    restore_saved_controls(delete_backup=False)
    if mode == 'NATIVE':
        return 0
    kc = bpy.context.window_manager.keyconfigs.user
    if kc is None:
        raise RuntimeError("Blender's user key configuration is unavailable")
    changed = 0
    for km in _target_keymaps(kc):
        for kmi in km.keymap_items:
            if _should_disable(kmi, mode):
                kmi.active = False
                changed += 1
    return changed


def restore_factory_keymap():
    try:
        bpy.ops.preferences.keymap_restore(all=True)
        backup_path().unlink(missing_ok=True)
        return True
    except Exception:
        return False


def _add_tool(km, key, tool_name):
    kmi = km.keymap_items.new("wm.tool_set_by_id", key, 'PRESS', ctrl=True)
    kmi.properties.name = tool_name
    addon_keymaps.append((km, kmi))


def register_addon_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc is None:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D', region_type='WINDOW')
    for op, key, value, kwargs in [
        ("wm.gameflow_toggle_navigation", 'F8', 'PRESS', {}),
        ("view3d.rotate", 'MIDDLEMOUSE', 'PRESS', {}),
        ("view3d.move", 'MIDDLEMOUSE', 'PRESS', {'shift': True}),
    ]:
        kmi = km.keymap_items.new(op, key, value, **kwargs)
        addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new("view3d.zoom", 'WHEELINMOUSE', 'PRESS'); kmi.properties.delta = 1; addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new("view3d.zoom", 'WHEELOUTMOUSE', 'PRESS'); kmi.properties.delta = -1; addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new("view3d.view_selected", 'F', 'PRESS'); addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new("wm.call_menu", 'RIGHTMOUSE', 'DOUBLE_CLICK'); kmi.properties.name = 'VIEW3D_MT_object_context_menu'; addon_keymaps.append((km, kmi))
    _add_tool(km, 'ONE', 'builtin.select_box')
    _add_tool(km, 'TWO', 'builtin.move')
    _add_tool(km, 'THREE', 'builtin.scale')
    _add_tool(km, 'FOUR', 'builtin.rotate')


def unregister_addon_keymaps():
    for km, kmi in reversed(addon_keymaps):
        try:
            km.keymap_items.remove(kmi)
        except (ReferenceError, RuntimeError):
            pass
    addon_keymaps.clear()


def save_preferences():
    try:
        bpy.ops.wm.save_userpref()
    except Exception:
        pass
