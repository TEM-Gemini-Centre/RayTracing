import numpy as np
import matplotlib.pyplot as plt
from warnings import warn

class Error(Exception):
    pass


class RayTraceError(Error):
    pass

class Ray(object):
    def __init__(self, x, angle, z, label=''):
        """
        Create a ray
        :param x: Distance of the ray origin from the optical axis
        :param angle: The angle of the ray relative to the optical axis in radians.
        :param z: The z-position of the ray. Only used for plotting purposes.
        :param label: The label of the ray. Default is ""
        :type x: float
        :type angle: float
        :type label: str
        """
        self.x = x
        self.z = z
        self.angle = angle
        self.label = label

    @property
    def matrix(self):
        return np.array([[self.x], [self.angle_rad]])

    @property
    def matrix_deg(self):
        return np.array([[self.x], [self.angle_deg]])

    @property
    def angle_deg(self):
        return self.angle_rad * 180 / np.pi

    @property
    def angle_rad(self):
        return self.angle

    def __format__(self, format_spec):
        try:
            precision = int(format_spec.split('.')[1][0])
        except IndexError as e:
            precision = None

        if precision is None:
            precision = 2
        with np.printoptions(suppress=True, precision=precision):
            return '{self.matrix_deg}'.format(self=self)

    def __str__(self):
        return '{self.__class__.__name__} "{self.label}" starting at {self.z}: [{self.x}, {self.angle_deg}]'.format(
            self=self)

    def __repr__(self):
        return '{self.__class__.__name__}({self.x!r}, {self.angle!r}, {self.z!r}, label={self.label!r})'.format(
            self=self)


class OpticalOperator(object):
    def __init__(self, value, offset=0, size=0, z=0, label=''):
        """
        Create an optical ABCD operator.

        :param value: The value or strength of the operator
        :param offset: The offset of the operator away from the optical axis
        :param size: The size of the element, used for plotting.
        :param z: The position of the element, used for plotting.
        :param label: The label of the operator
        :type value: Union[int, float, function]
        :type offset: float
        :type size: float
        :type z: float
        :type label: str
        """
        self._offset = offset
        self._size = size
        self._z = z
        self._value = value
        self._label = label

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self._z = value

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value!r}, {self.offset}, {self.size}, {self.z}, label={self.label}'

    def __str__(self):
        return f'{self.__class__.__name__} "{self.label}":\n\tvalue = {self.value}\n\toffset = {self.offset}\n\tsize = {self.size}\n\tz = {self.z}'

    def __mul__(self, other):
        raise NotImplemented

    def show(self, *args, ax=None, annotate=True, **kwargs):
        """
        Show the element on an axes object

        :param args: Optional positional arguments passed to plt.plot()
        :param ax: The axes to show object on. Default is None, in which case a new axis will be created.
        :param kwargs: Optional keyword arguments passed to plt.plot()
        :return: fig, ax
        """
        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = ax.get_figure()
        line = ax.axhline(self.z, *args, **kwargs)
        if annotate:
            ax.annotate(self.label, xy=(self.offset, self.z), ha='center', va='top',
                        transform=ax.transAxes)
        return fig, ax, [line]


class Propagator(OpticalOperator):
    def __init__(self, distance, *args, **kwargs):
        """
        Create a propagator for a given distance
        :param distance: The distance to propagate waves
        :type distance: float
        """
        super(Propagator, self).__init__(distance, *args, **kwargs)

    def __mul__(self, other):
        if isinstance(other, Ray):
            return Ray(other.x + np.tan(other.angle) * self.value, other.angle, other.z + self.value,
                       label=f'{self.label}({other.label})')
        else:
            raise TypeError(f'Invalid type: {self!r} cannot operate on {other!r}.')

    def show(self, *args, **kwargs):
        pass


class Lens(OpticalOperator):
    def __init__(self, focal_length, *args, **kwargs):
        """
        Create a lens of a given focal length
        :param focal_length: The focal length of the lens
        :type focal_length: float
        """
        super(Lens, self).__init__(focal_length, *args, **kwargs)

    def __mul__(self, other):
        if isinstance(other, Ray):
            x = self.offset - other.x
            if x == 0:
                angle = other.angle_rad
            elif self.value == 0:
                angle = np.inf * np.sign(x)
            else:
                angle = other.angle_rad + np.arcsin(-x / np.sqrt(x ** 2 + self.value ** 2))
            return Ray(other.x, angle, other.z, label=f'{self.label}({other.label})')
        else:
            raise TypeError(f'Invalid type: {self!r} cannot operate on {other!r}.')

    def show(self, *args, ax=None, annotate=False, focal_plane_args=[], focal_plane_kwargs={}, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()
        fig, ax, line = super().show(*args, ax=ax, annotate=annotate, **kwargs)
        f_line_1 = ax.axhline(self.z + abs(self.value), **focal_plane_kwargs)
        f_line_2 = ax.axhline(self.z - abs(self.value), **focal_plane_kwargs)
        if annotate:
            ax.annotate('{self.label} BFP'.format(self=self),
                        xy=(self.offset, self.z - self.focal_length), ha='center', va='top',
                        transform=ax.transAxes)
            ax.annotate('{self.label} FFP'.format(self=self),
                        xy=(self.offset, self.z + self.focal_length), ha='center', va='top',
                        transform=ax.transAxes)

        return fig, ax, line + [f_line_1, f_line_2]


class Deflector(OpticalOperator):
    """ A deflection operator"""

    def __init__(self, angle, *args, **kwargs):
        """
        Create a deflector operator

        The deflector adds a constant angle to the ray, independently on its lateral distance from the optical axis.
        :param angle: The anglular offset, in degrees
        :param args: Optional positional arguments passed to OpticalOperator constructor
        :param kwargs: Optional keyword arguments passed to OpticalOperator constructor.
        """
        super(Deflector, self).__init__(angle, *args, **kwargs)

    def __mul__(self, other):
        if isinstance(other, Ray):
            return Ray(other.x, other.angle_rad + self.value * np.pi / 180, other.z,
                       label=f'{self.label}({other.label})')
        else:
            raise TypeError(f'Invalid type: {self!r} cannot operate on {other!r}.')


class Source(object):
    """A source for an optical system"""

    def __init__(self, z, angles, size=0, offset=0, points=1, label='Source'):
        self._z = z
        self._label = label
        self._size = size
        self._angles = angles
        self._offset = offset
        self._points = points

    def __repr__(self):
        return f'{self.__class__.__name__}({self.z!r}, {self.angles!r}, size={self.size!r}, offset={self.offset!r}, points={self.points!r}, label={self.label!r})'

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        if isinstance(value, (int, float)):
            self._z = value
        else:
            raise TypeError(f'Cannot set {self.__class__.__name__}.z of {self!r}. Only ints and floats are accepted.')

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        if isinstance(value, str):
            self._label = value
        else:
            raise TypeError(f'Cannot set {self.__class__.__name__}.label of {self!r}. Only `str` objects are accepted.')

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if isinstance(value, (int, float)):
            self._size = value
        else:
            raise TypeError(
                f'Cannot set {self.__class__.__name__}.size of {self!r}. Only ints and floats are accepted.')

    @property
    def angles(self):
        return self._angles

    @angles.setter
    def angles(self, value):
        if isinstance(value, (list, tuple, np.ndarray)):
            if np.size(np.shape(value)) == 1:
                self._angles = np.array(value)
            else:
                raise TypeError(
                    f'Cannot set {self.__class__.__name__}.angles of {self!r}. Only 1D array objects are accepted.')
        else:
            raise TypeError(
                f'Cannot set {self.__class__.__name__}.angles of {self!r}. Only lists, tuples, and numpy-arrays are accepted.')

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        if isinstance(value, (int, float)):
            self._offset = value
        else:
            raise TypeError(
                f'Cannot set {self.__class__.__name__}.offset of {self!r}. Only ints and floats are accepted.')

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, value):
        if isinstance(value, int):
            if value > 0:
                self._points = value
            else:
                raise TypeError(
                    f'Cannot set {self.__class__.__name__}.points of {self!r}. Only positive ints are accepted.')
        else:
            raise TypeError(f'Cannot set {self.__class__.__name__}.points of {self!r}. Only ints are accepted.')

    def emit(self):
        rays = []
        i = 0
        xs = np.linspace(self.offset - self.size / 2, self.offset + self.size / 2, num=self.points)
        for x in xs:
            for angle in self.angles:
                rays.append(Ray(x, angle * np.pi / 180, z=self.z, label='R{i}'.format(i=i)))
                i += 1
                if all([self.angles[i] == angle for i in
                        range(len(self.angles))]):  # Do not repeat if all angles are the same
                    break
            if self.size == 0:  # Do not replicate rays if source is infinitesimal.
                break
        return rays


class Screen(object):
    """A screen for rays to draw on"""

    def __init__(self, z, label='Screen'):
        self._z = z
        self._label = label

    def __repr__(self):
        return '{self.__class__.__name__}({self.z!r}, label={self.label!r})'.format(self=self)

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        if isinstance(value, (int, float)):
            self._z = value
        else:
            raise TypeError(f'Cannot set {self.__class__.__name__}.z of {self!r}. Only ints and floats are accepted.')

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        if isinstance(value, str):
            self._label = value
        else:
            raise TypeError(f'Cannot set {self.__class__.__name__}.label of {self!r}. Only str objects are accepted.')

    def show(self, *args, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = ax.figure()

        ax.axhline(self.z, *args, **kwargs)
        return fig, ax


class RayTrace(list):
    def __init__(self, rays, label=''):
        """
        Create a new ray trace
        :param rays: The rays to trace. Must be given in the same order as to be traced
        :param label: The label of the raytrace
        :type rays: list
        :type label: str
        """
        if not all([isinstance(ray, Ray) for ray in rays]):
            raise TypeError('All objects in {rays!r} must be of type Ray.'.format(rays=rays))
        super(RayTrace, self).__init__(rays)
        self.label = label

    @property
    def rays(self):
        return [ray for ray in self]

    def __repr__(self):
        return f'{self.__class__.__name__}({self.rays!r}, label={self.label})'

    def __str__(self):
        rays = '\n\t'.join([str(ray) for ray in self])
        return f'{self.__class__.__name__} "{self.label}":\n\t{rays}'

    def __call__(self, *args, **kwargs):
        try:
            return self.trace(*args, **kwargs)
        except RayTraceError as e:
            warn(e)
            if len(self) > 0:
                warn('Reinitializing raytrace')
                self.initialize(self[0].x, self[0].angle, self[0].z, self[0].label)
            else:
                raise

    def initialize(self, *args, **kwargs):
        """
        Initialize the ray trace

        Clears the ray trace and creates a new initial ray.

        :param args: Positional arguments passed to Ray constructor
        :param kwargs: Keyword arguments passed to Ray constructor.
        :return: The ray trace
        :rtype: RayTrace
        """

        self.clear()
        self.append(Ray(*args, **kwargs))
        return self

    def trace(self, operators, set_z=True):
        if len(self) != 1:
            raise RayTraceError(
                f'Can only trace rays if ray trace {self!r} has only a single given ray (the initial ray)')

        for operator in operators:
            if isinstance(operator, OpticalOperator):
                self.append(operator * self[-1])
                if set_z:
                    operator.z = self[-1].z

        return self

    def show(self, *args, ax=None, annotate=True, operators=None, operator_args=None, operator_kwargs=None, **kwargs):
        if operator_kwargs is None:
            operator_kwargs = dict()

        if operator_args is None:
            operator_args = dict()

        # Default operator args:
        operator_args['lenses'] = operator_args.get('lenses', [])

        operator_args['deflectors'] = operator_args.get('deflectors', [])

        # Default operator_kwargs:
        operator_kwargs['lenses'] = operator_kwargs.get('lenses', {})
        operator_kwargs['lenses']['focal_plane_args'] = operator_kwargs['lenses'].get('focal_plane_args', ['--k'])
        operator_kwargs['lenses']['focal_plane_kwargs'] = operator_kwargs['lenses'].get('focal_plane_kwargs', {})
        operator_kwargs['lenses']['focal_plane_kwargs']['alpha'] = operator_kwargs['lenses']['focal_plane_kwargs'].get(
            'alpha', 0.25)

        operator_kwargs['deflectors'] = operator_kwargs.get('deflectors', {})
        operator_kwargs['deflectors']['alpha'] = operator_kwargs['deflectors'].get('alpha', 0.25)
        operator_kwargs['deflectors']['color'] = operator_kwargs['deflectors'].get('color', 'r')
        operator_kwargs['deflectors']['ls'] = operator_kwargs['deflectors'].get('ls', '--')

        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = ax.get_figure()
        lines = ax.plot([ray.x for ray in self], [ray.z for ray in self], *args, **kwargs)
        if annotate:
            [ax.annotate(ray.label, xy=(ray.x, ray.z), ha='left', va='center',
                         transform=ax.transAxes) if ray.x > 0 else ax.annotate(ray.label, xy=(ray.x, ray.z), ha='right',
                                                                               va='center', transform=ax.transAxes) for
             ray in self]

        if operators is not None:
            for operator in operators:
                if isinstance(operator, Lens):
                    operator.show(*operator_args['lenses'], ax=ax, **operator_kwargs['lenses'])
                elif isinstance(operator, Deflector):
                    operator.show(*operator_args['deflectors'], ax=ax, **operator_kwargs['deflectors'])
                else:
                    operator.show(ax=ax)

        return fig, ax, lines

class OpticalSystem(list):
    """A collection of optical operators"""

    def __init__(self, source, operators, screen, label='Optical system'):
        """
        Create an optical system.
        :param source: The source (start) of the optical system
        :param operators: A list of operators to add to the optical system
        :param screen: The screen (end) of the optical system
        :param label: The label of the optical system
        :type source: Source
        :type operators: iterable
        :type screen: Screen
        :type label: str
        """
        if not all([isinstance(operator, OpticalOperator) for operator in operators]):
            raise TypeError(f'All elements in {operators!r} must be an OpticalOperator')
        super(OpticalSystem, self).__init__(operators)
        self.label = label
        self.source = source
        self.screen = screen
        self.fill()

    @property
    def trace(self):
        return [RayTrace([initial_ray], label='RT{i}'.format(i=i)).trace(self, set_z=False) for i, initial_ray in
                enumerate(self.source.emit())]

    def __getitem__(self, item):
        if isinstance(item, str):
            matches = [operator for operator in self if operator.label == item]
            if len(matches) == 0:
                raise IndexError(f'No operator with label {item!r} in {self!r}')
            elif len(matches) > 1:
                raise IndexError(
                    f'Cannot determine which item to return: {len(matches)} matches found for label {item!r} in {self!r}')
            else:
                matches = matches.pop()
            return matches
        else:
            return super().__getitem__(item)

    def __isub__(self, other):
        if not isinstance(other, OpticalOperator):
            raise TypeError(f'Cannot remove {other!r} from {self!r}: Invalid type {type(other)}')
        self.remove(other)

    def __iadd__(self, other):
        if not isinstance(other, OpticalOperator):
            raise TypeError(f'Cannot add {other!r} to {self!r}: Invalid type {type(other)}')
        self.append(other)

    def __repr__(self):
        return '{self.__class__.__name__}({self.source!r}, {l}, {self.screen!r}, label={self.label!r})'.format(
            l=super().__repr__(), self=self)

    def __str__(self):
        return '{self.label}:\n-{self.source!r}\n-{t}\n-{self.screen!r}'.format(self=self, t='\n-'.join(
            '{!r}'.format(operator) for operator in self))

    def sort_operators(self, reverse=True):
        """Sort the operators by z"""
        self.sort(key=lambda operator: operator.z)
        if reverse:
            self.reverse()

    def length(self, kind=None):
        if kind is None:
            return len(self)
        else:
            return len([operator for operator in self if isinstance(operator, kind)])

    def fill(self):
        """Fill the optical system with the necessary propagators"""
        # Remove old propagators:
        super(OpticalSystem, self).__init__([operator for operator in self if not isinstance(operator, Propagator)])
        # Sort
        self.sort_operators()
        # Create new propagators
        propagators = [Propagator(self[i + 1].z - self[i].z, z=self[i + 1].z, label='S{i}'.format(i=i + 1)) for i in
                       range(len(self)) if i < len(self) - 1]
        if len(self) == 0:
            propagators.insert(0, Propagator(self.screen.z - self.source.z, z=self.source.z, label='S0'))
        else:
            propagators.insert(0,
                               Propagator(self[0].z - self.source.z, z=self[0].z, label='S0'))  # Propagator from source
            propagators.insert(-1, Propagator(self.screen.z - self[-1].z, z=self.screen.z,
                                              label='S{i}'.format(i=len(self))))  # Propagator to screen.
        # Add propagators
        for propagator in propagators:
            self.append(propagator)

        # Sort operators again
        self.sort_operators()

    def show(self, *args, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()
        [trace.show(*args, ax=ax, **kwargs) for trace in self.trace]

