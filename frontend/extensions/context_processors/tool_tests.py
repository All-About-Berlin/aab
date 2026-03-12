from pathlib import Path
from ursus.config import config
from ursus.context_processors import Context, ContextProcessor, Entry, EntryURI
from ursus.utils import get_files_in_path

tools_path = config.templates_path / "js/vue/tools"


class ToolTestEntriesProcessor(ContextProcessor):
    """
    Creates an Entry for each JS tool, so that a test page can be generated for that tool.
    """

    def process(self, context: Context, changed_files: set[Path] | None = None) -> Context:
        for file_path in get_files_in_path(config.templates_path, changed_files, ".mjs"):
            if file_path.is_relative_to("js/vue/tools"):
                relative_path = file_path.relative_to("js/vue/tools")
                entry_uri = EntryURI(str(Path("tests/tools") / relative_path))
                context["entries"][entry_uri] = Entry(
                    {
                        "url": f"{config.site_url}/{Path(entry_uri).with_suffix('')}",
                        "tag": file_path.stem,
                    }
                )

        return context
