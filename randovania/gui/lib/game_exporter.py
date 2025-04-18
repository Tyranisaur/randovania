from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from PySide6 import QtWidgets

from randovania.gui.lib import async_dialog, error_message_box
from randovania.patching.patchers.exceptions import UnableToExportError

if TYPE_CHECKING:
    from randovania.exporter.game_exporter import GameExporter
    from randovania.gui.dialog.game_export_dialog import GameExportDialog
    from randovania.gui.lib.background_task_mixin import BackgroundTaskMixin
    from randovania.layout.layout_description import LayoutDescription
    from randovania.lib.status_update_lib import ProgressUpdateCallable


async def export_game(
    exporter: GameExporter,
    export_dialog: GameExportDialog,
    patch_data: dict,
    layout_for_spoiler: LayoutDescription | None,
    background: BackgroundTaskMixin,
) -> None:
    export_params = export_dialog.get_game_export_params()
    if exporter.can_start_new_export:
        await async_dialog.message_box(
            None,
            QtWidgets.QMessageBox.Icon.Critical,
            "Can't export game",
            "Error: Unable to export multiple games at the same time and another window is exporting a game right now.",
        )
        return

    def work(progress_update: ProgressUpdateCallable) -> None:
        exporter.export_game(patch_data, export_params, progress_update=progress_update)

        if layout_for_spoiler is not None:
            if export_params.spoiler_output is not None and layout_for_spoiler.has_spoiler:
                export_params.spoiler_output.parent.mkdir(parents=True, exist_ok=True)
                layout_for_spoiler.save_to_file(export_params.spoiler_output)

        progress_update("Finished!", 1)

    try:
        await background.run_in_background_async(work, "Exporting...")

    except asyncio.exceptions.CancelledError:
        pass

    except UnableToExportError as e:
        logging.warning(e.reason)
        background.progress_update_signal.emit(f"Unable to export game: {e.reason}", 0.0)
        await export_dialog.handle_unable_to_export(e)

    except Exception as e:
        logging.exception("Unable to export game")
        background.progress_update_signal.emit("Fatal error, unable to export game", 0.0)

        box = error_message_box.create_box_for_exception(e)
        await async_dialog.execute_dialog(box)
