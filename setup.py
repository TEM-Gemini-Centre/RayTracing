from setuptools import setup, find_packages

setup(
    name='WaveOptics',
    version='0.0.1',
    license=license,
    author='Emil Christiansen',
    author_email='emil.christiansen@ntnu.no',
    description="Wave optical illustraon/simulation package",
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
    ],
    package_data={
        "": ["LICENSE", "README.md"],
        "": ["*.py"],
        "": ["*.ipynb"],
    },
)
