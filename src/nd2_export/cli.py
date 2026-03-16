import argparse
import logging
import sys
from pathlib import Path
from tkinter import Tk, filedialog

from .exporter import (
    ExportOptions,
    batch_export_nd2,
    default_export_dir,
    default_log_path,
    default_output_path,
    export_nd2_to_tiff,
    inspect_nd2,
)
from .logging_utils import configure_logging


def choose_nd2_file() -> Path:
    root = Tk()
    root.withdraw()
    root.update()
    selected = filedialog.askopenfilename(
        title="Select an ND2 file",
        filetypes=[("ND2 files", "*.nd2")],
    )
    root.destroy()
    if not selected:
        raise SystemExit("No ND2 file selected.")
    return Path(selected)


def choose_directory(title: str) -> Path:
    root = Tk()
    root.withdraw()
    root.update()
    selected = filedialog.askdirectory(title=title, mustexist=True)
    root.destroy()
    if not selected:
        raise SystemExit("No directory selected.")
    return Path(selected)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect and export large ND2 files to TIFF-based formats."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect one ND2 file.")
    inspect_parser.add_argument(
        "input_path",
        nargs="?",
        type=Path,
        help="Path to the ND2 file. If omitted, a file picker will open.",
    )

    export_parser = subparsers.add_parser("export", help="Export one ND2 file to OME-TIFF.")
    export_parser.add_argument(
        "input_path",
        nargs="?",
        type=Path,
        help="Path to the ND2 file. If omitted, a file picker will open.",
    )
    export_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output OME-TIFF path. Defaults to the input filename with .ome.tif.",
    )
    export_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing output file.",
    )
    export_parser.add_argument(
        "--no-unstructured-metadata",
        action="store_true",
        help="Skip unstructured ND2 metadata in the OME output.",
    )
    export_parser.add_argument(
        "--progress",
        action="store_true",
        help="Show library-level progress while exporting.",
    )

    batch_parser = subparsers.add_parser("batch", help="Export all ND2 files in a folder.")
    batch_parser.add_argument(
        "input_dir",
        nargs="?",
        type=Path,
        help="Directory containing ND2 files. If omitted, a directory picker will open.",
    )
    batch_parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Directory for exported OME-TIFF files. Defaults to an 'export' subfolder inside the selected input directory.",
    )
    batch_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing output files.",
    )
    batch_parser.add_argument(
        "--no-unstructured-metadata",
        action="store_true",
        help="Skip unstructured ND2 metadata in the OME output.",
    )
    batch_parser.add_argument(
        "--progress",
        action="store_true",
        help="Show library-level progress while exporting.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    logger = logging.getLogger(__name__)

    try:
        if args.command == "inspect":
            input_path = args.input_path or choose_nd2_file()
            configure_logging(default_log_path(input_path.parent))
            metadata = inspect_nd2(input_path)
            for key, value in metadata.items():
                print(f"{key}: {value}")
            return

        if args.command == "export":
            input_path = args.input_path or choose_nd2_file()
            output_path = args.output or default_output_path(input_path.expanduser().resolve())
            configure_logging(default_log_path(output_path.parent))
            exported = export_nd2_to_tiff(
                ExportOptions(
                    input_path=input_path,
                    output_path=output_path,
                    overwrite=args.overwrite,
                    include_unstructured_metadata=not args.no_unstructured_metadata,
                    progress=args.progress,
                )
            )
            print(exported)
            return

        if args.command == "batch":
            input_dir = args.input_dir or choose_directory("Select a folder of ND2 files")
            export_dir = args.output_dir.expanduser().resolve() if args.output_dir else default_export_dir(input_dir.expanduser().resolve())
            log_path = configure_logging(default_log_path(export_dir))
            logger.info("Batch command selected. Log file: %s", log_path)
            outputs = batch_export_nd2(
                input_dir=input_dir,
                output_dir=args.output_dir,
                overwrite=args.overwrite,
                include_unstructured_metadata=not args.no_unstructured_metadata,
                progress=args.progress,
            )
            for output in outputs:
                print(output)
            return

        parser.error(f"Unknown command: {args.command}")
    except Exception as exc:
        logger.exception("Command failed")
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
