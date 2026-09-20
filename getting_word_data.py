

#LEXIN, getting word definition

word = "erinra"

import requests
from pathlib import Path

#base URL

KARP = "https://spraakbanken4.it.gu.se/karp/v7"


#fecth lexin data.
def fetch_lexin(word, size = 20):
    #lexin structure
    q = f"languages(and(equals|lang|swe||equals|baseform|{word}))" #take swedish.
    r = requests.get(f"{KARP}/query/lexin", params={"q": q, "size": size}, timeout=20)
    r.raise_for_status()

    extracted_data =r.json() #full lexin return object
    hits = extracted_data.get("hits", []) #generate list of the results

    #words
    word_list = []
    for h in hits:
        entry = h.get("entry",h) #get the entries if they exist
        word_list.append(entry)

    return word_list


def parse_entry(entry):
    swe = entry["languages"][0]
    sense = entry.get("sense",{})
    #take out the stuff we need
    return {
        "baseform": swe["baseform"][0],
        "pos": swe.get("partOfSpeech"),
        "definition": sense.get("definition", {}).get("text"),
        "examples": [ex["text"] for ex in sense.get("examples", [])],
        "saldo_links": entry.get("saldoLinks", []),
    }

for e in fetch_lexin(word):
    print(parse_entry(e))



