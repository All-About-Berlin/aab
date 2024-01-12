#!/usr/bin/env python3
from datetime import datetime
from pathlib import Path
from ursus.config import config
from ursus.utils import import_module_or_path
import argparse
import re
import readline


if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")


expert_template = """---
Name: {name}
Job_title: {title}
Email: {email}
Website: {website}
Picture: experts/photos/{slug}.jpg
---

{description}
"""

review_template = """---
Related_expert: experts/{expert_slug}.md
Date_reviewed: {date}
---
"""


def get_user_input(title: str, autocompleter=None):
    print(f"\033[1m{title}:\033[0m")
    readline.set_completer_delims('/')
    readline.set_completer(autocompleter)
    return input("> \033[0m")


def autocomplete_guides(query, state):
    options = [p.stem for p in (config.content_path / 'guides').rglob(f'{query}*.md')]
    return options[state] if state < len(options) else None


def autocomplete_experts(query, state):
    options = [p.stem for p in (config.content_path / 'experts').rglob(f'{query}*.md')]
    return options[state] if state < len(options) else None


def add_expert(expert_slug: str):
    name = get_user_input("Expert name")

    file_content = expert_template.format(
        name=name,
        title=get_user_input("Job title"),
        email=get_user_input("Email"),
        website=get_user_input("Website"),
        description=get_user_input("Description"),
        slug=expert_slug,
    )

    file_path = config.content_path / f'experts/{expert_slug}.md'
    print(f"Saving to {str(file_path)}")
    with file_path.open('w') as file:
        file.writelines(file_content)
    print("\n---\n")


def add_review():
    guide_slug = get_user_input("Guide slug", autocomplete_guides)
    expert_slug = get_user_input("Expert slug", autocomplete_experts)

    if not (config.content_path / f'experts/{expert_slug}.md').exists():
        add_expert(expert_slug)

    file_content = review_template.format(
        expert_slug=expert_slug,
        date=datetime.now().strftime("%Y-%m-%d"),
    )

    review_path = config.content_path / f'reviews/{guide_slug}/{expert_slug}.md'
    print(f"Saving review to {str(review_path)}")
    review_path.parent.mkdir(parents=True, exist_ok=True)
    with review_path.open('w') as file:
        file.writelines(file_content)
    print("\n---\n")

    print(f"Adding review to guides/{guide_slug}.md")

    reviewers_regex = re.compile(r"Related_reviews:(\s*\n)(\s+)(.*)$", re.MULTILINE | re.DOTALL)
    guide_path = config.content_path / f'guides/{guide_slug}.md'
    with guide_path.open() as file:
        guide_content = file.read()

    relative_review_path = str(review_path.relative_to(config.content_path))

    if 'Related_reviews:' not in guide_content:
        guide_content = re.sub(
            re.compile(r"---(.*)---", re.MULTILINE | re.DOTALL),
            r"---\1Related_reviews:\n    " + relative_review_path + "\n---",
            guide_content
        )
    else:
        guide_content = re.sub(
            reviewers_regex,
            r"Related_reviews:\1\2" + relative_review_path + r"\n\2\3",
            guide_content
        )

    with guide_path.open('w') as file:
        file.writelines(guide_content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='add_expert',
        description='Creates an expert entry',
    )
    parser.add_argument(
        '-c', '--config',
        help="Path to a Python config file or module. The `config` variable will be imported from that file."
    )
    args = parser.parse_args()

    if args.config:
        import_module_or_path(args.config)
    elif Path('./ursus_config.py').exists():
        import_module_or_path('ursus_config.py')

    add_review()
