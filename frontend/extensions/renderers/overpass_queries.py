from pathlib import Path
from ursus.config import config
from ursus.context_processors import Context
from ursus.renderers import Renderer
from ursus.utils import get_files_in_path
import json
import logging
import osm2geojson


logger = logging.getLogger(__name__)


class OverpassGeojsonRenderer(Renderer):
    """
    Renders .overpassql files as geojson
    """

    def render(self, context: Context, changed_files: set[Path] | None = None) -> set[Path]:
        files_to_keep = set()
        for overpassql_path in get_files_in_path(config.content_path, changed_files, suffix=".overpassql"):
            geojson_file = overpassql_path.with_suffix(".json")
            logger.info("Rendering %s", str(geojson_file))
            query = (config.content_path / overpassql_path).read_text()
            geojson = json.dumps(osm2geojson.json2geojson(osm2geojson.overpass_call(query)))
            (config.output_path / geojson_file).parent.mkdir(parents=True, exist_ok=True)
            (config.output_path / geojson_file).write_text(geojson)
            files_to_keep.add(geojson_file)
        return files_to_keep
