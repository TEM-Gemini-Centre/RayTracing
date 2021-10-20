from setuptools import setup, find_packages

setup(
    name='RayTracing',
    version='0.0.1',
    license='MIT',
    author='Emil Christiansen',
    author_email='emil.christiansen@ntnu.no',
    description="Interactive geometrical raytracing package",
    long_description=open('README.md').read(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "PyQt5",
        "pathlib",
        "tabulate"
    ],
    package_data={
        "": ["LICENSE", "README.md"],
        "": ["*.py"],
        "": ["*.ipynb"],
    },
)
