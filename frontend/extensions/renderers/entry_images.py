from extensions.functions import soft_hyphen
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as ImageType
from ursus.config import config
from ursus.context_processors import Context, EntryContextProcessor, Entry, EntryURI
from ursus.renderers import Renderer
import hashlib
import logging


logger = logging.getLogger(__name__)


exif_description_field = 0x9286


def wrap_text(text: str, font: ImageFont.ImageFont, max_width: int) -> str:
    """
    Wrap text so that it fits inside a box; adjust the font size as needed.
    """
    words = text.split()
    lines: list[list[str]] = [[]]
    for word in words:
        line_width = font.getbbox(" ".join(lines[-1] + [word]))[2]
        if line_width <= max_width:
            lines[-1].append(word)
        elif font.getbbox(word)[2] > max_width:
            raise Exception("Word too long")
        else:
            lines.append(
                [
                    word,
                ]
            )

    return "\n".join(" ".join(line) for line in lines)


def text_height(text: str, font: ImageFont.ImageFont, line_spacing: int) -> int:
    """
    Get the vertical size of a block of text with a given font
    """
    ascent, descent = font.getmetrics()
    lines = text.split("\n")
    return sum([font.getmask(line).getbbox()[3] + descent for line in lines]) + (len(lines) - 1) * line_spacing


def text_width(text: str, font: ImageFont.ImageFont) -> int:
    """
    Get the horizontal size of a block of text with a given font
    """
    return max(int(font.getmask(line).getbox()[2]) for line in text.split("\n"))


def make_cover_image(text: str, templates_path: Path) -> ImageType:
    """
    Generates an All About Berlin cover image for social media.
    """
    padding = 50
    line_spacing = 25
    image_size = (1200, 630)
    logo_size = (70, 70)
    logo_position = (700, image_size[1] - logo_size[1] - 30)

    image = Image.new("RGB", image_size, (218, 81, 61))
    imgdraw = ImageDraw.Draw(image)

    # Place logo
    logo = Image.open(str(templates_path / "staticimages/logo.png"))
    logo.thumbnail(logo_size)
    image.paste(logo, logo_position)

    # Wrap the main text to fit available space
    font_size = 100
    while True:
        title_font = ImageFont.truetype(str(templates_path / "fonts/librefranklin-400.ttf"), font_size)
        try:
            wrapped_title = wrap_text(text, title_font, image.size[0] - 2 * padding)
        except Exception:
            font_size -= 3
        else:
            if len(wrapped_title.split("\n")) > 4:
                font_size -= 3
            else:
                break

    # Vertically align the text
    title_height = text_height(wrapped_title, title_font, line_spacing)
    content_offset = max(padding, (550 - title_height) // 2)

    imgdraw.multiline_text(
        (padding, content_offset),
        wrapped_title,
        font=title_font,
        fill=(255, 255, 255),
        spacing=line_spacing,
    )

    logo_font = ImageFont.truetype(str(templates_path / "fonts/librefranklin-400.ttf"), 50)
    imgdraw.multiline_text(
        (logo_position[0] + logo_size[0], logo_position[1] + 1),
        "All About Berlin",
        font=logo_font,
        fill=(255, 255, 255),
    )

    return image


class EntryImageUrlProcessor(EntryContextProcessor):
    def process_entry(
        self,
        context: Context,
        entry_uri: EntryURI,
        changed_files: set[Path] | None = None,
    ) -> None:
        context["entries"][entry_uri]["image_url"] = f"{config.site_url}/{str(Path(entry_uri).with_suffix('.png'))}"


class EntryImageRenderer(Renderer):
    """
    Creates social media images for entries
    """

    def get_image_text(self, entry: Entry) -> str:
        entry_title = entry.get("short_title") or entry.get("title")
        if not entry_title:
            raise ValueError("Entry has no image text")
        return str(entry_title).replace(soft_hyphen, "")

    def get_hash(self, entry: Entry) -> str:
        return hashlib.md5(self.get_image_text(entry).encode("utf-8")).hexdigest()

    def render(self, context: Context, changed_files: set[Path] | None = None) -> set[Path]:
        files_to_keep = set()

        entries_to_render = [
            (Path(entry_uri), entry)
            for entry_uri, entry in context["entries"].items()
            if entry_uri.lower().endswith(".md")
        ]

        for entry_path, entry in entries_to_render:
            try:
                image_text = self.get_image_text(entry)
            except ValueError:
                continue

            image_path = entry_path.with_suffix(".png")
            abs_image_path = config.output_path / image_path
            needs_rerender = False

            if changed_files is None or (config.content_path / entry_path) in changed_files:
                needs_rerender = True
                if abs_image_path.exists():
                    existing_image = Image.open(abs_image_path)
                    exif = existing_image.getexif()
                    needs_rerender = exif.get(exif_description_field) != self.get_hash(entry)

            if needs_rerender:
                logger.info(f"Rendering post image {str(image_path)}")
                image = make_cover_image(image_text, config.templates_path)

                # If the image hash has changed, rerender it.
                # Unicode strings cause problems, so a simple hash is more reliable.
                exif = image.getexif()
                exif[exif_description_field] = self.get_hash(entry)
                abs_image_path.parent.mkdir(parents=True, exist_ok=True)
                image.save(abs_image_path, optimize=True, exif=exif)

            files_to_keep.add(image_path)

        return files_to_keep
