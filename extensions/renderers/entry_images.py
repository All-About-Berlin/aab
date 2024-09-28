from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from ursus.config import config
from ursus.context_processors import EntryContextProcessor
from ursus.renderers import Renderer
import hashlib
import logging


logger = logging.getLogger(__name__)


exif_description_field = 0x9286


def wrap_text(text: str, font, max_width: int):
    words = text.split()
    lines = [[]]
    for word in words:
        line_width = font.getbbox(" ".join(lines[-1] + [word]))[2]
        if line_width <= max_width:
            lines[-1].append(word)
        elif font.getbbox(word)[2] > max_width:
            raise Exception("Word too long")
        else:
            lines.append([word, ])

    return "\n".join(" ".join(line) for line in lines)


def text_height(text: str, font, line_spacing: int):
    ascent, descent = font.getmetrics()
    lines = text.split('\n')
    return sum([
        font.getmask(line).getbbox()[3] + descent
        for line in lines
    ]) + (len(lines) - 1) * line_spacing


def text_width(text: str, font):
    return max(font.getmask(line).getbox()[2] for line in text.split('\n'))


def make_cover_image(text: str, templates_path: Path) -> Image:
    padding = 50
    line_spacing = 25
    image_size = (1200, 630)
    logo_size = (70, 70)
    logo_position = (700, image_size[1] - logo_size[1] - 30)

    image = Image.new("RGB", image_size, (218, 81, 61))
    imgdraw = ImageDraw.Draw(image)

    # Place logo
    logo = Image.open(str(templates_path / 'staticimages/logo.png'))
    logo.thumbnail(logo_size)
    image.paste(logo, logo_position)

    # Wrap the main text to fit available space
    font_size = 100
    while True:
        title_font = ImageFont.truetype(str(templates_path / 'fonts/librefranklin-400.ttf'), font_size)
        try:
            wrapped_title = wrap_text(text, title_font, image.size[0] - 2 * padding)
        except:
            font_size -= 3
        else:
            if len(wrapped_title.split('\n')) > 4:
                font_size -= 3
            else:
                break

    # Vertically align the text
    title_height = text_height(wrapped_title, title_font, line_spacing)
    content_offset = max(padding, (550 - title_height) // 2)

    imgdraw.multiline_text(
        (padding, content_offset), wrapped_title,
        font=title_font, fill=(255, 255, 255), spacing=line_spacing
    )

    logo_font = ImageFont.truetype(str(templates_path / 'fonts/librefranklin-400.ttf'), 50)
    imgdraw.multiline_text(
        (logo_position[0] + logo_size[0], logo_position[1] + 1), "All About Berlin",
        font=logo_font, fill=(255, 255, 255)
    )

    return image


class EntryImageUrlProcessor(EntryContextProcessor):
    def __init__(self):
        super().__init__()

    def process_entry(self, context: dict, entry_uri: str):
        if get_entry_image_text(context['entries'][entry_uri]):
            context['entries'][entry_uri]['image_url'] = f"{config.site_url}/{str(Path(entry_uri).with_suffix('.png'))}"


def get_entry_image_text(entry: dict) -> str:
    return entry.get('short_title') or entry.get('title')


class EntryImageRenderer(Renderer):
    """
    Creates social media images for entries
    """

    def get_hash(self, entry: dict) -> str:
        return hashlib.md5(get_entry_image_text(entry).encode("utf-8")).hexdigest()

    def render(self, context: dict, changed_files: set = None) -> set:
        files_to_keep = set()
        for entry_uri, entry in context['entries'].items():
            if not get_entry_image_text(entry):
                continue

            entry_path = Path(entry_uri)
            image_path = Path(entry_uri).with_suffix('.png')
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
                image = make_cover_image(get_entry_image_text(entry), config.templates_path)

                # Unicode strings cause problems, so a simple hash is more reliable
                exif = image.getexif()
                exif[exif_description_field] = self.get_hash(entry)
                image.save(abs_image_path, optimize=True, exif=exif)

            files_to_keep.add(image_path)

        return files_to_keep
