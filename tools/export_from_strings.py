"""Builds v1/packs.json from the premium string-arrays of the PartyPuzl app.

One-off migration tool: premium content used to ship in the app's strings.xml. Run it against
the app checkout that still has the arrays:

    python3 tools/export_from_strings.py ../partyPuzz/app/src/main/res > v1/packs.json

After the migration, edit v1/packs.json directly. See README.md for the format.
"""

import json
import sys
import xml.etree.ElementTree as ElementTree
from pathlib import Path

SCHEMA_VERSION = 1
LOCALES = {"en": "values", "es": "values-es"}


def unescape(raw):
    text = (raw or "").strip()
    if len(text) >= 2 and text[0] == text[-1] == '"':
        text = text[1:-1]
    for escaped, plain in (("\\'", "'"), ('\\"', '"'), ("\\n", "\n"), ("\\@", "@"), ("\\?", "?")):
        text = text.replace(escaped, plain)
    return text


def read_arrays(strings_xml):
    root = ElementTree.parse(strings_xml).getroot()
    arrays = {}
    for node in root:
        if node.tag in ("string-array", "integer-array", "array"):
            arrays[node.get("name")] = [unescape("".join(item.itertext())) for item in node]
    return arrays


def trivia(arrays):
    rows = zip(arrays["movie_quiz_questions"], arrays["movie_quiz_options_a"],
               arrays["movie_quiz_options_b"], arrays["movie_quiz_correct_options"])
    return [{"question": q, "optionA": a, "optionB": b, "correct": c} for q, a, b, c in rows]


def sticky(arrays, seconds):
    rows = zip(arrays["spicy_sticky_dares"], arrays["spicy_sticky_dares_present_continuous"], seconds)
    return [{"text": t, "presentContinuous": p, "durationSeconds": int(s)} for t, p, s in rows]


def packs_for(arrays, seconds):
    return {
        "premium_movie_night": {"trivia": trivia(arrays)},
        "premium_spicy": {"sticky": sticky(arrays, seconds)},
        "premium_nsfw": {"truths": arrays["nsfw_truth_texts"], "dares": arrays["nsfw_dare_texts"]},
    }


def main(res_dir):
    by_locale = {lang: read_arrays(Path(res_dir) / folder / "strings.xml") for lang, folder in LOCALES.items()}
    seconds = by_locale["en"]["spicy_sticky_dares_duration_seconds"]
    packs = {}
    for lang, arrays in by_locale.items():
        for pack_id, prompts in packs_for(arrays, seconds).items():
            packs.setdefault(pack_id, {})[lang] = prompts
    document = {"schemaVersion": SCHEMA_VERSION, "contentVersion": 1, "packs": packs}
    json.dump(document, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main(sys.argv[1])
