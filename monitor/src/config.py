from pathlib import Path
import tomllib


def load_config(config_paths: list[Path]) -> dict:
    """Load and deep-merge multiple TOML config files.

    Top-level sections (templates, monitors) are merged across files.
    Later files override earlier ones for the same key.
    """
    merged = {}
    for path in config_paths:
        try:
            with open(path, "rb") as f:
                config = tomllib.load(f)
            for key, value in config.items():
                if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key] = {**merged[key], **value}
                else:
                    merged[key] = value
        except:
            raise ValueError(f"Could not load config '{path}'")
    return merged


def resolve_template(config: dict, template_name: str, _seen: set | None = None) -> dict:
    """Resolve a template by name, following the 'extends' chain."""
    if _seen is None:
        _seen = set()
    if template_name in _seen:
        raise ValueError(f"Circular template inheritance: {template_name}")
    _seen.add(template_name)

    templates = config.get("templates", {})
    if template_name not in templates:
        raise ValueError(f"Template '{template_name}' not found")
    template = templates[template_name]
    parent_name = template.get("extends")
    if parent_name:
        parent = resolve_template(config, parent_name, _seen)
        return {**parent, **{k: v for k, v in template.items() if k != "extends"}}
    return {k: v for k, v in template.items() if k != "extends"}


def resolve_placeholders(merged: dict) -> dict:
    """Replace {key} placeholders in string values with other values from the dict."""
    resolved = {}
    for key, value in merged.items():
        if isinstance(value, str):
            resolved[key] = value.format_map(merged)
        else:
            resolved[key] = value
    return resolved


def get_monitor_config(config: dict, monitor_name: str) -> dict:
    """Get the fully merged config for a monitor (template + monitor overrides)."""
    monitor_config = config["monitors"][monitor_name]
    template_name = monitor_config.get("extends")
    if template_name:
        template = resolve_template(config, template_name)
        merged = {**template, **{k: v for k, v in monitor_config.items() if k != "extends"}}
    else:
        merged = dict(monitor_config)
    return resolve_placeholders(merged)
