from PyQt5 import QtWidgets, QtGui, QtCore, Qt, uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from WaveOptics.gui.mplwidget import *
from WaveOptics.Rays import *
from tabulate import tabulate
from pathlib import Path
import sys
import time
from typing import Tuple, Union, Optional, Dict


class OpticalOperatorModel(QtCore.QObject):
    """
    Model for interacting with an OpticalOperator
    """

    zChanged = pyqtSignal([], [float], name='zChanged')
    offsetChanged = pyqtSignal([], [float], name='offsetChanged')
    sizeChanged = pyqtSignal([], [float], name='sizeChanged')
    valueChanged = pyqtSignal([], [float], name='valueChanged')
    labelChanged = pyqtSignal([], [str], name='labelChanged')
    operatorChanged = pyqtSignal([], [OpticalOperator], name='operatorChanged')

    @property
    def z(self):
        return self._optical_operator.z

    @z.setter
    def z(self, value):
        self._optical_operator.set_z(value)
        self.zChanged.emit()
        self.zChanged[float].emit(self._optical_operator.z)

    @property
    def offset(self):
        return self._optical_operator.offset

    @offset.setter
    def offset(self, value):
        self._optical_operator.set_offset(value)
        self.offsetChanged.emit()
        self.offsetChanged[float].emit(self._optical_operator.offset)

    @property
    def size(self):
        return self._optical_operator.size

    @size.setter
    def size(self, value):
        self._optical_operator.size = value
        self.sizeChanged.emit()
        self.sizeChanged[float].emit(self._optical_operator.size)

    @property
    def value(self):
        return self._optical_operator.value

    @value.setter
    def value(self, val):
        self._optical_operator.set_value(val)
        self.valueChanged.emit()
        self.valueChanged[float].emit(self._optical_operator.value)

    @property
    def label(self):
        return self._optical_operator.label

    @label.setter
    def label(self, value):
        self._optical_operator.set_label(value)
        self.labelChanged.emit()
        self.labelChanged[str].emit(self._optical_operator.label)

    @property
    def optical_operator(self):
        return self._optical_operator

    @optical_operator.setter
    def optical_operator(self, value):
        self._optical_operator = value
        self.operatorChanged.emit()
        self.operatorChanged[OpticalOperator].emit(self._optical_operator)

    def __init__(self, optical_operator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(optical_operator, OpticalOperator):
            raise TypeError(
                f'Cannot create {self.__class__.__name__} for {optical_operator!r}: Invalid type {type(optical_operator)}')
        self._optical_operator = optical_operator


class MicroscopeModel(QtCore.QObject):
    modelChanged = pyqtSignal([], name='modelChanged')

    sourceZChanged = pyqtSignal([], [float], name='sourceZChanged')
    sourceOffsetChanged = pyqtSignal([], [float], name='sourceOffsetChanged')
    sourceSizeChanged = pyqtSignal([], [float], name='sourceSizeChanged')
    sourceAnglesChanged = pyqtSignal([], [list], name='sourceAnglesChanged')
    sourceAngleAdded = pyqtSignal([], [float], [list], name='sourceAngleAdded')
    sourceAngleRemoved = pyqtSignal([], [float], [list], name='sourceAngleRemoved')

    screenZChanged = pyqtSignal([], [float], name='screenZChanged')

    operatorZChanged = pyqtSignal([str, float], name='operatorZChanged')
    operatorOffsetChanged = pyqtSignal([str, float], name='operatorOffsetChanged')
    operatorValueChanged = pyqtSignal([str, float], name='operatorValueChanged')

    CL1ZChanged = pyqtSignal([], [float], name='CL1ZChanged')
    CL1OffsetChanged = pyqtSignal([], [float], name='CL1OffsetChanged')
    CL1ValueChanged = pyqtSignal([], [float], name='CL1ValueChanged')
    CL1Toggled = pyqtSignal([], [bool], name='CL1Toggled')

    CL2ZChanged = pyqtSignal([], [float])
    CL2OffsetChanged = pyqtSignal([], [float])
    CL2ValueChanged = pyqtSignal([], [float])
    CL2Toggled = pyqtSignal([], [bool])

    CL3ZChanged = pyqtSignal([], [float])
    CL3OffsetChanged = pyqtSignal([], [float])
    CL3ValueChanged = pyqtSignal([], [float])
    CL3Toggled = pyqtSignal([], [bool])

    CMZChanged = pyqtSignal([], [float])
    CMOffsetChanged = pyqtSignal([], [float])
    CMValueChanged = pyqtSignal([], [float])
    CMToggled = pyqtSignal([], [bool])

    OLPreZChanged = pyqtSignal([], [float])
    OLPreOffsetChanged = pyqtSignal([], [float])
    OLPreValueChanged = pyqtSignal([], [float])
    OLPreToggled = pyqtSignal([], [bool])

    OLPostZChanged = pyqtSignal([], [float])
    OLPostOffsetChanged = pyqtSignal([], [float])
    OLPostValueChanged = pyqtSignal([], [float])
    OLPostToggled = pyqtSignal([], [bool])

    OMZChanged = pyqtSignal([], [float])
    OMOffsetChanged = pyqtSignal([], [float])
    OMValueChanged = pyqtSignal([], [float])
    OMToggled = pyqtSignal([], [bool])

    IL1ZChanged = pyqtSignal([], [float])
    IL1OffsetChanged = pyqtSignal([], [float])
    IL1ValueChanged = pyqtSignal([], [float])
    IL1Toggled = pyqtSignal([], [bool])

    IL2ZChanged = pyqtSignal([], [float])
    IL2OffsetChanged = pyqtSignal([], [float])
    IL2ValueChanged = pyqtSignal([], [float])
    IL2Toggled = pyqtSignal([], [bool])

    IL3ZChanged = pyqtSignal([], [float])
    IL3OffsetChanged = pyqtSignal([], [float])
    IL3ValueChanged = pyqtSignal([], [float])
    IL3Toggled = pyqtSignal([], [bool])

    PLZChanged = pyqtSignal([], [float])
    PLOffsetChanged = pyqtSignal([], [float])
    PLValueChanged = pyqtSignal([], [float])
    PLToggled = pyqtSignal([], [bool])

    GUN1ZChanged = pyqtSignal([], [float])
    GUN1ValueChanged = pyqtSignal([], [float])
    GUN1Toggled = pyqtSignal([], [bool])

    GUN2ZChanged = pyqtSignal([], [float])
    GUN2ValueChanged = pyqtSignal([], [float])
    GUN2Toggled = pyqtSignal([], [bool])

    CLA1ZChanged = pyqtSignal([], [float])
    CLA1ValueChanged = pyqtSignal([], [float])
    CLA1Toggled = pyqtSignal([], [bool])

    CLA2ZChanged = pyqtSignal([], [float])
    CLA2ValueChanged = pyqtSignal([], [float])
    CLA2Toggled = pyqtSignal([], [bool])

    ILA1ZChanged = pyqtSignal([], [float])
    ILA1ValueChanged = pyqtSignal([], [float])
    ILA1Toggled = pyqtSignal([], [bool])

    ILA2ZChanged = pyqtSignal([], [float])
    ILA2ValueChanged = pyqtSignal([], [float])
    ILA2Toggled = pyqtSignal([], [bool])

    PLAZChanged = pyqtSignal([], [float])
    PLAValueChanged = pyqtSignal([], [float])
    PLAToggled = pyqtSignal([], [bool])

    beamShiftCompensatorChanged = pyqtSignal([], [float])
    beamTiltCompensatorChanged = pyqtSignal([], [float])

    beamShiftChanged = pyqtSignal([], [float], [float, float])
    beamTiltChanged = pyqtSignal([], [float], [float, float])

    imageShiftCompensatorChanged = pyqtSignal([], [float])
    imageTiltCompensatorChanged = pyqtSignal([], [float])

    imageShiftChanged = pyqtSignal([], [float], [float, float])
    imageTiltChanged = pyqtSignal([], [float], [float, float])

    @property
    def source_z(self):
        return self._source.z

    @source_z.setter
    def source_z(self, value):
        self._source.z = value
        self.sourceZChanged.emit()
        self.sourceZChanged[float].emit(value)
        self.modelChanged.emit()

    @property
    def source_offset(self):
        return self._source.offset

    @source_offset.setter
    def source_offset(self, value):
        self._source.offset = value
        self.sourceOffsetChanged.emit()
        self.sourceOffsetChanged[float].emit(value)
        self.modelChanged.emit()

    @property
    def source_size(self):
        return self._source.size

    @source_size.setter
    def source_size(self, value):
        self._source.size = value
        self.sourceSizeChanged.emit()
        self.sourceSizeChanged[float].emit(value)
        self.modelChanged.emit()

    @property
    def source_angles(self):
        return self._source.angles

    @source_angles.setter
    def source_angles(self, value):
        self._source.angles = value
        self.sourceAnglesChanged.emit()
        self.sourceAnglesChanged[list].emit(self._source.angles)
        self.modelChanged.emit()

    @property
    def screen_z(self):
        return self._screen.z

    @screen_z.setter
    def screen_z(self, value):
        self._screen.z = value
        self.screenZChanged.emit()
        self.screenZChanged[float].emit(value)
        self.modelChanged.emit()

    @property
    def CL1_z(self):
        return self._CL1.z

    @CL1_z.setter
    def CL1_z(self, value):
        self._CL1.z = value
        self.CL1ZChanged.emit()
        self.CL1ZChanged[float].emit(value)
        self.operatorZChanged[str, float].emit(self._CL1.label, value)
        self.modelChanged.emit()

    @property
    def CL1_offset(self):
        return self._CL1.offset

    @CL1_offset.setter
    def CL1_offset(self, value):
        self._CL1.offset = value
        self.CL1OffsetChanged.emit()
        self.CL1OffsetChanged[float].emit(value)
        self.operatorOffsetChanged[str, float].emit(self._CL1.label, value)
        self.modelChanged.emit()

    @property
    def CL1_value(self):
        return self._CL1.value

    @property
    def CL1_label(self):
        return self._CL1.label

    @CL1_value.setter
    def CL1_value(self, value):
        self._CL1.value = value
        self.CL1ValueChanged.emit()
        self.CL1ValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._CL1.label, value)
        self.modelChanged.emit()

    @property
    def CL2_z(self):
        return self._CL2.z

    @CL2_z.setter
    def CL2_z(self, value):
        self._CL2.z = value
        self.CL2ZChanged.emit()
        self.CL2ZChanged[float].emit(value)
        self.operatorZChanged[str, float].emit(self._CL2.label, value)
        self.modelChanged.emit()

    @property
    def CL2_offset(self):
        return self._CL2.offset

    @CL2_offset.setter
    def CL2_offset(self, value):
        self._CL2.offset = value
        self.CL2OffsetChanged.emit()
        self.CL2OffsetChanged[float].emit(value)
        self.operatorOffsetChanged[str, float].emit(self._CL2.label, value)
        self.modelChanged.emit()

    @property
    def CL2_value(self):
        return self._CL2.value

    @CL2_value.setter
    def CL2_value(self, value):
        self._CL2.value = value
        self.CL2ValueChanged.emit()
        self.CL2ValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._CL2.label, value)
        self.modelChanged.emit()

    @property
    def CL2_label(self):
        return self._CL2.label

    @property
    def CL3_z(self):
        return self._CL3.z

    @CL3_z.setter
    def CL3_z(self, value):
        self._CL3.z = value
        self.CL3ZChanged.emit()
        self.CL3ZChanged[float].emit(value)
        self.operatorZChanged[str, float].emit(self._CL3.label, value)
        self.modelChanged.emit()

    @property
    def CL3_offset(self):
        return self._CL3.offset

    @CL3_offset.setter
    def CL3_offset(self, value):
        self._CL3.offset = value
        self.CL3OffsetChanged.emit()
        self.CL3OffsetChanged[float].emit(value)
        self.operatorOffsetChanged[str, float].emit(self._CL3.label, value)
        self.modelChanged.emit()

    @property
    def CL3_value(self):
        return self._CL3.value

    @CL3_value.setter
    def CL3_value(self, value):
        self._CL3.value = value
        self.CL3ValueChanged.emit()
        self.CL3ValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._CL3.label, value)
        self.modelChanged.emit()

    @property
    def CL3_label(self):
        return self._CL3.label

    @property
    def CM_z(self):
        return self._CM.z

    @CM_z.setter
    def CM_z(self, value):
        self._CM.z = value
        self.CMZChanged.emit()
        self.CMZChanged[float].emit(value)
        self.operatorZChanged[str, float].emit(self._CM.label, value)
        self.modelChanged.emit()

    @property
    def CM_offset(self):
        return self._CM.offset

    @CM_offset.setter
    def CM_offset(self, value):
        self._CM.offset = value
        self.CMOffsetChanged.emit()
        self.CMOffsetChanged[float].emit(value)
        self.operatorOffsetChanged[str, float].emit(self._CM.label, value)
        self.modelChanged.emit()

    @property
    def CM_value(self):
        return self._CM.value

    @CM_value.setter
    def CM_value(self, value):
        self._CM.value = value
        self.CMValueChanged.emit()
        self.CMValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._CM.label, value)
        self.modelChanged.emit()

    @property
    def CM_label(self):
        return self._CM.label

    @property
    def OLPre_z(self):
        return self._OLpre.z

    @OLPre_z.setter
    def OLPre_z(self, value):
        self._OLpre.z = value
        self.OLPreZChanged.emit()
        self.OLPreZChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._OLpre.label, value)
        self.modelChanged.emit()

    @property
    def OLPre_offset(self):
        return self._OLpre.offset

    @OLPre_offset.setter
    def OLPre_offset(self, value):
        self._OLpre.offset = value
        self.OLPreOffsetChanged.emit()
        self.OLPreOffsetChanged[float].emit(value)
        self.operatorOffsetChanged[str, float].emit(self._OLpre.label, value)
        self.modelChanged.emit()

    @property
    def OLPre_value(self):
        return self._OLpre.value

    @OLPre_value.setter
    def OLPre_value(self, value):
        self._OLpre.value = value
        self.OLPreValueChanged.emit()
        self.OLPreValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._OLpre.label, value)
        self.modelChanged.emit()

    @property
    def OLPre_label(self):
        return self._OLpre.label

    @property
    def OLPost_z(self):
        return self._OLpost.z

    @OLPost_z.setter
    def OLPost_z(self, value):
        self._OLpost.z = value
        self.OLPostZChanged.emit()
        self.OLPostZChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._OLpost.label, value)
        self.modelChanged.emit()

    @property
    def OLPost_offset(self):
        return self._OLpost.offset

    @OLPost_offset.setter
    def OLPost_offset(self, value):
        self._OLpost.offset = value
        self.OLPostOffsetChanged.emit()
        self.OLPostOffsetChanged[float].emit(value)
        self.operatorOffsetChanged[str, float].emit(self._OLpost.label, value)
        self.modelChanged.emit()

    @property
    def OLPost_value(self):
        return self._OLpost.value

    @OLPost_value.setter
    def OLPost_value(self, value):
        self._OLpost.value = value
        self.OLPostValueChanged.emit()
        self.OLPostValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._OLpost.label, value)
        self.modelChanged.emit()

    @property
    def OLPost_label(self):
        return self._OLpost.label

    @property
    def OM_z(self):
        return self._OM.z

    @OM_z.setter
    def OM_z(self, value):
        self._OM.z = value
        self.OMZChanged.emit()
        self.OMZChanged[float].emit(value)
        self.operatorZChanged[str, float].emit(self._OM.label, value)
        self.modelChanged.emit()

    @property
    def OM_offset(self):
        return self._OM.offset

    @OM_offset.setter
    def OM_offset(self, value):
        self._OM.offset = value
        self.OMOffsetChanged.emit()
        self.OMOffsetChanged[float].emit(value)
        self.operatorOffsetChanged[str, float].emit(self._OM.label, value)
        self.modelChanged.emit()

    @property
    def OM_value(self):
        return self._OM.value

    @OM_value.setter
    def OM_value(self, value):
        self._OM.value = value
        self.OMValueChanged.emit()
        self.OMValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._OM.label, value)
        self.modelChanged.emit()

    @property
    def OM_label(self):
        return self._OM.label

    @property
    def IL1_z(self):
        return self._IL1.z

    @IL1_z.setter
    def IL1_z(self, value):
        self._IL1.z = value
        self.IL1ZChanged.emit()
        self.IL1ZChanged[float].emit(value)
        self.operatorZChanged[str, float].emit(self._IL1.label, value)
        self.modelChanged.emit()

    @property
    def IL1_offset(self):
        return self._IL1.offset

    @IL1_offset.setter
    def IL1_offset(self, value):
        self._IL1.offset = value
        self.IL1OffsetChanged.emit()
        self.IL1OffsetChanged[float].emit(value)
        self.operatorOffsetChanged[str, float].emit(self._IL1.label, value)
        self.modelChanged.emit()

    @property
    def IL1_value(self):
        return self._IL1.value

    @IL1_value.setter
    def IL1_value(self, value):
        self._IL1.value = value
        self.IL1ValueChanged.emit()
        self.IL1ValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._IL1.label, value)
        self.modelChanged.emit()

    @property
    def IL1_label(self):
        return self._IL1.label

    @property
    def IL2_z(self):
        return self._IL2.z

    @IL2_z.setter
    def IL2_z(self, value):
        self._IL2.z = value
        self.IL2ZChanged.emit()
        self.IL2ZChanged[float].emit(value)
        self.operatorZChanged[str, float].emit(self._IL2.label, value)
        self.modelChanged.emit()

    @property
    def IL2_offset(self):
        return self._IL2.offset

    @IL2_offset.setter
    def IL2_offset(self, value):
        self._IL2.offset = value
        self.IL2OffsetChanged.emit()
        self.IL2OffsetChanged[float].emit(value)
        self.operatorOffsetChanged[str, float].emit(self._IL2.label, value)
        self.modelChanged.emit()

    @property
    def IL2_value(self):
        return self._IL2.value

    @IL2_value.setter
    def IL2_value(self, value):
        self._IL2.value = value
        self.IL2ValueChanged.emit()
        self.IL2ValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._IL2.label, value)
        self.modelChanged.emit()

    @property
    def IL2_label(self):
        return self._IL2.label

    @property
    def IL3_z(self):
        return self._IL3.z

    @IL3_z.setter
    def IL3_z(self, value):
        self._IL3.z = value
        self.IL3ZChanged.emit()
        self.IL3ZChanged[float].emit(value)
        self.operatorZChanged[str, float].emit(self._IL3.label, value)
        self.modelChanged.emit()

    @property
    def IL3_offset(self):
        return self._IL3.offset

    @IL3_offset.setter
    def IL3_offset(self, value):
        self._IL3.offset = value
        self.IL3OffsetChanged.emit()
        self.IL3OffsetChanged[float].emit(value)
        self.operatorOffsetChanged[str, float].emit(self._IL3.label, value)
        self.modelChanged.emit()

    @property
    def IL3_value(self):
        return self._IL3.value

    @IL3_value.setter
    def IL3_value(self, value):
        self._IL3.value = value
        self.IL3ValueChanged.emit()
        self.IL3ValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._IL3.label, value)
        self.modelChanged.emit()

    @property
    def IL3_label(self):
        return self._IL3.label

    @property
    def PL_z(self):
        return self._PL.z

    @PL_z.setter
    def PL_z(self, value):
        self._PL.z = value
        self.PLZChanged.emit()
        self.PLZChanged[float].emit(value)
        self.operatorZChanged[str, float].emit(self._PL.label, value)
        self.modelChanged.emit()

    @property
    def PL_offset(self):
        return self._PL.offset

    @PL_offset.setter
    def PL_offset(self, value):
        self._PL.offset = value
        self.PLOffsetChanged.emit()
        self.PLOffsetChanged[float].emit(value)
        self.operatorOffsetChanged[str, float].emit(self._PL.label, value)
        self.modelChanged.emit()

    @property
    def PL_value(self):
        return self._PL.value

    @PL_value.setter
    def PL_value(self, value):
        self._PL.value = value
        self.PLValueChanged.emit()
        self.PLValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._PL.label, value)
        self.modelChanged.emit()

    @property
    def PL_label(self):
        return self._PL.label

    @property
    def GUN1_z(self):
        return self._Gun1.z

    @GUN1_z.setter
    def GUN1_z(self, value):
        self._Gun1.z = value
        self.GUN1ZChanged.emit()
        self.GUN1ZChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._Gun1.label, value)
        self.modelChanged.emit()

    @property
    def GUN1_value(self):
        return self._Gun1.value

    @GUN1_value.setter
    def GUN1_value(self, value):
        self._Gun1.value = value
        self.GUN1ValueChanged.emit()
        self.GUN1ValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._Gun1.label, value)
        self.modelChanged.emit()

    @property
    def GUN1_label(self):
        return self._Gun1.label

    @property
    def GUN2_z(self):
        return self._Gun2.z

    @GUN2_z.setter
    def GUN2_z(self, value):
        self._Gun2.z = value
        self.GUN2ZChanged.emit()
        self.GUN2ZChanged[float].emit(value)
        self.operatorZChanged[str, float].emit(self._Gun2.label, value)
        self.modelChanged.emit()

    @property
    def GUN2_value(self):
        return self._Gun2.value

    @GUN2_value.setter
    def GUN2_value(self, value):
        self._Gun2.value = value
        self.GUN2ValueChanged.emit()
        self.GUN2ValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._Gun2.label, value)
        self.modelChanged.emit()

    @property
    def GUN2_label(self):
        return self._Gun2.label

    @property
    def CLA1_z(self):
        return self._CLA1.z

    @CLA1_z.setter
    def CLA1_z(self, value):
        self._CLA1.z = value
        self.CLA1ZChanged.emit()
        self.CLA1ZChanged[float].emit(value)
        self.operatorZChanged[str, float].emit(self._CLA1.label, value)
        self.modelChanged.emit()

    @property
    def CLA1_value(self):
        return self._CLA1.value

    @CLA1_value.setter
    def CLA1_value(self, value):
        self._CLA1.value = value
        self.CLA1ValueChanged.emit()
        self.CLA1ValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._CLA1.label, value)
        self.modelChanged.emit()

    @property
    def CLA1_label(self):
        return self._CLA1.label

    @property
    def CLA2_z(self):
        return self._CLA2.z

    @CLA2_z.setter
    def CLA2_z(self, value):
        self._CLA2.z = value
        self.CLA2ZChanged.emit()
        self.CLA2ZChanged[float].emit(value)
        self.operatorZChanged[str, float].emit(self._CLA2.label, value)
        self.modelChanged.emit()

    @property
    def CLA2_value(self):
        return self._CLA2.value

    @CLA2_value.setter
    def CLA2_value(self, value):
        self._CLA2.value = value
        self.CLA2ValueChanged.emit()
        self.CLA2ValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._CLA2.label, value)
        self.modelChanged.emit()

    @property
    def CLA2_label(self):
        return self._CLA2.label

    @property
    def ILA1_z(self):
        return self._ILA1.z

    @ILA1_z.setter
    def ILA1_z(self, value):
        self._ILA1.z = value
        self.ILA1ZChanged.emit()
        self.ILA1ZChanged[float].emit(value)
        self.operatorZChanged[str, float].emit(self._ILA1.label, value)
        self.modelChanged.emit()

    @property
    def ILA1_value(self):
        return self._ILA1.value

    @ILA1_value.setter
    def ILA1_value(self, value):
        self._ILA1.value = value
        self.ILA1ValueChanged.emit()
        self.ILA1ValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._ILA1.label, value)
        self.modelChanged.emit()

    @property
    def ILA1_label(self):
        return self._ILA1.label

    @property
    def ILA2_z(self):
        return self._ILA2.z

    @ILA2_z.setter
    def ILA2_z(self, value):
        self._ILA2.z = value
        self.ILA2ZChanged.emit()
        self.ILA2ZChanged[float].emit(value)
        self.operatorZChanged[str, float].emit(self._ILA2.label, value)
        self.modelChanged.emit()

    @property
    def ILA2_value(self):
        return self._ILA2.value

    @ILA2_value.setter
    def ILA2_value(self, value):
        self._ILA2.value = value
        self.ILA2ValueChanged.emit()
        self.ILA2ValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._ILA2.label, value)
        self.modelChanged.emit()

    @property
    def ILA2_label(self):
        return self._ILA2.label

    @property
    def PLA_z(self):
        return self._PLA.z

    @PLA_z.setter
    def PLA_z(self, value):
        self._PLA.z = value
        self.PLAZChanged.emit()
        self.PLAZChanged[float].emit(value)
        self.operatorZChanged[str, float].emit(self._PLA.label, value)
        self.modelChanged.emit()

    @property
    def PLA_value(self):
        return self._PLA.value

    @PLA_value.setter
    def PLA_value(self, value):
        self._PLA.value = value
        self.PLAValueChanged.emit()
        self.PLAValueChanged[float].emit(value)
        self.operatorValueChanged[str, float].emit(self._PLA.label, value)
        self.modelChanged.emit()

    @property
    def PLA_label(self):
        return self._PLA.label

    @property
    def beam_compensator_tilt(self):
        return self._beam_tilt_compensator

    @beam_compensator_tilt.setter
    def beam_compensator_tilt(self, value):
        self._beam_tilt_compensator = value
        self.beamTiltCompensatorChanged.emit()
        self.beamTiltCompensatorChanged[float].emit(value)
        self.modelChanged.emit()

    @property
    def beam_compensator_shift(self):
        return self._beam_shift_compensator

    @beam_compensator_shift.setter
    def beam_compensator_shift(self, value):
        self._beam_shift_compensator = value
        self.beamShiftCompensatorChanged.emit()
        self.beamShiftCompensatorChanged[float].emit(value)
        self.modelChanged.emit()

    @property
    def image_compensator_tilt(self):
        return self._image_tilt_compensator

    @image_compensator_tilt.setter
    def image_compensator_tilt(self, value):
        self._image_tilt_compensator = value
        self.imageTiltCompensatorChanged.emit()
        self.imageTiltCompensatorChanged[float].emit(value)
        self.modelChanged.emit()

    @property
    def image_compensator_shift(self):
        return self._image_shift_compensator

    @image_compensator_shift.setter
    def image_compensator_shift(self, value):
        self._image_shift_compensator = value
        self.imageShiftCompensatorChanged.emit()
        self.imageShiftCompensatorChanged[float].emit(value)
        self.modelChanged.emit()

    @property
    def ray_trace(self):
        # Sort operators
        print('Calculating raytrace')
        tic = time.time()
        self._operators.sort(key=lambda operator: operator.z)
        self._operators.reverse()

        # Create propagators
        propagators = [Propagator(self._operators[i + 1].z - self._operators[i].z, z=self._operators[i].z,
                                  label='S{i}'.format(i=i + 1)) for i in
                       range(len(self._operators)) if i < len(self._operators) - 1]
        propagators.insert(0, Propagator(self._operators[0].z - self.source_z, z=self.source_z,
                                         label='S0'))  # Propagator from source
        propagators.insert(-1, Propagator(self.screen_z - self._operators[-1].z, z=self._operators[-1].z,
                                          label='S{i}'.format(i=len(self._operators))))  # Propagator to screen.

        # Add propatagors and sort again
        propagators.extend(list(self._operators))
        propagators.sort(key=lambda operator: operator.z)
        propagators.reverse()
        toc = time.time()
        print(f'Finished raytracing in {toc-tic:e}')
        return [RayTrace([initial_ray], label='RT{i}'.format(i=i)).trace(propagators, set_z=False) for
                i, initial_ray in enumerate(self._source.emit())]

    @property
    def beam_shift(self):
        return self._beam_shift

    @beam_shift.setter
    def beam_shift(self, value):
        old = self._beam_shift
        self._beam_shift = value
        self.beamShiftChanged.emit()
        self.beamShiftChanged[float].emit(value)
        self.beamShiftChanged[float, float].emit(value, old)
        self.modelChanged.emit()

    @property
    def beam_tilt(self):
        return self._beam_tilt

    @beam_tilt.setter
    def beam_tilt(self, value):
        old = self.beeam_tilt
        self._beam_tilt = value
        self.beamTiltChanged.emit()
        self.beamTiltChanged[float].emit(value)
        self.beamTiltChanged[float, float].emit(value, old)
        self.modelChanged.emit()

    @property
    def image_shift(self):
        return self._image_shift

    @image_shift.setter
    def image_shift(self, value):
        old = self._image_shift
        self._image_shift = value
        self.imageShiftChanged.emit()
        self.imageShiftChanged[float].emit(value)
        self.imageShiftChanged[float, float].emit(value, old)
        self.modelChanged.emit()

    @property
    def image_tilt(self):
        return self._image_tilt

    @image_tilt.setter
    def image_tilt(self, value):
        old = self.beeam_tilt
        self._image_tilt = value
        self.imageTiltChanged.emit()
        self.imageTiltChanged[float].emit(value)
        self.imageTiltChanged[float, float].emit(value, old)
        self.modelChanged.emit()

    @property
    def operators(self):
        return [operator for operator in self._operators]

    def __init__(self, *args, **kwargs):
        super(MicroscopeModel, self).__init__(*args, **kwargs)

        self._screen = Screen(-100)
        self._source = Source(100, [], 1)
        self._CL1 = Lens(10, label='CL1', z=90)
        self._Gun1 = Deflector(0, z=80, label='Gun1')
        self._Gun2 = Deflector(0, z=75, label='Gun2')
        self._CL2 = Lens(10, label='CL2', z=70)
        self._CL3 = Lens(10, label='CL3', z=65)
        self._CLA1 = Deflector(0, z=50, label='CLA1')
        self._CLA2 = Deflector(0, z=45, label='CLA2')
        self._CM = Lens(10, label='CM', z=30)
        self._OLpre = Lens(10, label='OLpre', z=5)
        self._OLpost = Lens(10, label='OLpost', z=-5)
        self._OM = Lens(10, label='OM', z=30)
        self._IL1 = Lens(10, label='IL1', z=-15)
        self._ILA1 = Deflector(0, z=-20, label='ILA1')
        self._ILA2 = Deflector(0, z=-25, label='ILA2')
        self._IL2 = Lens(10, label='IL2', z=-30)
        self._IL3 = Lens(10, label='IL3', z=-40)
        self._PLA = Deflector(0, z=-50, label='PLA')
        self._PL = Lens(10, label='PL', z=-60)

        self._operators = [
            self._CL1,
            self._CL2,
            self._CL3,
            self._CM,
            self._OLpre,
            self._OLpost,
            self._OM,
            self._IL1,
            self._IL2,
            self._IL3,
            self._PL,
            self._Gun1,
            self._Gun2,
            self._CLA1,
            self._CLA2,
            self._ILA1,
            self._ILA2,
            self._PLA
        ]

        self._beam_tilt_compensator = 0
        self._beam_shift_compensator = 0
        self._image_tilt_compensator = 0
        self._image_shift_compensator = 0

        self._beam_shift = 0
        self._beam_tilt = 0
        self._image_shift = 0
        self._image_tilt = 0

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def __str__(self):
        operator_strings = "\n\t".join([repr(operator) for operator in self._operators])
        tiltshift_table = tabulate([["beam tilt", self.beam_tilt, self.beam_compensator_tilt],
                                    ['beam shift', self.beam_shift, self.beam_compensator_shift],
                                    ['image tilt', self.image_tilt, self.image_compensator_tilt],
                                    ['image shift', self.image_shift, self.image_compensator_shift]],
                                   headers=['', 'Value', 'Compensator value']
                                   )
        return f'{self.__class__.__name__}:\n\t{self._source}\n\t{operator_strings}\n\t{self._screen}\nTilt and shift parameters:\n{tiltshift_table}\n'

    @pyqtSlot(float)
    def add_angle(self, value):
        self._source.angles.append(value)
        self.sourceAngleAdded.emit()
        self.sourceAngleAdded[float].emit(value)
        self.sourceAngleAdded[list].emit(list(self._source.angles))
        self.sourceAnglesChanged.emit()
        self.sourceAnglesChanged[list].emit(list(self._source.angles))

    @pyqtSlot()
    def remove_angle(self):
        removed_angle = self._source.angles.pop()
        self.sourceAngleRemoved.emit()
        self.sourceAngleRemoved[float].emit(removed_angle)
        self.sourceAngleRemoved[list].emit(list(self._source.angles))
        self.sourceAnglesChanged.emit()
        self.sourceAnglesChanged[list].emit(list(self._source.angles))


class MicroscopeView(QtWidgets.QMainWindow):
    def __init__(self, model, controller, *args, **kwargs):
        super(MicroscopeView, self).__init__(*args, **kwargs)
        uic.loadUi(Path('./source/RayGui/MicroscopeView.ui'), self)
        if not isinstance(model, MicroscopeModel):
            raise TypeError(
                f'Cannot create {self.__class__.__name__} for model {model!r}: Invalid type {type(model)}. Accepted types are MicroscopeModel')
        if not isinstance(controller, MicroscopeController):
            raise TypeError(
                f'Cannot create {self.__class__.__name__} for controller {controller!r}: Invalid type {type(controller)}. Accepted types are MicroscopeController')

        self._model = model
        self._controller = controller
        self.printButton.clicked.connect(lambda: print(f'{self._model}'))

        self._operatorView = OperatorView(self._model, self._controller, self)
        self.actionOperators.triggered.connect(lambda: self._operatorView.show())

        self._sourceView = SourceView(self._model, self._controller, self)
        self.actionSource.triggered.connect(lambda: self._sourceView.show())

        # Setup widgets
        self.spotDial.setMinimum(min(self._controller.presetSpotValues.keys()))
        self.spotDial.setMaximum(max(self._controller.presetSpotValues.keys()))
        self.spotSpinbox.setEnabled(False)
        self.alphaDial.setMinimum(min(self._controller.presetAlphaValues.keys()))
        self.alphaDial.setMaximum(max(self._controller.presetAlphaValues.keys()))
        self.alphaSpinbox.setEnabled(False)
        self.brightnessDial.setMinimum(min(self._controller.brightnessRange))
        self.brightnessDial.setMaximum(max(self._controller.brightnessRange))
        self.brightnessSpinbox.setEnabled(False)

        # Setup controls
        self.brightnessDial.valueChanged[int].connect(self._controller.setIntBrightness)
        #self.brightnessSpinbox.valueChanged[float].connect(self._controller.setFloatBrightness)
        self.spotDial.valueChanged[int].connect(self._controller.setIntSpot)
        self.spotSpinbox.valueChanged[float].connect(self._controller.setFloatSpot)
        self.alphaDial.valueChanged[int].connect(self._controller.setIntAlpha)
        self.alphaSpinbox.valueChanged[float].connect(self._controller.setFloatAlpha)

        # Setup listeners
        self._model.modelChanged.connect(self.plot_raytrace)
        self._model.CL1ValueChanged[float].connect(self.on_CL1_changed)
        self._model.CL3ValueChanged[float].connect(self.on_CL3_changed)
        self._model.CMValueChanged[float].connect(self.on_CM_changed)

    @pyqtSlot(float)
    def on_CL1_changed(self, value):
        if value > self.spotSpinbox.maximum():
            self.spotSpinbox.setMaximum(value)
        elif value < self.spotSpinbox.minimum():
            self.spotSpinbox.setMinimum(value)
        self.spotSpinbox.blockSignals(True)
        self.spotSpinbox.setValue(value)
        self.spotSpinbox.blockSignals(False)

        if value in self._controller.presetSpotValues.values():
            spots = [spot for spot in self._controller.presetSpotValues if
                     self._controller.presetSpotValues[spot] == value]
            if len(spots) > 0:
                spot = spots[0]
            else:
                spot = None
        else:
            spot = None

        if spot is not None:
            self.spotDial.setStyleSheet('background-color : lightgreen')
            self.spotDial.setValue(spot)
        else:
            self.spotDial.setStyleSheet('background-color : lightblue')

    @pyqtSlot(float)
    def on_CL3_changed(self, value):
        if value > self.brightnessSpinbox.maximum():
            self.brightnessSpinbox.setMaximum(value)
        elif value < self.brightnessSpinbox.minimum():
            self.brightnessSpinbox.setMinimum(value)
        self.brightnessSpinbox.blockSignals(True)
        self.brightnessSpinbox.setValue(value)
        self.brightnessSpinbox.blockSignals(False)

        if min(self._controller.brightnessRange) <= value <= max(self._controller.brightnessRange):
            self.brightnessDial.setStyleSheet('background-color : lightgreen')
            self.brightnessDial.setValue(int(value))
        else:
            self.brightnessDial.setStyleSheet('background-color : lightblue')

    @pyqtSlot(float)
    def on_CM_changed(self, value):
        if value > self.alphaSpinbox.maximum():
            self.alphaSpinbox.setMaximum(value)
        elif value < self.alphaSpinbox.minimum():
            self.alphaSpinbox.setMinimum(value)
        self.alphaSpinbox.blockSignals(True)
        self.alphaSpinbox.setValue(value)
        self.alphaSpinbox.blockSignals(False)

        if value in self._controller.presetAlphaValues.values():
            alphas = [alpha for alpha in self._controller.presetAlphaValues if
                      self._controller.presetAlphaValues[alpha] == value]
            if len(alphas) > 0:
                alpha = alphas[0]
            else:
                alpha = None
        else:
            alpha = None

        if alpha is not None:
            self.alphaDial.setStyleSheet('background-color : lightgreen')
            self.alphaDial.setValue(alpha)
        else:
            self.alphaDial.setStyleSheet('background-color : lightblue')

    def plot_raytrace(self):
        tic = time.time()
        print('Plotting raytrace...')
        self.plotWidget.canvas.ax.cla()
        raytraces = self._model.ray_trace
        [raytrace.show(ax=self.plotWidget.canvas.ax, annotate=False, operators=self._model.operators) for raytrace in
         raytraces]
        self.plotWidget.canvas.draw()
        toc = time.time()
        print(f'Finished plotting raytrace in {toc-tic:e}')


class OperatorView(QtWidgets.QMainWindow):
    zMin = -999.
    zMax = 999.
    zDecimals = 2
    zStep = 1.
    offsetMin = -999.
    offsetMax = 999.
    offsetDecimals = 2
    offsetStep = 1.
    valueMin = -999.
    valueMax = 999.
    valueDecimals = 2
    valueStep = 1.

    def __init__(self, model, controller, *args, **kwargs):
        super(OperatorView, self).__init__(*args, **kwargs)
        uic.loadUi(Path('./source/RayGui/OperatorControl.ui'), self)
        self.setWindowTitle('Operator controls')
        self._model = model
        self._controller = controller

        # Setup widgets
        [self.setupWidget(widget, self.zMin, self.zMax, val, self.zDecimals, self.zStep) for widget, val in [
            [self.CL1ZSpinbox, self._model.CL1_z],
            [self.CL2ZSpinbox, self._model.CL2_z],
            [self.CL3ZSpinbox, self._model.CL3_z],
            [self.CMZSpinbox, self._model.CM_z],
            [self.OLPreZSpinbox, self._model.OLPre_z],
            [self.OLPostZSpinbox, self._model.OLPost_z],
            [self.OMZSpinbox, self._model.OM_z],
            [self.IL1ZSpinbox, self._model.IL1_z],
            [self.IL2ZSpinbox, self._model.IL2_z],
            [self.IL3ZSpinbox, self._model.IL3_z],
            [self.PLZSpinbox, self._model.PL_z],
            [self.GUN1ZSpinbox, self._model.GUN1_z],
            [self.GUN2ZSpinbox, self._model.GUN2_z],
            [self.CLA1ZSpinbox, self._model.CLA1_z],
            [self.CLA2ZSpinbox, self._model.CLA2_z],
            [self.ILA1ZSpinbox, self._model.ILA1_z],
            [self.ILA2ZSpinbox, self._model.ILA2_z],
            [self.PLAZSpinbox, self._model.PLA_z]
        ]]

        [self.setupWidget(widget, self.offsetMin, self.offsetMax, val, self.offsetDecimals, self.offsetStep) for
         widget, val in [
             [self.CL1OffsetSpinbox, self._model.CL1_offset],
             [self.CL2OffsetSpinbox, self._model.CL2_offset],
             [self.CL3OffsetSpinbox, self._model.CL3_offset],
             [self.CMOffsetSpinbox, self._model.CM_offset],
             [self.OLPreOffsetSpinbox, self._model.OLPre_offset],
             [self.OLPostOffsetSpinbox, self._model.OLPost_offset],
             [self.OMOffsetSpinbox, self._model.OM_offset],
             [self.IL1OffsetSpinbox, self._model.IL1_offset],
             [self.IL2OffsetSpinbox, self._model.IL2_offset],
             [self.IL3OffsetSpinbox, self._model.IL3_offset],
             [self.PLOffsetSpinbox, self._model.PL_offset],
         ]]

        [self.setupWidget(widget, self.valueMin, self.valueMax, val, self.valueDecimals, self.valueStep) for widget, val
         in [
             [self.CL1ValueSpinbox, self._model.CL1_value],
             [self.CL2ValueSpinbox, self._model.CL2_value],
             [self.CL3ValueSpinbox, self._model.CL3_value],
             [self.CMValueSpinbox, self._model.CM_value],
             [self.OLPreValueSpinbox, self._model.OLPre_value],
             [self.OLPostValueSpinbox, self._model.OLPost_value],
             [self.OMValueSpinbox, self._model.OM_value],
             [self.IL1ValueSpinbox, self._model.IL1_value],
             [self.IL2ValueSpinbox, self._model.IL2_value],
             [self.IL3ValueSpinbox, self._model.IL3_value],
             [self.PLValueSpinbox, self._model.PL_value],
             [self.GUN1ValueSpinbox, self._model.GUN1_value],
             [self.GUN2ValueSpinbox, self._model.GUN2_value],
             [self.CLA1ValueSpinbox, self._model.CLA1_value],
             [self.CLA2ValueSpinbox, self._model.CLA2_value],
             [self.ILA1ValueSpinbox, self._model.ILA1_value],
             [self.ILA2ValueSpinbox, self._model.ILA2_value],
             [self.PLAValueSpinbox, self._model.PLA_value]
         ]]

        # Setup controllers
        self.CL1ZSpinbox.valueChanged.connect(lambda value: self._controller.setOperatorParameter('CL1', 'Z', value))
        self.CL2ZSpinbox.valueChanged.connect(lambda value: self._controller.setOperatorParameter('CL2', 'Z', value))
        self.CL3ZSpinbox.valueChanged.connect(lambda value: self._controller.setOperatorParameter('CL3', 'Z', value))
        self.CMZSpinbox.valueChanged.connect(lambda value: self._controller.setOperatorParameter('CM', 'Z', value))
        self.OLPreZSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('OLPre', 'Z', value))
        self.OLPostZSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('OLPost', 'Z', value))
        self.OMZSpinbox.valueChanged.connect(lambda value: self._controller.setOperatorParameter('OM', 'Z', value))
        self.IL1ZSpinbox.valueChanged.connect(lambda value: self._controller.setOperatorParameter('IL1', 'Z', value))
        self.IL2ZSpinbox.valueChanged.connect(lambda value: self._controller.setOperatorParameter('IL2', 'Z', value))
        self.IL3ZSpinbox.valueChanged.connect(lambda value: self._controller.setOperatorParameter('IL3', 'Z', value))
        self.PLZSpinbox.valueChanged.connect(lambda value: self._controller.setOperatorParameter('PL', 'Z', value))
        self.GUN1ZSpinbox.valueChanged.connect(lambda value: self._controller.setOperatorParameter('GUN1', 'Z', value))
        self.GUN2ZSpinbox.valueChanged.connect(lambda value: self._controller.setOperatorParameter('GUN2', 'Z', value))
        self.CLA1ZSpinbox.valueChanged.connect(lambda value: self._controller.setOperatorParameter('CLA1', 'Z', value))
        self.CLA2ZSpinbox.valueChanged.connect(lambda value: self._controller.setOperatorParameter('CLA2', 'Z', value))
        self.ILA1ZSpinbox.valueChanged.connect(lambda value: self._controller.setOperatorParameter('ILA1', 'Z', value))
        self.ILA2ZSpinbox.valueChanged.connect(lambda value: self._controller.setOperatorParameter('ILA2', 'Z', value))
        self.PLAZSpinbox.valueChanged.connect(lambda value: self._controller.setOperatorParameter('PLA', 'Z', value))

        # Offset
        self.CL1OffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('CL1', 'Offset', value))
        self.CL2OffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('CL2', 'Offset', value))
        self.CL3OffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('CL3', 'Offset', value))
        self.CMOffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('CM', 'Offset', value))
        self.OLPreOffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('OLPre', 'Offset', value))
        self.OLPostOffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('OLPost', 'Offset', value))
        self.OMOffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('OM', 'Offset', value))
        self.IL1OffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('IL1', 'Offset', value))
        self.IL2OffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('IL2', 'Offset', value))
        self.IL3OffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('IL3', 'Offset', value))
        self.PLOffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('PL', 'Offset', value))
        self.GUN1OffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('GUN1', 'Offset', value))
        self.GUN2OffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('GUN2', 'Offset', value))
        self.CLA1OffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('CLA1', 'Offset', value))
        self.CLA2OffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('CLA2', 'Offset', value))
        self.ILA1OffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('ILA1', 'Offset', value))
        self.ILA2OffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('ILA2', 'Offset', value))
        self.PLAOffsetSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('PLA', 'Offset', value))

        # Value
        self.CL1ValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('CL1', 'Value', value))
        self.CL2ValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('CL2', 'Value', value))
        self.CL3ValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('CL3', 'Value', value))
        self.CMValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('CM', 'Value', value))
        self.OLPreValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('OLPre', 'Value', value))
        self.OLPostValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('OLPost', 'Value', value))
        self.OMValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('OM', 'Value', value))
        self.IL1ValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('IL1', 'Value', value))
        self.IL2ValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('IL2', 'Value', value))
        self.IL3ValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('IL3', 'Value', value))
        self.PLValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('PL', 'Value', value))
        self.GUN1ValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('GUN1', 'Value', value))
        self.GUN2ValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('GUN2', 'Value', value))
        self.CLA1ValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('CLA1', 'Value', value))
        self.CLA2ValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('CLA2', 'Value', value))
        self.ILA1ValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('ILA1', 'Value', value))
        self.ILA2ValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('ILA2', 'Value', value))
        self.PLAValueSpinbox.valueChanged.connect(
            lambda value: self._controller.setOperatorParameter('PLA', 'Value', value))

        # Setup listeners
        # Z
        self._model.CL1ZChanged[float].connect(self.onCL1ZChanged)
        self._model.CL2ZChanged[float].connect(self.onCL2ZChanged)
        self._model.CL3ZChanged[float].connect(self.onCL3ZChanged)
        self._model.CMZChanged[float].connect(self.onCMZChanged)
        self._model.OLPreZChanged[float].connect(self.onOLPreZChanged)
        self._model.OLPostZChanged[float].connect(self.onOLPostZChanged)
        self._model.OMZChanged[float].connect(self.onOMZChanged)
        self._model.IL1ZChanged[float].connect(self.onIL1ZChanged)
        self._model.IL2ZChanged[float].connect(self.onIL2ZChanged)
        self._model.IL3ZChanged[float].connect(self.onIL3ZChanged)
        self._model.PLZChanged[float].connect(self.onPLZChanged)
        self._model.GUN1ZChanged[float].connect(self.onGUN1ZChanged)
        self._model.GUN2ZChanged[float].connect(self.onGUN2ZChanged)
        self._model.CLA1ZChanged[float].connect(self.onCLA1ZChanged)
        self._model.CLA2ZChanged[float].connect(self.onCLA2ZChanged)
        self._model.ILA1ZChanged[float].connect(self.onILA1ZChanged)
        self._model.ILA2ZChanged[float].connect(self.onILA2ZChanged)
        self._model.PLAZChanged[float].connect(self.onPLAZChanged)

        # Offset
        self._model.CL1OffsetChanged[float].connect(self.onCL1OffsetChanged)
        self._model.CL2OffsetChanged[float].connect(self.onCL2OffsetChanged)
        self._model.CL3OffsetChanged[float].connect(self.onCL3OffsetChanged)
        self._model.CMOffsetChanged[float].connect(self.onCMOffsetChanged)
        self._model.OLPreOffsetChanged[float].connect(self.onOLPreOffsetChanged)
        self._model.OLPostOffsetChanged[float].connect(self.onOLPostOffsetChanged)
        self._model.OMOffsetChanged[float].connect(self.onOMOffsetChanged)
        self._model.IL1OffsetChanged[float].connect(self.onIL1OffsetChanged)
        self._model.IL2OffsetChanged[float].connect(self.onIL2OffsetChanged)
        self._model.IL3OffsetChanged[float].connect(self.onIL3OffsetChanged)
        self._model.PLOffsetChanged[float].connect(self.onPLOffsetChanged)

        # Value
        self._model.CL1ValueChanged[float].connect(self.onCL1ValueChanged)
        self._model.CL2ValueChanged[float].connect(self.onCL2ValueChanged)
        self._model.CL3ValueChanged[float].connect(self.onCL3ValueChanged)
        self._model.CMValueChanged[float].connect(self.onCMValueChanged)
        self._model.OLPreValueChanged[float].connect(self.onOLPreValueChanged)
        self._model.OLPostValueChanged[float].connect(self.onOLPostValueChanged)
        self._model.OMValueChanged[float].connect(self.onOMValueChanged)
        self._model.IL1ValueChanged[float].connect(self.onIL1ValueChanged)
        self._model.IL2ValueChanged[float].connect(self.onIL2ValueChanged)
        self._model.IL3ValueChanged[float].connect(self.onIL3ValueChanged)
        self._model.PLValueChanged[float].connect(self.onPLValueChanged)
        self._model.GUN1ValueChanged[float].connect(self.onGUN1ValueChanged)
        self._model.GUN2ValueChanged[float].connect(self.onGUN2ValueChanged)
        self._model.CLA1ValueChanged[float].connect(self.onCLA1ValueChanged)
        self._model.CLA2ValueChanged[float].connect(self.onCLA2ValueChanged)
        self._model.ILA1ValueChanged[float].connect(self.onILA1ValueChanged)
        self._model.ILA2ValueChanged[float].connect(self.onILA2ValueChanged)
        self._model.PLAValueChanged[float].connect(self.onPLAValueChanged)

        # Toggle
        self._model.CL1Toggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.CL2Toggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.CL3Toggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.CMToggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.OLPreToggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.OLPostToggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.OMToggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.IL1Toggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.IL2Toggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.IL3Toggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.PLToggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.GUN1Toggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.GUN2Toggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.CLA1Toggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.CLA2Toggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.ILA1Toggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.ILA2Toggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))
        self._model.PLAToggled.connect(lambda state: self.onOperatorToggled(state, self.CL1Button))

    @pyqtSlot(float)
    def onCL1ZChanged(self, value):
        self.CL1ZSpinbox.blockSignals(True)
        self.CL1ZSpinbox.setValue(value)
        self.CL1ZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onCL1OffsetChanged(self, value):
        self.CL1OffsetSpinbox.blockSignals(True)
        self.CL1OffsetSpinbox.setValue(value)
        self.CL1OffsetSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onCL1ValueChanged(self, value):
        self.CL1ValueSpinbox.blockSignals(True)
        self.CL1ValueSpinbox.setValue(value)
        self.CL1ValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onCL2ZChanged(self, value):
        self.CL2ZSpinbox.blockSignals(True)
        self.CL2ZSpinbox.setValue(value)
        self.CL2ZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onCL2OffsetChanged(self, value):
        self.CL2OffsetSpinbox.blockSignals(True)
        self.CL2OffsetSpinbox.setValue(value)
        self.CL2OffsetSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onCL2ValueChanged(self, value):
        self.CL2ValueSpinbox.blockSignals(True)
        self.CL2ValueSpinbox.setValue(value)
        self.CL2ValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onCL3ZChanged(self, value):
        self.CL3ZSpinbox.blockSignals(True)
        self.CL3ZSpinbox.setValue(value)
        self.CL3ZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onCL3OffsetChanged(self, value):
        self.CL3OffsetSpinbox.blockSignals(True)
        self.CL3OffsetSpinbox.setValue(value)
        self.CL3OffsetSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onCL3ValueChanged(self, value):
        self.CL3ValueSpinbox.blockSignals(True)
        self.CL3ValueSpinbox.setValue(value)
        self.CL3ValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onCMZChanged(self, value):
        self.CMZSpinbox.blockSignals(True)
        self.CMZSpinbox.setValue(value)
        self.CMZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onCMOffsetChanged(self, value):
        self.CMOffsetSpinbox.blockSignals(True)
        self.CMOffsetSpinbox.setValue(value)
        self.CMOffsetSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onCMValueChanged(self, value):
        self.CMValueSpinbox.blockSignals(True)
        self.CMValueSpinbox.setValue(value)
        self.CMValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onOLPreZChanged(self, value):
        self.OLPreZSpinbox.blockSignals(True)
        self.OLPreZSpinbox.setValue(value)
        self.OLPreZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onOLPreOffsetChanged(self, value):
        self.OLPreOffsetSpinbox.blockSignals(True)
        self.OLPreOffsetSpinbox.setValue(value)
        self.OLPreOffsetSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onOLPreValueChanged(self, value):
        self.OLPreValueSpinbox.blockSignals(True)
        self.OLPreValueSpinbox.setValue(value)
        self.OLPreValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onOLPostZChanged(self, value):
        self.OLPostZSpinbox.blockSignals(True)
        self.OLPostZSpinbox.setValue(value)
        self.OLPostZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onOLPostOffsetChanged(self, value):
        self.OLPostOffsetSpinbox.blockSignals(True)
        self.OLPostOffsetSpinbox.setValue(value)
        self.OLPostOffsetSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onOLPostValueChanged(self, value):
        self.OLPostValueSpinbox.blockSignals(True)
        self.OLPostValueSpinbox.setValue(value)
        self.OLPostValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onOMZChanged(self, value):
        self.OMZSpinbox.blockSignals(True)
        self.OMZSpinbox.setValue(value)
        self.OMZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onOMOffsetChanged(self, value):
        self.OMOffsetSpinbox.blockSignals(True)
        self.OMOffsetSpinbox.setValue(value)
        self.OMOffsetSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onOMValueChanged(self, value):
        self.OMValueSpinbox.blockSignals(True)
        self.OMValueSpinbox.setValue(value)
        self.OMValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onIL1ZChanged(self, value):
        self.IL1ZSpinbox.blockSignals(True)
        self.IL1ZSpinbox.setValue(value)
        self.IL1ZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onIL1OffsetChanged(self, value):
        self.IL1OffsetSpinbox.blockSignals(True)
        self.IL1OffsetSpinbox.setValue(value)
        self.IL1OffsetSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onIL1ValueChanged(self, value):
        self.IL1ValueSpinbox.blockSignals(True)
        self.IL1ValueSpinbox.setValue(value)
        self.IL1ValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onIL2ZChanged(self, value):
        self.IL2ZSpinbox.blockSignals(True)
        self.IL2ZSpinbox.setValue(value)
        self.IL2ZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onIL2OffsetChanged(self, value):
        self.IL2OffsetSpinbox.blockSignals(True)
        self.IL2OffsetSpinbox.setValue(value)
        self.IL2OffsetSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onIL2ValueChanged(self, value):
        self.IL2ValueSpinbox.blockSignals(True)
        self.IL2ValueSpinbox.setValue(value)
        self.IL2ValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onIL3ZChanged(self, value):
        self.IL3ZSpinbox.blockSignals(True)
        self.IL3ZSpinbox.setValue(value)
        self.IL3ZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onIL3OffsetChanged(self, value):
        self.IL3OffsetSpinbox.blockSignals(True)
        self.IL3OffsetSpinbox.setValue(value)
        self.IL3OffsetSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onIL3ValueChanged(self, value):
        self.IL3ValueSpinbox.blockSignals(True)
        self.IL3ValueSpinbox.setValue(value)
        self.IL3ValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onPLZChanged(self, value):
        self.PLZSpinbox.blockSignals(True)
        self.PLZSpinbox.setValue(value)
        self.PLZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onPLOffsetChanged(self, value):
        self.PLOffsetSpinbox.blockSignals(True)
        self.PLOffsetSpinbox.setValue(value)
        self.PLOffsetSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onPLValueChanged(self, value):
        self.PLValueSpinbox.blockSignals(True)
        self.PLValueSpinbox.setValue(value)
        self.PLValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onGUN1ZChanged(self, value):
        self.GUN1ZSpinbox.blockSignals(True)
        self.GUN1ZSpinbox.setValue(value)
        self.GUN1ZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onGUN1ValueChanged(self, value):
        self.GUN1ValueSpinbox.blockSignals(True)
        self.GUN1ValueSpinbox.setValue(value)
        self.GUN1ValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onGUN2ZChanged(self, value):
        self.GUN2ZSpinbox.blockSignals(True)
        self.GUN2ZSpinbox.setValue(value)
        self.GUN2ZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onGUN2ValueChanged(self, value):
        self.GUN2ValueSpinbox.blockSignals(True)
        self.GUN2ValueSpinbox.setValue(value)
        self.GUN2ValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onCLA1ZChanged(self, value):
        self.CLA1ZSpinbox.blockSignals(True)
        self.CLA1ZSpinbox.setValue(value)
        self.CLA1ZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onCLA1ValueChanged(self, value):
        self.CLA1ValueSpinbox.blockSignals(True)
        self.CLA1ValueSpinbox.setValue(value)
        self.CLA1ValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onCLA2ZChanged(self, value):
        self.CLA2ZSpinbox.blockSignals(True)
        self.CLA2ZSpinbox.setValue(value)
        self.CLA2ZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onCLA2ValueChanged(self, value):
        self.CLA2ValueSpinbox.blockSignals(True)
        self.CLA2ValueSpinbox.setValue(value)
        self.CLA2ValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onILA1ZChanged(self, value):
        self.ILA1ZSpinbox.blockSignals(True)
        self.ILA1ZSpinbox.setValue(value)
        self.ILA1ZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onILA1ValueChanged(self, value):
        self.ILA1ValueSpinbox.blockSignals(True)
        self.ILA1ValueSpinbox.setValue(value)
        self.ILA1ValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onILA2ZChanged(self, value):
        self.ILA2ZSpinbox.blockSignals(True)
        self.ILA2ZSpinbox.setValue(value)
        self.ILA2ZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onILA2ValueChanged(self, value):
        self.ILA2ValueSpinbox.blockSignals(True)
        self.ILA2ValueSpinbox.setValue(value)
        self.ILA2ValueSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onPLAZChanged(self, value):
        self.PLAZSpinbox.blockSignals(True)
        self.PLAZSpinbox.setValue(value)
        self.PLAZSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def onPLAValueChanged(self, value):
        self.PLAValueSpinbox.blockSignals(True)
        self.PLAValueSpinbox.setValue(value)
        self.PLAValueSpinbox.blockSignals(False)


    @pyqtSlot(QtWidgets.QPushButton)
    def changeColor(self, button):
        if button.isChecked():
            button.setStyleSheet('background-color : lightblue')
        else:
            button.setStyleSheet('bacground-color : lightgrey')

    @pyqtSlot(bool, QtWidgets.QPushButton)
    def onOperatorToggled(self, state, button):
        button.setChecked(state)
        if button.isChecked():
            button.setStyleSheet('background-color : lightblue')
        else:
            button.setStyleSheet('bacground-color : lightgrey')

    def setupWidget(self, widget, *args, **kwargs):
        """
        Setup widget parameters

        To setup a QDoubleSpinbox, supply the `min`, `max`, `value`, `decimals`, and `singleStep` as optional positional arguments, or as keyword arguments `minval`=`min` `maxval`=`max`, `value`=`value`, `decimals`=`decimals`, `step`=`singleStep`.

        :param widget: The widget to setup - should be a member of self
        :param args: Optional positional arguments
        :param kwargs: Optional keyword arguments
        :return: None
        :type widget: Union[QtWidgets.QDoubleSpinBox]
        """
        if isinstance(widget, QtWidgets.QDoubleSpinBox):
            try:
                minval = args[0]
            except IndexError:
                minval = kwargs.get('minval', -999.)
            finally:
                if not isinstance(minval, float):
                    raise TypeError(
                        f'Cannot setup widget {widget}: minval {minval!r} has invalid type {type(minval)}. Allowed types are {float}')

            try:
                maxval = args[1]
            except IndexError:
                maxval = kwargs.get('maxval', 999.)
            finally:
                if not isinstance(maxval, float):
                    raise TypeError(
                        f'Cannot setup widget {widget}: maxval {maxval!r} has invalid type {type(maxval)}. Allowed types are {float}')

            if maxval < minval:
                raise ValueError(
                    f'Cannot setup widget {widget}: Minimum value {minval} cannot be larger than maxval {maxval}')

            try:
                value = args[2]
            except IndexError:
                value = kwargs.get('value', minval)
            finally:
                if not minval <= value <= maxval:
                    raise ValueError(
                        f'Cannot setup widget {widget}: Value {value} lies outside widget range [{minval}, {maxval}].')

            try:
                decimals = args[3]
            except IndexError:
                decimals = kwargs.get('decimals', 2)
            finally:
                if not isinstance(decimals, int):
                    raise TypeError(
                        f'Cannot setup widget {widget}: decimals {decimals!r} has invalid type {type(decimals)}. Allowed types are {int}')
                if decimals < 0:
                    raise ValueError(f'Cannot setup widget {widget}: decimals {decimals!r} must be larger than 0')

            try:
                step = args[4]
            except IndexError:
                step = kwargs.get('step', 1.)
            finally:
                if not isinstance(step, float):
                    raise TypeError(
                        f'Cannot setup widget {widget}: step {step!r} has invalid type {type(step)}. Allowed types are {float}')
                if step < 0:
                    raise ValueError(f'Cannot setup widget {widget}: step {step!r} must be larger than 0.')

            widget.setMinimum(minval)
            widget.setMaximum(maxval)
            widget.setDecimals(decimals)
            widget.setSingleStep(step)
            widget.setValue(value)
        elif isinstance(widget, QtWidgets.QLabel):
            try:
                text = args[0]
            except IndexError:
                text = kwargs.get('text', 'TextLabel')
            finally:
                text = str(text)
            widget.setText(text)


class SourceView(QtWidgets.QMainWindow):
    z_min = -999.
    z_max = 999.
    z_decimals = 2
    z_step = 1.

    offset_min = -999.
    offset_max = 999.
    offset_decimals = 2
    offset_step = 1.

    size_min = 0.
    size_max = offset_max * 2
    size_decimals = 2
    size_step = 1.

    angle_min = -180.
    angle_max = 180
    angle_decimals = 2
    angle_step = 1.

    def __init__(self, model, controller, *args, **kwargs):
        super(SourceView, self).__init__(*args, **kwargs)
        uic.loadUi(Path('./source/RayGui/sourceControl.ui'), self)
        if not isinstance(model, MicroscopeModel):
            raise TypeError(f'Cannot create {self.__class__.__name__} for model {model}: Invalid type {type(model)}')
        if not isinstance(controller, MicroscopeController):
            raise TypeError(
                f'Cannot create {self.__class__.__name__} for controller {controller}: Invalid type {type(controller)}')
        self._model = model
        self._controller = controller
        self.angles_dict = {}

        # Setup widgets
        self.sourceZSpinbox.setMinimum(self.z_min)
        self.sourceZSpinbox.setMaximum(self.z_max)
        self.sourceZSpinbox.setDecimals(self.z_decimals)
        self.sourceZSpinbox.setSingleStep(self.z_decimals)
        self.sourceZSpinbox.setValue(self._model.source_z)

        self.sourceOffsetSpinbox.setMinimum(self.offset_min)
        self.sourceOffsetSpinbox.setMaximum(self.offset_max)
        self.sourceOffsetSpinbox.setDecimals(self.offset_decimals)
        self.sourceOffsetSpinbox.setSingleStep(self.offset_decimals)
        self.sourceOffsetSpinbox.setValue(self._model.source_offset)

        self.sourceSizeSpinbox.setMinimum(self.size_min)
        self.sourceSizeSpinbox.setMaximum(self.size_max)
        self.sourceSizeSpinbox.setDecimals(self.size_decimals)
        self.sourceSizeSpinbox.setSingleStep(self.size_decimals)
        self.sourceSizeSpinbox.setValue(self._model.source_size)

        self.sourceAnglesWidget.setLayout(QtWidgets.QHBoxLayout())

        # Setup signals
        self.sourceZSpinbox.valueChanged.connect(self._controller.setSourceZ)
        self.sourceSizeSpinbox.valueChanged.connect(self._controller.setSourceSize)
        self.sourceOffsetSpinbox.valueChanged.connect(self._controller.setSourceOffset)
        self.sourceAddAngleButton.clicked.connect(lambda: self._controller.addAngle(0))
        self.sourceRemoveAngleButton.clicked.connect(lambda: self._controller.removeAngle())
        self.sourceRemoveAngleButton.setEnabled(False)

        # listen for model changes
        self._model.sourceZChanged[float].connect(self.on_z_changed)
        self._model.sourceOffsetChanged[float].connect(self.on_offset_changed)
        self._model.sourceSizeChanged[float].connect(self.on_size_changed)
        self._model.sourceAngleAdded.connect(self.on_angle_added)
        self._model.sourceAngleRemoved.connect(self.on_angle_removed)
        self._model.sourceAnglesChanged[list].connect(self.on_angles_changed)

    @pyqtSlot(float)
    def on_z_changed(self, value):
        self.sourceZSpinbox.setValue(value)

    @pyqtSlot(float)
    def on_offset_changed(self, value):
        self.sourceOffsetSpinbox.setValue(value)

    @pyqtSlot(float)
    def on_size_changed(self, value):
        self.sourceSizeSpinbox.setValue(value)

    @pyqtSlot(list)
    def on_angles_changed(self, angles):
        for index, angle in enumerate(angles):
            value = angle * 180. / np.pi
            spinbox = self.sourceAnglesWidget.layout().itemAt(index).widget()
            print(f'Setting angle number {index} to {value}. Old spinbox value: {spinbox.value()}:')
            spinbox.setValue(value)
            print(f'\tFinished setting angle to {spinbox.value()}')

    @pyqtSlot()
    def on_angle_added(self):
        spinbox = QtWidgets.QDoubleSpinBox()
        self.sourceAnglesWidget.layout().addWidget(spinbox)
        self.angles_dict[self.sourceAnglesWidget.layout().count()] = spinbox

        spinbox.setMinimum(self.angle_min)
        spinbox.setMaximum(self.angle_max)
        spinbox.setValue(0)
        spinbox.setDecimals(self.angle_decimals)
        spinbox.setSingleStep(self.angle_step)

        row = self.sourceAnglesWidget.layout().count() - 1
        spinbox.valueChanged.connect(
            lambda angle: self._controller.setAngle(row, angle * np.pi / 180.))

        self.sourceRemoveAngleButton.setEnabled(True)

    @pyqtSlot()
    def on_angle_removed(self):
        n = self.sourceAnglesWidget.layout().count()
        widget = self.angles_dict.pop(n)
        widget.deleteLater()
        if n <= 1:
            self.sourceRemoveAngleButton.setEnabled(False)


class MicroscopeController(QtCore.QObject):
    presetAlphaValues = dict([[i + 1, (i + 1) ** 2] for i in range(5)])
    presetSpotValues = dict([[i + 1, (i + 1) ** 2] for i in range(5)])
    brightnessRange = (5, 30)

    def __init__(self, model, *args, **kwargs):
        super(MicroscopeController, self).__init__(*args, **kwargs)
        if not isinstance(model, MicroscopeModel):
            raise TypeError(f'Cannot create {self.__class__.__name__} for {model!r}: Invalid type {type(model)}')
        self._model = model

    def __repr__(self):
        return f'{self.__class__.__name__}({self._model!r}, {self.parent()})'

    @pyqtSlot(float)
    def setSourceZ(self, value):
        if value >= self._model.CL1_z:
            self._model.source_z = value
        else:
            pass

    @pyqtSlot(float)
    def setSourceOffset(self, value):
        self._model.source_offset = value

    @pyqtSlot(float)
    def setSourceSize(self, value):
        self._model.source_size = value

    @pyqtSlot(float)
    def setScreenZ(self, value):
        if value <= self._model.PL_z:
            self._model.screen_z = value
        else:
            pass

    @pyqtSlot(int, float)
    def setAngle(self, index, value):
        copy = self._model.source_angles
        copy[index] = value
        self._model.source_angles = copy

    @pyqtSlot()
    def addAngle(self):
        print('Controller adding angle')
        self._model.add_angle(0.0)

    @pyqtSlot(float)
    def addAngle(self, value):
        print('Controller adding angle')
        self._model.add_angle(value)

    @pyqtSlot()
    def removeAngle(self):
        self._model.remove_angle()

    @pyqtSlot(float, name='setBrightness')
    def setFloatBrightness(self, value):
        self._model.CL3_value = value

    @pyqtSlot(int, name='setBrightness')
    def setIntBrightness(self, value):
        if min(self.brightnessRange) <= value <= max(self.brightnessRange):
            self._model.CL3_value = value
        else:
            warn(
                f'Brightness value {value} lies outside predefined brightness values {self.brightnessRange}. Will not change CL3 value.')

    @pyqtSlot(float, name='setSpot')
    def setFloatSpot(self, value):
        if isinstance(value, float):
            self._model.CL1_value = value

    @pyqtSlot(int, name='setSpot')
    def setIntSpot(self, value):
        lens_value = self.presetSpotValues.get(value, None)
        if lens_value is None:
            warn(
                f'Spot {value} is not recognized among preset spot values {self.presetSpotValues}. Will not change CL1 value')
        else:
            self._model.CL1_value = lens_value

    @pyqtSlot(float, name='setAlpha')
    def setFloatAlpha(self, value):
        self._model.CM_value = value

    @pyqtSlot(int, name='setAlpha')
    def setIntAlpha(self, value):
        lens_value = self.presetAlphaValues.get(value, None)
        if lens_value is None:
            warn(
                f'Alpha {value} is not recognized among preset alpha values {self.presetAlphaValues}. Will not change CM value')
        else:
            self._model.CM_value = lens_value

    @pyqtSlot(float)
    def setFocus(self, value):
        self._model.OLPre_value = value
        self._model.OLPost_value = value

    @pyqtSlot(float)
    def setDiffFocus(self, value):
        self._model.IL1_value = value

    @pyqtSlot(float)
    def BeamShift(self, value):
        old_CLA1 = self._model.CLA1_value
        old_CLA2 = self._model.CLA2_value
        old_shift_value = self._model.beam_shift

        # FCalculate base values for deflectors
        old_CLA1_base = old_CLA1 - old_shift_value
        old_CLA2_base = old_CLA2 - old_shift_value * self._model.beam_compensator_shift

        self._model.CLA1_value = old_CLA1_base + value
        self._model.CLA2_value = old_CLA2_base + value * self._model.beam_compensator_shift
        self._model.beam_shift = value

    @pyqtSlot(float)
    def beamTilt(self, value):
        old_CLA1 = self._model.CLA1_value
        old_CLA2 = self._model.CLA2_value
        old_tilt_value = self._model.beam_tilt
        old_CLA1_base = old_CLA1 - old_tilt_value
        old_CLA2_base = old_CLA2 - old_tilt_value * self._model.beam_compensator_tilt

        self._model.CLA1_value = old_CLA1_base + value
        self._model.CLA2_value = old_CLA2_base + value * self._model.beam_compensator_tilt
        self._model.beam_tilt = value

    @pyqtSlot(float)
    def ImageShift(self, value):
        old_ILA1 = self._model.ILA1_value
        old_ILA2 = self._model.ILA2_value
        old_shift_value = self._model.image_shift
        old_ILA1_base = old_ILA1 - old_shift_value
        old_ILA2_base = old_ILA2 - old_shift_value * self._model.image_compensator_shift

        self._model.ILA1_value = old_ILA1_base + value
        self._model.ILA2_value = old_ILA2_base + value * self._model.image_compensator_shift
        self._model.image_shift = value

    @pyqtSlot(float)
    def imageTilt(self, value):
        old_ILA1 = self._model.ILA1_value
        old_ILA2 = self._model.ILA2_value
        old_tilt_value = self._model.image_tilt
        old_ILA1_base = old_ILA1 - old_tilt_value
        old_ILA2_base = old_ILA2 - old_tilt_value * self._model.image_compensator_tilt

        self._model.ILA1_value = old_ILA1_base + value
        self._model.ILA2_value = old_ILA2_base + value * self._model.image_compensator_tilt
        self._model.image_tilt = value

    @pyqtSlot(str, str, float)
    def setOperatorParameter(self, name, parameter, value):
        parameter = parameter.lower()
        if name == 'CL1':
            if parameter == 'z':
                if self._model.CL2_z <= value <= self._model.source_z:
                    self._model.CL1_z = value
                else:
                    warn(f'Cannot set {name} z-position above/below bounding operators')
            elif parameter == 'offset':
                self._model.CL1_offset = value
            elif parameter == 'value':
                self._model.CL1_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'CL2':
            if parameter == 'z':
                if self._model.CL3_z <= self._model.CL1_z:
                    self._model.CL2_z = value
                else:
                    warn(f'Cannot set {name} z-position above/below bounding operators')
            elif parameter == 'offset':
                self._model.CL2_offset = value
            elif parameter == 'value':
                self._model.CL2_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'CL3':
            if parameter == 'z':
                if self._model.CM_z <= value <= self._model.CL2_z:
                    self._model.CL3_z = value
                else:
                    warn(f'Cannot set {name} z-position above/below bounding operators')
            elif parameter == 'offset':
                self._model.CL3_offset = value
            elif parameter == 'value':
                self._model.CL3_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'CM':
            if parameter == 'z':
                if self._model.OLPre_z <= value <= self._model.CL3_z:
                    self._model.CM_z = value
                else:
                    warn(f'Cannot set {name} z-position above/below bounding operators')
            elif parameter == 'offset':
                self._model.CM_offset = value
            elif parameter == 'value':
                self._model.CM_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'OLPre':
            if parameter == 'z':
                if self._model.OLpost_z <= value <= self._model.CM_z:
                    self._model.OLPre_z = value
                else:
                    warn(f'Cannot set {name} z-position above/below bounding operators')
            elif parameter == 'offset':
                self._model.OLPre_offset = value
            elif parameter == 'value':
                self._model.OLPre_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'OLPost':
            if parameter == 'z':
                if self._model.OM_z <= value <= self._model.OLPre_z:
                    self._model.OLPost_z = value
                else:
                    warn(f'Cannot set {name} z-position above/below bounding operators')
            elif parameter == 'offset':
                self._model.OLPost_offset = value
            elif parameter == 'value':
                self._model.OLPost_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'OM':
            if parameter == 'z':
                if self._model.IL1_z <= value <= self._model.OLPost_z:
                    self._model.OM_z = value
                else:
                    warn(f'Cannot set {name} z-position above/below bounding operators')
            elif parameter == 'offset':
                self._model.OM_offset = value
            elif parameter == 'value':
                self._model.OM_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'IL1':
            if parameter == 'z':
                if self._model.IL2_z <= value <= self._model.OM_z:
                    self._model.IL1_z = value
                else:
                    warn(f'Cannot set {name} z-position above/below bounding operators')
            elif parameter == 'offset':
                self._model.IL1_offset = value
            elif parameter == 'value':
                self._model.IL1_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'IL2':
            if parameter == 'z':
                if self._model.IL3_z <= value <= self._model.IL1_z:
                    self._model.IL2_z = value
                else:
                    warn(f'Cannot set {name} z-position above/below bounding operators')
            elif parameter == 'offset':
                self._model.IL2_offset = value
            elif parameter == 'value':
                self._model.IL2_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'IL3':
            if parameter == 'z':
                if self._model.PL_z <= value <= self._model.IL2_z:
                    self._model.IL3_z = value
                else:
                    warn(f'Cannot set {name} z-position above/below bounding operators')
            elif parameter == 'offset':
                self._model.IL3_offset = value
            elif parameter == 'value':
                self._model.IL3_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'PL':
            if parameter == 'z':
                if self._model.screen_z <= value <= self._model.IL3_z:
                    self._model.PL_z = value
                else:
                    warn(f'Cannot set {name} z-position above/below bounding operators')
            elif parameter == 'offset':
                self._model.PL_offset = value
            elif parameter == 'value':
                self._model.PL_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'PLA':
            if parameter == 'z':
                self._model.PLA_z = value
            elif parameter == 'offset':
                self._model.PLA_offset = value
            elif parameter == 'value':
                self._model.PLA_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'GUN1':
            if parameter == 'z':
                self._model.GUN1_z = value
            elif parameter == 'value':
                self._model.GUN1_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'GUN2':
            if parameter == 'z':
                self._model.GUN2_z = value
            elif parameter == 'value':
                self._model.GUN2_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'CLA1':
            if parameter == 'z':
                self._model.CLA1_z = value
            elif parameter == 'value':
                self._model.CLA1_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'CLA2':
            if parameter == 'z':
                self._model.CLA2_z = value
            elif parameter == 'value':
                self._model.CLA2_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'ILA1':
            if parameter == 'z':
                self._model.ILA1_z = value
            elif parameter == 'value':
                self._model.ILA1_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'ILA2':
            if parameter == 'z':
                self._model.ILA2_z = value
            elif parameter == 'value':
                self._model.ILA2_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        elif name == 'PLA':
            if parameter == 'z':
                self._model.PLA_z = value
            elif parameter == 'value':
                self._model.PLA_value = value
            else:
                raise ValueError(
                    f'Cannot change parameter {parameter} of {name} to {value}: Parameter is not recognized.')
        else:
            raise ValueError(f'Cannot change parameter {parameter} of {name}  to {value}: Name is not recognized.')


def main():
    mygui = QtWidgets.QApplication(sys.argv)

    model = MicroscopeModel()
    controller = MicroscopeController(model)
    main_window = MicroscopeView(model, controller)
    main_window.show()

    # operator_window = OperatorView(model, controller)
    # operator_window.show()

    sys.exit(mygui.exec_())


if __name__ == '__main__':
    main()
