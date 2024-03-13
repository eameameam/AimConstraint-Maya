import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance

def maya_main_window():
    """Return the Maya main window widget as a Python object"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    if main_window_ptr is not None:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def create_joint_at_locator(locator_name):
    locator_position = cmds.xform(locator_name, query=True, worldSpace=True, translation=True)
    cmds.select(clear=True)
    return cmds.joint(position=locator_position)

def create_aim_constraint(bone1, bone2, aim_axis, up_axis):
    aim_vector = get_vector_from_axis(aim_axis)
    cmds.aimConstraint(bone2, bone1, aimVector=aim_vector, upVector=up_axis, worldUpType="scene")

def get_vector_from_axis(axis):
    return {
        'x': (1, 0, 0), '-x': (-1, 0, 0),
        'y': (0, 1, 0), '-y': (0, -1, 0),
        'z': (0, 0, 1), '-z': (0, 0, -1)
    }[axis]

class AimConstraintDialog(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(AimConstraintDialog, self).__init__(parent)
        self.setWindowTitle('Aim Constraint Setup')
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.update_up_axis1_options()
        self.update_up_axis2_options() 

    def create_widgets(self):
        self.aim_axis1_label = QtWidgets.QLabel('Choose Aim Axis for Bone 1:')
        self.aim_axis1_dropdown = QtWidgets.QComboBox()
        self.aim_axis1_dropdown.addItems(['x', '-x', 'y', '-y', 'z', '-z'])

        self.up_axis1_label = QtWidgets.QLabel('Choose Up Axis for Bone 1:')
        self.up_axis1_dropdown = QtWidgets.QComboBox()
        self.up_axis1_dropdown.addItems(['x', '-x', 'y', '-y', 'z', '-z'])

        self.aim_axis2_label = QtWidgets.QLabel('Choose Aim Axis for Bone 2:')
        self.aim_axis2_dropdown = QtWidgets.QComboBox()
        self.aim_axis2_dropdown.addItems(['x', '-x', 'y', '-y', 'z', '-z'])

        self.up_axis2_label = QtWidgets.QLabel('Choose Up Axis for Bone 2:')
        self.up_axis2_dropdown = QtWidgets.QComboBox()
        self.up_axis2_dropdown.addItems(['x', '-x', 'y', '-y', 'z', '-z'])

        self.create_button = QtWidgets.QPushButton('Create Aim Constraint')

    def create_layouts(self):
        self.axis1_layout = QtWidgets.QVBoxLayout()

        self.axis1_aim_layout = QtWidgets.QVBoxLayout()
        self.axis1_aim_layout.addWidget(self.aim_axis1_label)
        self.axis1_aim_layout.addWidget(self.aim_axis1_dropdown)

        self.axis1_up_layout = QtWidgets.QVBoxLayout()
        self.axis1_up_layout.addWidget(self.up_axis1_label)
        self.axis1_up_layout.addWidget(self.up_axis1_dropdown)

        self.axis1_layout.addLayout(self.axis1_aim_layout)
        self.axis1_layout.addLayout(self.axis1_up_layout)

        self.axis2_layout = QtWidgets.QVBoxLayout()

        self.axis2_aim_layout = QtWidgets.QVBoxLayout()
        self.axis2_aim_layout.addWidget(self.aim_axis2_label)
        self.axis2_aim_layout.addWidget(self.aim_axis2_dropdown)

        self.axis2_up_layout = QtWidgets.QVBoxLayout()
        self.axis2_up_layout.addWidget(self.up_axis2_label)
        self.axis2_up_layout.addWidget(self.up_axis2_dropdown)

        self.axis2_layout.addLayout(self.axis2_aim_layout)
        self.axis2_layout.addLayout(self.axis2_up_layout)

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.axis_main_layout = QtWidgets.QHBoxLayout(self)

        self.axis_main_layout.addLayout(self.axis1_layout)
        self.axis_main_layout.addLayout(self.axis2_layout)

        self.main_layout.addLayout(self.axis_main_layout)

        self.main_layout.addWidget(self.create_button)


    def create_connections(self):
        self.create_button.clicked.connect(self.on_create_clicked)
        self.aim_axis1_dropdown.currentIndexChanged.connect(self.update_up_axis1_options)
        self.aim_axis2_dropdown.currentIndexChanged.connect(self.update_up_axis2_options)

    def update_up_axis_options(self, aim_axis_dropdown, up_axis_dropdown):
        current_aim = aim_axis_dropdown.currentText()
        up_axis_options = ['x', '-x', 'y', '-y', 'z', '-z']
        up_axis_options.remove(current_aim)
        up_axis_options.remove('-' + current_aim if current_aim[0] != '-' else current_aim[1:])
        
        up_axis_dropdown.clear()
        up_axis_dropdown.addItems(up_axis_options)

    def update_up_axis1_options(self):
        self.update_up_axis_options(self.aim_axis1_dropdown, self.up_axis1_dropdown)

    def update_up_axis2_options(self):
        self.update_up_axis_options(self.aim_axis2_dropdown, self.up_axis2_dropdown)

    def on_create_clicked(self):
        aim_axis1 = self.aim_axis1_dropdown.currentText()
        up_axis1 = self.convert_to_vector(self.up_axis1_dropdown.currentText())
        aim_axis2 = self.aim_axis2_dropdown.currentText()
        up_axis2 = self.convert_to_vector(self.up_axis2_dropdown.currentText())

        selected = cmds.ls(selection=True)
        if len(selected) != 2:
            cmds.warning('Please select exactly two objects.')
            return

        bone1 = create_joint_at_locator(selected[0])
        bone2 = create_joint_at_locator(selected[1])

        temp_constraint = cmds.aimConstraint(bone2, bone1, aimVector=get_vector_from_axis(aim_axis1), upVector=up_axis1, worldUpType="vector")
        cmds.delete(temp_constraint) 

        temp_constraint = cmds.aimConstraint(bone1, bone2, aimVector=get_vector_from_axis(aim_axis2), upVector=up_axis2, worldUpType="vector")
        cmds.delete(temp_constraint)

        rotations_bone1 = cmds.xform(bone1, query=True, ws=True, rotation=True)
        rotations_bone2 = cmds.xform(bone2, query=True, ws=True, rotation=True)

        cmds.makeIdentity(bone1, apply=True, rotate=True)
        cmds.makeIdentity(bone2, apply=True, rotate=True)

        cmds.joint(bone1, edit=True, orientation=rotations_bone1)
        cmds.joint(bone2, edit=True, orientation=rotations_bone2)

        create_aim_constraint(bone1, bone2, aim_axis=aim_axis1, up_axis=up_axis1)
        create_aim_constraint(bone2, bone1, aim_axis=aim_axis2, up_axis=up_axis2)

    def convert_to_vector(self, axis):
        return {
            'x': (1, 0, 0), '-x': (-1, 0, 0),
            'y': (0, 1, 0), '-y': (0, -1, 0),
            'z': (0, 0, 1), '-z': (0, 0, -1)
        }[axis]

def show_aim_constraint_dialog():
    global dialog
    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass
    dialog = AimConstraintDialog()
    dialog.show()

show_aim_constraint_dialog()