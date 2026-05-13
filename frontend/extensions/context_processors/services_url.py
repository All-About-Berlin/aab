from pathlib import Path
from ursus.config import config
from ursus.context_processors import Context, EntryContextProcessor, Entry, EntryURI


class ServicesUrlProcessor(EntryContextProcessor):
    def process_entry(
        self,
        context: Context,
        entry_uri: EntryURI,
        changed_files: set[Path] | None = None,
    ) -> None:
        if not entry_uri.lower().endswith(".md"):
            return
        if not (entry_uri == "services" or entry_uri.startswith("services/")):
            return
        services_url = getattr(config, "services_site_url", None)
        if not services_url:
            return
        entry: Entry = context["entries"][entry_uri]
        path_without_prefix = str(Path(entry_uri).with_suffix(config.html_url_extension))
        path_without_prefix = path_without_prefix.removeprefix("services/")
        entry["url"] = f"{services_url}/{path_without_prefix}"
