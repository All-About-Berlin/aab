"""
Custom template loaders used by the dual-backend TEMPLATES setup.

The Admin still uses the Django template renderer, while the rest of the backend
uses Jinja2.
"""

from django.template.loaders.app_directories import Loader as AppDirectoriesLoader


class AdminOnlyLoader(AppDirectoriesLoader):
    def get_template_sources(self, template_name):
        if not template_name.startswith("admin/"):
            return
        yield from super().get_template_sources(template_name)
