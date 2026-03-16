# Local Test Data

This folder is intentionally kept out of versioned binary test data.

## Why

ND2 files can be large, may have redistribution restrictions, and are not ideal as normal Git fixtures.

## Suggested local workflow

Place a very small local `.nd2` file in this folder if you want to run manual integration checks during development.

Example filename:

- `tests/data/sample.nd2`

## Manual integration checks

Inspect:

```bash
PYTHONPATH=src .venv/bin/python -m nd2_export.cli inspect tests/data/sample.nd2
```

Export one file:

```bash
PYTHONPATH=src .venv/bin/python -m nd2_export.cli export tests/data/sample.nd2 --overwrite
```

GUI:

1. Start the GUI launcher.
2. Choose the `tests/data/` folder or another folder containing local ND2 files.
3. Confirm that outputs are written into an `export/` subfolder and that `nd2_export.log` is created.
