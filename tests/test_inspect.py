from pathlib import Path

import pytest

from nd2_export.cli import build_parser
from nd2_export.exporter import (
    _normalize_input_path,
    batch_export_nd2,
    default_export_dir,
    default_log_path,
    default_output_path,
)


def test_normalize_input_path_accepts_existing_nd2(tmp_path: Path) -> None:
    sample = tmp_path / "sample.nd2"
    sample.write_bytes(b"placeholder")

    assert _normalize_input_path(sample) == sample.resolve()


def test_normalize_input_path_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        _normalize_input_path(tmp_path / "missing.nd2")


def test_default_output_path_uses_ome_tif_suffix(tmp_path: Path) -> None:
    sample = tmp_path / "sample.nd2"

    assert default_output_path(sample) == tmp_path / "sample.ome.tif"


def test_batch_parser_allows_missing_directory_for_picker() -> None:
    parser = build_parser()

    args = parser.parse_args(["batch"])

    assert args.command == "batch"
    assert args.input_dir is None


def test_export_parser_allows_missing_input_for_picker() -> None:
    parser = build_parser()

    args = parser.parse_args(["export", "--overwrite"])

    assert args.command == "export"
    assert args.input_path is None
    assert args.overwrite is True


def test_batch_export_defaults_to_export_subfolder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    nd2_file = input_dir / "sample.nd2"
    nd2_file.write_bytes(b"placeholder")

    captured_output_paths: list[Path] = []

    def fake_export(options, on_frame=None):  # type: ignore[no-untyped-def]
        captured_output_paths.append(options.output_path)
        options.output_path.parent.mkdir(parents=True, exist_ok=True)
        options.output_path.write_bytes(b"fake")
        return options.output_path

    monkeypatch.setattr("nd2_export.exporter.export_nd2_to_tiff", fake_export)

    outputs = batch_export_nd2(input_dir=input_dir)

    assert outputs == [input_dir / "export" / "sample.ome.tif"]
    assert captured_output_paths == [input_dir / "export" / "sample.ome.tif"]


def test_default_log_path_is_inside_export_dir(tmp_path: Path) -> None:
    export_dir = default_export_dir(tmp_path / "input")

    assert default_log_path(export_dir) == export_dir / "nd2_export.log"


def test_batch_export_reports_start_and_finish_messages(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    nd2_file = input_dir / "sample.nd2"
    nd2_file.write_bytes(b"placeholder")

    messages: list[str] = []

    def fake_export(options, on_frame=None):  # type: ignore[no-untyped-def]
        options.output_path.parent.mkdir(parents=True, exist_ok=True)
        options.output_path.write_bytes(b"fake")
        return options.output_path

    monkeypatch.setattr("nd2_export.exporter.export_nd2_to_tiff", fake_export)

    batch_export_nd2(input_dir=input_dir, on_file_status=messages.append)

    assert messages[0].startswith("Starting file 1/1: sample.nd2")
    assert messages[1] == "Finished file 1/1: sample.ome.tif"
