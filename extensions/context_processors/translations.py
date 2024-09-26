from hashlib import sha256
from openai import OpenAI
from pathlib import Path
from typing import List, Tuple
from ursus.config import config
from ursus.utils import get_files_in_path, import_module_or_path, parse_markdown_head_matter
import logging
import re

logging.basicConfig(**config.logging)
logger = logging.getLogger(__name__)


def split_document(text: str) -> Tuple[str, str]:
    head_pattern = r'^---\s*\n(.*?\n)*?---\s*\n'
    if head_match := re.search(head_pattern, text, re.DOTALL):
        head_matter = head_match.group(0)
        content = text[len(head_matter):]
        return head_matter, content
    else:
        return "", text


def chunk_text(text: str) -> List[[str, str]]:
    chunks = []
    for line in text.split('\n'):
        if line.startswith('## ') or not chunks:
            chunks.append([
                line.removeprefix('## ') if line.startswith('## ') else None,
                ''
            ])

        chunks[-1][1] += (line + '\n')

    return chunks


def hash_section(translation_prompt: str, text: str) -> str:
    return sha256((translation_prompt + text).encode('utf-8')).hexdigest()


def translate_metadata_field(translation_prompt: str, value: str):
    return f"{value} (DE)"


def translate_metadata(translation_prompt: str, metadata: dict, fields: List[str]) -> str:
    translated_metadata = {**metadata}
    translated_fields = {name: translate_metadata_field(translation_prompt, metadata.get(name)) for name in fields}
    translated_metadata.update(translated_fields)
    return translated_metadata


def dict_to_head_matter(metadata: dict) -> str:
    return "\n".join([
        "---",
        *[f"{key}: {value}" for key, value in metadata.items()],
        "---\n",
    ])


def translate_markdown(translation_prompt: str, text: str, language: str, document_title: str, section_title: str = None) -> str:
    if not text.strip():
        return text

    # ChatGPT tends to lose whitespace at the start and end of the text, so we preserve and restore it
    whitespace_before = text[:len(text) - len(text.lstrip())]
    whitespace_after = text[len(text.rstrip()):]
    stripped_text = text.strip()

    translation = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "system", "content": f"The document to translate is titled \"{document_title}\". This section is titled \"{section_title}\""},
            {"role": "assistant", "content": "Input the Markdown text to translate. I will only return the translated Markdown."},
            {"role": "user", "content": stripped_text}
        ],
        n=1,
        temperature=0.2,
    ).choices[0].message.content.strip()

    return "".join([whitespace_before, translation, whitespace_after])


def translate_file(translation_prompt: str, metadata_prompt: str, original_file: Path, translated_file: Path, language: str):
    original_text = (config.content_path / original_file).read_text()

    translation_dict = {}
    section_hashes = []

    head_matter, body = split_document(original_text)

    logging.info(f"Translating {str(original_file)} to {language}")

    metadata, _ = parse_markdown_head_matter(head_matter.split('\n'))
    translated_head_matter = dict_to_head_matter(translate_metadata(metadata_prompt, metadata, ('title', 'description')))

    for section_title, chunk in chunk_text(body):
        section_hash = hash_section(translation_prompt, chunk)
        section_hashes.append(section_hash)

        cache_path = config.translation_cache_path / translated_file / f'{section_hash}.md'
        if cache_path.exists():
            translation = cache_path.read_text()
        else:
            logging.info(f"➞ Translating section '{section_title or 'Introduction'}' to {language}")
            translation = translate_markdown(translation_prompt, chunk, language, metadata.get('title'), section_title)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(translation)

        translation_dict[section_hash] = translation

    # Assemble the chunks into a full translation
    full_translation = translated_head_matter + ''.join([translation_dict[h] for h in section_hashes])
    (config.content_path / translated_file).parent.mkdir(parents=True, exist_ok=True)
    (config.content_path / translated_file).write_text(full_translation)


def translate_content(translation_prompt: str, metadata_prompt: str, content_path: Path, languages: List[str]):
    content_files = [
        f for f in get_files_in_path(content_path, suffix='.md')
        if f.parts[0] not in languages  # e.g. de/path/to/file.md
    ]
    for original_file in content_files:
        for language in languages:
            translated_file = language / original_file
            translate_file(translation_prompt, metadata_prompt, original_file, translated_file, language)


if __name__ == '__main__':
    import_module_or_path('ursus_config.py')
    client = OpenAI(
        api_key=config.openai_api_key
    )
    languages = ('de', )
    prompt = "\n".join((
        "You are an expert legal translator for guides written in Markdown. The guides are about German immigration law, and about moving to Germany. Your translation must be as accurate as possible.",
        "Translate the given Markdown texts from English to German. Your translations are accurate. They not to deviate from the original structure, content, writing style, tone and formatting. You must always follow these translation rules:",
        "- Preserve the format and whitespace of the original text.",
        "- Preserve all whitespace, even at the end of a line.",
        "- Do not translate German terms.",
        "- Do not translate URLs.",
        "- Do not translate footnote symbols. For example '[^123]'.",
        "- Do not translate any text between {% braces with percent signs %}, {{ double curly braces }} or [[ double square braces ]].",
        "- Prefer simple and straightforward language.",
        # "- Prefer translations from the dictionary below.",
        "- Prefer gender-neutral terms.",
        "- If you use a gender asterisk (Genderstern), always add a backslash in front of it. For example, 'Reader' becomes 'Leser\\*in'.",
        "- Always address the reader with the informal form 'Du' with a capital D, not the formal 'Sie'.",
        "- Only return the translated Markdown. Do not wrap the translation in a code block.",
    ))

    metadata_prompt = "\n".join((
        "You are an expert legal translator. You translate texts about German immigration law, and about moving to Germany. Your translation must be as accurate as possible.",
        "Translate the given texts from English to German. Your translations are accurate. They not to deviate from the original structure, content, writing style, tone and formatting. You must always follow these translation rules:",
        # "- Prefer translations from the dictionary below.",
        "- Prefer gender-neutral terms.",
        "- Always address the reader with the informal form 'Du' with a capital D, not the formal 'Sie'.",
        "- Only return the translated text.",
    ))

    translate_content(prompt, metadata_prompt, config.content_path, languages)
