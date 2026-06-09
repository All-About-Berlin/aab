from jinja2_simple_tags import StandaloneTag, InclusionTag
from subprocess import CalledProcessError, run
from ursus.config import config

from ursus.renderers.jinja import JsLoaderExtension
import hashlib
import json
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class ToolExtension(StandaloneTag):
    """Jinja extension. Adds tag for cleanly including Vue widgets in markdown.
    Usage: {% tool "health-insurance-calculator", initial_occupation="hello", static=True, html_attribute=value %}

    Outputs all the code needed to render a Vue component from /js/vue/tools.
    """

    tags = {"tool"}
    safe_output = True

    def render(self, component_name: str, **kwargs):
        js_path = f"js/vue/tools/{component_name}.mjs"
        abs_js_path = config.templates_path / js_path
        assert abs_js_path.exists(), f"Component <{component_name}> does not exist at {abs_js_path}"

        # HTML component names are kebab-case. VueJS component class names are CamelCase.
        js_class = "".join(word.title() for word in component_name.split("-"))

        # js_fragments are output only once by {% alljs %}. Load each line as a fragment so that it's only included once
        self.environment.js_fragments.add("import Vue from '/js/vue/vue.mjs';")
        self.environment.js_fragments.add(f"import {js_class} from '/{js_path}';")
        self.environment.js_fragments.add(f"""
            document.querySelectorAll('section[is={component_name}]').forEach(
                el => new Vue({{
                    el,
                    components: {{ '{component_name}': {js_class} }},
                }})
            );
        """)

        # Create the HTML for the unloaded tool. This will be replaced with the JS component.
        html_attrs = {
            "v-cloak": "",
            "is": component_name,  # <section is="tax-calculator"> instead of <tax-calculator>. Better for accessibility.
        }

        # Set the element title and description for crawlers, screen readers and users without JS
        metadata_path = abs_js_path.with_suffix(".metadata.json")
        metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
        if label := metadata.get("label"):
            html_attrs["aria-label"] = label
        if description := metadata.get("description"):
            html_attrs["aria-description"] = description

        # Set all other attributes passed to the tag: {% tool ..., attribute=value %}
        for attr, value in kwargs.items():
            attr = attr.replace("_", "-")
            if value is True:
                # For example, disabled="disabled"
                html_attrs[attr] = attr
            elif value is False:
                continue
            else:
                html_attrs[attr] = value

        # Use <section> as the base tag
        # Set a helpful title and placeholder text for crawlers that don't use JS
        html_element = ET.Element("section", html_attrs)
        if label:
            temporary_title = ET.SubElement(html_element, "h4")
            temporary_title.text = label
        if description:
            temporary_description = ET.SubElement(html_element, "p")
            temporary_description.text = description

        # Add a <noscript> tag for AI crawlers and people with JS disabled
        noscript = ET.SubElement(html_element, "noscript")
        noscript_p = ET.SubElement(noscript, "p")
        noscript_p.text = "This tool requires JavaScript to work."

        return ET.tostring(html_element, method="html", encoding="unicode")

    def get_context(self, *args, **kwargs):
        return kwargs


class EsbuildJsLoaderExtension(JsLoaderExtension):
    """
    Use esbuild to bundle JS
    """

    def __init__(self, *args, **kwargs) -> None:
        self.build_cache = {}
        super().__init__(*args, **kwargs)

    def get_ts_config(self):
        return {
            "compilerOptions": {
                "baseUrl": ".",
                "paths": {
                    # The Javascript import root is the static site root
                    "/*": [f"{config.output_path}/*"],
                },
            },
        }

    def minify(self, js_code: str) -> str:
        """
        esbuild doubles the build time. Many pages have the same JS code.
        Use caching to avoid rebundling the same code again and again.
        """
        code_hash = hashlib.md5(js_code.encode()).hexdigest()
        if code_hash not in self.build_cache:
            try:
                output = run(
                    [
                        "esbuild",
                        "--bundle",
                        "--minify",
                        "--loader=js",
                        f"--tsconfig-raw={json.dumps(self.get_ts_config())}",
                    ],
                    input=js_code,
                    capture_output=True,
                    text=True,
                    check=True,
                )
            except CalledProcessError as e:
                raise Exception(f"Could not run esbuild: {e.stderr}")

            self.build_cache[code_hash] = output.stdout

        return self.build_cache[code_hash]


class TableOfContentsExtension(InclusionTag, StandaloneTag):
    """Jinja extension. Adds {% tableOfContents %}"""

    tags = {"tableOfContents"}
    safe_output = True

    def get_template_names(self) -> str:
        return "_blocks/tableOfContents.html"
