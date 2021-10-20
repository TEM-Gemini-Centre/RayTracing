def createOperatorWidgets(operator: OpticalOperator, parent: Optional[QtCore.QObject] = None, layout: Optional[
    Union[QtWidgets.QGridLayout, QtWidgets.QHBoxLayout, QtWidgets.QVBoxLayout]] = None, z_min: float = -999.,
                          z_max: float = 999., z_decimals: int = 2, z_step: float = 1., offset_min: float = -999.,
                          offset_max: float = 999., offset_decimals: int = 2, offset_step: float = 1.,
                          value_min: float = -999., value_max=999., value_decimals: int = 2, value_step: float = 1.,
                          **kwargs) -> dict:
    """
    Create widgets for an OpticalOperator
    :param operator: The operator to create widgets for (used for determining type and name only)
    :param parent: The parent to assign widgets to
    :param layout: The layout to assign widgets to
    :param z_min: minimum value of z spinbox
    :param z_max: maximum value of z spinbox
    :param z_decimals: number of decimals for z spinbox
    :param z_step: the step size for the z spinbox
    :param offset_min: minimum value of offset spinbox
    :param offset_max: maximum value of offset spinbox
    :param offset_decimals: number of decimals for offset spinbox
    :param offset_step: the step size for the offset spinbox
    :param value_min: minimum value of value spinbox
    :param value_max: maximum value of value spinbox
    :param value_decimals: number of decimals for value spinbox
    :param value_step: the step size for the value spinbox
    :returns: typeLabel, nameLabel, zSpinbox, offsetSpinbox, valueSpinbox

    Widgets for the type, name, z, offset, and value will be created, and added to a parent and/or layout if provided.

    """
    if not isinstance(operator, OpticalOperator):
        raise TypeError(f'{__name__} can only create widgets for OpticalOperators, not {type(operator)}')

    typeLabel = QtWidgets.QLabel(operator.__class__.__name__)
    nameLabel = QtWidgets.QLabel(str(operator.label))

    zSpinbox = QtWidgets.QDoubleSpinBox()
    zSpinbox.setDecimals(z_decimals)
    zSpinbox.setMinimum(z_min)
    zSpinbox.setMaximum(z_max)
    zSpinbox.setSingleStep(z_step)
    zSpinbox.setValue(operator.z)

    offsetSpinbox = QtWidgets.QDoubleSpinBox()
    offsetSpinbox.setDecimals(offset_decimals)
    offsetSpinbox.setMinimum(offset_min)
    offsetSpinbox.setMaximum(offset_max)
    offsetSpinbox.setSingleStep(offset_step)
    offsetSpinbox.setValue(operator.offset)
    if isinstance(operator, Deflector):
        offsetSpinbox.setEnabled(False)

    valueSpinbox = QtWidgets.QDoubleSpinBox()
    valueSpinbox.setDecimals(value_decimals)
    valueSpinbox.setMinimum(value_min)
    valueSpinbox.setMaximum(value_max)
    valueSpinbox.setSingleStep(value_step)
    valueSpinbox.setValue(operator.value)
    widgets = [typeLabel, nameLabel, zSpinbox, offsetSpinbox, valueSpinbox]
    if isinstance(layout, QtWidgets.QGridLayout):
        row = layout.rowCount()
        print(f'Adding widgets to row {row}')
        [layout.addWidget(widget, row, col) for col, widget in enumerate(widgets)]
    elif isinstance(layout, (QtWidgets.QHBoxLayout, QtWidgets.QVBoxLayout)):
        [layout.addWidget(widget) for widget in widgets]
    else:
        warn('Operator widgets not added to any layout on creation')
    print(zSpinbox)
    return {'type': typeLabel, 'name': nameLabel, 'z': zSpinbox, 'offset': offsetSpinbox, 'value': valueSpinbox}


class SourceModel(QtCore.QObject):
    """
    Model for interacting with a Source object
    """
    zChanged = pyqtSignal([], [float], name='zChanged')
    sizeChanged = pyqtSignal([], [float], name='sizeChanged')
    offsetChanged = pyqtSignal([], [float], name='offsetChanged')
    anglesChanged = pyqtSignal([], [list], name='anglesChanged')
    angleAdded = pyqtSignal([], [float], [list], name='angleAdded')
    angleRemoved = pyqtSignal([], [float], [list], name='angleRemoved')

    @property
    def z(self):
        return self._source.z

    @z.setter
    def z(self, value):
        self._source.z = value
        self.zChanged.emit()
        self.zChanged[float].emit(self._source.z)

    @property
    def size(self):
        return self._source.size

    @size.setter
    def size(self, value):
        self._source.size = value
        self.sizeChanged.emit()
        self.sizeChanged[float].emit(self._source.size)

    @property
    def offset(self):
        return self._source.offset

    @offset.setter
    def offset(self, value):
        self._source.size = value
        self.offsetChanged.emit()
        self.offsetChanged[float].emit(self._source.offset)

    @property
    def angles(self):
        return self._source.angles

    @angles.setter
    def angles(self, value):
        self._source.angles = value
        self.anglesChanged.emit()
        self.anglesChanged[list].emit(self._source.angles)

    def __init__(self, source, *args, **kwargs):
        super(SourceModel, self).__init__(*args, **kwargs)
        if not isinstance(source, Source):
            raise TypeError(f'Cannot create {self.__class__.__name__} for {source!r}: Invalid type {type(source)}')
        self._source = source

    @pyqtSlot(float)
    def add_angle(self, value):
        self._source.angles.append(value)
        self.angleAdded.emit()
        self.angleAdded[float].emit(value)
        self.angleAdded[list].emit(self._source.angles)

    @pyqtSlot(int, float)
    def add_angle(self, index, value):
        self._source.angles.insert(index, value)
        self.angleAdded.emit()
        self.angleAdded[float].emit(value)
        self.angleAdded[list].emit(self._source.angles)

    @pyqtSlot()
    def remove_angle(self):
        angle = self._source.angles.pop()
        self.angleRemoved.emit()
        self.angleRemoved[float].emit(angle)
        self.angleRemoved[list].emit(self._source.angles)

    @pyqtSlot(int)
    def remove_angle(self, index):
        angle = self._source.angles.pop(index)
        self.angleRemoved.emit()
        self.angleRemoved[float].emit(angle)
        self.angleRemoved[list].emit(self._source.angles)

    @pyqtSlot(float)
    def remove_angle(self, value):
        self._source.angles.remove(value)
        self.angleRemoved.emit()
        self.angleRemoved[float].emit(value)
        self.angleRemoved[list].emit(self._source.angles)


class ScreenModel(QtCore.QObject):
    """
    A model for interacting with a Screen object
    """

    zChanged = pyqtSignal([], [float], name='zChanged')

    @property
    def z(self):
        return self._screen.z

    @z.setter
    def z(self, value):
        self._screen.z = value
        self.zChanged.emit()
        self.zChanged[float].emit(self._screen.z)

    def __init__(self, screen, *args, **kwargs):
        super(ScreenModel, self).__init__(*args, **kwargs)
        if not isinstance(screen, Screen):
            raise TypeError(f'Cannot create {self.__class__.__name__} for {screen!r}: Invalid type {screen!r}')
        self._screen = screen


class MicroscopeView(QtWidgets.QWidget):

    def __init__(self, model, controller, *args, **kwargs):
        super(MicroscopeView, self).__init__(*args, **kwargs)
        if not isinstance(model, MicroscopeModel):
            raise TypeError(f'Cannot create {self.__class__.__name__} for model {model!r}: Invalid type {type(model)}')
        if not isinstance(controller, MicroscopeController):
            raise TypeError(
                f'Cannot create {self.__class__.__name__} for controller {controller!r}: Invalid type {type(controller)}')

        self._model = model
        self._controller = controller

        self.setLayout(QtWidgets.QVBoxLayout(self))

        # Set up toolbox for all parameters.
        self.toolbox = QtWidgets.QToolBox(self)
        self.screenWidget = QtWidgets.QWidget(self)
        self.sourceWidget = QtWidgets.QWidget(self)
        self.operatorsWidget = QtWidgets.QWidget(self)

        self.toolbox.addItem(self.sourceWidget, 'Source')
        self.toolbox.addItem(self.screenWidget, 'Screen')
        self.toolbox.addItem(self.operatorsWidget, 'Lenses/Deflectors')

        # Add toolbox
        self.layout().addWidget(self.toolbox)

        # Create widgets for controlling the source
        self.sourceWidget.setLayout(QtWidgets.QGridLayout())
        self.sourceWidget.layout().addWidget(QtWidgets.QLabel('Z'), 0, 0)
        self.sourceWidget.layout().addWidget(QtWidgets.QLabel('Offset'), 0, 1)
        self.sourceWidget.layout().addWidget(QtWidgets.QLabel('Size'), 0, 2)
        self.sourceWidget.layout().addWidget(QtWidgets.QLabel('Angles'), 0, 3)
        self.sourceZWidget = QtWidgets.QDoubleSpinBox(self.sourceWidget)
        self.sourceOffsetWidget = QtWidgets.QDoubleSpinBox(self.sourceWidget)
        self.sourceSizeWidget = QtWidgets.QDoubleSpinBox(self.sourceWidget)
        [widget.setMinimum(-999) for widget in [self.sourceZWidget, self.sourceOffsetWidget, self.sourceSizeWidget]]
        [widget.setMaximum(999) for widget in [self.sourceZWidget, self.sourceOffsetWidget, self.sourceSizeWidget]]
        [widget.setDecimals(2) for widget in [self.sourceZWidget, self.sourceOffsetWidget, self.sourceSizeWidget]]
        [widget.setSingleStep(1) for widget in [self.sourceZWidget, self.sourceOffsetWidget, self.sourceSizeWidget]]
        self.sourceZWidget.setValue(self._model.source_z)
        self.sourceOffsetWidget.setValue(self._model.source_offset)
        self.sourceSizeWidget.setValue(self._model.source_size)
        self.anglesWidget = QtWidgets.QWidget(self.sourceWidget)
        self.sourceWidget.layout().addWidget(self.sourceZWidget, 1, 0)
        self.sourceWidget.layout().addWidget(self.sourceOffsetWidget, 1, 1)
        self.sourceWidget.layout().addWidget(self.sourceSizeWidget, 1, 2)
        self.sourceWidget.layout().addWidget(self.anglesWidget, 1, 3)
        self.anglesWidget.setLayout(QtWidgets.QHBoxLayout())
        self.anglesWidget.layout().addWidget(QtWidgets.QWidget(self.anglesWidget))
        self.anglesWidget.layout().itemAt(0).widget().setLayout(QtWidgets.QHBoxLayout())
        self.addAngleButton = QtWidgets.QPushButton('Add', self.anglesWidget)
        self.removeAngleButton = QtWidgets.QPushButton('Remove', self.anglesWidget)
        self.anglesWidget.layout().addWidget(self.addAngleButton)
        self.anglesWidget.layout().addWidget(self.removeAngleButton)

        # Setup screen widgets
        self.screenWidget.setLayout(QtWidgets.QHBoxLayout())
        self.screenWidget.layout().addWidget(QtWidgets.QLabel('Z'))
        self.screenZWidget = QtWidgets.QDoubleSpinBox(self.screenWidget)
        self.screenZWidget.setMinimum(-999)
        self.screenZWidget.setMaximum(999)
        self.screenZWidget.setDecimals(2)
        self.screenZWidget.setSingleStep(1)
        self.screenZWidget.setValue(self._model.screen_z)
        self.screenWidget.layout().addWidget(self.screenZWidget)

        # Setup operator widgets
        self.operatorsWidget.setLayout(QtWidgets.QGridLayout())
        self.operatorsWidget.layout().addWidget(QtWidgets.QLabel('Type'), 0, 0)
        self.operatorsWidget.layout().addWidget(QtWidgets.QLabel('Name'), 0, 1)
        self.operatorsWidget.layout().addWidget(QtWidgets.QLabel('Z'), 0, 2)
        self.operatorsWidget.layout().addWidget(QtWidgets.QLabel('Offset'), 0, 3)
        self.operatorsWidget.layout().addWidget(QtWidgets.QLabel('Value'), 0, 4)
        self.operator_widgets = {}
        for operator in self._model.operators:
            self.operator_widgets[operator.label] = {
                'type': QtWidgets.QLabel(operator.__class__.__name__, self.operatorsWidget),
                'name': QtWidgets.QLabel(str(operator.label), self.operatorsWidget),
                'z': QtWidgets.QDoubleSpinBox(self.operatorsWidget),
                'offset': QtWidgets.QDoubleSpinBox(self.operatorsWidget),
                'value': QtWidgets.QDoubleSpinBox(self.operatorsWidget)}
        print(self.operator_widgets)

        for key in self.operator_widgets:
            self.operator_widgets[key]['z'].setDecimals(2)
            self.operator_widgets[key]['z'].setMinimum(-999)
            self.operator_widgets[key]['z'].setMaximum(999)
            self.operator_widgets[key]['z'].setSingleStep(1)
            # self.operator_widgets[key]['z'].setValue(operator.z)

            self.operator_widgets[key]['offset'].setDecimals(2)
            self.operator_widgets[key]['offset'].setMinimum(-999)
            self.operator_widgets[key]['offset'].setMaximum(999)
            self.operator_widgets[key]['offset'].setSingleStep(1)
            # self.operator_widgets[key]['offset'].setValue(operator.offset)
            if self.operator_widgets[key]['type'].text() == 'Deflector':
                self.operator_widgets[key]['offset'].setEnabled(False)

            self.operator_widgets[key]['value'].setDecimals(2)
            self.operator_widgets[key]['value'].setMinimum(-999)
            self.operator_widgets[key]['value'].setMaximum(999)
            self.operator_widgets[key]['value'].setSingleStep(1)
            # self.operator_widgets[key]['value'].setValue(operator.value)

            for key in self.operator_widgets:
                for parameter in ['z', 'offset', 'value']:
                    self.operator_widgets[key][parameter].valueChanged.connect(
                        lambda x: self._controller.setOperatorParameter(key, parameter, x))

            row = self.operatorsWidget.layout().rowCount()
            print(row)
            self.operatorsWidget.layout().addWidget(self.operator_widgets[key]['type'], row, 0)
            self.operatorsWidget.layout().addWidget(self.operator_widgets[key]['name'], row, 1)
            self.operatorsWidget.layout().addWidget(self.operator_widgets[key]['z'], row, 2)
            self.operatorsWidget.layout().addWidget(self.operator_widgets[key]['offset'], row, 3)
            self.operatorsWidget.layout().addWidget(self.operator_widgets[key]['value'], row, 4)

        # Setup print button
        self.printButton = QtWidgets.QPushButton('Print')
        self.layout().addWidget(self.printButton)
        self.printButton.clicked.connect(lambda: print(self._model))

        # setup signals
        self.sourceZWidget.valueChanged.connect(self._controller.setSourceZ)
        self.sourceOffsetWidget.valueChanged.connect(self._controller.setSourceOffset)
        self.sourceSizeWidget.valueChanged.connect(self._controller.setSourceSize)
        self.addAngleButton.clicked.connect(lambda: self._controller.addAngle(0.0))
        self.removeAngleButton.clicked.connect(lambda: self._controller.removeAngle())
        self.screenZWidget.valueChanged.connect(self._controller.setScreenZ)
        print(tabulate([[str(key), self.operator_widgets[key]['type'].text(), self.operator_widgets[key]['name'].text(),
                         self.operator_widgets[key]['z'],
                         self.operator_widgets[key]['offset'].__class__.__name__,
                         self.operator_widgets[key]['value'].__class__.__name__] for key in self.operator_widgets]))

        # setup listeners
        self._model.sourceSizeChanged[float].connect(lambda value: self.sourceSizeWidget.setValue(value))
        self._model.sourceZChanged[float].connect(lambda value: self.sourceZWidget.setValue(value))
        self._model.sourceOffsetChanged[float].connect(lambda value: self.sourceOffsetWidget.setValue(value))
        self._model.sourceAngleAdded.connect(self.on_angle_added)
        self._model.sourceAngleRemoved.connect(self.on_angle_removed)
        self._model.sourceAnglesChanged[list].connect(self.on_angles_changed)
        self._model.screenZChanged[float].connect(lambda value: self.screenZWidget.setValue(value))
        self._model.CL1ZChanged[float].connect(lambda value: self.operator_widgets['CL1']['z'].setValue(value))
        self._model.PLAZChanged[float].connect(lambda value: self.operator_widgets['PLA']['z'].setValue(value))

    @pyqtSlot()
    def on_angle_added(self):
        container_widget = self.anglesWidget.layout().itemAt(0).widget()
        spinbox = QtWidgets.QDoubleSpinBox(container_widget)
        spinbox.setMinimum(-180)
        spinbox.setMaximum(180)
        spinbox.setDecimals(2)
        spinbox.setSingleStep(1)
        row = container_widget.layout().count()
        spinbox.valueChanged.connect(lambda value: self._controller.setAngle(row, value))
        container_widget.layout().addWidget(spinbox)
        self.removeAngleButton.setEnabled(True)

    @pyqtSlot()
    def on_angle_removed(self):
        self.anglesWidget.layout().itemAt(0).widget().layout().itemAt(0).widget().deleteLater()
        if len(self._model.source_angles) < 1:
            self.removeAngleButton.setEnabled(False)

    @pyqtSlot(list)
    def on_angles_changed(self, angles):
        [self.anglesWidget.layout().itemAt(0).widget().layout().itemAt(col).widget().setValue(angle) for col, angle in
         enumerate(angles)]

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setCentralWidget(QtWidgets.QWidget(self))
        self.centralWidget().setLayout(QtWidgets.QVBoxLayout())

        self.optical_system = OpticalSystem(Source(100, [-2, 2], 1), [], Screen(-100))

        self.sourceWidget = SourceView(self.optical_system.source)
        self.screenWidget = ScreenView(self.optical_system.screen)
        self.operatorPanel = QtWidgets.QGroupBox('System')
        self.operatorPanel.setLayout(QtWidgets.QVBoxLayout())
        self.operatorWidget = QtWidgets.QWidget()
        self.operatorWidget.setLayout(QtWidgets.QGridLayout())
        [self.operatorWidget.layout().addWidget(QtWidgets.QLabel(text), 0, i) for i, text in
         enumerate(['Operator', 'Name', 'Z', 'X', 'Value', ''])]
        self.operatorPanel.layout().addWidget(self.operatorWidget)
        self.addLensWidget = QtWidgets.QPushButton('Add Lens')
        self.addDeflectorWidget = QtWidgets.QPushButton('Add Deflector')
        self.operatorPanel.layout().addWidget(self.addLensWidget)
        self.operatorPanel.layout().addWidget(self.addDeflectorWidget)

        self.centralWidget().layout().addWidget(self.sourceWidget)
        self.centralWidget().layout().addWidget(self.operatorPanel)
        self.centralWidget().layout().addWidget(self.screenWidget)

        self.printButton = QtWidgets.QPushButton('Print')
        self.printButton.clicked.connect(lambda: print(self.optical_system))
        self.centralWidget().layout().addWidget(self.printButton)

        # Signals
        self.addLensWidget.clicked.connect(lambda: self.add_lens())
        self.addDeflectorWidget.clicked.connect(lambda: self.add_deflector())

    @pyqtSlot()
    def add_lens(self):
        self.add_operator(Lens(0))

    @pyqtSlot()
    def add_deflector(self):
        self.add_operator(Deflector(0))

    def add_operator(self, operator):
        self.optical_system.append(operator)
        self.optical_system.fill()
        view = OpticalOperatorView(operator, self.operatorWidget)  # Create a new view for the operator
        view.model.zChanged.connect(lambda: self.optical_system.fill())

        view.destroyed.connect(
            lambda: self.remove_operator(operator))  # When the view is destroyed, also remove the operator

    @pyqtSlot(Lens)
    @pyqtSlot(Deflector)
    def remove_operator(self, operator):
        self.optical_system.remove(operator)  # Remove operator from system
        self.optical_system.fill()  # Refill system with propagators


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, model, controller, *args, **kwargs):
        super(MainWindow2, self).__init__(*args, **kwargs)

        if not isinstance(model, MicroscopeModel):
            raise TypeError(f'Cannot create {self.__class__.__name__} for {model!r}: Invald type {type(model)}')

        if not isinstance(controller, MicroscopeController):
            raise TypeError(
                f'Cannot create {self.__class__.__name__} for {controller!r}: Invald type {type(controller)}')

        self.setCentralWidget(QtWidgets.QWidget(self))
        self.centralWidget().setLayout(QtWidgets.QHBoxLayout())

        self._model = model
        self._controller = controller
        self._view = MicroscopeView(self._model, self._controller, self)

        self.centralWidget().layout().addWidget(self._view)
        # self.centralWidget().layout().addWidget(QtWidgets.QDoubleSpinBox())



class ScreenController(QtCore.QObject):
    """
    Class for handeling screen logic
    """

    def __init__(self, model, *args, **kwargs):
        super(ScreenController, self).__init__(*args, **kwargs)
        self._model = model

    @pyqtSlot(float)
    def change_z(self, value):
        self._model.z = value


class ScreenView(QtWidgets.QWidget):
    """
    Widget for interacting with a Screen object
    """

    def __init__(self, screen, *args, **kwargs):
        super(ScreenView, self).__init__(*kwargs, **kwargs)
        self._model = ScreenModel(screen)
        self._controller = ScreenController(self._model)

        self.setLayout(QtWidgets.QHBoxLayout())

        self.zSpinBox = QtWidgets.QDoubleSpinBox()
        self.zSpinBox.setMinimum(-999)
        self.zSpinBox.setMaximum(999)
        self.zSpinBox.setDecimals(2)
        self.zSpinBox.setSingleStep(1)
        self.zSpinBox.setValue(self._model.z)

        self.layout().addWidget(QtWidgets.QLabel('Z'))
        self.layout().addWidget(self.zSpinBox)

        # Connect widgets to controller
        self.zSpinBox.valueChanged[float].connect(self._controller.change_z)

        # Listen for model changes
        self._model.zChanged[float].connect(self.on_z_changed)

    @pyqtSlot(float)
    def on_z_changed(self, value):
        self.zSpinBox.setValue(value)


class SourceController(QtCore.QObject):
    """
    A controller for handling source logic
    """

    def __init__(self, model, *args, **kwargs):
        super(SourceController, self).__init__(*args, **kwargs)
        if not isinstance(model, SourceModel):
            raise TypeError(f'Cannot create {self.__class__.__name__} for {model!r}: Invalid type {type(model)}')
        self._model = model

    @pyqtSlot(float)
    def change_z(self, value):
        self._model.z = value

    @pyqtSlot(float)
    def change_offset(self, value):
        self._model.offset = value

    @pyqtSlot(float)
    def change_size(self, value):
        self._model.size = value

    @pyqtSlot(list)
    def change_angles(self, value):
        self._model.angles = value

    @pyqtSlot(float)
    def change_angle(self, value):
        self._model.angles = [value] * len(self._model.angles)

    @pyqtSlot(int, float)
    def change_angle(self, index, value):
        self._model.angles[index] = value
        self._model.angles = self._model.angles

    @pyqtSlot(float)
    def add_angle(self, value):
        self._model.add_angle(value)

    @pyqtSlot(float)
    def remove_angle(self, value):
        self._model.remove_angle(value)

    @pyqtSlot(int)
    def remove_angle(self, index):
        self._model.remove_angle(index)

    @pyqtSlot()
    def remove_angle(self):
        self._model.remove_angle()


class SourceView(QtWidgets.QWidget):
    """
    A widget for interacting with a source object
    """

    def __init__(self, source, *args, **kwargs):
        super(SourceView, self).__init__(*args, **kwargs)

        if not isinstance(source, Source):
            raise TypeError(f'Cannot create {self.__class__.__name__} for {source!r}: Invalid type {type(source)}')

        self._model = SourceModel(source)
        self._controller = SourceController(self._model)

        self.setLayout(QtWidgets.QGridLayout(self))

        self.layout().addWidget(QtWidgets.QLabel('Z'), 0, 0)
        self.layout().addWidget(QtWidgets.QLabel('X'), 0, 1)
        self.layout().addWidget(QtWidgets.QLabel('Size'), 0, 2)
        self.layout().addWidget(QtWidgets.QLabel('Angles'), 0, 3)

        self.zWidget = QtWidgets.QDoubleSpinBox()
        self.offsetWidget = QtWidgets.QDoubleSpinBox()
        self.sizeWidget = QtWidgets.QDoubleSpinBox()
        self.addAngleWidget = QtWidgets.QPushButton('Add')
        self.removeAngleWidget = QtWidgets.QPushButton('Remove')

        self.angles_dict = {}
        self.anglesMainWidget = QtWidgets.QWidget()
        self.anglesMainWidget.setLayout(QtWidgets.QHBoxLayout(self.anglesMainWidget))
        self.anglesWidget = QtWidgets.QWidget()
        self.anglesWidget.setLayout(QtWidgets.QHBoxLayout())
        self.anglesMainWidget.layout().addWidget(self.anglesWidget)
        self.anglesMainWidget.layout().addWidget(self.addAngleWidget)
        self.anglesMainWidget.layout().addWidget(self.removeAngleWidget)

        self.layout().addWidget(self.zWidget, 0, 0)
        self.layout().addWidget(self.offsetWidget, 0, 1)
        self.layout().addWidget(self.sizeWidget, 0, 2)
        self.layout().addWidget(self.anglesMainWidget, 0, 3)

        # connect widgets to controller
        self.zWidget.valueChanged.connect(self._controller.change_z)
        self.offsetWidget.valueChanged.connect(self._controller.change_offset)
        self.sizeWidget.valueChanged.connect(self._controller.change_size)
        # Angles widgets will be connected upon creation

        # listen for model changes
        self._model.zChanged[float].connect(self.on_z_changed)
        self._model.offsetChanged[float].connect(self.on_offset_changed)
        self._model.sizeChanged[float].connect(self.on_size_changed)
        self._model.angleAdded.connect(self.on_angle_added)
        self._model.angleRemoved.connect(self.on_angle_removed)
        self._model.anglesChanged[list].connect(self.on_angles_changed)

    @pyqtSlot(float)
    def on_z_changed(self, value):
        self.zWidget.setValue(value)

    @pyqtSlot(float)
    def on_offset_changed(self, value):
        self.offsetWidget.setValue(value)

    @pyqtSlot(float)
    def on_size_changed(self, value):
        self.sizeWidget.setValue(value)

    @pyqtSlot(list)
    def on_angles_changed(self, angles):
        [self.anglesWidget.layout().itemAt(index).widget().setValue(value) for index, value in enumerate(angles)]

    @pyqtSlot()
    def on_angle_added(self):
        spinbox = QtWidgets.QDoubleSpinBox()
        self.anglesWidget.layout().addWidget(spinbox)
        self.angles_dict[self.anglesWidget.layout().count()] = spinbox

        spinbox.setMinimum(-180)
        spinbox.setMaximum(180)
        spinbox.setValue(0)
        spinbox.setDecimals(2)
        spinbox.setSingleStep(1)

        spinbox.valueChanged.connect(
            lambda angle: self._controller.change_angle(self.anglesWidget.layout().count(), angle))

    @pyqtSlot()
    def on_angle_removed(self):
        widget = self.angles_dict.pop(self.anglesWidget.layout().count())
        widget.deleteLater()

class OpticalOperatorController(QtCore.QObject):
    """
    Controller class for handeling Optical operator logic
    """

    def __init__(self, model, *args, **kwargs):
        super(OpticalOperatorController, self).__init__(*args, **kwargs)
        if not isinstance(model, OpticalOperatorModel):
            raise TypeError(f'Cannot create {self.__class__.__name__} for {model!r}: Invalid type {type(model)}')
        self._model = model

    @pyqtSlot(float)
    def change_z(self, value):
        self._model.z = value

    @pyqtSlot(float)
    def change_offset(self, value):
        self._model.offset = value

    @pyqtSlot(float)
    def change_size(self, value):
        self._model.size = value

    @pyqtSlot(float)
    def change_value(self, value):
        self._model.value = value

    @pyqtSlot(str)
    def change_label(self, value):
        self._model.label = value


class OpticalOperatorView(QtWidgets.QWidget):
    """
    View class for viewing and controlling OpticalOperators.
    """

    def __init__(self, operator, *args, **kwargs):
        super(OpticalOperatorView, self).__init__(*args, **kwargs)
        if not isinstance(operator, OpticalOperator):
            raise TypeError(f'Cannot create {self.__class__.__name__} for {operator!r}: Invalid type {type(operator)}')

        self._model = OpticalOperatorModel(operator)
        self._controller = OpticalOperatorController(self._model)

        if self.parent() is None:
            self.setLayout(QtWidgets.QGridLayout())
            self.layout().addWidget(QtWidgets.QLabel('Type'), 0, 0)
            self.layout().addWidget(QtWidgets.QLabel('Name'), 0, 1)
            self.layout().addWidget(QtWidgets.QLabel('Z'), 0, 2)
            self.layout().addWidget(QtWidgets.QLabel('X'), 0, 3)
            self.layout().addWidget(QtWidgets.QLabel('Value'), 0, 4)
            self.layout().addWidget(QtWidgets.QLabel(''), 0, 5)
        else:
            if not isinstance(self.parent().layout(), QtWidgets.QGridLayout):
                raise TypeError(
                    f'Layout {self.parent().layout()!r} of {self.parent()!r} must be a QGridLayout, not {type(self.parent().layout())}')
            # self.setLayout(self.parent().layout())

        self.typeLabel = QtWidgets.QLabel(f'{self._model.optical_operator.__class__.__name__}')
        self.labelLineEdit = QtWidgets.QLineEdit(self)
        self.zSpinBox = QtWidgets.QDoubleSpinBox(self)
        self.offsetSpinBox = QtWidgets.QDoubleSpinBox(self)
        self.valueSpinBox = QtWidgets.QDoubleSpinBox(self)
        self.removeButton = QtWidgets.QPushButton('Remove', self)

        row = self.parent().layout().rowCount() + 1
        self.parent().layout().addWidget(self.typeLabel, row, 0)
        self.parent().layout().addWidget(self.labelLineEdit, row, 1)
        self.parent().layout().addWidget(self.zSpinBox, row, 2)
        self.parent().layout().addWidget(self.offsetSpinBox, row, 3)
        self.parent().layout().addWidget(self.valueSpinBox, row, 4)
        self.parent().layout().addWidget(self.removeButton, row, 5)

        # Connect auxilliary widgets to self
        self.removeButton.clicked.connect(self.on_remove_button_pressed)

        # Connect widgets to controller
        self.labelLineEdit.textEdited.connect(self._controller.change_label)
        self.zSpinBox.valueChanged.connect(self._controller.change_z)
        self.offsetSpinBox.valueChanged.connect(self._controller.change_offset)
        self.valueSpinBox.valueChanged.connect(self._controller.change_value)

        # Listen for model changes
        self._model.zChanged[float].connect(self.on_z_changed)
        self._model.offsetChanged[float].connect(self.on_offset_changed)
        self._model.labelChanged[str].connect(self.on_label_changed)
        self._model.valueChanged[float].connect(self.on_value_changed)

    @property
    def model(self):
        return self._model

    @property
    def controller(self):
        return self._controller

    @property
    def widgets(self):
        return [self.typeLabel, self.labelLineEdit, self.zSpinBox, self.offsetSpinBox, self.valueSpinBox,
                self.removeButton]

    @pyqtSlot(float)
    def on_z_changed(self, value):
        self.zSpinBox.setValue(value)

    @pyqtSlot(float)
    def on_offset_changed(self, value):
        self.offsetSpinBox.setValue(value)

    @pyqtSlot(float)
    def on_value_changed(self, value):
        self.valueSpinBox.setValue(value)

    @pyqtSlot(str)
    def on_label_changed(self, value):
        self.labelLineEdit.setText(value)

    @pyqtSlot()
    def on_remove_button_pressed(self):
        # Calling delete on all widgets of the view ensures that all listeneres for widget destructions are notified.
        self._model.deleteLater()  # Delete model
        self._controller.deleteLater()  # Delete controller
        [widget.deleteLater() for widget in self.widgets]  # Delete widgets
        self.deleteLater()  # Delete self
