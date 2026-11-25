# Day 8 Labs: Fine-Tuning an Open-Source LLM on the Fund's Material

Yesterday you saw what a general-purpose open model can and can't do with the Fund's questions. Today you'll adapt one:
teach it the Fund's tone, its answer format, its habit of refusing what it shouldn't answer, and as many of the common
answers as it can hold.

You'll do the three jobs that every fine-tuning project consists of, in the proportions they really take:

1. **Prepare the data** (most of the effort, and most of the value): turn a messy FAQ export and the handbook into a
   clean instruction dataset.
2. **Fine-tune** with LoRA, a parameter-efficient method that trains a few million parameters instead of hundreds of
   millions, and runs on a laptop GPU.
3. **Evaluate** honestly against the base model, on questions the model never saw, and check that nothing else got worse.

## Today's labs

| Lab | File | Time |
|---|---|---|
| 1. Building an instruction-tuning dataset | `Lab1_Instruction_Dataset.ipynb` | about 75 min |
| 2. Fine-tuning with LoRA (and QLoRA) | `Lab2_LoRA_Fine_Tuning.ipynb` | about 60 min |
| 3. Did it work? Evaluating against the base model | `Lab3_Evaluate_Fine_Tuned_Model.ipynb` | about 75 min |

Lab 2 uses the dataset Lab 1 writes. Lab 3 uses the adapter Lab 2 saves.

## Files in this folder

| File / folder | What it is |
|---|---|
| `faq_export.csv` | An export of the Fund's website FAQ from its content management system, exactly as messy as those usually are |
| `handbook/`, `circulars/` | The Member Handbook (Training Edition) and circulars, the authoritative sources |
| `heldout_questions.csv` | 22 questions written by staff, in their own words, with reference answers. **Never used for training.** |
| `requirements.txt` | Today's libraries |

## Setup

Open `Lab1_Instruction_Dataset.ipynb` and run its first code cell. It finds the course environment you built on Day 1,
installs today's libraries into it, and tells you if the notebook needs switching to the
**Python (fund-ai)** kernel. If it asks you to switch, do that and run the cell once more. You can run it as
often as you like; it only installs what's missing.

The base model for the labs is **Qwen2.5-0.5B-Instruct** (Apache 2.0 licence, about 1 GB). It's small enough to fine-tune
on a laptop GPU in a couple of minutes, and on a CPU in a reasonable time using the `QUICK_RUN` switch. It downloads from
Hugging Face the first time Lab 2 runs.

If you have an NVIDIA GPU with 8 GB or more, Lab 2 shows how to fine-tune a larger model (1.5B-3B) with **QLoRA**, which
loads the base model in 4-bit precision. That needs one extra package:

```bash
python -m pip install bitsandbytes
```

Lab 1 uses Ollama from Day 7 for one optional step (drafting extra questions). If Ollama isn't running, that step is
skipped automatically.
