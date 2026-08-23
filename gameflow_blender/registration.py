import bpy
from bpy.types import AddonPreferences


def _matching_stale_preferences(current_cls, addon_id):
    matches = []
    try:
        subclasses = list(AddonPreferences.__subclasses__())
    except Exception:
        subclasses = []

    for candidate in subclasses:
        if candidate is current_cls:
            continue
        try:
            same_name = candidate.__name__ == current_cls.__name__
            same_id = getattr(candidate, 'bl_idname', None) == addon_id
            same_module = str(getattr(candidate, '__module__', '')).endswith('.preferences') and 'gameflow' in str(getattr(candidate, '__module__', '')).lower()
            if same_name or same_id or same_module:
                matches.append(candidate)
        except Exception:
            continue
    return matches


def cleanup_stale_preferences(current_cls, addon_id):
    """Remove stale AddonPreferences classes left alive by Blender reloads.

    Blender 5.x can retain a previously registered Python/RNA subclass even
    when it is no longer exposed as bpy.types.<ClassName>. Scanning
    AddonPreferences.__subclasses__() reaches those stale class objects.
    """
    removed = 0
    for candidate in reversed(_matching_stale_preferences(current_cls, addon_id)):
        try:
            bpy.utils.unregister_class(candidate)
            removed += 1
        except (RuntimeError, ValueError, ReferenceError):
            pass
    return removed


def register_preferences(preferences_module):
    classes = tuple(getattr(preferences_module, 'classes', ()))
    if not classes:
        return

    current_cls = classes[0]
    addon_id = getattr(preferences_module, 'ADDON_ID', current_cls.__module__.split('.')[0])
    cleanup_stale_preferences(current_cls, addon_id)

    try:
        preferences_module.register()
        return
    except RuntimeError as exc:
        # Blender 5.0.x can still race an old RNA subclass during a legacy
        # add-on reinstall. Clean again and retry exactly once.
        if 'already registered as a subclass' not in str(exc):
            raise

    cleanup_stale_preferences(current_cls, addon_id)
    preferences_module.register()
