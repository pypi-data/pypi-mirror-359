#!/usr/bin/env python3

from __future__ import annotations

from enum import Enum
from typing import Optional, Dict, List

import numpy

from multiverse_parser import logging
from .geom_builder import GeomBuilder, GeomProperty, GeomInertial
from .points_builder import PointsBuilder, PointProperty
from .joint_builder import JointBuilder, JointProperty
from ..utils import get_transform, xform_cache, modify_name, diagonalize_inertia, shift_inertia_tensor

from pxr import Usd, UsdGeom, Sdf, Gf, UsdPhysics


class InertiaSource(Enum):
    FROM_SRC = 0
    FROM_VISUAL_MESH = 1
    FROM_COLLISION_MESH = 2


class BodyBuilder:
    stage: Usd.Stage
    xform: UsdGeom.Xform
    joint_builders: List[JointBuilder]
    geom_builders: List[GeomBuilder]
    point_builders: List[PointsBuilder]
    child_body_builders: List[BodyBuilder]

    def __init__(self,
                 stage: Usd.Stage, name: str,
                 parent_xform: Optional[UsdGeom.Xform] = None) -> None:
        path = parent_xform.GetPath().AppendPath(name) if parent_xform is not None else Sdf.Path("/").AppendPath(name)
        self._xform = UsdGeom.Xform.Define(stage, path)
        self._joint_builders: Dict[str, JointBuilder] = {}
        self._geom_builders: Dict[str, GeomBuilder] = {}
        self._point_builders: Dict[str, PointsBuilder] = {}
        self._child_body_builders: Dict[str, BodyBuilder] = {}

    def set_transform(
            self,
            pos: numpy.ndarray = numpy.array([0.0, 0.0, 0.0]),
            quat: numpy.ndarray = numpy.array([0.0, 0.0, 0.0, 1.0]),
            scale: numpy.ndarray = numpy.array([1.0, 1.0, 1.0]),
            relative_to_xform: Optional[UsdGeom.Xform] = None,
    ) -> None:
        """
        Set the transform of the body.
        :param pos: Array of x, y, z position.
        :param quat: Array of x, y, z, w quaternion.
        :param scale: Array of x, y, z scale.
        :param relative_to_xform: Relative transform prim to apply the transform to.
        :return: None
        """
        mat = get_transform(pos=pos, quat=quat, scale=scale)

        if relative_to_xform is not None:
            relative_to_prim = relative_to_xform.GetPrim()
            if relative_to_prim:
                parent_prim = self._xform.GetPrim().GetParent()
                if parent_prim.IsValid() and parent_prim != relative_to_prim:
                    parent_to_relative_mat, _ = xform_cache.ComputeRelativeTransform(relative_to_prim, parent_prim)
                    mat *= parent_to_relative_mat
            else:
                raise ValueError(f"Prim at path {relative_to_xform.GetPath()} not found.")

        self._xform.AddTransformOp().Set(mat)

    def add_joint(self, joint_name: str, joint_property: JointProperty) -> JointBuilder:
        if joint_name in self._joint_builders:
            raise ValueError(f"Joint {joint_name} already exists.")
        else:
            joint_builder = JointBuilder(joint_name=joint_name, joint_property=joint_property)
            joint_builder.build()
            self._joint_builders[joint_name] = joint_builder

        return joint_builder

    def enable_rigid_body(self) -> None:
        parent_prim = self._xform.GetPrim().GetParent()
        while parent_prim.GetPath() != Sdf.Path("/"):
            if parent_prim.HasAPI(UsdPhysics.RigidBodyAPI):
                return
            parent_prim = parent_prim.GetParent()
        for child_prim in self._xform.GetPrim().GetChildren():
            if child_prim.HasAPI(UsdPhysics.RigidBodyAPI):
                child_prim.RemoveAPI(UsdPhysics.RigidBodyAPI)
                child_prim.RemoveProperty("physics:rigidBodyEnabled")

        physics_rigid_body_api = UsdPhysics.RigidBodyAPI(self._xform.GetPrim())
        physics_rigid_body_api.CreateRigidBodyEnabledAttr(True)
        physics_rigid_body_api.Apply(self._xform.GetPrim())

    def add_geom(self, geom_name: str, geom_property: GeomProperty) -> GeomBuilder:
        if geom_name in self._geom_builders:
            logging.warning(f"Geom {geom_name} already exists.")
            geom_builder = self._geom_builders[geom_name]
        else:
            geom_builder = GeomBuilder(
                stage=self.stage,
                geom_name=geom_name,
                body_path=self._xform.GetPath(),
                geom_property=geom_property
            )
            self._geom_builders[geom_name] = geom_builder

        return geom_builder

    def add_point(self,
                  points_name: str,
                  point_property: PointProperty,
                  points_rgba: Optional[numpy.ndarray] = None) -> PointsBuilder:
        if points_name in self._point_builders:
            point_builder = self._point_builders[points_name]
            point_builder.add_point(point_property=point_property)
        else:
            points_path = self.xform.GetPrim().GetPath().AppendChild(f"{self.xform.GetPrim().GetName()}_{points_name}")
            point_builder = PointsBuilder(
                stage=self.stage,
                points_path=points_path,
                points_property=[point_property],
                points_rgba=points_rgba
            )
            self._point_builders[points_name] = point_builder
        return point_builder

    def get_joint_builder(self, joint_name: str) -> JointBuilder:
        joint_name = modify_name(in_name=joint_name)
        if joint_name not in self._joint_builders:
            raise ValueError(f"Joint {joint_name} not found in {self.__class__.__name__}.")
        return self._joint_builders[joint_name]

    def get_geom_builder(self, geom_name: str) -> GeomBuilder:
        geom_name = modify_name(in_name=geom_name)
        if geom_name not in self._joint_builders:
            raise ValueError(f"Geom {geom_name} not found in {self.__class__.__name__}.")
        return self._geom_builders[geom_name]

    def set_inertial(self,
                     mass: float,
                     center_of_mass: numpy.ndarray,
                     diagonal_inertia: numpy.ndarray,
                     principal_axes: numpy.ndarray = numpy.array([0.0, 0.0, 0.0, 1.0])) -> UsdPhysics.MassAPI:
        self.enable_rigid_body()

        physics_mass_api = UsdPhysics.MassAPI(self.xform)
        physics_mass_api.CreateMassAttr(mass)
        physics_mass_api.CreateCenterOfMassAttr(Gf.Vec3f(*center_of_mass))
        physics_mass_api.CreateDiagonalInertiaAttr(Gf.Vec3f(*diagonal_inertia))
        physics_mass_api.CreatePrincipalAxesAttr(Gf.Quatf(principal_axes[3], *principal_axes[:3]))
        physics_mass_api.Apply(self.xform.GetPrim())

        return physics_mass_api

    def compute_and_set_inertial(self, inertia_source: InertiaSource) -> (GeomInertial, UsdPhysics.MassAPI):
        body_inertial = GeomInertial(mass=0.0,
                                     center_of_mass=numpy.zeros((1, 3)),
                                     inertia_tensor=numpy.zeros((3, 3)))
        for child_body_builder in self.child_body_builders:
            child_body_inertial, _ = child_body_builder.compute_and_set_inertial(inertia_source)
            body_inertial.mass += child_body_inertial.mass
            body_inertial.center_of_mass += child_body_inertial.center_of_mass * child_body_inertial.mass
            body_inertial.inertia_tensor += child_body_inertial.inertia_tensor

        if body_inertial.mass > 0.0:
            body_inertial.center_of_mass /= body_inertial.mass

        for geom_builder in self._geom_builders.values():
            if (geom_builder.is_visible and inertia_source == InertiaSource.FROM_VISUAL_MESH or
                    geom_builder.is_collidable and inertia_source == InertiaSource.FROM_COLLISION_MESH):
                geom_inertial = geom_builder.calculate_inertial()
                body_inertial.mass += geom_inertial.mass
                body_inertial.center_of_mass += geom_inertial.center_of_mass * geom_inertial.mass
                body_inertial.inertia_tensor += geom_inertial.inertia_tensor

        if body_inertial.mass > 0.0:
            body_inertial.center_of_mass /= body_inertial.mass

        body_inertia_tensor = shift_inertia_tensor(mass=body_inertial.mass,
                                                   inertia_tensor=body_inertial.inertia_tensor)

        diagonal_inertia, principal_axes = diagonalize_inertia(inertia_tensor=body_inertia_tensor)

        return body_inertial, self.set_inertial(mass=body_inertial.mass,
                                                center_of_mass=body_inertial.center_of_mass[0],
                                                diagonal_inertia=diagonal_inertia,
                                                principal_axes=principal_axes)

    def add_child_body_builder(self, child_body_builder: BodyBuilder) -> None:
        child_body_name = child_body_builder.xform.GetPrim().GetName()
        if child_body_name in self._child_body_builders:
            logging.warning(f"Child body {child_body_name} already exists.")
        else:
            self._child_body_builders[child_body_name] = child_body_builder

    @property
    def stage(self) -> Usd.Stage:
        return self.xform.GetPrim().GetStage()

    @property
    def xform(self) -> Usd.Stage:
        return self._xform

    @property
    def joint_builders(self) -> List[JointBuilder]:
        return list(self._joint_builders.values())

    @property
    def geom_builders(self) -> List[GeomBuilder]:
        return list(self._geom_builders.values())

    @property
    def points_builders(self) -> List[PointsBuilder]:
        return list(self._point_builders.values())

    @property
    def child_body_builders(self) -> List[BodyBuilder]:
        return list(self._child_body_builders.values())
