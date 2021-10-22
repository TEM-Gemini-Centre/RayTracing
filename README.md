# RayTracing

This package is meant to provide interactive illustrations and control of ray traces of optical systems. In particular, it is designed with transmission electron microscopes in mind.

## Installation
Install this package using pip:
```bash
cd <...>/RayTracing/RayTracing
pip install --editable .
```

## Usage
Run the gui from a terminal:
```bash
cd <...>/RayTracing/RayTracing/gui
python gui.py
```

To set up a view of a condenser system only, run
```bash
cd <...>/RayTracing/RayTracing/gui
python gui.py --system condenser
```

see ``` python gui.py --help``` for further information