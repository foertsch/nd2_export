# nd2_export

Streaming tools for exporting large Nikon ND2 files to TIFF-based formats.

## Goal

This project is intended to export ND2 datasets that are too large for a comfortable Fiji/ImageJ workflow. The implementation will favor lazy reading and incremental writing so multi-GB files can be converted without loading the entire dataset into memory.

## Current status

The exporter is implemented as a Python CLI that wraps `nd2`'s TIFF writer for large-file-safe OME-TIFF export.

- `inspect`: report ND2 sizes, dtype, and voxel metadata
- `export`: convert one ND2 file to OME-TIFF
- `batch`: convert every ND2 file in a folder into an `export/` subfolder

The first export was validated on a real 2-channel widefield acquisition. It produced a 2.2 GB OME-TIFF with:

- shape `CYX = (2, 24240, 24240)`
- dtype `uint16`
- OME metadata present
- BigTIFF enabled

## Project layout

- `pyproject.toml`: project metadata and dependencies
- `src/nd2_export/`: package source
- `tests/`: test scaffolding
- `tests/data/README.md`: instructions for optional local ND2 integration fixtures

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install nd2 tifffile numpy pytest
```

## Usage

Inspect one file:

```bash
PYTHONPATH=src .venv/bin/python -m nd2_export.cli inspect path/to/sample.nd2
```

Export one file:

```bash
mkdir -p output
PYTHONPATH=src .venv/bin/python -m nd2_export.cli export \
  path/to/sample.nd2 \
  -o output/sample.ome.tif \
  --progress \
  --overwrite
```

Batch export a folder:

```bash
PYTHONPATH=src .venv/bin/python -m nd2_export.cli batch \
  path/to/folder \
  --progress
```

If you run `batch` without an argument, a folder picker opens and the exporter creates `selected_folder/export/` automatically.

## Local Integration Testing

We do not commit `.nd2` binaries to the repository by default.

If you want a manual end-to-end test during development, place a small local ND2 file in `tests/data/` and follow the instructions in [`tests/data/README.md`](tests/data/README.md).

## Docker

A CLI-only container image is defined in [`Dockerfile`](Dockerfile). It builds the package in a multi-stage build and runs `nd2-export` as its entrypoint. The GUI is not included in the image because it depends on tkinter; use the GUI paths below for desktop use.

Build:

```bash
docker build -t nd2-export:latest .
```

Inspect a file (mount the folder that contains your ND2 at `/data`):

```bash
docker run --rm -v "$PWD:/data" nd2-export:latest inspect sample.nd2
```

Batch-export a folder:

```bash
docker run --rm -v "$PWD:/data" nd2-export:latest batch . --progress
```

The container writes outputs into the mounted folder exactly as the local CLI does, so the same `export/` subfolder convention applies.

## Click-To-Run GUI

For a simple desktop workflow, launch the GUI and pick a folder. It will create an `export/` subfolder inside the folder you choose and export every `.nd2` file there.

### Version 1: Python Installed Locally

This version assumes Python is installed on Windows, but the project installs itself into a local `.venv`.

1. Install Python 3.9+ on Windows.
2. Double-click [`install_windows_python.bat`](install_windows_python.bat).
3. After setup finishes, double-click [`launch_nd2_export_gui.bat`](launch_nd2_export_gui.bat).

Manual Python entrypoint:

```bash
PYTHONPATH=src .venv/bin/python -m nd2_export.gui
```

### Version 2: Windows `.exe`

This version is meant for distribution to users who should not need Python installed separately.

Build it on a Windows machine with:

1. Double-click [`build_windows_exe.bat`](build_windows_exe.bat)
2. Wait for PyInstaller to create `dist/nd2_export_gui.exe`

The PyInstaller configuration lives in [`nd2_export_gui.spec`](nd2_export_gui.spec).

### Notes

- We verified the Python code path on macOS.
- We did not build or run the Windows `.exe` here because that needs a Windows environment.
- The GUI always asks for a folder, then exports every `.nd2` file into `selected_folder/export/`.
- Errors and run details are logged to `selected_folder/export/nd2_export.log`.

## Next steps

1. Run the batch export on the remaining ND2 files.
2. Add logging and richer progress reporting.
3. Add regression tests around CLI behavior and output-path handling.
