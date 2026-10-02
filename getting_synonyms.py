
#SWESAURUS, getting synonyms

import requests
import json
#base URL

KARP = "https://spraakbanken4.it.gu.se/karp/v7"


#fetch data
def fetch_swesaurus(sense_id, size = 20):
    q = f"equals|saldo|{sense_id}"
    r = requests.get(
        f"{KARP}/query/swesaurus",
        params={"q": q, "size": size},
        timeout=20,
    )
    r.raise_for_status()

    extracted_data =r.json() #full swesaurus return object
    hits = extracted_data.get("hits", []) #generate list of the results

    #words
    word_list = []
    for h in hits:
        entry = h.get("entry",h) #get the entries if they exist
        word_list.append(entry)

    return word_list

def clean_sense_id(sense_id):
    """'komma_ihåg..1' -> 'komma ihåg'"""
    return sense_id.split("..")[0].replace("_", " ")

def parse_relations(entry):
    results = []
    for rel in entry.get("relations") or []:
        sense = rel.get("saldo")
        if not sense:
            continue
        results.append([clean_sense_id(sense), rel.get("degree", 0)])
    return results

#the sense:id is gotten from the word data program
def synonym_catcher(sense_id):
    entries = fetch_swesaurus(sense_id)

    synonym_list = []

    for entry in entries:
        synonym_list.extend(parse_relations(entry))

    return synonym_list

#for testing

if __name__ == "__main__":
    print(synonym_catcher("erinra..1"))
    print(synonym_catcher("beivra..1"))

