from WaveOptics.Rays import *
from WaveOptics.gui.mplwidget import *
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore, Qt
from pathlib import Path
import sys


class LensWidget(QtWidgets.QWidget):
    def __init__(self, name, *args, **kwargs):
        super(LensWidget, self).__init__(*args, **kwargs)
        self.lensName = QtWidgets.QLineEdit(name)
        self.lensZ = QtWidgets.QDoubleSpinBox()
        self.lensX = QtWidgets.QDoubleSpinBox()
        self.lensF = QtWidgets.QDoubleSpinBox()

        self.lensZ.setPrefix('z: ')
        self.lensX.setPrefix('x: ')
        self.lensF.setPrefix('f: ')

        self.lensName.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        self.lensZ.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.lensX.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.lensF.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel('Name'))
        layout.addWidget(self.lensName)
        layout.addWidget(self.lensZ)
        layout.addWidget(self.lensX)
        layout.addWidget(self.lensF)
        layout.addStretch()


class SourceWidget(QtWidgets.QGroupBox):
    source_updated = Qt.pyqtSignal([])

    def __init__(self, source, *args, **kwargs):
        super(SourceWidget, self).__init__('Source', *args, **kwargs)
        self.source = source
        self.source_layout = QtWidgets.QGridLayout(self)
        self.source_layout.addWidget(QtWidgets.QLabel('Z'), 0, 0)
        self.source_layout.addWidget(QtWidgets.QLabel('X'), 0, 1)
        self.source_layout.addWidget(QtWidgets.QLabel('Size'), 0, 2)
        self.source_layout.addWidget(QtWidgets.QLabel('Angle'), 0, 3)

        self.zWidget = QtWidgets.QDoubleSpinBox()
        self.xWidget = QtWidgets.QDoubleSpinBox()
        self.sizeWidget = QtWidgets.QDoubleSpinBox()
        self.angleWidget = QtWidgets.QDoubleSpinBox()
        self.source_layout.addWidget(self.zWidget)
        self.source_layout.addWidget(self.xWidget)
        self.source_layout.addWidget(self.sizeWidget)
        self.source_layout.addWidget(self.angleWidget)

        self.angleWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.angleWidget.setDecimals(1)
        self.angleWidget.setMaximum(180)
        self.angleWidget.setMinimum(-180)
        self.angleWidget.setValue(0)
        self.angleWidget.setSingleStep(0.1)
        for widget in [self.zWidget, self.xWidget, self.sizeWidget]:
            widget.setDecimals(2)
            widget.setSingleStep(0.05)
            widget.setMinimum(-999)
            widget.setMaximum(999)
            widget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

        self.zWidget.setValue(self.source.z)
        self.xWidget.setValue(self.source.offset)
        self.sizeWidget.setValue(self.source.size)
        self.angleWidget.setValue(self.source.angles[0])

        self.zWidget.valueChanged.connect(self.source.set_z)
        self.xWidget.valueChanged.connect(self.source.set_offset)
        self.sizeWidget.valueChanged.connect(self.source.set_size)
        self.angleWidget.valueChanged.connect(lambda x: self.source.set_angles([-x, x]))
        for widget in [self.zWidget, self.xWidget, self.sizeWidget, self.angleWidget]:
            widget.valueChanged.connect(self.source_updated)


class ScreenWidget(QtWidgets.QGroupBox):
    screen_updated = Qt.pyqtSignal([])

    def __init__(self, screen, *args, **kwargs):
        super(ScreenWidget, self).__init__('Screen', *args, **kwargs)
        self.screen = screen
        self.setLayout(QtWidgets.QHBoxLayout(self))
        self.zWidget = QtWidgets.QDoubleSpinBox()
        self.zWidget.setDecimals(2)
        self.zWidget.setMinimum(-999)
        self.zWidget.setMaximum(999)
        self.zWidget.setSingleStep(0.05)
        self.zWidget.setValue(screen.z)
        self.zWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.zWidget.valueChanged.connect(screen.set_z)
        self.zWidget.valueChanged.connect(self.screen_updated)
        self.layout().addWidget(QtWidgets.QLabel('Z:'))
        self.layout().addWidget(self.zWidget)


class OpticalSystemWidget(QtWidgets.QWidget):
    optical_system_updated = Qt.pyqtSignal([])

    def __init__(self, microscope, *args, **kwargs):
        super(OpticalSystemWidget, self).__init__(*args, **kwargs)

        self.model = microscope
        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.source_widget = SourceWidget(self.model.source)
        self.source_widget.source_updated.connect(self.optical_system_updated)
        self.screen_widget = ScreenWidget(self.model.screen)
        self.screen_widget.screen_updated.connect(self.optical_system_updated)
        self.system_group = QtWidgets.QGroupBox('System')
        self.system_group.setLayout(QtWidgets.QVBoxLayout())
        self.system_scroll = QtWidgets.QScrollArea(self.system_group)
        self.system_group.layout().addWidget(self.system_scroll)
        self.system_scroll.setLayout(QtWidgets.QVBoxLayout())
        self.system_widget = QtWidgets.QWidget(self.system_scroll)
        self.system_scroll.setWidget(self.system_widget)
        self.system_scroll.setWidgetResizable(True)
        self.system_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.system_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #self.system_widget.setWidgetResizable(True)
        #self.system_group.layout().addWidget(self.system_widget)
        self.addLens = QtWidgets.QPushButton('Add Lens')
        self.addDeflector = QtWidgets.QPushButton('Add Deflector')
        self.addLens.clicked.connect(lambda: self.add_element(kind=Lens))
        self.addLens.clicked.connect(self.optical_system_updated)
        self.addDeflector.clicked.connect(lambda: self.add_element(kind=Deflector))
        self.addDeflector.clicked.connect(self.optical_system_updated)
        self.printSystem = QtWidgets.QPushButton('Print system')
        self.printSystem.clicked.connect(lambda: print(f'{self.model}'))

        self.layout().addWidget(self.source_widget)
        self.layout().addWidget(self.system_group)
        self.layout().addWidget(self.addLens)
        self.layout().addWidget(self.addDeflector)
        self.layout().addWidget(self.screen_widget)
        self.layout().addWidget(self.printSystem)

        self.system_layout = QtWidgets.QGridLayout(self.system_widget)
        #self.system_widget.setLayout(self.system_layout)
        self.system_layout.addWidget(QtWidgets.QLabel('Type'), 0, 0)
        self.system_layout.addWidget(QtWidgets.QLabel('Name'), 0, 1)
        self.system_layout.addWidget(QtWidgets.QLabel('Z'), 0, 2)
        self.system_layout.addWidget(QtWidgets.QLabel('X'), 0, 3)
        self.system_layout.addWidget(QtWidgets.QLabel('Value'), 0, 4)
        self.widgets = {}

        [self.add_element(operator) for operator in self.model if not isinstance(operator, Propagator)]

    def get_next_name(self, kind):
        """
        Return the next generic name of the element of `kind`
        :param kind:
        :return:
        """

        taken_labels = [element.label for element in self.model if isinstance(element, kind)]
        if kind is Lens:
            prefix = 'L'
        elif kind is Deflector:
            prefix = 'D'
        else:
            prefix = 'O'
        labels = [f'{prefix}{n}' for n in range(self.model.length(kind))]
        for label in labels:
            if label in taken_labels:
                pass
            else:
                return label

    def add_element(self, optical_operator=None, kind=None):
        if optical_operator is None:
            if kind is None:
                kind = Lens
            else:
                optical_operator = kind(1, z=self.model.screen.z)
        else:
            kind = type(optical_operator)

        # Rename default widget names
        if optical_operator.label == '':
            optical_operator.label = self.get_next_name(kind)

        if not isinstance(optical_operator, OpticalOperator):
            raise TypeError(f'Only objects of type `OpticalOperator` can be added to {self.__class__.__name}')
        if optical_operator in self.model:
            warn(f'Operator {optical_operator!r} is already in {self.model!r}')
        else:
            self.model.append(optical_operator)
        self.model.sort_operators()
        self.model.fill()

        if optical_operator.label in self.widgets:
            warn(f'Warning, changing label of {optical_operator!r}, as there already exists a widget for that label.')
            optical_operator.label = self.get_next_name(kind)

        type_widget = QtWidgets.QLabel(f'{optical_operator.__class__.__name__}')

        label_widget = QtWidgets.QLineEdit()
        label_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        label_widget.returnPressed.connect(self.optical_system_updated)

        remove_widget = QtWidgets.QPushButton('Remove')
        remove_widget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

        z_widget = QtWidgets.QDoubleSpinBox()
        x_widget = QtWidgets.QDoubleSpinBox()
        value_widget = QtWidgets.QDoubleSpinBox()
        for widget in [z_widget, x_widget, value_widget]:
            widget.setDecimals(2)
            widget.setSingleStep(1)
            widget.setMinimum(-999)
            widget.setMaximum(999)
            widget.valueChanged.connect(self.optical_system_updated)
            widget.valueChanged.connect(lambda: print(optical_operator))
            self.optical_system_updated.connect(lambda: print('hei!'))
            widget.setKeyboardTracking(False)
            widget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

        label_widget.setText(optical_operator.label)
        z_widget.setValue(optical_operator.z)
        x_widget.setValue(optical_operator.offset)
        value_widget.setValue(optical_operator.value)

        label_widget.textEdited.connect(lambda text: self.rename_element(optical_operator, text))
        z_widget.valueChanged.connect(lambda z: optical_operator.set_z(z))
        x_widget.valueChanged.connect(lambda x: optical_operator.set_offset(x))
        value_widget.valueChanged.connect(lambda value: optical_operator.set_value(value))
        remove_widget.clicked.connect(lambda: self.remove_element(optical_operator))
        remove_widget.clicked.connect(self.optical_system_updated)

        self.widgets[optical_operator.label] = {'Operator': optical_operator,
                                                'Widgets':
                                                    {'Type': type_widget,
                                                     'Name': label_widget,
                                                     'Z': z_widget,
                                                     'X': x_widget,
                                                     'Value': value_widget,
                                                     'Remove': remove_widget
                                                     }
                                                }

        row = self.system_layout.rowCount()
        self.system_layout.addWidget(type_widget, row, 0)
        self.system_layout.addWidget(label_widget, row, 1)
        self.system_layout.addWidget(z_widget, row, 2)
        self.system_layout.addWidget(x_widget, row, 3)
        self.system_layout.addWidget(value_widget, row, 4)
        self.system_layout.addWidget(remove_widget, row, 5)
        self.optical_system_updated.emit()

    def remove_element(self, optical_operator):
        if not isinstance(optical_operator, OpticalOperator):
            raise TypeError(f'Only objects of type `OpticalOperator` can be removed from {self.__class__.__name}')
        if not optical_operator in self.model:
            raise IndexError(f'Cannot remove {optical_operator!r} from {self.model!r} because it is not a member.')
        widgets = self.widgets.pop(optical_operator.label)
        for widget in widgets['Widgets'].values():
            widget.setParent(None)
        self.model.remove(optical_operator)
        del optical_operator
        self.optical_system_updated.emit()

    def rename_element(self, operator, new_name):
        if not isinstance(operator, OpticalOperator):
            raise TypeError(
                f'Cannot set name of Operator {operator!r} to {new_name!r}, the operator is not an OpticalOperator.')
        if not operator in self.model:
            raise IndexError(
                f'Cannot set name of Operator {operator!r} to {new_name!r}, the operator is not a member of {self.model!r}')
        if new_name in self.widgets:
            raise ValueError(
                f'Cannot set name of Operator {operator!r} to {new_name!r}, the name is already used for a different operator in {self.widgets!r}')
        self.widgets[new_name] = self.widgets.pop(operator.label)  # Change key
        operator.set_label(new_name)  # Change label


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setCentralWidget(QtWidgets.QWidget())
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralWidget())

        self.horizontalLayout = QtWidgets.QHBoxLayout()

        self.plotWidget = MplWidget(self)
        self.horizontalLayout.addWidget(self.plotWidget)

        self.microscope = JEM2100F()
        self.operatorPanel = OpticalSystemWidget(microscope=self.microscope)
        self.operatorPanel.optical_system_updated.connect(self.refresh)
        self.horizontalLayout.addWidget(self.operatorPanel)

        # Create style controls
        self.lensStyleWidgets = {
            'Lenses': {
                'lw': QtWidgets.QDoubleSpinBox(),
                'ls': QtWidgets.QComboBox(),
                'color': QtWidgets.QComboBox(),
                'alpha': QtWidgets.QDoubleSpinBox()},
            'Focal planes': {
                'lw': QtWidgets.QDoubleSpinBox(),
                'ls': QtWidgets.QComboBox(),
                'color': QtWidgets.QComboBox(),
                'alpha': QtWidgets.QDoubleSpinBox()},
            'Deflectors': {
                'lw': QtWidgets.QDoubleSpinBox(),
                'ls': QtWidgets.QComboBox(),
                'color': QtWidgets.QComboBox(),
                'alpha': QtWidgets.QDoubleSpinBox()}
        }
        for category in self.lensStyleWidgets:
            for style in self.lensStyleWidgets[category]:
                widget = self.lensStyleWidgets[category][style]
                if style == 'lw':
                    widget.setMinimum(0)
                    widget.setMaximum(99.99)
                    widget.setDecimals(2)
                    widget.setSingleStep(0.1)
                    if category == 'Deflectors':
                        widget.setValue(0.25)
                    elif category == 'Focal planes':
                        widget.setValue(0.5)
                    else:
                        widget.setValue(1)
                    widget.setSuffix(' pt')
                elif style == 'ls':
                    widget.addItems(['-', ':', '--', '-.'])
                    if category == 'Deflectors':
                        widget.setCurrentIndex(3)
                    elif category == 'Focal planes':
                        widget.setCurrentIndex(2)
                    else:
                        pass
                elif style == 'color':
                    widget.addItems(['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w'])
                    if category == 'Deflectors':
                        widget.setCurrentIndex(2)
                    elif category == 'Focal planes':
                        widget.setCurrentIndex(1)
                    else:
                        pass
                elif style == 'alpha':
                    widget.setMinimum(0)
                    widget.setMaximum(1)
                    widget.setDecimals(2)
                    if category == 'Deflectors':
                        widget.setValue(0.25)
                    elif category == 'Focal planes':
                        widget.setValue(0.5)
                    else:
                        widget.setValue(0.75)
                    widget.setSingleStep(0.1)
                if isinstance(widget, QtWidgets.QComboBox):
                    widget.currentIndexChanged.connect(self.refresh)
                elif isinstance(widget, QtWidgets.QDoubleSpinBox):
                    widget.valueChanged.connect(self.refresh)
        self.styleLayout = QtWidgets.QVBoxLayout()
        self.lensStyleGroupBox = QtWidgets.QGroupBox('Lens style')
        self.lensStyleLayout = QtWidgets.QGridLayout(self.lensStyleGroupBox)
        for i, category in enumerate(self.lensStyleWidgets):
            self.lensStyleLayout.addWidget(QtWidgets.QLabel(category), 0, i + 1)
            for k, style in enumerate(self.lensStyleWidgets[category]):
                if i == 0:
                    self.lensStyleLayout.addWidget(QtWidgets.QLabel(style), k + 1, 0)
                self.lensStyleLayout.addWidget(self.lensStyleWidgets[category][style], k + 1, i + 1)
        self.styleLayout.addWidget(self.lensStyleGroupBox)

        # Create axis limits controls
        self.axisLimitControlGroupBox = QtWidgets.QGroupBox('Axis control')
        self.axisLimitControlWidgets = dict(
            [(label, QtWidgets.QDoubleSpinBox()) for label in ['xmin', 'xmax', 'ymin', 'ymax']])
        [widget.valueChanged.connect(self.refresh) for widget in self.axisLimitControlWidgets.values()]
        [widget.setDecimals(2) for widget in self.axisLimitControlWidgets.values()]
        [widget.setSingleStep(0.1) for widget in self.axisLimitControlWidgets.values()]
        self.axisLimitControlWidgets['auto'] = QtWidgets.QCheckBox()
        self.axisLimitControlWidgets['auto'].setChecked(True)
        self.axisLimitControlWidgets['auto'].clicked.connect(self.refresh)
        self.axisLimitControlGroupBox.setLayout(QtWidgets.QGridLayout())
        for i, label in enumerate(self.axisLimitControlWidgets):
            widget = self.axisLimitControlWidgets[label]
            self.axisLimitControlGroupBox.layout().addWidget(QtWidgets.QLabel(label), 0, i)
            self.axisLimitControlGroupBox.layout().addWidget(widget, 1, i)
        self.styleLayout.addWidget(self.axisLimitControlGroupBox)

        self.mainLayout.addLayout(self.horizontalLayout)
        self.mainLayout.addLayout(self.styleLayout)

        self.refresh()

    def refresh(self):
        self.plotWidget.canvas.ax.cla()
        self.operatorPanel.model.fill()
        self.plot()

    def update_plot_limits(self):
        current_limits = [self.plotWidget.canvas.ax.get_xlim(), self.plotWidget.canvas.ax.get_ylim()]
        self.axisLimitControlWidgets['xmin'].setMaximum(current_limits[0][1] * 0.99)
        self.axisLimitControlWidgets['xmin'].setMinimum(current_limits[0][0])
        self.axisLimitControlWidgets['xmax'].setMaximum(current_limits[0][1])
        self.axisLimitControlWidgets['xmax'].setMinimum(current_limits[0][0] * 0.99)
        self.axisLimitControlWidgets['ymin'].setMaximum(current_limits[1][1] * 0.99)
        self.axisLimitControlWidgets['ymin'].setMinimum(current_limits[1][0])
        self.axisLimitControlWidgets['ymax'].setMaximum(current_limits[1][1])
        self.axisLimitControlWidgets['ymax'].setMinimum(current_limits[1][0] * 0.99)
        if self.axisLimitControlWidgets['auto'].isChecked():
            for label in self.axisLimitControlWidgets:
                widget = self.axisLimitControlWidgets[label]
                if isinstance(widget, QtWidgets.QDoubleSpinBox):
                    if 'min' in label:
                        widget.setValue(widget.minimum())
                    else:
                        widget.setValue(widget.maximum())

    def plot(self):
        lens_kwargs = dict([(style, self.lensStyleWidgets['Lenses'][style].value()) if isinstance(
            self.lensStyleWidgets['Lenses'][style], (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)) else (
            style, self.lensStyleWidgets['Lenses'][style].currentText()) for style in self.lensStyleWidgets['Lenses']])
        focal_plane_kwargs = dict([(style, self.lensStyleWidgets['Focal planes'][style].value()) if isinstance(
            self.lensStyleWidgets['Focal planes'][style], (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)) else (
            style, self.lensStyleWidgets['Focal planes'][style].currentText()) for style in self.lensStyleWidgets['Focal planes']])
        lens_kwargs['focal_plane_kwargs'] = focal_plane_kwargs
        deflector_kwargs = dict([(style, self.lensStyleWidgets['Deflectors'][style].value()) if isinstance(
            self.lensStyleWidgets['Deflectors'][style], (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)) else (
            style, self.lensStyleWidgets['Deflectors'][style].currentText()) for style in self.lensStyleWidgets['Deflectors']])

        print(focal_plane_kwargs)
        # self.plotWidget.canvas.ax.plot(np.arange(10), np.arange(10) ** 2, **kwargs)
        # self.operatorPanel.model.sort()
        self.operatorPanel.model.show(ax=self.plotWidget.canvas.ax, annotate=False, operator_kwargs = {'lenses': lens_kwargs, 'deflectors': deflector_kwargs}, operators=self.microscope)  # , **kwargs)
        self.plotWidget.canvas.draw()
        self.update_plot_limits()
        if self.axisLimitControlWidgets['auto'].isChecked():
            pass
        else:
            self.plotWidget.canvas.ax.set_xlim(self.axisLimitControlWidgets['xmin'].value(),
                                               self.axisLimitControlWidgets['xmax'].value())
            self.plotWidget.canvas.ax.set_ylim(self.axisLimitControlWidgets['ymin'].value(),
                                               self.axisLimitControlWidgets['ymax'].value())
        self.plotWidget.canvas.draw()


def main():
    myqui = QtWidgets.QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(myqui.exec_())


if __name__ == '__main__':
    main()
