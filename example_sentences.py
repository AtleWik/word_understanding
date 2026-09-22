
import requests

KORP_API = "https://ws.spraakbanken.gu.se/ws/korp/v8/query"


#corpora choice, utgår initialt från Göteborgsposten 2012 och 2013
DEFAULT_CORPORA = ["GP2012", "GP2013"]
#fallback, olika bonnier Roman data (ROMI), SUC3 specifict general 
FALLBACK_CORPORA = ["ROMI", "ROMII", "SUC3"]


NO_SPACE_BEFORE = {".", ",", "!", "?", ":", ";", ")", "]", "}", "\u201d", "\u2019"}

NO_SPACE_AFTER = {"(", "[", "{", "\u201c", "\u2018"}

def build_cqp_multi_parts(baseform):
    #if multiple parts, split them.
    parts =baseform.split()
    if len(parts) == 1:
        return f'[lemma contains "{parts[0]}"]'

    #if more words we have to stack them together in correct position
    first = f'[lemma contains "{parts[0]}"]'
    rest = ""
    for p in parts[1:]:
        rest += f'[word="{p}"] '
    rest = rest.strip()
    return f"{first} {rest}"

def tokens_to_text(tokens):
    #make the Korp token list into a readable string
    out = ""
    for token in tokens:
        word = token["word"]
        if not out:
            out = word
        elif word in NO_SPACE_BEFORE:
            out += word
        elif out[-1] in NO_SPACE_AFTER:
            out += word
        else:
            out += " " + word
    return out


def get_examples_sentences(baseform, max_examples=5, corpora=None, context="20 words", fetch_count=10):

    corpora = corpora or DEFAULT_CORPORA

    cqp = build_cqp_multi_parts(baseform)

    params = {
        "corpus": ",".join(corpora),
        "cqp": cqp,
        "start": 0,
        "end": fetch_count - 1,
        "default_context": context,
        "show": "lemma",
    }

    response = requests.get(KORP_API, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    seen = set()
    examples = []

    for hit in data.get("kwic", []):
        text = tokens_to_text(hit["tokens"])

        if text in seen:
            continue

        seen.add(text)

        examples.append(text)

        if len(examples) >= max_examples:
            break

    return examples




if __name__ == "__main__":
    for word in ["erinra", "beivra", "erinra sig"]:
        print(f"\n{word}:")
        for sentence in get_examples_sentences(word):
            print(f"  - {sentence}")