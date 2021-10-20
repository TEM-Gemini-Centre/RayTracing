import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from math import inf, isinf, nan, isnan, pi
from scipy.fft import fft2, ifft2, fftshift
from warnings import warn
from matplotlib.animation import FuncAnimation


class Wave(object):
    def __init__(self, nx=None, ny=None, extent=None, resolution=0.1, wavelength=1, *args, **kwargs):
        """
        Create a new wave
        :param nx: The number of sampling points along x. Default is None which will use either the extent adn the resolution to decide the number of points, or use 32 points
        :param ny: The number of sampling points along y. Default is None which will use either the extent adn the resolution to decide the number of points, or use 32 points
        :param extent: The extent of the wave [left, right, bottom, top]. Default is None which will use either nx and ny and the resolution, or use 32 points.
        :param resolution: The resolution of the sampling grid. Default is 0.1
        :param wavelength: The wavelength of the wave. Used as a scaling factor. Default is 1.
        :param args: Optional positional arguments passed to make_wave
        :param kwargs: Optional keyword arguments passed to make_wave
        :type nx: Union[None, int]
        :type ny: Union[None, int]
        :type extent: Union[None, list, tuple]
        :type resolution: float
        :type wavelength: float
        """

        if extent is None:
            if nx is None:
                nx = 32
            if ny is None:
                ny = 32
            extent = np.array([-nx / 2, nx / 2, -ny / 2, ny / 2]) * resolution
        else:
            if nx is not None:
                raise TypeError(
                    'Invalid value for `nx`: {nx!r}. `nx` cannot be specified when an extent is given.'.format(nx=nx))
            if ny is not None:
                raise TypeError(
                    'Invalid value for `ny`: {ny!r}. `ny` cannot be specified when an extent is given.'.format(ny=ny))
            nx = abs(int((extent[1] - extent[0]) / resolution))
            ny = abs(int((extent[3] - extent[2]) / resolution))

        self.nx = nx
        self.ny = ny
        self.x = np.linspace(extent[0], extent[1], self.nx)
        self.y = np.linspace(extent[2], extent[3], self.ny)
        self.field = make_wave(self.x, self.y, *args, **kwargs)
        self.wavelength = wavelength

    @property
    def resolution(self):
        dx = abs(self.x[1] - self.x[0])
        dy = abs(self.y[1] - self.y[0])
        if dx != dy:
            warn('{self!r} has non-equal resolution in x and y: {dx}!={dy}'.format(self=self, dx=dx, dy=dy))
        return dx

    @property
    def extent(self):
        return [min(self.x), max(self.x), min(self.y), max(self.y)]

    @property
    def intensity(self):
        return abs(self) ** 2

    def __repr__(self):
        return '{self.__class__.__name__}(nx=None, ny=None, extent={self.extent}, resolution={self.resolution}, wavelength={self.wavelength})'.format(
            self=self)

    def __str__(self):
        return 'Wave({self.nx}, {self.ny}) with wavelength {self.wavelength} and extent ([l, r, b, t]): {self.extent}'.format(
            self=self)

    def __format__(self, format_spec):
        precision = int(format_spec.split('.')[1][0])
        with np.printoptions(precision=precision, suppress=True, linewidth=None):
            return 'Wave({self.nx}, {self.ny}) with wavelength {self.wavelength}, extent ([l, r, b, t]): {self.extent} and data:\n{self.field!s}'.format(
                self=self)

    def __add__(self, other):
        return self.field + other

    def __radd__(self, other):
        return other + self.field

    def __iadd__(self, other):
        self.field += other
        return self

    def __sub__(self, other):
        return self.field - other

    def __rsub__(self, other):
        return other - self.field

    def __isub__(self, other):
        self.field -= other
        return self

    def __mul__(self, other):
        return self.field * other

    def __rmul__(self, other):
        return other * self.field

    def __imul__(self, other):
        self.field *= other
        return self

    def __truediv__(self, other):
        return self.field / other

    def __rtruediv__(self, other):
        return other / self.field

    def __itruediv__(self, other):
        self.field /= other
        return self

    def __abs__(self):
        return np.abs(self.field)

    def show(self):
        fig, axes = plt.subplots(nrows=1, ncols=3, subplot_kw={'xticks': [], 'yticks': [], 'frameon': False},
                                 frameon=False)
        axes[0].imshow(np.real(self.field))
        axes[1].imshow(np.imag(self.field))
        axes[2].imshow(np.abs(self.field) ** 2)
        axes[0].set_title('Re')
        axes[1].set_title('Im')
        axes[2].set_title(r'$|\phi|^2$')


class Lens(object):
    def __init__(self, focal_length, z, x=0, y=0, lx=inf, ly=inf):
        """
        Create a new lens

        :param focal_length: The focal length of the lens
        :param z: The position of the lens
        :param x: The position of the lens centre along x. Defaults to 0
        :param y: The position of the lens centre along y. Defaults to 0
        :param lx: The size of the lens in the x-direction. Defaults to inf
        :param ly: The size of the lens in the y-direction. Defaults to inf
        :type focal_length: float
        :type z: float
        :type x: float
        :type y: float
        :type lx: float
        :type ly: float
        """
        self.focal_length = focal_length
        self.z = z
        self.x = x
        self.y = y
        self.lx = lx
        self.ly = ly

    @property
    def f(self):
        return self.focal_length

    @f.setter
    def f(self, focal_length):
        self.focal_length = focal_length

    def __mul__(self, other):
        if not isinstance(other, Wave):
            raise TypeError(
                '{other!r} is invalid type. {self.__class__.__name__} can only operate on Wave objects.'.format(
                    self=self, other=other))
        pass


class Propagator(object):
    def __init__(self, distance):
        """
        Create a new propagator.
        :param distance: The free-space distance to propagate waves
        :type distance: float
        """
        self.distance = distance

    def __str__(self):
        return 'P({self.distance})'.format(self=self)

    def __format__(self, format_spec):
        return 'P({self.distance:{f}})'.format(self=self, f=format_spec)

    def __repr__(self):
        return '{self.__class__.__name__}({self.distance!r})'.format(self=self)

    def __mul__(self, other):
        return self.propagate(other)

    def propagate(self, wave):
        if not isinstance(wave, Wave):
            raise TypeError('{self!r} cannot propagate {wave!r}, it is not a Wave.'.format(self=self, wave=wave))

        w = Wave(extent=wave.extent, resolution=wave.resolution, wavelength=wave.wavelength)
        X, Y = np.meshgrid(wave.x, wave.y)
        ft = fft2(np.exp(2j * pi * (X ** 2 + Y ** 2) / (2 * wave.wavelength * self.distance)) * wave.field)
        ft = fftshift(ft)
        w.field = np.exp(1j*self.distance/w.wavelength)/(1j*self.distance/w.wavelength) * np.exp(1j * (X ** 2 + Y ** 2) / (2 * w.wavelength * self.distance)) * ft
        return w


def make_wave(x, y, *args, kind=None, **kwargs):
    """
    Create a wave of a specified kind

    :param nx: The extent of the wave in the x-direction
    :param ny: The extent of the wave in the y-direction
    :param kind: The kind of wave. Accepted kinds are "plane", "converged". Default is None which gives a plane wave.
    :return: The wave
    :type nx: Union[list, tuple, numpy.ndarray]
    :type ny: Union[list, tuple, numpy.ndarray]
    :type kind: Union[None, str]
    :rtype: np.complex_
    """
    funcs = {None: plane_wave, 'plane': plane_wave, 'converged': converged_wave}
    if kind not in funcs:
        raise ValueError('Kind {kind} is not an accepted wave. Accepted values are {kinds}'.format(kind=kind,
                                                                                                   kinds=','.join(
                                                                                                       funcs.keys())))
    return funcs[kind](x, y, *args, **kwargs)


def plane_wave(x, y):
    """
    Return a plane wave field

    :param nx: The extent of the wave in the x-direction
    :param ny: The extent of the wave in the y-direction
    :type nx: int
    :type ny: int
    :return: The plane wave
    :rtype: np.complex_
    """

    field = np.zeros((len(x), len(y)), dtype=np.complex_)
    field += np.ones((len(x), len(y)))
    return field


def converged_wave(x, y):
    """
    Return a convergent wave field

    :param x: The x-grid of the wave
    :param y: The y-grid of the wave
    :type x: Union[list, tuple, numpy.ndarray]
    :type y: Union[list, tuple, numpy.ndarray]
    :return: The converged wave
    :rtype: np.complex_
    """

    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X ** 2 + Y ** 2)
    field = np.zeros((len(x), len(y)), dtype=np.complex_)
    field += np.ones((len(x), len(y)))
    field += R * 1j
    return field


def animate(wave, scaling_factor = 0.1, log=False, *args, **kwargs):
    fig, ax = plt.subplots()
    if log:
        im = ax.imshow(np.log(wave.intensity))
    else:
        im = ax.imshow(wave.intensity)
    label = ax.text(0.02, 0.98, 'Frame 0', color='w', transform=ax.transAxes, va='top', ha='left')

    def update(frame):
        if frame == 0:
            image = wave.intensity
        else:
            image = (Propagator(frame*scaling_factor) * wave).intensity
        if log:
            image = np.log(image)
        im.set_data(image)
        im.set_clim(0, np.max(image))
        label.set_text('Frame {}'.format(frame))
        return im, label
    ani = FuncAnimation(fig, update, *args, **kwargs)
    return ani


def main():
    wave = Wave(32, 32, kind='plane')
    print('{:.2f}'.format(wave))
    wave.show()


if __name__ == '__main__':
    main()
