# Day 7 Labs: Large Language Models, On Your Own Hardware

For six days you've built models that do one job each: score a claim, forecast a series, route a complaint. Today
you meet models that do many jobs from a written instruction: summarise this letter, classify this message, answer
this question from the handbook. These are **large language models (LLMs)**.

The Fund handles personal and financial data about millions of Tanzanians. So the question today isn't only "which
model is cleverest?" It's **"which models can we run on our own hardware, under our own control, that are good enough
for the job?"** Everything today runs locally. No member data leaves the machine.

## Today's labs

| Lab | File | Time |
|---|---|---|
| 1. Running and querying open-source LLMs locally | `Lab1_Running_LLMs_Locally.ipynb` | about 60 min |
| 2. Prompt engineering for Fund tasks | `Lab2_Prompt_Engineering.ipynb` | about 75 min |
| 3. A model-selection scorecard | `Lab3_Model_Selection_Scorecard.ipynb` | about 75 min |

## Files in this folder

| File / folder | What it is |
|---|---|
| `handbook/` | The Member Handbook (Training Edition), one file per section. **Fictional** and simplified for the course; see `00_read_me_first.md`. |
| `circulars/` | Three training-edition circulars that update the handbook, including one that changes the late-payment penalty |
| `documents/` | Letters and a memo to summarise and extract information from, in English and Swahili |
| `member_feedback.csv` | The member feedback from Day 6, for classification with prompts |
| `requirements.txt` | Today's libraries |

A note on the handbook: you know the Fund's real rules far better than this document does. Some figures in it have
been simplified or changed on purpose. When a model gets something "wrong" according to your experience but "right"
according to the handbook, that's a useful conversation, not a problem.

## Setup: Ollama

Ollama runs open-source LLMs on your own machine and gives them a simple local web API.

1. Install it from https://ollama.com (Windows, macOS and Linux installers). On a locked-down machine, ask the
   facilitator for the offline installer.
2. Check it's running: open http://localhost:11434 in a browser. You should see "Ollama is running".
3. Pull the models for today. Start this **before** the lab, since each download is 1-2 GB:

```bash
ollama pull qwen2.5:1.5b
ollama pull llama3.2:1b
ollama pull gemma2:2b
```

If your laptop has 16 GB of RAM or a GPU with 8 GB or more, also pull larger versions, which are noticeably better:

```bash
ollama pull llama3.2:3b
ollama pull qwen2.5:3b
```

Then open `Lab1_Running_LLMs_Locally.ipynb` and run its first code cell. It installs today's Python libraries
into your Day 1 environment, checks that Ollama is running, and lists any of the three models you still need
to pull. If it asks you to switch the kernel to **Python (fund-ai)**, do that and run the cell once more.

The notebooks talk to Ollama over `http://localhost:11434`. If your Ollama runs on a shared server instead, set the
`OLLAMA_URL` variable at the top of each notebook.

**GPU or CPU?** Ollama uses an NVIDIA or Apple GPU automatically if there is one. The small models above run on a
CPU too, just more slowly: expect a few seconds per answer rather than under a second.
