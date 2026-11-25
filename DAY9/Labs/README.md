# Day 9 Labs: A Handbook Assistant, Built Properly

Day 7 showed that an LLM answering from memory will get policy wrong. Day 8 showed that fine-tuning changes a model's
style more reliably than its facts, and that giving the model the right text works better. Today you build that properly:

- **Retrieval-augmented generation (RAG):** for every question, find the few passages of the handbook and circulars that
  answer it, and have the model answer *from those passages only*, with citations.
- **An internal API:** wrap the assistant in a service that other Fund systems can call, with authentication, rate
  limits and logging.
- **The cloud question:** what would change if the same pipeline ran on Azure, AWS or Google Cloud instead of the Fund's
  own servers?

## Today's labs

| Lab | File | Time |
|---|---|---|
| 1. A RAG pipeline over the handbook and circulars | `Lab1_RAG_Pipeline.ipynb` | about 90 min |
| 2. Wrapping it in a FastAPI service and calling it from an in-house app | `Lab2_RAG_API_Service.ipynb` | about 60 min |
| 3. The same pipeline on a cloud platform: a side-by-side comparison | `Lab3_Cloud_Deployment_Comparison.md` + `Lab3_Cost_Worksheet.ipynb` | about 60 min |

Lab 2 uses the index Lab 1 saves. Lab 3 mostly needs a pen and a good argument.

## Files in this folder

| File / folder | What it is |
|---|---|
| `handbook/` | The Member Handbook (Training Edition), one file per section |
| `circulars/` | Three circulars. One updates the late-payment penalty and partly supersedes another. |
| `rag_eval_questions.csv` | 20 test questions, each with the document that should answer it and the key fact the answer must contain. Two can't be answered from the documents at all. |
| `requirements.txt` | Today's libraries |

## Setup

Open `Lab1_RAG_Pipeline.ipynb` and run its first code cell. It finds the course environment you built on Day 1,
installs today's libraries into it, and tells you if the notebook needs switching to the
**Python (fund-ai)** kernel. If it asks you to switch, do that and run the cell once more. You can run it as
often as you like; it only installs what's missing.

You also need Ollama from Day 7, running, with at least one model. `gemma2:2b` did best in most Day 7 scorecards;
`qwen2.5:1.5b` works too. Lab 1 downloads two embedding models from Hugging Face the first time it runs (about 470 MB
each): `intfloat/multilingual-e5-small`, which the pipeline uses because it handles Swahili, and
`paraphrase-multilingual-MiniLM-L12-v2`, which you'll test and find doesn't.

Everything runs on a laptop. A GPU makes the embedding step faster but isn't required.
