import html

from rest_framework import serializers


HIGHLIGHT_PRE_TAG = "\u0001HL\u0001"
HIGHLIGHT_POST_TAG = "\u0001/HL\u0001"


def _safe_highlight(text: str) -> str:
    return html.escape(text).replace(HIGHLIGHT_PRE_TAG, "<mark>").replace(HIGHLIGHT_POST_TAG, "</mark>")


class SearchHitSerializer(serializers.Serializer):
    def to_representation(self, instance):
        formatted = instance["_formatted"]
        return {
            "title": _safe_highlight(formatted["title"]),
            "url": instance["url"],
            "snippet": _safe_highlight(formatted["body"]),
            "type": instance["type"],
            "date": instance["date"],
        }
