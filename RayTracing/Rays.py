import numpy as np
from warnings import warn
import matplotlib.pyplot as plt


class Error(Exception):
    pass


class RayTraceError(Error):
    pass


class MatrixComponent(object):
    """
    A raytracing matrix component
    """

    def __init__(self, component=None):
        """Create a matrix component for ray tracing analysis

        The component may be either linear or nonlinear. To create a non-linear component, supply a function rather than an object.

        :param component: The component value or function.
        :type component: Union[int, float, function]
        """
        self.component = component

    def __mul__(self, other):
        if callable(self.component):
            return self.component(other)
        else:
            if self.component is None:
                return None
            else:
                return self.component * other

    def __rmul__(self, other):
        if callable(self.component):
            raise NotImplemented
        else:
            if self.component is None:
                return None
            else:
                return other * self.component

    def __imul__(self, other):
        if callable(self.component):
            raise NotImplemented
        else:
            if self.component is None:
                return self
            else:
                self.component *= other
                return self

    def __truediv__(self, other):
        if callable(self.component):
            raise NotImplemented
        else:
            if self.component is None:
                return None
            else:
                return self.component / other

    def __rtruediv__(self, other):
        if callable(self.component):
            raise NotImplemented
        else:
            if self.component is None:
                return None
            else:
                return other / self.component

    def __itruediv__(self, other):
        if callable(self.component):
            raise NotImplemented
        else:
            if self.component is None:
                return None
            else:
                self.component /= other
                return self

    def __add__(self, other):
        if callable(self.component):
            raise NotImplemented
        else:
            if self.component is None:
                return None
            else:
                return self.component + other

    def __radd__(self, other):
        if callable(self.component):
            raise NotImplemented
        else:
            if self.component is None:
                return None
            else:
                return other + self.component

    def __iadd__(self, other):
        if callable(self.component):
            raise NotImplemented
        else:
            if self.component is None:
                return None
            else:
                self.component += other
                return self

    def __sub__(self, other):
        if callable(self.component):
            raise NotImplemented
        else:
            if self.component is None:
                return None
            else:
                return self.component - other

    def __rsub__(self, other):
        if callable(self.component):
            raise NotImplemented
        else:
            if self.component is None:
                return None
            else:
                return other - self.component

    def __isub__(self, other):
        if callable(self.component):
            raise NotImplemented
        else:
            if self.component is None:
                return None
            else:
                self.component -= other
                return self

    def __repr__(self):
        return '{self.__class__.__name__}({self.component!r})'.format(self=self)

    def __str__(self):
        if callable(self.component):
            return '{self.__class__.__name__} = {self.component.__name__}(x)'.format(self=self)
        else:
            return '{self.__class__.__name__} = {self.component!r}'.format(self=self)

    def __call__(self, *args, **kwargs):
        if callable(self.component):
            return self.component(*args, **kwargs)
        else:
            return self.component


class RayTracingMatrix(object):
    """
    A matrix for raytracing applications.
    """

    def __init__(self, a, b, c, d, label=''):
        """
        Create a new RayTracing matrix.

        A ray tracing matrix is a 2x2 matrix of the form [[A, B], [C, D]] so that a ray with [x, theta] is mapped to another ray [Ax+Btheta, Cx+Dtheta].

        :param a: The A component
        :param b: The B component
        :param c: The C component
        :param d: The D component
        :param label: The label of the matrix. Default is ""
        :type a: Union[int, float, function]
        :type b: Union[int, float, function]
        :type c: Union[int, float, function]
        :type d: Union[int, float, function]
        :type label: str
        """
        self.a = MatrixComponent(a)
        self.b = MatrixComponent(b)
        self.c = MatrixComponent(c)
        self.d = MatrixComponent(d)
        self.label = label

    @property
    def matrix(self):
        return np.array([[self.a, self.b], [self.c, self.d]])

    def __iter__(self):
        for param in [self.a, self.b, self.c, self.d]:
            yield param

    def __repr__(self):
        return '{self.__class__.__name__}({self.a!r}, {self.b!r}, {self.c!r}, {self.d!r}, label={self.label!r})'.format(
            self=self)

    def __str__(self):
        return '{self.label}:\n\t{l}'.format(self=self, l='\n\t'.join(['{}'.format(param) for param in self]))

    def __mul__(self, other):
        return self(other)

    def __call__(self, ray, *args, **kwargs):
        if isinstance(ray, Ray):
            return Ray(self.a * ray.x + self.b * ray.angle, self.c * ray.x + self.d * ray.angle, ray.z,
                       label='{self.label}({ray.label})'.format(self=self, ray=ray))
        else:
            raise TypeError(
                '{self.__class__.__name__} may only operate on Ray objects, not {ray!r}'.format(self=self, ray=ray))


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
        return self.angle_rad * 180 / np.pi  # * 180 / np.pi

    @property
    def angle_rad(self):
        return self.angle  # _deg * np.pi/180

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


class OpticalOperator(RayTracingMatrix):
    def __init__(self, a, b, c, d, label='', offset=0, size=1, z=0):
        """
        Create an optical ABCD operator.

        :param a: The A component
        :param b: The B component
        :param c: The C component
        :param d: The D component
        :param offset: The offset of the operator away from the optical axis
        :param size: The size of the element, used for plotting.
        :param z: The position of the element, used for plotting.
        :param label: The label of the operator
        :type a: Union[int, float, function]
        :type b: Union[int, float, function]
        :type c: Union[int, float, function]
        :type d: Union[int, float, function]
        :type offset: float
        :type size: float
        :type z: float
        :type label: str
        """
        super(OpticalOperator, self).__init__(a, b, c, d, label=label)
        self.offset = offset
        self.size = size
        self.z = z
        self._value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def set_z(self, z):
        self.z = z

    def set_offset(self, offset):
        self.offset = offset

    def set_value(self, value):
        self.value = value

    def set_label(self, label):
        self.label = label

    def __repr__(self):
        return '{self.__class__.__name__}({self.a!r}, {self.b!r}, {self.c!r}, {self.d!r}, label={self.label}, self.offset={self.offset!r}, size={self.size!r}, z={self.z!r})'.format(
            self=self)

    def __str__(self):
        return '{super_str}\n\toffset = {self.offset}\n\tsize = {self.size}\n\tz = {self.z}'.format(
            super_str=super().__str__(), self=self)

    def __mul__(self, other):
        if not isinstance(other, Ray):
            raise TypeError(
                'Invalid object {other!r}: {self.__class__.__name__} may only operate on Ray objects.'.format(
                    other=other, self=self))

        return super(OpticalOperator, self).__mul__(other)

        # return Ray(*list(np.dot(self.matrix, other.matrix).flatten()), other.z,
        #           label='{self.label}({other.label})'.format(self=self, other=other))

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
        # ax.plot([self.offset - self.size / 2, self.offset + self.size / 2], [self.z, self.z], *args, **kwargs)
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
        # super(Propagator, self).__init__(1, lambda x: np.sin(x) * self.distance, 0, 1, *args, **kwargs)
        super(Propagator, self).__init__(1, lambda x: np.tan(x) * self.distance, 0, 1, *args, **kwargs)
        self._value = distance

    def __repr__(self):
        return '{self.__class__.__name__}({self.distance!r}, label={self.label!r}, offset={self.offset!r}, size={self.size!r}, z={self.z!r})'.format(
            self=self)

    def __mul__(self, other):
        propagated_ray = super().__mul__(other)
        propagated_ray.z += self.distance
        return propagated_ray

    def show(self, *args, **kwargs):
        pass

    @property
    def distance(self):
        return self._value

    @distance.setter
    def distance(self, value):
        self._value = value


class Lens(OpticalOperator):
    def __init__(self, focal_length, *args, **kwargs):
        """
        Create a lens of a given focal length
        :param focal_length: The focal length of the lens
        :type focal_length: float
        """
        super(Lens, self).__init__(1., 0., self.C, 1, *args, **kwargs)  # lambda x: -np.pi / 2 / x, *args, **kwargs)
        self._value = focal_length

    def __repr__(self):
        return '{self.__class__.__name__}({self.focal_length!r}, label={self.label!r}, offset={self.offset!r}, size={self.size!r}, z={self.z!r})'.format(
            self=self)

    @property
    def focal_length(self):
        return self._value

    @focal_length.setter
    def focal_length(self, value):
        self._value = value

    def C(self, x):
        x = self.offset - x
        if x == 0:
            return 0
        if self.focal_length == 0:
            return np.inf * np.sign(x)
        return np.arcsin(- x / np.sqrt(x ** 2 + self.focal_length ** 2))

    def show(self, *args, ax=None, annotate=False, focal_plane_args=[], focal_plane_kwargs={}, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()
        fig, ax, line = super().show(*args, ax=ax, annotate=annotate, **kwargs)
        f_line_1 = ax.axhline(self.z + self.focal_length, **focal_plane_kwargs)
        f_line_2 = ax.axhline(self.z - self.focal_length, **focal_plane_kwargs)
        # ax.plot([self.offset - self.size / 2, self.offset + self.size / 2],
        #        [self.z - self.focal_length, self.z - self.focal_length], *focal_plane_args, **focal_plane_kwargs)
        # ax.plot([self.offset - self.size / 2, self.offset + self.size / 2],
        #        [self.z + self.focal_length, self.z + self.focal_length], *focal_plane_args, **focal_plane_kwargs)
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

    def __init__(self, angle, *args, n=2.0, **kwargs):
        """
        Create a deflector operator

        The deflector adds a constant angle to the ray, independently on its lateral distance from the optical axis.
        :param angle: The anglular offset, in degrees
        :param args: Optional positional arguments passed to OpticalOperator constructor
        :param kwargs: Optional keyword arguments passed to OpticalOperator constructor.
        """
        super(Deflector, self).__init__(1, 0, 0, self.D, *args, **kwargs)
        self._value = angle
        self._n = n

    def __repr__(self):
        return f'{self.__class__.__name__}({self.angle!r}, n={self._n!r}, label={self.label!r}, offset={self.offset!r}, size={self.size!r}, z={self.z!r})'

    @property
    def angle(self):
        return self._value

    @angle.setter
    def angle(self, value):
        self._value = value

    @property
    def alpha(self):
        return np.arcsin(np.sin(self.angle*np.pi/180.)/(self.n - 1))

    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, value):
        self._n = value

    def D(self, angle):
        d = np.arcsin(self.n * np.sin(self.alpha - np.arcsin(np.sin(angle * np.pi / 180.) / self.n))) - self.alpha
        #return d
        #return angle + d
        return angle + self.angle * np.pi / 180

    # def show(self, *args, ax=None, annotate=True, **kwargs):
    #     if ax is None:
    #         fig, ax = plt.subplots()
    #     else:
    #
    #     lines = ax.axhline(self.z, *args, **kwargs)
    #
    #     return fig, ax, [lines]


class Source(object):
    """A source for an optical system"""

    def __init__(self, z, angles, size=0, offset=0, label='Source'):
        self.z = z
        self.label = label
        self.size = size
        self.angles = angles
        self.offset = offset

    def __repr__(self):
        return '{self.__class__.__name__}({self.z!r}, {self.angles!r}, size={self.size!r}, offset={self.offset!r}, label={self.label!r})'.format(
            self=self)

    def set_z(self, z):
        self.z = z

    def set_size(self, size):
        self.size = size

    def set_offset(self, offset):
        self.offset = offset

    def set_angles(self, angles):
        self.angles = angles

    def emit(self):
        rays = []
        i = 0
        xs = [self.offset - self.size / 2, self.offset + self.size / 2]
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
        self.z = z
        self.label = label

    def __repr__(self):
        return '{self.__class__.__name__}({self.z!r}, label={self.label!r})'.format(self=self)

    def set_z(self, z):
        self.z = z

    def show(self, *args, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()

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
        return '{self.__class__.__name__}({self.rays!r}, label={self.label})'.format(self=self)

    def __str__(self):
        return '{self.__class__.__name__} "{self.label}":\n\t{rays}'.format(self=self, rays='\n\t'.join(
            [str(ray) for ray in self]))

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
                'Can only trace rays if ray trace {self!r} has only a single given ray (the initial ray)'.format(
                    self=self))

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
        # if len(operator_args['lenses']) == 0:
        #    operator_args['lenses'].append('--k')

        operator_args['deflectors'] = operator_args.get('deflectors', [])
        # if len(operator_args['deflectors']) == 0:
        #     operator_args['deflectors'].append('--r')

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


class Microscope():

    def __init__(self):
        super(Microscope, self).__init__(
            source=Source(100, [-0.2, 0.2], size=1, offset=0),
            operators=[
                Lens(10, label='CL1', z=90),
                Deflector(0, z=80, label='Gun1'),
                Deflector(0, z=75, label='Gun2'),
                Lens(10, label='CL3', z=65),
                Deflector(0, z=50, label='CLA1'),
                Deflector(0, z=45, label='CLA2'),
                Lens(10, label='CM', z=30),
                Lens(10, label='OLpre', z=5),
                Lens(10, label='OLpost', z=-5),
                Lens(10, label='IL1', z=-15),
                Deflector(0, z=-20, label='ILA1'),
                Deflector(0, z=-25, label='ILA2'),
                Lens(10, label='IL2', z=-30),
                Lens(10, label='IL3', z=-40),
                Deflector(0, z=-50, label='PLA'),
                Lens(10, label='PL', z=-60)],
            screen=Screen(-100),
            label='JEM2100F')

    @property
    def CL1(self):
        return self.get_optical_operator('CL1', Lens)

    @property
    def CL2(self):
        return self.get_optical_operator('CL2', Lens)

    @property
    def CL3(self):
        return self.get_optical_operator('CL3', Lens)

    @property
    def CM(self):
        return self.get_optical_operator('CM', Lens)

    @property
    def OLpre(self):
        return self.get_optical_operator('OLpre', Lens)

    @property
    def OLpost(self):
        return self.get_optical_operator('OLpost', Lens)

    @property
    def IL1(self):
        return self.get_optical_operator('IL1', Lens)

    @property
    def IL2(self):
        return self.get_optical_operator('IL2', Lens)

    @property
    def IL3(self):
        return self.get_optical_operator('IL3', Lens)

    @property
    def PL(self):
        return self.get_optical_operator('PL', Lens)

    @property
    def Gun1(self):
        return self.get_optical_operator('Gun1', Deflector)

    @property
    def Gun2(self):
        return self.get_optical_operator('Gun2', Deflector)

    @property
    def CLA1(self):
        return self.get_optical_operator('CLA1', Deflector)

    @property
    def CLA2(self):
        return self.get_optical_operator('CLA2', Deflector)

    @property
    def ILA1(self):
        return self.get_optical_operator('ILA1', Deflector)

    @property
    def ILA2(self):
        return self.get_optical_operator('ILA2', Deflector)

    @property
    def PL(self):
        return self.get_optical_operator('PL', Deflector)

    @property
    def brightness(self):
        return self.CL3.value

    @brightness.setter
    def brightness(self, value):
        self.Cl3.value = value

    def get_optical_operator(self, name, kind):
        try:
            operator = self[name]
        except IndexError as e:
            operator = None
        else:
            if not isinstance(operator, kind):
                raise TypeError(f'Error when getting {name}: Found match {operator!r}, but object is not a {kind!r}.')
        finally:
            return operator


def main():
    Microscope().show()
    plt.show()


def square(x):
    return x ** 2


def main2():
    none_component = MatrixComponent()
    float_component = MatrixComponent(10.)
    func_component = MatrixComponent(square)

    # print(none_component)
    # print(float_component)
    # print(func_component)

    # print(none_component*1)
    # print(float_component*2)
    # print(func_component*3)

    # ray = Ray(0, 45 * np.pi / 180, 0, 'R')
    ray = Ray(0, 0, 0, 'R')
    propagator = Propagator(1, 'S1')
    lens = Lens(5, offset=5, label='L1')
    # print(propagator)
    # print(propagator.matrix)
    # print(propagator.B)
    # print([propagator.A * ray.matrix[0] + propagator.B * ray, propagator.C*ray.matrix[0] + propagator.D*ray.matrix[1]])
    # print(propagator.matrix * 2)
    print(ray)
    print(propagator)
    print(lens)
    print(propagator * ray)
    print(lens * (propagator * ray))


if __name__ == '__main__':
    main()
