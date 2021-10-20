from PyQt5 import QtWidgets, QtGui, QtCore, Qt, uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from WaveOptics.gui.mplwidget import *
from WaveOptics.RayTracing import *
from tabulate import tabulate
from pathlib import Path
from matplotlib.lines import lineStyles
from matplotlib.colors import to_hex, to_rgb
import sys
import time


class Error(Exception):
    pass


class OperatorModelError(Error):
    pass


class OpticalOperatorModel(QtCore.QObject):
    """
    Model for controlling an OpticalOperator

    The model should ensure that proper signals are sent whenever the data of the OpticalOperator has been changed.

    The model emits the following signals:
    :param valueChanged: Signal ([], [float]) emitted whenever the value of the OpticalOperator has changed.
    :param zChanged: Signal ([], [float]) emitted whenever the z-value of the OpticalOperator has changed.
    :param offsetChanged: Signal ([], [float]) emitted whenever the offset-value of the OpticalOperator has changed.
    :param labelChanged: Signal([], [float]) emitted whenever the label of the OpticalOperator has changed.
    :param operatorChanged: Signal wmitted whenever any change has been made to the OpticalOperator, inculding the above.
    """
    valueChanged = pyqtSignal([], [float], name='valueChanged')
    zChanged = pyqtSignal([], [float], name='zChanged')
    offsetChanged = pyqtSignal([], [float], name='offsetChanged')
    labelChanged = pyqtSignal([], [str], name='labelChanged')
    operatorChanged = pyqtSignal(name='operatorChanged')
    styleChanged = pyqtSignal([dict], name='styleChanged')

    @property
    def z(self):
        return self._operator.z

    @z.setter
    def z(self, value):
        if isinstance(value, float):
            self._operator.z = value
            self.zChanged.emit()
            self.zChanged[float].emit(value)
            self.operatorChanged.emit()
        else:
            raise OperatorModelError(
                f'Cannot set Z-value of {self.__class__.__name__} of {self._operator!r}.') from TypeError(
                f'Value {value!r} must be `float`')

    @property
    def offset(self):
        return self._operator.offset

    @offset.setter
    def offset(self, value):
        if isinstance(value, float):
            self._operator.offset = value
            self.offsetChanged.emit()
            self.offsetChanged[float].emit(value)
            self.operatorChanged.emit()
        else:
            raise OperatorModelError(
                f'Cannot set offset-value of {self.__class__.__name__} of {self._operator!r}.') from TypeError(
                f'Value {value!r} must be `float`')

    @property
    def value(self):
        return self._operator.value

    @value.setter
    def value(self, value):
        if isinstance(value, float):
            self._operator.value = value
            self.valueChanged.emit()
            self.valueChanged[float].emit(value)
            self.operatorChanged.emit()
        else:
            raise OperatorModelError(
                f'Cannot set operator-value of {self.__class__.__name__} of {self._operator!r}.') from TypeError(
                f'Value {value!r} must be `float`')

    @property
    def label(self):
        return self._operator.label

    @label.setter
    def label(self, value):
        if isinstance(value, str):
            self._operator.label = value
            self.labelChanged.emit()
            self.labelChanged[str].emit(value)
            self.operatorChanged.emit()
        else:
            raise OperatorModelError(
                f'Cannot set label-value of {self.__class__.__name__} of {self._operator!r}.') from TypeError(
                f'Value {value!r} must be `str`')

    @property
    def silent(self):
        return self._silent

    @silent.setter
    def silent(self, value):
        self._silent = bool(value)
        self.blockSignals(self._silent)

    @property
    def operator_type(self):
        return type(self._operator)

    @property
    def operator_classname(self):
        return self._operator.__class__.__name__

    @property
    def is_deflector(self):
        return isinstance(self._operator, Deflector)

    @property
    def is_lens(self):
        return isinstance(self._operator, Lens)

    @property
    def is_propagator(self):
        return isinstance(self._operator, Propagator)

    @property
    def style(self):
        return dict(self._style)

    @property
    def focal_style(self):
        if self.is_lens:
            return dict(self._focal_style)
        else:
            return dict()  # raise AttributeError(f'Cannot get focal_style for {self}. Operator {self._operator!r} is not a lens')

    def __init__(self, operator, *args, **kwargs):
        """
        Create a model for an OpticalOperator

        :param operator: The OpticalOperator to model
        :param args: Optional positional arguments passed to QtCore.QObject constructor
        :param kwargs: Optional keyword arguments passed to QtCore.QObject constructor
        :type operator: OpticalOperator
        """
        super(OpticalOperatorModel, self).__init__(*args, **kwargs)

        if not isinstance(operator, OpticalOperator):
            raise TypeError(
                f'Cannot create {self.__class__.__name__} for {operator!r}. Invalid type {type(operator)}. Accepted types are OpticalOperator and subclasses.')
        self._operator = operator
        self._silent = False
        self._style = dict([['ls', '-'], ['alpha', 1.], ['color', 'k'], ['lw', 1.]])
        self._focal_style = dict([['ls', '--'], ['alpha', 0.5], ['color', 'k'], ['lw', 0.5]])

    def __repr__(self):
        return f'{self.__class__.__name__}({self._operator!r}, {self.parent()})'

    def __str__(self):
        return f'{self._operator}'

    def show(self, *args, **kwargs):
        """
        Shows the operator

        :param args: Optional positional arguments passed to OpticalOperator.show()
        :param kwargs: Optional keyword arguments passed to OpticalOperator.show()
        :return:
        """
        kwargs.update(self.style)
        print(kwargs)
        if self.is_lens:
            return self._operator.show(*args, focal_plane_kwargs=self._focal_style, **kwargs)
        else:
            return self._operator.show(*args, **kwargs)

    def set_style(self, key, value, focal=False):
        f"""
        Sets one of the style fields to the given value
        :param focal: Whether to set the style for focal planes or not. Only applicable if the optical operator is a Lens.
        :param key: The key to set. Should be one of {list(self._style.keys())}
        :param value: The value to set the field to.
        :type key: str
        :type value: Union[float, int, str]
        :return: 
        """
        if focal:
            if key in self.focal_style:
                self._focal_style[key] = value
            else:
                raise ValueError(f'Cannot set focal style {key} to {value} for {self}: Key {key!r} not recognized')
        else:
            if key in self.style:
                self._style[key] = value
            else:
                raise ValueError(f'Cannot set style {key} to {value} for {self}: Key {key!r} not recognized')
        self.styleChanged.emit()


class OpticalOperatorController(QtCore.QObject):
    """
    Controller for controlling an OpticalOperatorModel

    The controller has a series of preset values that can be used to store certain values in a dictionary with integer keys.
    """
    presetsChanged = pyqtSignal([], name='presetsChanged')

    @property
    def value_presets(self):
        return self._value_presets

    @property
    def model_name(self):
        return str(self._model.label)

    @property
    def model(self):
        return self._model

    def __init__(self, model, *args, **kwargs):
        """
        Create a controller for an OpticalOperatorModel

        :param model: The model to control
        :param args: Optional positional arguments passed to QtCore.QObject constructor
        :param kwargs: Optional keyword arguments passed to QtCore.QObject constructor
        :type model: OpticalOperatorModel
        """
        super(OpticalOperatorController, self).__init__(*args, **kwargs)
        if not isinstance(model, OpticalOperatorModel):
            raise TypeError(
                f'Cannot create {self.__class__.__name__} for {model!r}. Invalid type {type(model)}. Accepted types are `OpticalOperatorModel` and subclasses')
        self._model = model
        self._value_presets = dict()

    @pyqtSlot(int, float, name='setValuePreset')
    def setValuePreset(self, preset, value):
        """
        Sets/adds a preset value
        :param preset: Preset-key
        :param value: Preset-value
        :type preset: int
        :type value: float
        """
        self._value_presets[preset] = value
        self.presetsChanged.emit()

    @pyqtSlot(int, name='setSilent')
    @pyqtSlot(bool, name='setSilent')
    @pyqtSlot(float, name='setSilent')
    def setSilent(self, value):
        """
        Disable signals from the model
        :param value: whether to disable or enable signals
        :param value: Union[int, float, bool]
        :return:
        """
        self._model.silent = value

    @pyqtSlot(float, name='setZ')
    def setZ(self, value):
        """
        Set the z-position of the model
        :param value: z-value
        :type value: float
        """
        self._model.z = value

    @pyqtSlot(float, name='setOffset')
    def setOffset(self, value):
        """
        Set the offset-value of the model
        :param value: offset-value
        :type value: float
        :return:
        """
        self._model.offset = value

    @pyqtSlot(float, name='setValue')
    def setFloatValue(self, value):
        """
        Set the value of the model
        :param value: the value
        :type value: float
        :return:
        """
        self._model.value = value

    @pyqtSlot(int, name='setValue')
    def setIntValue(self, value):
        """
        Set the value of the model based on preset values
        :param value: The preset-key to use
        :type value: int
        :return:
        """
        operator_value = self._value_presets.get(value, float(value))
        self._model.value = operator_value

    @pyqtSlot(str, float)
    def setParameter(self, parameter, value):
        """
        Sets a given parameter to a given value
        :param parameter: The parameter to set. SHould be either "z", "offset", "value-float" or "value-int"
        :param value: The value to set
        :type parameter: str
        :type value: float
        :return:
        """
        if parameter.lower() == 'z':
            self.setZ(value)
        elif parameter.lower() == 'offset':
            self.setOffset(value)
        elif parameter.lower() == 'value-float':
            self.setFloatValue(value)
        elif parameter.lower() == 'value-int':
            self.setIntValue(int(value))
        else:
            raise ValueError(f'Could not set parameter {parameter} to {value} for {self!r}: Parameter not recognized.')

    @pyqtSlot(str, float, bool)
    @pyqtSlot(str, int, bool)
    @pyqtSlot(str, str, bool)
    def setStyle(self, field, value, focal):
        if self._model.is_lens:
            self._model.set_style(field, value, focal)
        else:
            self._model.set_style(field, value, False)

    @pyqtSlot(dict, bool)
    def setStyleDict(self, styles, focal):
        blocked = self._model.signalsBlocked()
        if not blocked:
            self._model.blockSignals(True)
        for key in styles:
            self._model.set_style(key, styles[key], focal)
        if not blocked:
            self._model.blockSignals(False)
        self._model.styleChanged[dict].emit(styles)



class StyleWidget(QtWidgets.QWidget):
    styleChanged = pyqtSignal([dict])

    @property
    def styleDict(self):
        return dict(self._styledict)

    @property
    def widgets(self):
        return {'style': self._linestyleCombobox, 'width': self._linewidthSpinbox, 'alpha': self._aSpinbox, 'color': self._colorWidget}

    def __init__(self, *args, **kwargs):
        super(StyleWidget, self).__init__(*args, **kwargs)
        self._styledict = dict()
        self._linewidthSpinbox = QtWidgets.QDoubleSpinBox(self)
        self._linestyleCombobox = QtWidgets.QComboBox(self)
        self._colorWidget = QtWidgets.QWidget(self)
        self._rSpinbox = QtWidgets.QDoubleSpinBox(self._colorWidget)
        self._gSpinbox = QtWidgets.QDoubleSpinBox(self._colorWidget)
        self._bSpinbox = QtWidgets.QDoubleSpinBox(self._colorWidget)
        self._aSpinbox = QtWidgets.QDoubleSpinBox(self._colorWidget)

        self._linewidthSpinbox.setMinimum(0)
        self._linewidthSpinbox.setMaximum(10)
        self._linewidthSpinbox.setDecimals(2)
        self._linewidthSpinbox.setSingleStep(0.1)
        self._linewidthSpinbox.blockSignals(True)
        self._linewidthSpinbox.setValue(1)
        self._linewidthSpinbox.blockSignals(False)

        self._linestyleCombobox.addItems(lineStyles.keys())
        self._linestyleCombobox.blockSignals(True)
        self._linestyleCombobox.setCurrentText('-')
        self._linestyleCombobox.blockSignals(False)

        self._rSpinbox.setMinimum(0)
        self._rSpinbox.setMaximum(1)
        self._rSpinbox.setDecimals(2)
        self._rSpinbox.setSingleStep(0.1)
        self._rSpinbox.blockSignals(True)
        self._rSpinbox.setValue(1)
        self._rSpinbox.blockSignals(False)

        self._gSpinbox.setMinimum(0)
        self._gSpinbox.setMaximum(1)
        self._gSpinbox.setDecimals(2)
        self._gSpinbox.setSingleStep(0.1)
        self._gSpinbox.blockSignals(True)
        self._gSpinbox.setValue(1)
        self._gSpinbox.blockSignals(False)

        self._bSpinbox.setMinimum(0)
        self._bSpinbox.setMaximum(1)
        self._gSpinbox.setDecimals(2)
        self._bSpinbox.setSingleStep(0.1)
        self._bSpinbox.blockSignals(True)
        self._bSpinbox.setValue(1)
        self._bSpinbox.blockSignals(False)

        self._aSpinbox.setMinimum(0)
        self._aSpinbox.setMaximum(1)
        self._aSpinbox.setDecimals(2)
        self._aSpinbox.setSingleStep(0.1)
        self._aSpinbox.blockSignals(True)
        self._aSpinbox.setValue(1.)
        self._aSpinbox.blockSignals(False)

        gridlayout = QtWidgets.QGridLayout()
        gridlayout.addWidget(QtWidgets.QLabel('R'), 0, 0)
        gridlayout.addWidget(QtWidgets.QLabel('G'), 0, 1)
        gridlayout.addWidget(QtWidgets.QLabel('B'), 0, 2)
        gridlayout.addWidget(QtWidgets.QLabel('A'), 0, 3)
        gridlayout.addWidget(self._rSpinbox, 1, 0)
        gridlayout.addWidget(self._gSpinbox, 1, 1)
        gridlayout.addWidget(self._bSpinbox, 1, 2)
        gridlayout.addWidget(self._aSpinbox, 1, 3)
        self._colorWidget.setLayout(gridlayout)

        self._styledict['lw'] = self._linewidthSpinbox.value()
        self._styledict['ls'] = self._linestyleCombobox.currentText()
        self._styledict['color'] = to_hex([self._rSpinbox.value(), self._gSpinbox.value(), self._bSpinbox.value()])
        self._styledict['alpha'] = self._aSpinbox.value()

    @pyqtSlot(float, float, float)
    def setColorRGB(self, r, g, b):
        blocked = self.signalsBlocked()
        if not blocked:
            self.blockSignals(True)
        self.setRValue(r)
        self.setGValue(g)
        self.setBValue(b)
        if not blocked:
            self.blockSignals(False)
        self.styleChanged[dict].emit(self.styleDict)

    @pyqtSlot(str)
    def setColorHex(self, hex):
        try:
            color = to_rgb(hex)
        except ValueError as e:
            raise ValueError(f'Cannot set color for {self!r} for hex-string {hex!r}') from e
        else:
            self.setColorRGB(*color)

    @pyqtSlot(float)
    def setRValue(self, value):
        self._rSpinbox.blockSignals(True)
        self._rSpinbox.setValue(value)
        self._rSpinbox.blockSignals(False)
        self._styledict['color'] = to_hex([self._rSpinbox.value(), self._gSpinbox.value(), self._bSpinbox.value()])
        self.styleChanged[dict].emit(self.styleDict)

    @pyqtSlot(float)
    def setGValue(self, value):
        self._gSpinbox.blockSignals(True)
        self._gSpinbox.setValue(value)
        self._gSpinbox.blockSignals(False)
        self._styledict['color'] = to_hex([self._rSpinbox.value(), self._gSpinbox.value(), self._bSpinbox.value()])
        self.styleChanged[dict].emit(self.styleDict)

    @pyqtSlot(float)
    def setBValue(self, value):
        self._bSpinbox.blockSignals(True)
        self._bSpinbox.setValue(value)
        self._bSpinbox.blockSignals(False)
        self._styledict['color'] = to_hex([self._rSpinbox.value(), self._gSpinbox.value(), self._bSpinbox.value()])
        self.styleChanged[dict].emit(self.styleDict)

    @pyqtSlot(float)
    def setAValue(self, value):
        self._aSpinbox.blockSignals(True)
        self._aSpinbox.setValue(value)
        self._aSpinbox.blockSignals(False)
        self._styledict['alpha'] = self._aSpinbox.value()
        self.styleChanged[dict].emit(self.styleDict)

    @pyqtSlot(float)
    def setLinewidth(self, value):
        self._linewidthSpinbox.blockSignals(True)
        self._linewidthSpinbox.setValue(value)
        self._linewidthSpinbox.blockSignals(False)
        self._styledict['lw'] = self._linewidthSpinbox.value()
        self.styleChanged[dict].emit(self.styleDict)

    @pyqtSlot(str)
    def setLinestyle(self, value):
        self._linestyleCombobox.blockSignals(True)
        self._linestyleCombobox.setCurrentText(value)
        self._linestyleCombobox.blockSignals(False)
        self._styledict['ls'] = self._linestyleCombobox.currentText()
        self.styleChanged[dict].emit(self._styledict)

    @pyqtSlot(dict)
    def setStyles(self, styles):
        blocked = self.signalsBlocked()
        if not blocked:
            self.blockSignals(True)
        self.setLinestyle(styles['ls'])
        self.setLinewidth(styles['lw'])
        self.setAValue(styles['alpha'])
        self.setColorHex(styles['color'])
        if not blocked:
            self.blockSignals(False)
        self.styleChanged[dict].emit(self.styleDict)


class OpticalOperatorView(QtWidgets.QWidget):
    """
    Create a view for an OpticalOperator.

    This object provides a series of widgets and setup-tools for the widgets. The widgets are connected to a controller that controls the model, and changes in the model are reflected in the view - as long as the underlying data object (i.e. the OpticalOperator) is changed directly (not through the corresponding OpticalOperatorModel)
    """
    value_min = -999
    value_max = 999
    value_step = 0.1
    value_decimals = 2

    z_min = -999
    z_max = 999
    z_step = 0.5
    z_decimals = 2

    offset_min = -999
    offset_max = 999
    offset_step = 0.05
    offset_decimals = 2

    plotUpdated = pyqtSignal(name='plotUpdated')

    @property
    def model(self):
        return self._model

    def __init__(self, controller, *args, plot_widget=None, **kwargs):
        """
        Create a view for a controller.

        The following widgets will be created:
        -typeLabel: A QLabel to show the type of the operator
        -nameLabel: A QLabel to show the name of the operator
        -zSpinbox: A QDoubleSpinBox to control/show the z-position of the operator
        -offsetSpinbox: A QDoubleSpinBox to control/show the offset of the operator
        -valueSpinbox: A QDoubleSpinBox to control/show the value of the operator
        -valueDial: A QDial to control/show the value of the operator through preset values
        -valueIndicator: A QLabel to show the current value of the operator below the valueDial.
        -zStepSpinbox: A QDoubleSpinBox to control/show the singleStep of the zSpinbox.
        -offsetStepSpinbox: A QDoubleSpinBox to control/show the singleStep of the offsetSpinbox.
        -valueStepSpinbox: A QDoubleSpinBox to control/show the singleStep of the valueSpinbox.
        -plotWidget: A MplWidget to show the operator graphically in a plot area.

        :param controller: The controller to connect to. The model will be extracted from this controller.
        :param args: Optional positional arguments passed to QtWidgets.QWidget
        :param plot_widget: The plot-widget to use to show the optical operator on
        :param kwargs: Optional keyword arguments passed to QtWidgets.QWidget
        :type controller: OpticalOperatorController
        :type plot_widget: MplWidget
        """
        super(OpticalOperatorView, self).__init__(*args, **kwargs)
        if not isinstance(controller, OpticalOperatorController):
            raise TypeError()
        self._controller = controller
        self._model = self._controller.model

        self.typeLabel = QtWidgets.QLabel(self._model.operator_classname, self)
        self.nameLabel = QtWidgets.QLabel(self._model.label, self)
        self.zSpinbox = QtWidgets.QDoubleSpinBox(self)
        self.offsetSpinbox = QtWidgets.QDoubleSpinBox(self)
        self.valueSpinbox = QtWidgets.QDoubleSpinBox(self)
        self.valueDial = QtWidgets.QDial(self)
        self.valueIndicator = QtWidgets.QLabel(self)
        self.styleWidget = StyleWidget(self)
        if self._model.is_lens:
            self.focalStyleWidget = StyleWidget(self)
        else:
            self.focalStyleWidget = None

        # self.zStepSpinbox = QtWidgets.QDoubleSpinBox(self)
        # self.offsetStepSpinbox = QtWidgets.QDoubleSpinBox(self)
        # self.valueStepSpinbox = QtWidgets.QDoubleSpinBox(self)
        # self.zDecimalsSpinbox = QtWidgets.QSpinBox(self)
        # self.offsetDecimalsSpinbox = QtWidgets.QSpinBox(self)
        # self.valueDecimalsSpinbox = QtWidgets.QSpinBox(self)
        # self.zMinimumLineEdit = QtWidgets.QLineEdit(self)
        # self.offsetMinimumLineEdit = QtWidgets.QLineEdit(self)
        # self.valueMinimumLineEdit = QtWidgets.QLineEdit(self)
        # self.zMaximumLineEdit = QtWidgets.QLineEdit(self)
        # self.offsetMaximumLineEdit = QtWidgets.QLineEdit(self)
        # self.valueMaximumLineEdit = QtWidgets.QLineEdit(self)
        if plot_widget is None:
            self.plotWidget = MplWidget(self)
        else:
            if isinstance(plot_widget, MplWidget):
                self.plotWidget = plot_widget
            else:
                raise TypeError(
                    f'Cannot create {self.__class__.__name__} for controller {self._controller!r} with model {self._model!r}. Provided plotWidget is not a MplWidget but a {type(plot_widget)}')
        self._plot_data = None

        self.setupZSpinbox()
        self.setupValueDial()
        self.setupValueSpinbox()
        self.setupOffsetSpinbox()
        self.setupValueIndicator()
        self.styleWidget.setStyles(self._model.style) #Simple setup for the stylewidgets

        # Listeners
        self._model.valueChanged[float].connect(self.on_value_changed)
        self._model.zChanged[float].connect(self.on_z_changed)
        self._model.offsetChanged[float].connect(self.on_offset_changed)
        self._model.labelChanged[str].connect(self.on_label_changed)
        self._model.operatorChanged.connect(lambda: self.on_model_changed())
        self._model.styleChanged[dict].connect(self.on_style_changed)

        # Signals
        self.zSpinbox.valueChanged[float].connect(self._controller.setZ)
        self.offsetSpinbox.valueChanged[float].connect(self._controller.setOffset)
        self.valueSpinbox.valueChanged[float].connect(self._controller.setFloatValue)
        self.valueDial.valueChanged[int].connect(self._controller.setIntValue)
        self.styleWidget.styleChanged[dict].connect(lambda x: self._controller.setStyleDict(x, False))

    def setupValueSpinbox(self):
        """
        Sets up the value spinbox
        :return:
        """
        self.valueSpinbox.setMinimum(self.value_min)
        self.valueSpinbox.setMaximum(self.value_max)
        self.valueSpinbox.setDecimals(self.value_decimals)
        self.valueSpinbox.setSingleStep(self.value_step)
        self.valueSpinbox.blockSignals(True)
        self.valueSpinbox.setValue(self._model.value)
        self.valueSpinbox.blockSignals(False)

    def setupZSpinbox(self):
        self.zSpinbox.setMinimum(self.z_min)
        self.zSpinbox.setMaximum(self.z_max)
        self.zSpinbox.setDecimals(self.z_decimals)
        self.zSpinbox.setSingleStep(self.z_step)
        self.zSpinbox.blockSignals(True)
        self.zSpinbox.setValue(self._model.z)
        self.zSpinbox.blockSignals(False)

    def setupOffsetSpinbox(self):
        if self._model.is_deflector or self._model.is_propagator:
            self.offsetSpinbox.setEnabled(False)
        else:
            self.offsetSpinbox.setMinimum(self.offset_min)
            self.offsetSpinbox.setMaximum(self.offset_max)
            self.offsetSpinbox.setDecimals(self.offset_decimals)
            self.offsetSpinbox.setSingleStep(self.offset_step)
        self.offsetSpinbox.blockSignals(True)
        self.offsetSpinbox.setValue(self._model.offset)
        self.offsetSpinbox.blockSignals(False)

    def setupValueDial(self):
        if len(self._controller.value_presets) < 2:
            self.valueDial.setEnabled(False)
            dial_value = None
        else:
            self.valueDial.setMinimum(min(self._controller.value_presets.keys()))
            self.valueDial.setMaximum(max(self._controller.value_presets.keys()))
            preset_matches = [key for key in self._controller.value_presets if
                              self._controller.value_presets[key] == self._model.value]
            if len(preset_matches) > 0:
                dial_value = min(preset_matches)
            else:
                dial_value = None

        self.valueDial.setTracking(True)
        self.valueDial.setNotchesVisible(True)

        if dial_value is None:
            if self.valueDial.isEnabled():
                self.valueDial.setStyleSheet('background-color : lightblue')
            else:
                pass
        else:
            self.valueDial.setStyleSheet('background-color : lightgreen')
            self.valueDial.blockSignals(True)
            self.valueDial.setValue(dial_value)
            self.valueDial.blockSignals(False)

    def setupValueIndicator(self):
        self.valueIndicator.setText(f'{self._model.value}')


    @pyqtSlot(float)
    def on_z_changed(self, value):
        if self.zSpinbox.minimum() > value:
            self.zSpinbox.setMinimum(value)
        if self.zSpinbox.maximum() < value:
            self.zSpinbox.setMaximum(value)

        self.zSpinbox.blockSignals(True)
        self.zSpinbox.setValue(value)
        self.zSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def on_offset_changed(self, value):
        if self.offsetSpinbox.minimum() > value:
            self.offsetSpinbox.setMinimum(value)
        if self.offsetSpinbox.maximum() < value:
            self.offsetSpinbox.setMaximum(value)

        self.offsetSpinbox.blockSignals(True)
        self.offsetSpinbox.setValue(value)
        self.offsetSpinbox.blockSignals(False)

    @pyqtSlot(float)
    def on_value_changed(self, value):
        if self.valueSpinbox.minimum() > value:
            self.valueSpinbox.setMinimum(value)
        if self.valueSpinbox.maximum() < value:
            self.valueSpinbox.setMaximum(value)

        self.valueSpinbox.blockSignals(True)
        self.valueSpinbox.setValue(value)
        self.valueSpinbox.blockSignals(False)

        preset_values = [key for key in self._controller.value_presets if self._controller.value_presets[key] == value]
        if len(preset_values) == 0:
            self.valueDial.setStyleSheet('background-color : lightblue')
        else:
            self.valueDial.setStyleSheet('background-color : lightgreen')
            self.valueDial.blockSignals(True)
            self.valueDial.setValue(preset_values[0])
            self.valueDial.blockSignals(False)

        self.valueIndicator.setText(f'{value}')

    @pyqtSlot(str)
    def on_label_changed(self, value):
        self.nameLabel.setText(value)

    def on_model_changed(self, *args, **kwargs):
        kwargs.update({'ax': self.plotWidget.canvas.ax})
        if self._plot_data is None:
            _, _, self._plot_data = self._model.show(*args, **kwargs)
        else:
            if self._model.is_deflector:
                self._plot_data[0].set_ydata([self._model.z, self._model.z])
            elif self._model.is_lens:
                [line.set_ydata([z, z]) for z, line in
                 zip([self._model.z, self._model.z + self._model.value, self._model.z - self._model.value],
                     self._plot_data)]
        self.plotUpdated.emit()

    @pyqtSlot(dict)
    def on_style_changed(self, style):
        self.styleWidget.blockSignals(True)
        self.styleWidget.setStyles(style)
        self.styleWidget.blockSignals(False)
        self.on_model_changed()

class MicroscopeModel(QtCore.QObject):
    modelChanged = pyqtSignal([], name='modelChanged')
    systemFilled = pyqtSignal([], name='systemFilled')
    systemTraced = pyqtSignal([list], name='systemTraced')

    @property
    def operatorModels(self):
        return [model for model in self._operatorModels]

    @property
    def sourceModel(self):
        return self._sourceModel

    @property
    def screenModel(self):
        return self._screenModel

    def __init__(self, optical_system, *args, **kwargs):
        super(MicroscopeModel, self).__init__(*args, **kwargs)
        if not isinstance(optical_system, OpticalSystem):
            raise TypeError(
                f'Cannot create {self.__class__.__name__} for source: {optical_system!r}. Expected type OpticalSystem not {type(optical_system)}')

        self._optical_system = optical_system

        self._sourceModel = None
        self._screenModel = None
        self._operatorModels = [OpticalOperatorModel(operator, self.parent()) for operator in self._optical_system]

    def __iter__(self):
        for obj in [self.sourceModel] + self.operatorModels + [self.screenModel]:
            yield obj

    @pyqtSlot()
    def fillSystem(self):
        self._optical_system.fill()
        self.systemFilled.emit()

    @pyqtSlot(name='trace', result=list)
    def trace(self):
        self.blockSignals(True)
        self.fillSystem()
        self.blockSignals(False)
        traces = self._optical_system.trace
        self.systemTraced[list].emit(traces)
        return traces

    @pyqtSlot(name='printSystem')
    def printSystem(self):
        print(self._optical_system)

    @pyqtSlot(name='printTraces')
    def printTraces(self):
        traces = self._optical_system.trace
        for trace in traces:
            print(f'Trace {trace.label}:')
            t = tabulate([[i, ray.x, ray.angle_deg, ray.z] for i, ray in enumerate(trace)],
                         headers=['#', 'X', 'Angle [deg]', 'Z'])
            print(t)


class MicroscopeController(QtCore.QObject):

    @property
    def model(self):
        return self._model

    @property
    def sourceController(self):
        return self._sourceController

    @property
    def screenController(self):
        return self._screenController

    @property
    def operatorControllers(self):
        return [controller for controller in self._operatorControllers]

    def __init__(self, model, *args, **kwargs):
        super(MicroscopeController, self).__init__(*args, **kwargs)
        if not isinstance(model, MicroscopeModel):
            raise TypeError(
                f'Cannot create {self.__class__.__name__} for model: {model!r}. Expected type MicroscopeModel not {type(model)}')
        self._model = model

        self._sourceController = None
        self._screenController = None
        self._operatorControllers = [OpticalOperatorController(model) for model in self._model.operatorModels if
                                     (model.is_lens or model.is_deflector)]

    def __iter__(self):
        for obj in [self.sourceController] + self.operatorControllers + [self.screenController]:
            yield obj

    @pyqtSlot(str, str, float)
    def setOperatorParameterByName(self, name, parameter, value):
        print(f'Setting {name} {parameter}={value}')
        changes = len([controller.setParameter(parameter, value) for controller in self._operatorControllers if
                       controller.model_name == name])
        if changes > 0:
            self._model.modelChanged.emit()

    @pyqtSlot(name='trace', result=list)
    def trace(self):
        return self._model.trace()


class MicroscopeView(QtWidgets.QMainWindow):
    #colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    #colors = plt.get_cmap('inferno', 10)
    colors = plt.get_cmap('tab20', 10)

    @property
    def screenView(self):
        return self._screenView

    @property
    def sourceView(self):
        return self._sourceView

    @property
    def operatorViews(self):
        return [view for view in self._operatorViews]

    def __init__(self, controller, *args, **kwargs):
        super(MicroscopeView, self).__init__(*args, **kwargs)
        if not isinstance(controller, MicroscopeController):
            raise TypeError()

        self._controller = controller
        self._model = self._controller.model

        self.plot_widget = MplWidget(self)
        self.lens_widgets = QtWidgets.QWidget(self)
        self.lens_widgets.setLayout(QtWidgets.QGridLayout())
        self.plot_button = QtWidgets.QPushButton('Plot')
        self.print_system_button = QtWidgets.QPushButton('Print system')
        self.print_traces_button = QtWidgets.QPushButton('Print rays')

        # self._screenView = None
        # self._sourceView = None
        self._operatorViews = [OpticalOperatorView(controller, self, plot_widget=self.plot_widget) for controller in
                               self._controller.operatorControllers]
        self._trace_lines = None

        self.setCentralWidget(QtWidgets.QWidget(self))
        self.centralWidget().setLayout(QtWidgets.QGridLayout())

        self.centralWidget().layout().addWidget(self.plot_widget, 0, 0)
        self.centralWidget().layout().addWidget(self.lens_widgets, 0, 1)
        self.centralWidget().layout().addWidget(self.plot_button, 1, 0)
        self.centralWidget().layout().addWidget(self.print_system_button, 2, 0)
        self.centralWidget().layout().addWidget(self.print_traces_button, 3, 0)


        self.lensStyleWindow = QtWidgets.QMainWindow(self)
        self.lensStyleWindow.setCentralWidget(QtWidgets.QWidget(self))
        self.lensStyleWindow.centralWidget().setLayout(QtWidgets.QGridLayout())
        self.lensStyleWindow.centralWidget().layout().addWidget(QtWidgets.QLabel('Name'), 0, 0)
        self.lensStyleWindow.centralWidget().layout().addWidget(QtWidgets.QLabel('Style'), 0, 1)
        self.lensStyleWindow.centralWidget().layout().addWidget(QtWidgets.QLabel('Width'), 0, 2)
        self.lensStyleWindow.centralWidget().layout().addWidget(QtWidgets.QLabel('Color'), 0, 4)
        [self.lensStyleWindow.centralWidget().layout().addWidget(QtWidgets.QLabel(f'{view.nameLabel.text()}'), i + 1, 0) for
         i, view in enumerate(self.operatorViews) if view.model.is_lens]
        [self.lensStyleWindow.centralWidget().layout().addWidget(view.styleWidget.widgets['style'], i+1, 1) for
         i, view in enumerate(self.operatorViews) if view.model.is_lens]
        [self.lensStyleWindow.centralWidget().layout().addWidget(view.styleWidget.widgets['width'], i + 1, 2) for
         i, view in enumerate(self.operatorViews) if view.model.is_lens]
        [self.lensStyleWindow.centralWidget().layout().addWidget(view.styleWidget.widgets['color'], i + 1, 4) for
         i, view in enumerate(self.operatorViews) if view.model.is_lens]
        #[v for view in self.operatorViews]
        menubar = self.menuBar()
        self.controlMenu = menubar.addMenu('Controls')
        self.operatorAction = QtWidgets.QAction('&Operators', self)
        self.sourceAction = QtWidgets.QAction('&Source', self)
        self.screenAction = QtWidgets.QAction('&Screen', self)
        self.controlMenu.addAction(self.operatorAction)
        self.controlMenu.addAction(self.sourceAction)
        self.controlMenu.addAction(self.screenAction)

        self.styleMenu = menubar.addMenu('Styles')
        self.lensStyleAction = QtWidgets.QAction('&Lenses', self)
        self.deflectorStyleAction = QtWidgets.QAction('&Deflectors', self)
        self.rayStyleAction = QtWidgets.QAction('&Rays', self)

        self.styleMenu.addAction(self.lensStyleAction)
        self.styleMenu.addAction(self.deflectorStyleAction)
        self.styleMenu.addAction(self.rayStyleAction)

        self.lensStyleAction.triggered.connect(self.openLensStyle)


        # Signals
        self.plot_button.clicked.connect(self.on_model_changed)
        self.print_system_button.clicked.connect(self._model.printSystem)
        [view.plotUpdated.connect(self._model.modelChanged) for view in self._operatorViews]
        self.print_traces_button.clicked.connect(self._model.printTraces)

        # Listeners
        self._model.modelChanged.connect(self.on_model_changed)
        self._model.systemTraced[list].connect(self.on_retraced)

        self.setup_lens_widgets()

        # show lenses
        [operator_view.on_model_changed(annotate=False) for operator_view in self._operatorViews]
        #Run raytracing and update the plot fo an initial inspection
        self.on_model_changed()

    def setup_lens_widgets(self):
        self.lens_widgets.layout().addWidget(QtWidgets.QLabel('Type', self.lens_widgets), 0, 0)
        self.lens_widgets.layout().addWidget(QtWidgets.QLabel('Name', self.lens_widgets), 0, 1)
        self.lens_widgets.layout().addWidget(QtWidgets.QLabel('Z', self.lens_widgets), 0, 2)
        self.lens_widgets.layout().addWidget(QtWidgets.QLabel('Offset', self.lens_widgets), 0, 3)
        self.lens_widgets.layout().addWidget(QtWidgets.QLabel('Value', self.lens_widgets), 0, 4)

        for i, view in enumerate(self.operatorViews):
            self.lens_widgets.layout().addWidget(view.typeLabel, i + 1, 0)
            self.lens_widgets.layout().addWidget(view.nameLabel, i + 1, 1)
            self.lens_widgets.layout().addWidget(view.zSpinbox, i + 1, 2)
            self.lens_widgets.layout().addWidget(view.offsetSpinbox, i + 1, 3)
            self.lens_widgets.layout().addWidget(view.valueSpinbox, i + 1, 4)

    @pyqtSlot(list, name='on_retraced')
    def on_retraced(self, traces):
        if len(traces) > self.colors.N:
            self.colors = plt.get_cmap(self.colors.name, len(traces))
        if self._trace_lines is not None:
            [line[0].remove() for line in self._trace_lines]
        self.plot_widget.canvas.ax.set_prop_cycle(None)
        colors = {}
        for trace in traces:
            if trace[0].x in colors:
                pass
            else:
                #colors[trace[0].x] = self.colors[len(colors)]
                colors[trace[0].x] = self.colors(len(colors)/len(traces))
        self._trace_lines = [trace.show(ax=self.plot_widget.canvas.ax, annotate=False, color=colors[trace[0].x])[2] for
                             i, trace in enumerate(traces)]
        xs = [[ray.x for ray in raytrace] for raytrace in traces]
        minimum_x = min([min(x) for x in xs])
        maximum_x = max([max(x) for x in xs])

        ys = [[ray.z for ray in raytrace] for raytrace in traces]
        minimum_y = min([min(y) for y in ys])
        maximum_y = max([max(y) for y in ys])

        ticks = [(operator.z, operator.label) for operator in self._model.operatorModels if
                 (operator.is_deflector or operator.is_lens)]
        additional_ticks = [(operator.z + operator.value, f'{operator.label} FFP') for operator in
                            self._model.operatorModels if operator.is_lens]
        additional_ticks.extend(
            [(operator.z - operator.value, f'{operator.label} BFP') for operator in self._model.operatorModels if
             operator.is_lens])
        ticks.extend(additional_ticks)
        self.plot_widget.canvas.ax.set_yticks([tick[0] for tick in ticks])
        self.plot_widget.canvas.ax.set_yticklabels([tick[1] for tick in ticks])
        self.plot_widget.canvas.ax.set_xlim(minimum_x, maximum_x)
        self.plot_widget.canvas.ax.set_ylim(minimum_y, maximum_y)

        print('Plot updated')
        self.plot_widget.canvas.draw()

    @pyqtSlot()
    def on_model_changed(self):
        self._model.trace()

    @pyqtSlot()
    def openLensStyle(self):
        self.lensStyleWindow.show()


def main():
    mygui = QtWidgets.QApplication(sys.argv)
    mainwindow = QtWidgets.QMainWindow()
    mainwindow.setCentralWidget(QtWidgets.QWidget())
    mainwindow.centralWidget().setLayout(QtWidgets.QGridLayout())

    CL1 = Lens(10, label='CL1', z=100)
    CL2 = Lens(10, label='CL2', z=70)

    CL1model = OpticalOperatorModel(CL1, mainwindow)
    CL2model = OpticalOperatorModel(CL2, mainwindow)

    CL1controller = OpticalOperatorController(CL1model, CL1model.parent())
    CL2controller = OpticalOperatorController(CL2model, CL2model.parent())

    [CL1controller.setValuePreset((i + 1), float(i + 1) ** 2) for i in range(5)]

    CL1view = OpticalOperatorView(CL1model, CL1controller, CL1model.parent())
    CL2view = OpticalOperatorView(CL2model, CL2controller, CL2model.parent())

    mainwindow.centralWidget().layout().addWidget(QtWidgets.QLabel('Type'), 0, 0)
    mainwindow.centralWidget().layout().addWidget(QtWidgets.QLabel('Name'), 0, 1)
    mainwindow.centralWidget().layout().addWidget(QtWidgets.QLabel('Z'), 0, 2)
    mainwindow.centralWidget().layout().addWidget(QtWidgets.QLabel('Offset'), 0, 3)
    mainwindow.centralWidget().layout().addWidget(QtWidgets.QLabel('Value'), 0, 4)
    mainwindow.centralWidget().layout().addWidget(QtWidgets.QLabel('Value (2)'), 0, 5)

    for i, view in enumerate([CL1view, CL2view]):
        mainwindow.centralWidget().layout().addWidget(view.typeLabel, i + 1, 0)
        mainwindow.centralWidget().layout().addWidget(view.nameLabel, i + 1, 1)
        mainwindow.centralWidget().layout().addWidget(view.zSpinbox, i + 1, 2)
        mainwindow.centralWidget().layout().addWidget(view.offsetSpinbox, i + 1, 3)
        mainwindow.centralWidget().layout().addWidget(view.valueSpinbox, i + 1, 4)

        w = QtWidgets.QWidget(mainwindow.centralWidget())
        w.setLayout(QtWidgets.QVBoxLayout())
        w.layout().addWidget(view.valueDial)
        view.valueIndicator.setAlignment(QtCore.Qt.AlignCenter)
        w.layout().addWidget(view.valueIndicator)
        mainwindow.centralWidget().layout().addWidget(w, i + 1, 5)

    mainwindow.show()

    sys.exit(mygui.exec_())


def main2():
    mygui = QtWidgets.QApplication(sys.argv)

    source = Source(150, [-1, 1], size=1)
    screen = Screen(-100)
    GUN1 = Deflector(0, label='GUN1', z=95)
    GUN2 = Deflector(0, label='GUN2', z=85)
    CL1 = Lens(10, label='CL1', z=80)
    CL2 = Lens(10, label='CL2', z=70)
    CL3 = Lens(10, label='CL3', z=60)
    CLA1 = Deflector(0, label='CLA1', z=50)
    CLA2 = Deflector(0, label='CLA2', z=40)
    CM = Lens(10, label='CM', z=30)
    OLPre = Lens(10, label='OLPre', z=5)
    OLPost = Lens(10, label='OLPost', z=-5)
    OM = Lens(10, label='OM', z=-15)
    ILA1 = Deflector(0, label='ILA1', z=-25)
    ILA2 = Deflector(0, label='ILA2', z=-30)
    IL1 = Lens(10, label='IL1', z=-40)
    IL2 = Lens(10, label='IL2', z=-50)
    IL3 = Lens(10, label='IL3', z=-60)
    PLA = Deflector(0, label='PLA', z=-70)
    PL = Lens(10, label='PLA', z=-80)
    optical_system = OpticalSystem(source,
                                   [GUN1, GUN2, CL1, CL2, CL3, CLA1, CLA2, CM, OLPre, OLPost, OM, ILA1, ILA2, IL1, IL2,
                                    IL3, PLA, PL], screen)
    microscope_model = MicroscopeModel(optical_system)
    microscope_controller = MicroscopeController(microscope_model)
    microscope_view = MicroscopeView(microscope_controller)
    microscope_view.show()
    sys.exit(mygui.exec_())

def main3():
    mygui = QtWidgets.QApplication(sys.argv)

    source = Source(100, np.linspace(-1, 1, num=3), size=0.1, points=9)
    screen = Screen(0)
    CL1 = Lens(6.3, label='CL1', z=82)
    CL3 = Lens(8, label='CL3', z=60)
    CLA1 = Deflector(0, label='CLA1', z=49)
    CLA2 = Deflector(0, label='CLA2', z=42.5)
    CM = Lens(10, label='CM', z=27)
    OLPre = Lens(8.5, label='OLPre', z=8.5)
    optical_system = OpticalSystem(source,
                                   [CL1, CL3, CLA1, CLA2, CM, OLPre], screen)
    microscope_model = MicroscopeModel(optical_system)
    microscope_controller = MicroscopeController(microscope_model)
    microscope_view = MicroscopeView(microscope_controller)
    microscope_view.show()
    sys.exit(mygui.exec_())

if __name__ == '__main__':
    main3()
