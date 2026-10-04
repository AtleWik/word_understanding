
import os
from dotenv import load_dotenv
import json
import requests

from getting_word_data import get_definition
from getting_synonyms import synonym_catcher
from example_sentences import fetch_examples_sentences


experimental_word_list = ["beivra", "erinra", "kokettera", "plombering", "fadäs", "ingalunda", "förfördela", "björntjänst"]


#getting the API KEY from the enc
load_dotenv()
API_KEY = os.environ["API_KEY"]
LLM_BASE_URL = os.environ["LLM_BASE_URL"]
LLM_MODEL = os.environ["LLM_MODEL"]



#extracting the data from the different files
def get_word_data(word):
    #getting info
    general_word_info = get_definition(word)

    #since one word can have multiple def eg: "erinra", we need to keep them tidy, put the data with the sense_ids
    #get synonyms
    synonyms_by_sense = {}
    for information_dict in general_word_info:
        for sid in information_dict["saldo_links"]:
            if sid not in synonyms_by_sense:
                synonyms_by_sense[sid] = synonym_catcher(sid)

    return {
        "word": word,
        "senses": general_word_info,
        "synonyms_by_sense": synonyms_by_sense,
    }

#needs to be revist this, fucntual meaning chekc has not been completed

#checking if a very good synonym was used, if so is the case, just give the user a correct answer and pass without running a LLM CALL
def good_synonym_used(user_answer, synonyms):

    MULTI_SYNONYM_SCORING_THRESHOLD = 180

    #check if a perfect definition or a synonym with high ranking is used, if it is, do a pass, do not make a LLM CALL
    

    parsed_user_answer = user_answer.lower().strip().strip(".,!?")
    answer_padded = f" {parsed_user_answer} " 
    user_score = 0

    for synonym in synonyms:
        clean_synonym = synonym[0].lower().strip().strip(".,!?")
        if f" {clean_synonym} " in answer_padded:
            if synonym[1] >= 70:
                return True
            else:
                user_score += synonym[1]

    if user_score > MULTI_SYNONYM_SCORING_THRESHOLD:
        return True

    return False

#scoring system needs tweaking

#prep for llm call, getting contexts
def get_corpora(word):
    examples_sentences = fetch_examples_sentences(word)
    if len(examples_sentences) < 1:
        print("PROBLEM, does this word even exist?")

    return  examples_sentences


def build_prompt(word_data, exmaples, user_answer):

    # skriv ut definitioner
    definitions_text = ""
    for sense in word_data["senses"]:
        definitions_text += f"- {sense['definition']}\n"

    synonym_set = set()
    for sense_synonyms in word_data["synonyms_by_sense"].values():
        for synonym, degree in sense_synonyms:
            synonym_set.add(synonym)

    synonyms_text = ", ".join(sorted(synonym_set))

    if not synonyms_text:
        synonyms_text = "inga synonymer funna"

    examples_text =""

    for copora_example in exmaples:
        examples_text += f"- {copora_example}\n"

    if not examples_text:
        examples_text = "inga exmpel tillgängliga"

    prompt = f"""Din uppgift är att göra en bedömning av en elevsvar om den förstår det ord som den testas på.
    
    Regler:
    - Ignorera stavfel och enkla grammatiska fel
    - Om eleven korrekt beskriver minst ett av ordets betydelser är svaret correct.
    - partial betyder att eleven är på rätt spår men beskrivningen är ofullständigt eller otillfredställande
    - Fältet "verdict" ska vara exakt ett av följande ord: correct, partial, wrong.

    Ord: {word_data['word']}
    Definitioner: 
    {definitions_text}

    Ordets olika synonymer: {synonyms_text}

    Ordet som skall bedömmas i olika textutdrag (för att bygga din föreståelse):
    {examples_text}

    Elevensvar: {user_answer}

    Noter att all ovan given information förutom elevsvaret är för att bygga kontext så du själv kan göra en bättre bedömning av elevens svar.
    Svara endast med JSON, ingen annan text. Se till att svara enligt formatet nedan:
    {{"verdict": "correct, partial eller wrong", "reason": "En mening på svenska som förklarar bedömningen"}} """

    return prompt

def call_llm(prompt):
    url = f"{LLM_BASE_URL}/chat/completions"

    headers = {"Authorization": f"Bearer {API_KEY}"}

    body = {
        "model": LLM_MODEL ,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
    }

    r = requests.post(url, headers=headers, json=body, timeout=20)
    r.raise_for_status()

    data = r.json()
    return {
        "content": data["choices"][0]["message"]["content"],
        "usage": data["usage"],
    }

def check_answer(word, user_answer):
    word_data = get_word_data(word)

    synonyms = []

    for sense_synonyms in word_data["synonyms_by_sense"].values():
        synonyms.extend(sense_synonyms)

    #aviod calling LLM if needed
    if good_synonym_used(user_answer, synonyms):
        return {"verdict": "correct", "reason": "Du använde en synonym."}

    
    examples = get_corpora(word)
    prompt = build_prompt(word_data, examples, user_answer)
    result = call_llm(prompt)
    return json.loads(result["content"])



#init testing
#if __name__ == "__main__":
#    for word in ["erinra", "beivra"]:
#        data = get_word_data(word)
#        examples = get_corpora(word)
#        print(build_prompt(data, examples, "minnas"))

#more test
#if __name__ == "__main__":
#    for word in ["erinra", "beivra"]:
#        data = get_word_data(word)
#        examples = get_corpora(word)
#        prompt = build_prompt(data, examples, "minnas")
#        result = call_llm(prompt)
#        print(word, result["content"])
#        print(result["usage"])
#nya :D

if __name__ == "__main__":
    for word in experimental_word_list:
        print(f"Ditt ord är {word} \n")

        user_answer = input("Vad betyder ordet? Det är ok att bara svara direkt med definition eller synonymer")

        verdict = check_answer(word, user_answer)

        if verdict["verdict"] == "correct":
            print("Bra jobbat, du vet vad ordet betyder!\n")
        else:
            print("Inte riktigt: " + verdict["reason"] + "\n")
        
