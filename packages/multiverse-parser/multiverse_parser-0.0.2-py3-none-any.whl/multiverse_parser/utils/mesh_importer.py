#!/usr/bin/env python3

from typing import List
import numpy

clean_up_meshes_script = """
for armature in bpy.data.armatures:
    bpy.data.armatures.remove(armature)
for mesh in bpy.data.meshes:
    bpy.data.meshes.remove(mesh)
for from_obj in bpy.data.objects:
    bpy.data.objects.remove(from_obj)
for material in bpy.data.materials:
    bpy.data.materials.remove(material)
for camera in bpy.data.cameras:
    bpy.data.cameras.remove(camera)
for light in bpy.data.lights:
    bpy.data.lights.remove(light)
for image in bpy.data.images:
    bpy.data.images.remove(image)
"""


def import_usd(in_usds: List[str],
               mesh_scale: numpy.ndarray = numpy.array([1.0, 1.0, 1.0]),
               clean_up: bool = True) -> str:
    return (f"{clean_up_meshes_script}" if clean_up else "") + f"""
for in_usd in {in_usds}:
    bpy.ops.wm.usd_import(filepath=in_usd, scale=1.0)
    for obj in bpy.data.objects:
        obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True, isolate_users=True)
    bpy.context.view_layer.objects.active.scale = {mesh_scale.tolist()}
"""


def import_dae(in_daes: List[str],
               mesh_scale: numpy.ndarray = numpy.array([1.0, 1.0, 1.0]),
               clean_up: bool = True) -> str:
    return (f"{clean_up_meshes_script}" if clean_up else "") + f"""
import math
for in_dae in {in_daes}:
    bpy.ops.wm.collada_import(filepath=in_dae)
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, isolate_users=True)
    bpy.context.view_layer.objects.active.scale = {mesh_scale.tolist()}
    
# Set alpha to 1
for mat in bpy.data.materials:
    if hasattr(mat.node_tree, "nodes"):
        mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 1.0
"""


def import_obj(in_objs: List[str],
               mesh_scale: numpy.ndarray = numpy.array([1.0, 1.0, 1.0]),
               clean_up: bool = True) -> str:
    return (f"{clean_up_meshes_script}" if clean_up else "") + f"""
for in_obj in {in_objs}:
    bpy.ops.wm.obj_import(filepath=in_obj, up_axis='Z', forward_axis='Y')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, isolate_users=True)
    bpy.context.view_layer.objects.active.scale = {mesh_scale.tolist()}
"""


def import_stl(in_stls: List[str],
               mesh_scale: numpy.ndarray = numpy.array([1.0, 1.0, 1.0]),
               clean_up: bool = True) -> str:
    return (f"{clean_up_meshes_script}" if clean_up else "") + f"""
import re
for in_stl in {in_stls}:
    bpy.ops.wm.stl_import(filepath=in_stl, up_axis='Z', forward_axis='Y')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, isolate_users=True)
    bpy.context.view_layer.objects.active.scale = {mesh_scale.tolist()}
    mesh = bpy.context.view_layer.objects.active.data
    mesh.name = re.sub(r'\.\d+$', '', mesh.name)
"""
