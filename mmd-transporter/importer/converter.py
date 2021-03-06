#-*- encoding: utf-8
import sys
import maya.OpenMaya
import maya.OpenMayaMPx

class ToMaya:
  @classmethod
  def vector3(cls, v):
    return maya.OpenMaya.MFloatPoint(v.x, v.y, -v.z)

  @classmethod
  def fvector3(cls, v):
    return maya.OpenMaya.MVector(v.x, v.y, -v.z)

  @classmethod
  def uv(cls, uv, index, uArray, vArray):
    uArray[index] = uv.x
    vArray[index] = 1.0 - uv.y