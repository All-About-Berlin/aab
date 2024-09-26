from hashlib import sha256
from openai import OpenAI
from pathlib import Path
from typing import List, Tuple
from ursus.config import config
from ursus.utils import get_files_in_path, import_module_or_path, parse_markdown_head_matter, format_markdown_head_matter
import logging
import re


language_names = {
    'de': 'German',
}


def split_document(text: str) -> Tuple[str, str]:
    """
    Split the document into head matter and body
    """
    head_pattern = r'^---\s*\n(.*?\n)*?---\s*\n'
    if head_match := re.search(head_pattern, text, re.DOTALL):
        head_matter = head_match.group(0)
        body = text[len(head_matter):]
        return head_matter, body
    else:
        return "", text


def translate_path(original_path: Path, language_code: str) -> Path:
    return language_code / original_path


def translate_string(text: str, language_code: str, cache_path: Path) -> str:
    if not text.strip():
        return text

    stripped_text = text.strip()

    prompt = "\n".join((
        "You are an expert legal translator. You translate texts about German immigration law, and about moving to Germany. Your translation must be as accurate as possible.",
        f"Translate the given texts from English to {language_names[language_code]}. You must always follow these translation rules:",
        # "- Prefer translations from the dictionary below.",
        "- Preserve the format, whitespace and punctuation of the original text.",
        "- Prefer gender-neutral terms.",
        "- Always address the reader with the informal form 'Du' with a capital D, not the formal 'Sie'.",
        "- Only return the translated text.",
    ))

    cache_hash = sha256((prompt + stripped_text).encode('utf-8')).hexdigest()
    string_cache_path = cache_path / f"{cache_hash}.txt"

    if string_cache_path.exists():
        return string_cache_path.read_text()
    else:
        preview = stripped_text[0:20].replace('\n', ' ').strip()
        logging.info(f"└── Translating string \"{preview}\" to {language_names[language_code]}")
        translation = OpenAI(api_key=config.openai_api_key).chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "assistant", "content": "Input the text to translate. I will only return the translated text."},
                {"role": "user", "content": stripped_text}
            ],
            n=1,
            temperature=0.2,
        ).choices[0].message.content.strip()
        string_cache_path.parent.mkdir(parents=True, exist_ok=True)
        string_cache_path.write_text(translation)
        return translation


def translate_head_matter(head_matter: str, language_code: str, cache_path: Path) -> str:
    if not head_matter.strip():
        return

    metadata, _ = parse_markdown_head_matter(head_matter.split('\n'))
    translated_metadata = {**metadata}
    for field_name in config.metadata_fields_to_translate:
        if field_name not in metadata:
            continue
        elif len(metadata[field_name]) != 1:
            raise ValueError(f"Field is an array: {field_name}")

        translated_metadata[field_name] = [translate_string(metadata[field_name][0], language_code, cache_path), ]

    return format_markdown_head_matter(translated_metadata)


def chunk_markdown(text: str) -> List[[str, str]]:
    chunks = []
    for line in text.split('\n'):
        if line.startswith('## ') or not chunks:
            chunks.append([
                line.removeprefix('## ') if line.startswith('## ') else None,
                ''
            ])

        chunks[-1][1] += (line + '\n')

    return chunks


def translate_markdown(text: str, language_code: str, cache_path: Path) -> str:
    if not text.strip():
        return text

    prompt = "\n".join((
        "You are an expert legal translator for guides written in Markdown. The guides are about German immigration law, and about moving to Germany. Your translation must be as accurate as possible.",
        f"Translate the given Markdown texts from English to {language_names[language_code]}. You must always follow these translation rules:",
        "- Preserve the format, whitespace and punctuation of the original text.",
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

    translated_chunks = []
    for chunk_title, chunk_text in chunk_markdown(text):
        chunk_hash = sha256((prompt + chunk_text).encode('utf-8')).hexdigest()
        chunk_cache_path = cache_path / f"{chunk_hash}.md"

        if chunk_cache_path.exists():
            translated_chunks.append(chunk_cache_path.read_text())
        else:
            # ChatGPT tends to lose whitespace at the start and end of the text, so we preserve and restore it
            whitespace_before = chunk_text[:len(chunk_text) - len(chunk_text.lstrip())]
            whitespace_after = chunk_text[len(chunk_text.rstrip()):]
            stripped_chunk_text = chunk_text.strip()

            preview = stripped_chunk_text[0:20].replace('\n', ' ').strip()
            logging.info(f"└── Translating chunk \"{preview}\" to {language_names[language_code]}")
            translated_chunk = whitespace_before + OpenAI(api_key=config.openai_api_key).chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "system", "content": f"The text to translate is titled \"{chunk_title}\""},
                    {"role": "assistant", "content": "Input the Markdown text to translate. I will only return the translated Markdown."},
                    {"role": "user", "content": stripped_chunk_text}
                ],
                n=1,
                temperature=0.2,
            ).choices[0].message.content.strip() + whitespace_after

            chunk_cache_path.parent.mkdir(parents=True, exist_ok=True)
            chunk_cache_path.write_text(translated_chunk)

            translated_chunks.append(translated_chunk)

    return "".join(translated_chunks)


def translate_file(original_file: Path, language_code: str):
    logging.info(f"Translating {str(original_file)} to {language_names[language_code]}")

    text = (config.content_path / original_file).read_text()
    head_matter, body = split_document(text)

    translated_file = translate_path(original_file, language_code)
    translation_cache_path = config.translation_cache_path / translated_file
    translated_head_matter = translate_head_matter(head_matter, language_code, cache_path=translation_cache_path)
    translated_body = translate_markdown(body, language_code, cache_path=translation_cache_path)

    (config.content_path / translated_file).parent.mkdir(parents=True, exist_ok=True)
    (config.content_path / translated_file).write_text(f"{translated_head_matter}\n{translated_body}")


def translate_content(language_code: str):
    content_files = [
        f for f in get_files_in_path(config.content_path, suffix='.md')
        if f.parts[0] != language_code  # e.g. de/path/to/file.md
    ]

    for original_file in content_files:
        translate_file(original_file, language_code)


if __name__ == '__main__':
    import_module_or_path('ursus_config.py')
    logging.basicConfig(**config.logging)
    languages = ('de', )
    for language_code in languages:
        translate_content(language_code)
