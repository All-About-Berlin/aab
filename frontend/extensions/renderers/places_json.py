import json
from datetime import date, datetime
from pathlib import Path
from ursus.config import config
from ursus.context_processors import Context
from ursus.renderers import Renderer
from ursus.utils import get_files_in_path
import logging
import yaml


logger = logging.getLogger(__name__)


class DateEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        return super().default(o)


class PlacesRenderer(Renderer):
    """
    Reads .yaml place files and writes them to the output directory as compressed JSON.
    """

    def render(self, context: Context, changed_files: set[Path] | None = None) -> set[Path]:
        files_to_keep = set()
        changed_places = {f for f in changed_files or set() if f.is_relative_to(config.content_path / "places")}

        for file_path in get_files_in_path(config.content_path, suffix=".yaml"):
            if not file_path.is_relative_to(Path("places")):
                continue

            source_path = config.content_path / file_path
            output_path = (config.output_path / file_path).with_suffix(".json")
            files_to_keep.add(output_path.relative_to(config.output_path))

            if changed_files is not None and source_path not in changed_places:
                continue

            places = yaml.safe_load(source_path.read_text())
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps({"places": places}, separators=(",", ":"), cls=DateEncoder))

        return files_to_keep
