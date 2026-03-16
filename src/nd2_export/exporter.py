from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict

import nd2


ProgressCallback = Callable[[int, int, dict[str, int]], None]
FileStatusCallback = Callable[[str], None]
logger = logging.getLogger(__name__)


@dataclass
class ExportOptions:
    input_path: Path
    output_path: Path
    overwrite: bool = False
    ome: bool = True
    include_unstructured_metadata: bool = True
    progress: bool = False


def _normalize_input_path(input_path: Path) -> Path:
    resolved = input_path.expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"ND2 file not found: {resolved}")
    if resolved.suffix.lower() != ".nd2":
        raise ValueError(f"Expected an .nd2 file, got: {resolved.name}")
    return resolved


def default_output_path(input_path: Path) -> Path:
    return input_path.with_suffix(".ome.tif")


def default_export_dir(input_dir: Path) -> Path:
    return input_dir / "export"


def default_log_path(base_dir: Path) -> Path:
    return base_dir / "nd2_export.log"


def inspect_nd2(input_path: Path) -> Dict[str, Any]:
    input_path = _normalize_input_path(input_path)
    logger.info("Inspecting ND2 file: %s", input_path)
    with nd2.ND2File(input_path) as nd2_file:
        voxel_size = nd2_file.voxel_size()
        channels = getattr(nd2_file.metadata, "channels", None) or []

        return {
            "input_path": str(input_path),
            "output_path_default": str(default_output_path(input_path)),
            "dtype": str(nd2_file.dtype),
            "shape": tuple(int(dim) for dim in nd2_file.shape),
            "sizes": {axis: int(size) for axis, size in nd2_file.sizes.items()},
            "is_legacy": bool(nd2_file.is_legacy),
            "nbytes": int(nd2_file.nbytes),
            "channel_count": len(channels),
            "voxel_size_um": {
                "x": float(voxel_size.x) if voxel_size.x is not None else None,
                "y": float(voxel_size.y) if voxel_size.y is not None else None,
                "z": float(voxel_size.z) if voxel_size.z is not None else None,
            },
        }


def export_nd2_to_tiff(
    options: ExportOptions,
    on_frame: ProgressCallback | None = None,
) -> Path:
    input_path = _normalize_input_path(options.input_path)
    output_path = options.output_path.expanduser().resolve()
    logger.info("Preparing export from %s to %s", input_path, output_path)

    if output_path.exists() and not options.overwrite:
        raise FileExistsError(
            f"Output already exists: {output_path}. Pass overwrite=True to replace it."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        output_path.unlink()

    with nd2.ND2File(input_path) as nd2_file:
        logger.info(
            "Starting TIFF export: shape=%s dtype=%s sizes=%s",
            nd2_file.shape,
            nd2_file.dtype,
            nd2_file.sizes,
        )
        nd2_file.write_tiff(
            output_path,
            include_unstructured_metadata=options.include_unstructured_metadata,
            progress=options.progress,
            on_frame=on_frame,
        )

    logger.info("Finished export: %s", output_path)
    return output_path


def batch_export_nd2(
    input_dir: Path,
    output_dir: Path | None = None,
    overwrite: bool = False,
    include_unstructured_metadata: bool = True,
    progress: bool = False,
    on_file_status: FileStatusCallback | None = None,
) -> list[Path]:
    input_dir = input_dir.expanduser().resolve()
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input directory not found: {input_dir}")

    export_dir = output_dir.expanduser().resolve() if output_dir else default_export_dir(input_dir)
    export_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Batch export input directory: %s", input_dir)
    logger.info("Batch export output directory: %s", export_dir)

    outputs: list[Path] = []
    nd2_files = sorted(input_dir.glob("*.nd2"))
    logger.info("Found %d ND2 files", len(nd2_files))
    for index, input_path in enumerate(nd2_files, start=1):
        output_path = export_dir / default_output_path(input_path).name
        start_message = (
            f"Starting file {index}/{len(nd2_files)}: "
            f"{input_path.name} -> {output_path.name}"
        )
        logger.info(start_message)
        if on_file_status is not None:
            on_file_status(start_message)
        try:
            exported_path = export_nd2_to_tiff(
                    ExportOptions(
                        input_path=input_path,
                        output_path=output_path,
                        overwrite=overwrite,
                        include_unstructured_metadata=include_unstructured_metadata,
                        progress=progress,
                    )
                )
            outputs.append(exported_path)
            finish_message = f"Finished file {index}/{len(nd2_files)}: {exported_path.name}"
            logger.info(finish_message)
            if on_file_status is not None:
                on_file_status(finish_message)
        except Exception:
            logger.exception("Failed while exporting %s", input_path)
            raise

    return outputs
