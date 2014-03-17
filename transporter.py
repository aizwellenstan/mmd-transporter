#-*- encoding: utf-8
import maya.OpenMaya
import maya.OpenMayaMPx
import maya.cmds as cmds

from csv_importer import *
from model_importer import *
from array_maker import *
from material_importer import * 
from face_material_importer import *


class MMDTransporter(maya.OpenMayaMPx.MPxNode):
  widthHeight = maya.OpenMaya.MObject()
  outputMesh = maya.OpenMaya.MObject()

  @classmethod
  def nodeCreator():
    csv_file_path = cmds.fileDialog2(dialogStyle=2, selectFileFilter="*.csv", okCaption="Select")[0]
    return maya.OpenMayaMPx.asMPxPtr(MMDTransporter(csv_file_path))

  @classmethod
  def nodeInitializer():
    nAttr = maya.OpenMaya.MFnNumericAttribute()
    MMDTransporter.widthHeight = nAttr.create('widthHeight', 'wh', maya.OpenMaya.MFnNumericData.kFloat, 1.0)
    nAttr.setStorable(1)

    typedAttr = maya.OpenMaya.MFnTypedAttribute()
    MMDTransporter.outputMesh = typedAttr.create('outputMesh', 'out', maya.OpenMaya.MFnData.kMesh)
    MMDTransporter.addAttribute(MMDTransporter.widthHeight)
    MMDTransporter.addAttribute(MMDTransporter.outputMesh)
    MMDTransporter.attributeAffects(MMDTransporter.widthHeight, MMDTransporter.outputMesh)

  def __init__(self, csv_file_path):
    self.csv_file_path = csv_file_path
    maya.OpenMayaMPx.MPxNode.__init__(self)
    

  def _createMesh(self, outData):
    maker = ArrayMaker()
    records = CSVImporter().toRowList(self.csv_file_path)
    model_imp = ModelImporter(records)

    points = maker.MakePoints(model_imp.vertices)
    faceConnects = maker.MakeFaceConnects(model_imp.indices)
    faceCounts = maker.MakeFaceCounts(len(model_imp.indices) / 3)
    uArray = maker.MakeSingles(model_imp.us)
    vArray = maker.MakeSingles(model_imp.vs)

    meshFS = maya.OpenMaya.MFnMesh()
    newMesh = meshFS.create(points.length(), faceCounts.length(), points, faceCounts, faceConnects, uArray, vArray, outData)
    
    meshFS.assignUVs(faceCounts, faceConnects)
    return newMesh


  def compute(self, plug, data):
    if plug == MMDTransporter.outputMesh:
      dataHandle = data.inputValue(MMDTransporter.widthHeight)
      size = dataHandle.asFloat()

      dataCreator = maya.OpenMaya.MFnMeshData()
      newOutputData = dataCreator.create()
      self._createMesh(newOutputData)

      outputHandle = data.outputValue(MMDTransporter.outputMesh)
      outputHandle.setMObject(newOutputData)
      data.setClean(plug)
    else:
      return maya.OpenMaya.kUnknownParameter
