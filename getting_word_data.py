

#LEXIN, getting word definition

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

#clean the data
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

#this is the stuff we call, note that it returns alot and can return several "definitions".
def get_definition(word):
    entries = fetch_lexin(word)

    definitions = []

    for entry in entries:
        definitions.append(parse_entry(entry))

    return definitions
    


if __name__ == "__main__":
    for sense in get_definition("erinra"):
        print(sense)
