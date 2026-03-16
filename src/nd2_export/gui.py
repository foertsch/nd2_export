from __future__ import annotations

import threading
import traceback
from pathlib import Path
from tkinter import BOTH, END, DISABLED, NORMAL, Button, Label, Text, Tk, filedialog, messagebox

import logging

from .exporter import batch_export_nd2, default_export_dir, default_log_path
from .logging_utils import configure_logging


class ExportApp:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.title("ND2 Export")
        self.root.geometry("720x420")

        self.status_label = Label(
            self.root,
            text="Choose a folder containing ND2 files. Exports are written to an 'export' subfolder.",
            anchor="w",
            justify="left",
            wraplength=680,
        )
        self.status_label.pack(fill="x", padx=12, pady=(12, 8))

        self.choose_button = Button(
            self.root,
            text="Choose Folder and Export",
            command=self.choose_and_export,
        )
        self.choose_button.pack(padx=12, pady=(0, 8))

        self.log = Text(self.root, height=18, state=DISABLED)
        self.log.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))

        self.root.after(150, self.choose_and_export)
        self.logger = logging.getLogger(__name__)

    def append_log(self, message: str) -> None:
        self.log.configure(state=NORMAL)
        self.log.insert(END, message + "\n")
        self.log.see(END)
        self.log.configure(state=DISABLED)

    def choose_and_export(self) -> None:
        selected = filedialog.askdirectory(
            title="Select a folder containing ND2 files",
            mustexist=True,
        )
        if not selected:
            self.status_label.configure(text="No folder selected yet.")
            return

        input_dir = Path(selected)
        log_path = configure_logging(default_log_path(default_export_dir(input_dir)))
        self.status_label.configure(text=f"Exporting ND2 files from: {input_dir}")
        self.choose_button.configure(state=DISABLED)
        self.append_log(f"Selected folder: {input_dir}")
        self.append_log(f"Output folder: {input_dir / 'export'}")
        self.append_log(f"Log file: {log_path}")
        self.logger.info("GUI export started for %s", input_dir)

        worker = threading.Thread(
            target=self._run_export,
            args=(input_dir,),
            daemon=True,
        )
        worker.start()

    def _run_export(self, input_dir: Path) -> None:
        try:
            nd2_files = sorted(input_dir.glob("*.nd2"))
            if not nd2_files:
                self.root.after(
                    0,
                    lambda: self._finish_with_message(
                        "No ND2 files found in the selected folder.",
                        error=False,
                    ),
                )
                return

            self.root.after(0, lambda: self.append_log(f"Found {len(nd2_files)} ND2 file(s)."))
            outputs = batch_export_nd2(
                input_dir=input_dir,
                overwrite=True,
                on_file_status=lambda message: self.root.after(
                    0,
                    lambda: self.append_log(message),
                ),
            )
            self.root.after(0, lambda: self._report_success(outputs))
        except Exception as exc:  # pragma: no cover - GUI path
            self.logger.exception("GUI export failed")
            details = "".join(traceback.format_exception_only(type(exc), exc)).strip()
            self.root.after(0, lambda: self._finish_with_message(details, error=True))

    def _report_success(self, outputs: list[Path]) -> None:
        for output in outputs:
            self.append_log(f"Exported: {output}")
        self._finish_with_message(
            f"Finished exporting {len(outputs)} file(s) to {outputs[0].parent}",
            error=False,
        )

    def _finish_with_message(self, message: str, error: bool) -> None:
        self.status_label.configure(text=message)
        self.choose_button.configure(state=NORMAL)
        self.append_log(message)
        if error:
            messagebox.showerror(
                "ND2 Export",
                f"{message}\n\nSee the log file in the export folder for details.",
            )
        else:
            messagebox.showinfo("ND2 Export", message)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = ExportApp()
    app.run()


if __name__ == "__main__":
    main()
