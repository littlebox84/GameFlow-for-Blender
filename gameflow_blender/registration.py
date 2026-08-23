import bpy
from bpy.types import AddonPreferences


def is_registered_class(cls):
    """Return True when Blender has already registered this exact class object."""
    try:
        return getattr(cls, 'bl_rna', None) is not None
    except Exception:
        return False


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
            module_name = str(getattr(candidate, '__module__', ''))
            same_module = module_name.endswith('.preferences') and 'gameflow' in module_name.lower()
            if same_name or same_id or same_module:
                matches.append(candidate)
        except Exception:
            continue
    return matches


def cleanup_stale_preferences(current_cls, addon_id):
    """Remove stale AddonPreferences classes left alive by Blender reloads."""
    removed = 0
    for candidate in reversed(_matching_stale_preferences(current_cls, addon_id)):
        try:
            bpy.utils.unregister_class(candidate)
            removed += 1
        except (RuntimeError, ValueError, ReferenceError):
            pass
    return removed


def register_preferences(preferences_module):
    """Register GameFlow preferences safely across Blender install/reload cycles.

    Blender's legacy Install from Disk flow may invoke register() again while
    the exact same Python class object is already registered. In that case the
    correct behavior is to treat registration as complete rather than calling
    bpy.utils.register_class() a second time.
    """
    classes = tuple(getattr(preferences_module, 'classes', ()))
    if not classes:
        return

    current_cls = classes[0]
    addon_id = getattr(preferences_module, 'ADDON_ID', current_cls.__module__.split('.')[0])

    # Same module/class already registered: this is an idempotent second call.
    if is_registered_class(current_cls):
        return

    cleanup_stale_preferences(current_cls, addon_id)

    # Cleanup may expose/leave the current class as already registered.
    if is_registered_class(current_cls):
        return

    try:
        preferences_module.register()
        return
    except RuntimeError as exc:
        if 'already registered as a subclass' not in str(exc):
            raise

    # If Blender registered this exact class during the attempted operation,
    # there is nothing left to do.
    if is_registered_class(current_cls):
        return

    # Otherwise one stale RNA generation is still alive. Remove it and retry
    # exactly once so a real unrelated error is never hidden in a loop.
    cleanup_stale_preferences(current_cls, addon_id)
    if is_registered_class(current_cls):
        return
    preferences_module.register()
