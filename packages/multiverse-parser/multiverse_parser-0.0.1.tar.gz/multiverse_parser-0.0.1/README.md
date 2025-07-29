# Multiverse Parser

[![Python Tests with Coverage (Ubuntu 22.04)](https://github.com/Multiverse-Framework/Multiverse-Parser/actions/workflows/ubuntu-22.04.yml/badge.svg)](https://github.com/Multiverse-Framework/Multiverse-Parser/actions/workflows/ubuntu-22.04.yml)
[![Python Tests with Coverage  (Ubuntu 24.04)](https://github.com/Multiverse-Framework/Multiverse-Parser/actions/workflows/ubuntu-24.04.yml/badge.svg)](https://github.com/Multiverse-Framework/Multiverse-Parser/actions/workflows/ubuntu-24.04.yml)
[![Python Tests with Coverage (Windows)](https://github.com/Multiverse-Framework/Multiverse-Parser/actions/workflows/windows.yml/badge.svg)](https://github.com/Multiverse-Framework/Multiverse-Parser/actions/workflows/windows.yml)
[![codecov](https://codecov.io/gh/Multiverse-Framework/Multiverse-Parser/graph/badge.svg?token=QYFC2RFVLG)](https://codecov.io/gh/Multiverse-Framework/Multiverse-Parser)

The **Multiverse Parser** module provides seamless conversion between different scene description formats, using [**USD** (Universal Scene Description)](https://openusd.org/release/index.html) as a universal translation layer.

---

## 📋 Prerequisites

- **Python** ≥ 3.10 (Linux), 3.12 (Windows)
- Python packages listed in [requirements.txt](https://github.com/Multiverse-Framework/Multiverse-Parser/blob/main/requirements.txt)

Install the required packages:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Setup

First, clone the repository:

```bash
git clone https://github.com/Multiverse-Framework/Multiverse-Parser.git --depth 1
```

Then, run the setup script to automatically download and link [**Blender**](https://www.blender.org/):

**Linux:**
```bash
./Multiverse-Parser/setup.sh
```

**Windows:**
```bat
.\Multiverse-Parser\setup.bat
```

---

### ✨ Optional: Rebuild USD

To upgrade or rebuild USD:

1. Install the additional Python dependencies:

    ```bash
    pip install pyside6 pyopengl jinja2
    ```

2. Run the setup script with the `--usd` flag:

    **Linux:**
    ```bash
    ./Multiverse-Parser/setup.sh --usd
    ```

    **Windows:**
    ```bat
    .\Multiverse-Parser\setup.bat --usd
    ```

---

## 🚀 Usage

To view all available options:

**Linux:**

```bash
./Multiverse-Parser/scripts/multiverse_parser --help
```

**Windows:**

```bat
.\Multiverse-Parser\scripts\multiverse_parser.cmd --help
```

Example output:

```bash
usage: multiverse_parser [-h] --input INPUT --output OUTPUT [--fixed_base] [--root_name ROOT_NAME] [--add_xform_for_each_geom] [--relative_to_ros_package RELATIVE_TO_ROS_PACKAGE] [--no-physics] [--no-visual]
                         [--no-collision] [--keepusd] [--inertiasource INERTIASOURCE] [--defaultrgba DEFAULTRGBA [DEFAULTRGBA ...]]

Multiverse parser

options:
  -h, --help            show this help message and exit
  --input INPUT         Import scene description as (URDF, MJCF, WORLD or USD)
  --output OUTPUT       Export scene description as (URDF, MJCF, WORLD or USD)
  --fixed_base          Set the base link as fixed
  --root_name ROOT_NAME
                        The name of the root body
  --add_xform_for_each_geom
                        Add additional parent xform for each geom (only for input USD)
  --relative_to_ros_package RELATIVE_TO_ROS_PACKAGE
                        The path to the ROS package that contains the URDF file (only for output URDF)
  --no-physics          Exclude the physics properties
  --no-visual           Exclude the visual meshes
  --no-collision        Exclude the collision meshes
  --keepusd             Keep the temporary USD file after exporting
  --inertiasource INERTIASOURCE
                        Where to get the inertia from (from_src, from_visual_mesh or from_collision_mesh)
  --defaultrgba DEFAULTRGBA [DEFAULTRGBA ...]
                        The default color of the meshes

```

---

## 🐍 For Python Users

If you want to use `multiverse_parser` programmatically in Python, you can install it as a local Python package using a symbolic link (editable mode):

```bash
pip install -e .
```

This allows you to make changes to the source code and immediately reflect them without reinstalling.

You can then test it in a Python shell:

```python
from multiverse_parser import InertiaSource, MjcfImporter, UrdfExporter

def main():
    input_path = "input/path.xml"
    output_path = "output/path.urdf"
    factory = MjcfImporter(file_path=input_path,
                           fixed_base=False,
                           root_name="world", # Or robot root link
                           with_physics=True,
                           with_visual=True,
                           with_collision=True,
                           inertia_source=InertiaSource.FROM_SRC)
    factory.import_model()
    exporter = UrdfExporter(file_path=output_path,
                            factory=factory)
    exporter.build()
    exporter.export(keep_usd=False)

if __name__ == "__main__":
    main()
```
