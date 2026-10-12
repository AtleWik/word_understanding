
## Simple General

A small python tool, that quizzes you on difficult swedish words and judges your answer utilizing open lexical resources via Språkbanken and an LLM.

> **Status:** Work in progress....

## How it works

For each word, the program chains several external tool calls before
(optionally) calling an LLM:

1. **Definitions** from Lexin, via Språkbanken's Karp v7 API
2. **Synonyms** for each word sense from Swesaurus (Karp v7), with a synonym-strength degree
3. **Example sentences** from the Korp v8 corpus API (Göteborgs-Posten
   2012–2013, with fallback to novel corpora and SUC3 when too few hits
   are found)
   This to give extra context to the user.
4. **LLM judgement**: the user's answer, definitions, synonyms and
   corpus examples are sent to an OpenAI-compatible chat API, which
   returns a JSON verdict (`correct` / `partial` / `wrong`) with a
   short explanation

If the user's answer contains a strong synonym, the LLM call is skipped entirely, saving latency and cost.

## Setup

    pip install requests python-dotenv
    cp .env.example .env   # then add your API key

default model: `openai/gpt-oss-120b` via Groq (any OpenAI-compatible
endpoint works).

## Run

    python main.py

Words are read from `word.txt`, one per line.

## Planned

- Tracing of each tool and LLM call (latency, result counts, token
  usage) to analyse where time is spent and how often lookups fail
- Tuning of the synonym scoring threshold
- Running independent lookups in parallel, to minimize API calls if possible
- Increased feedback towards user
- System for feedback, and basic flashcard function, showing words the user got wrong
- Optionally, a prettier real frontend