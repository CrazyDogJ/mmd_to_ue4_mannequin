bl_info = {
    "name": "CrazyDog's tools",
    "author": "CrazyDog",
    "version": (1, 0),
    "blender": (4, 0, 2),
    "location": "View3D > Tool Shelf > Cd Tools",
    "description": "Every tools you need for editing MMD models or UE4 Mannequin",
    "warning": "",
    "wiki_url": "",
    "category": "3D View",
}

# New Armature button
from .templates import add_new_armature_operation

from .ue import ue4_operations

# Tools Panel
from .tools import other_tools_panel
#bone edit
from .tools import bone_rotation_panel
#rename
from .tools import bones_mapping_panel
#import batch shape key panel tool
from .tools import batch_shape_key_panel
#import vertex group sorting panel tool
from .tools import vertex_group_sorting_panel
# Tools Panel

fileList = {
    bone_rotation_panel,
    bones_mapping_panel,
    batch_shape_key_panel,
    vertex_group_sorting_panel,
    other_tools_panel,
    add_new_armature_operation,
    ue4_operations
}

def register():
    for fileSingle in fileList:
        fileSingle.register()

def unregister():
    for fileSingle in fileList:
        fileSingle.unregister()

if __name__ == "__main__":
    register()