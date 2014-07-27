#-*- encoding: utf-8
import maya.cmds
import maya.OpenMaya
#import pymel.core as pm
#import pymel.api as api
import copy
import math

class JointMath:

  def _getChildParentPos(self, child, parent):
    cpos = maya.cmds.xform(child, q=True, ws=True, t=True)
    ppos = maya.cmds.xform(parent, q=True, ws=True, t=True)
    return (cpos, ppos)


  def _getDirectionList(self, cpos, ppos):
    direction = []
    for i in range(3):
      direction.append(cpos[i] - ppos[i])
    return direction
  
  
  def Length(self, child, parent):
    cpos, ppos = self._getChildParentPos(child, parent)
    direction = self._getDirectionList(cpos, ppos)
    length = 0.0
    for d in direction:
      length += d * d
    return math.sqrt(length)


  def Direction(self, child, parent):
    cpos, ppos = self._getChildParentPos(child, parent)
    dList = self._getDirectionList(cpos, ppos)
    direction = maya.OpenMaya.MVector(dList[0], dList[1], dList[2])
    direction.normalize()
    return direction


  def ListToMatrix(self, matrixList):
    matrixUtil = maya.OpenMaya.MScriptUtil()
    matrix = maya.OpenMaya.MMatrix()
    matrixUtil.createMatrixFromList(matrixList, matrix)
    return matrix


  def VectorListToMatrix(self, vx, vy, vz):
    vx.append(0.0)
    vy.append(0.0)
    vz.append(0.0)
    vw = [0.0, 0.0, 0.0, 0.0]
    matrixList = vx + vy + vz + vw
    return self.ListToMatrix(matrixList)


  def VectorToMatrix(self, vx, vy, vz):
    matrixList = [
      vx.x, vx.y, vx.z, 0.0,
      vy.x, vy.y, vy.z, 0.0,
      vz.x, vz.y, vz.z, 0.0,
      0.0, 0.0, 0.0, 0.0]
    return self.ListToMatrix(matrixList)



class SetJointWrapper:
  def __init__(self):
    pass

  def GetJoint(self):
    lsArray = maya.cmds.ls(sl=True)
    if len(lsArray) < 1 or len(lsArray) > 1:
      raise "Do not select a joint. Please, select one joint."
    if maya.cmds.nodeType(lsArray[0]) != "joint":
      raise "Do not select joint."
    return lsArray[0]


  def GetChildren(self, joint):
    children = maya.cmds.listRelatives(joint, c=True, typ="joint")
    if len(children) < 1:
      raise "%s do not have children." % joint
    return children


  def SetTextScrollList(self, scrollList, children):
    for child in children:
      maya.cmds.textScrollList(scrollList, e=True, a=child)


class SelectScrollWrapper:
  
  def GetSelectFrontDirection(self, scrollList):
    selectIndex = maya.cmds.textScrollList(scrollList, q=True, sl=True)
    if selectIndex == 0:
      raise "Do not select child bones"
    return selectIndex - 1
  

  def GetFrontDirection(self, scrollList):
    selectIndex = self.selectScrollWrap.GetSelectFrontDirection(scrollList)
    selectChild = self._children[selectIndex]
    direction = self.math.Direction(selectChild, self._joint) 


class JointOrientViews:

  def __init__(self):
    self.width = 340
    self.math = JointMath()
    self.selectScrollWrap = SelectScrollWrapper()
    self.setJointWrap = SetJointWrapper()


  def _setJoint(self, *args):
    self._joint = self.setJointWrap.GetJoint()
    self._children = self.setJointWrap.GetChildren(self._joint)
    self.setJointWrap.SetTextScrollList(self._scrollList, self._children)


  def _selectScrollList(self, *args):
    pass


  def _layout(self):
    maya.cmds.columnLayout()

    maya.cmds.button(l="Set Joint", w=self.width, h=32, command=self._setJoint)

    maya.cmds.rowLayout(nc=2)
    maya.cmds.text(l="  Selected Joint  ", w=82)
    self._selectedJoint = maya.cmds.textField(editable=False)
    maya.cmds.setParent("..")

    maya.cmds.rowLayout(nc=2)
    maya.cmds.text(l="  Front Direction  ")
    self._scrollList = maya.cmds.textScrollList(w=250, h=128, sc=self._selectScrollList)
    maya.cmds.setParent("..")
    
    maya.cmds.rowLayout(nc=5)
    maya.cmds.text(l="Front", w=82)
    maya.cmds.button(l="X", w=32)
    maya.cmds.button(l="Y", w=32)
    maya.cmds.button(l="Z", w=32)
    maya.cmds.button(l="+/-", w=32)
    maya.cmds.setParent("..")

    maya.cmds.rowLayout(nc=5)
    maya.cmds.text(l="Side", w=82)
    maya.cmds.button(l="X", w=32)
    maya.cmds.button(l="Y", w=32)
    maya.cmds.button(l="Z", w=32)
    maya.cmds.button(l="+/-", w=32)
    maya.cmds.setParent("..")

  def show(self):
    self.window = maya.cmds.window(t="Joint Orient Adjuster", w=self.width, h=300)

    self._layout()

    maya.cmds.showWindow(self.window)


def show():
  joa = JointOrientViews()
  joa.show()

show()