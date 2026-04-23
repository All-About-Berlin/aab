import json
from pathlib import Path
from ursus.config import config
from ursus.context_processors import Context
from ursus.renderers import Renderer
from ursus.utils import get_files_in_path
import logging


logger = logging.getLogger(__name__)


class JsonRenderer(Renderer):
    """
    Copies .json content files to the output directory as compressed JSON.
    """

    def render(self, context: Context, changed_files: set[Path] | None = None) -> set[Path]:
        files_to_keep = set()

        for file_path in get_files_in_path(config.content_path, changed_files, ".json"):
            source_path = config.content_path / file_path
            output_path = config.output_path / file_path
            files_to_keep.add(file_path)

            data = json.loads(source_path.read_text())
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(data, separators=(",", ":")))

        return files_to_keep
