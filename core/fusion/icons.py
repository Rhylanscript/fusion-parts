import os

# core/ sits one level below the add in folder, so go up three levels from this file
_ADDIN_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def icon_folder(name):
    """Absolute path of `resources/<name>`, the folder holding 16x16.png & co."""
    return os.path.join(_ADDIN_ROOT, "resources", name)
