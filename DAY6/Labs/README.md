# Day 6 Labs: Understanding What Members Tell You

Members contact the Fund thousands of times a year: at branches, through the call centre, by email, on WhatsApp and
on social media. They write in English, in Swahili, and very often in both in the same message. Buried in that text
is the most direct evidence you have of what's going wrong: delayed benefits, employers not remitting, an app that
won't let people log in.

Nobody can read it all. Today you'll build tools that do the first pass:

- **how members feel** (sentiment), and how that changes by channel and over time,
- **what they're writing about** (complaint category), so each message reaches the right team,
- **the facts inside free text** (names, member numbers, dates, amounts, claim references) pulled out as structured
  data.

## Today's labs

| Lab | File | Time |
|---|---|---|
| 1. Text processing, sentiment and topics with classical NLP | `Lab1_Sentiment_Classical_NLP.ipynb` | about 75 min |
| 2. Fine-tuning a small BERT model to route complaints | `Lab2_BERT_Complaint_Routing.ipynb` | about 60 min |
| 3. Extracting names, dates and amounts with spaCy | `Lab3_Entity_Extraction_spaCy.ipynb` | about 75 min |

## Files in this folder

| File | What it is |
|---|---|
| `member_feedback.csv` | About 6,200 messages from 2023-2025, with channel, region, language, and two labels added by the customer service team: `category` (9 categories) and `sentiment` (negative, neutral, positive) |
| `case_notes.csv` | 900 short notes written by branch and claims officers, with the entities in each note marked up by hand (`entities` column) so you can measure extraction accuracy |
| `requirements.txt` | Today's libraries |

The labels were added by people, so, as with any hand-labelled data, a few of them are wrong. You'll find some.

## Setup

Open `Lab1_Sentiment_Classical_NLP.ipynb` and run its first code cell. It finds the course environment you built on Day 1,
installs today's libraries into it along with the small English spaCy model, and tells you if the notebook needs switching to the
**Python (fund-ai)** kernel. If it asks you to switch, do that and run the cell once more. You can run it as
often as you like; it only installs what's missing.

Lab 2 downloads a pre-trained model (`distilbert-base-multilingual-cased`, about 540 MB) from Hugging Face the first
time it runs. If your network is slow, start that download early: run the first code cells of Lab 2 during the
morning break.

**GPU or CPU?** Lab 2 fine-tunes a neural network. On a laptop NVIDIA GPU it takes one or two minutes. On a CPU it
takes much longer, so the notebook has a `QUICK_RUN` switch that trains on a sample. Use it if you don't have a GPU.
