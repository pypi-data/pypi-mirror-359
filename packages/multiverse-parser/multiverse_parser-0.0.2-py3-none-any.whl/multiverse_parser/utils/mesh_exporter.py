#!/usr/bin/env python3

import os


clean_up_meshes_script = """
if len(bpy.data.objects) == 0:
    raise ValueError("No object in the scene.")

for selected_object in bpy.data.objects:    
    # Check if the active object is a mesh
    if selected_object.type != 'MESH':
        continue
    
    # Select the object
    bpy.context.view_layer.objects.active = selected_object

    # Switch to Edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    if selected_object.scale[0] * selected_object.scale[1] * selected_object.scale[2] < 0:
        bpy.ops.mesh.flip_normals()

    # Switch back to Object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    if 'TRIANGULATE' not in [modifier.type for modifier in selected_object.modifiers]:
        bpy.ops.object.modifier_add(type='TRIANGULATE')

    for modifier_name in [modifier.name for modifier in selected_object.modifiers]:
        bpy.ops.object.modifier_apply(modifier=modifier_name)
"""


def export_usd(out_usd: str, merge_mesh: bool = False) -> str:
    if os.name == "nt":
        out_usd = out_usd.replace("\\", "\\\\")
    return f"""
import os.path

{clean_up_meshes_script}
if {merge_mesh}:
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    for selected_object in bpy.context.selected_objects:
        if selected_object.type != "MESH":
            selected_object.select_set(False)
    if len(bpy.context.selected_objects) > 1:
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
        bpy.ops.object.join()
out_usd_dir = os.path.dirname('{out_usd}')
os.makedirs(out_usd_dir, exist_ok=True)
bpy.ops.wm.usd_export(filepath='{out_usd}', selected_objects_only=True, overwrite_textures=True, root_prim_path='')
"""


def export_dae(out_dae: str) -> str:
    if os.name == "nt":
        out_dae = out_dae.replace("\\", "\\\\")
    return f"""
import os.path
import re
import shutil

{clean_up_meshes_script}
out_dae_dir = os.path.dirname('{out_dae}')
os.makedirs(name=out_dae_dir, exist_ok=True)
os.makedirs(name=os.path.join(out_dae_dir, "..", "..", "textures"), exist_ok=True)
bpy.ops.wm.collada_export(filepath='{out_dae}', 
                          use_texture_copies=True, 
                          export_global_forward_selection="Y", 
                          export_global_up_selection="Z")

with open('{out_dae}', encoding="utf-8") as file:
    file_contents = file.read()

pattern = r'<init_from>([^<]*\.png)</init_from>'
matches = re.findall(pattern, file_contents)
for match in matches:
    new_value = "../../textures/" + match
    file_contents = file_contents.replace("<init_from>" + match + "</init_from>", f"<init_from>" + new_value + "</init_from>")
    
    texture_abspath = match
    if not os.path.isabs(texture_abspath):
        texture_abspath = os.path.join(out_dae_dir, texture_abspath)
    new_texture_path = new_value
    new_texture_abspath = os.path.join(out_dae_dir, new_texture_path)
    if not os.path.exists(new_texture_abspath):
        shutil.copy(texture_abspath, new_texture_abspath)
    os.remove(texture_abspath)
    
with open('{out_dae}', "w", encoding="utf-8") as output:
    output.write(file_contents)
"""


def export_obj(out_obj: str) -> str:
    if os.name == "nt":
        out_obj = out_obj.replace("\\", "\\\\")
    return f"""
import os.path
import shutil
from PIL import Image

{clean_up_meshes_script}
out_obj_dir = os.path.dirname('{out_obj}')
os.makedirs(name=out_obj_dir, exist_ok=True)
os.makedirs(name=os.path.join(out_obj_dir, "..", "..", "textures"), exist_ok=True)

bpy.ops.wm.obj_export(filepath='{out_obj}', 
                      export_selected_objects=False, 
                      forward_axis="Y", 
                      up_axis="Z", 
                      path_mode="RELATIVE")
out_mtl = '{out_obj}'.replace(".obj", ".mtl")
with open(out_mtl, "r") as file:
    lines = file.readlines()
    
for i, line in enumerate(lines):
    if line.startswith("map_Kd"):
        texture_path = os.path.join(out_obj_dir, line.split("map_Kd")[1].strip())
        texture_file_name = os.path.basename(texture_path)
        new_texture_path = os.path.join("..", "..", "textures", texture_file_name)
        new_texture_abspath = os.path.join(out_obj_dir, new_texture_path)
        
        if not os.path.exists(new_texture_abspath):
            print(new_texture_abspath)
            shutil.copy(texture_path, new_texture_abspath)
        lines[i] = "map_Kd " + new_texture_path + "\\n"
        img = Image.open(texture_path)
        png_file_name = texture_file_name.replace(".jpg", ".png").replace(".JPG", ".png")
        img.save(os.path.join(out_obj_dir, new_texture_path).replace(".jpg", ".png").replace(".JPG", ".png"), "PNG")

with open(out_mtl, "w") as file:
    file.writelines(lines)
"""


def export_stl(out_stl: str) -> str:
    if os.name == "nt":
        out_stl = out_stl.replace("\\", "\\\\")
    return f"""
import os.path

{clean_up_meshes_script}
out_stl_dir = os.path.dirname('{out_stl}')
os.makedirs(name=out_stl_dir, exist_ok=True)
selected_object = bpy.context.object
if len([vertex for obj in bpy.data.objects for vertex in obj.data.vertices]) > 1000:
    selected_object.modifiers.new("Weld", "WELD")
    bpy.ops.object.modifier_apply(modifier="Weld")
bpy.ops.wm.stl_export(filepath='{out_stl}', 
                      export_selected_objects=False, 
                      forward_axis="Y", 
                      up_axis="Z")
"""


def export_fbx(out_fbx: str) -> str:
    if os.name == "nt":
        out_fbx = out_fbx.replace("\\", "\\\\")
    return f"""
{clean_up_meshes_script}
bpy.ops.export_scene.fbx(filepath='{out_fbx}', 
                         use_selection=False, 
                         axis_forward="Y", 
                         axis_up="Z",
                         mesh_smooth_type="FACE",
                         use_triangles=True,
                         object_types={{"MESH"}})
"""
