import maya.cmds
import string

class RigidbodyRegulaterWindow:

  def _getMotherGroup(self):
    errorMessage = "Do not select MMD Model's transform."
    selection = maya.cmds.ls(sl=True)
    if len(selection) <= 0:
      raise StandardError, errorMessage

    transform = selection[0]
    try:
      motherGroup = maya.cmds.listRelatives(transform, p=True)[0]
    except:
      raise StandardError, errorMessage
    nodeType = maya.cmds.getAttr("%s.mmdModel" % motherGroup)
    if not nodeType:
      raise StandardError, errorMessage
    return motherGroup


  def _getNodeType(self, nodeType):
    children = maya.cmds.listRelatives(self.motherGroup, c=True)
    for child in children:
      try:
        nodeTypeChecker = maya.cmds.getAttr("%s.nodeType" % child)
        if nodeTypeChecker == nodeType:
          return child
      except:
        #nodeTypeが存在しない
        pass
    raise StandardError, "Do not found nodeType == %s." % nodeType


  def _getRigidbodyGroup(self):
    return self._getNodeType("rigidbodyGroup")


  def _getConstraintGroup(self):
    return self._getNodeType("constraintGroup")


  def _listingShapes(self):
    return maya.cmds.listRelatives(self.rigidbodyGroup, c=True)


  def _listingColliders(self):
    colliders = []
    for shape in self.rigidbodyShapes:
      collider = shape.replace("rcube_", "rigid_")
      colliders.append(collider)
    return colliders


  def _getJointFromSolver(self, solver):
    solverChildren = maya.cmds.listRelatives(solver, c=True)
    for schild in solverChildren:
      nodeType = maya.cmds.nodeType(schild)
      if nodeType == "bulletRigidBodyConstraintShape":
        return schild
    return None


  def _listingJoints(self):
    joints = []
    children = maya.cmds.listRelatives(self.constraintGroup, c=True)
    for child in children:
      if "solver_" in child:
        joint = self._getJointFromSolver(child)
        if joint != None:
          joints.append(joint)


  def __init__(self):
    self.motherGroup = self._getMotherGroup()
    self.rigidbodyGroup = self._getRigidbodyGroup()
    self.rigidbodyShapes = self._listingShapes()
    self.constraintGroup = self._getConstraintGroup()
    self.joints = self._listingJoints()
    self.colliders = self._listingColliders()
    self.joints = self._listingJoints()


  def _createDefaultName(self, label):
    attrName = label.replace(" ", "")
    return "default" + attrName


  def _createAttributeName(self, label):
    try:
      strs = label.split(" ")   # 空白文字を削除して、先頭文字を小文字にする
      strs[0] = strs[0].lower()
      attribute = strs[0] + strs[1]
    except:
      return label.lower()
    return attribute


  def _changeFloatField(self, defaultName, attributeName, value):
    for collider in self.colliders:
      try:
        defaultValue = maya.cmds.getAttr("%s.%s" % (collider, defaultName))
        maya.cmds.setAttr("%s.%s" % (collider, attributeName), defaultValue * value)
      except:
        pass  # lengthなど存在しないColliderもあるのでパス


  def _showLine(self, label):
    width = 150
    changeMehod = lambda *args:self._changeFloatField(defaultName, attributeName, args[0])
    defaultName = self._createDefaultName(label)
    attributeName = self._createAttributeName(label)
    maya.cmds.rowLayout(numberOfColumns=2, columnWidth2=(width, 200))
    maya.cmds.text(label=label,
      align="right",
      width=width-20)
    maya.cmds.floatField(v=1.0,
      changeCommand=changeMehod,
      dragCommand=changeMehod)
    maya.cmds.setParent("..")


  def _layout(self):
    maya.cmds.columnLayout()

    maya.cmds.frameLayout(l="Rigidbody Properties")
    self._showLine("Mass")
    self._showLine("Linear Damping")
    self._showLine("Angular Damping")
    self._showLine("Friction")
    self._showLine("Restitution")
    
    maya.cmds.frameLayout(l="Collider Properties")
    self._showLine("Length")
    self._showLine("Radius")
    self._showLine("ExtentsX")
    self._showLine("ExtentsY")
    self._showLine("ExtentsZ")

    # JointConstraintの設定をする

  def show(self):
    window = maya.cmds.window(t="Rigidbody Regulater", w=400, h=300)

    self._layout()

    maya.cmds.showWindow(window)

maya.cmds.select("rigidbodies")
w = RigidbodyRegulaterWindow()
w.show()