# Lab 3: The Same Pipeline on a Cloud Platform, Side by Side

**Time:** about 60 minutes (with `Lab3_Cost_Worksheet.ipynb`)
**You'll finish with:** a clear view of what changes when the handbook assistant runs on Azure, AWS or Google Cloud
instead of the Fund's own servers, a cost comparison built on your own numbers, and a short written recommendation for the
ICT steering committee.

This lab is a walkthrough and a written comparison, not a deployment. You won't need a cloud account. What you need is the
assistant from Labs 1 and 2, your Day 7 scorecard, and a clear head about data.

---

## Part 1: What changes, and what doesn't

Look at the pipeline you built today:

```
            ┌────────────── self-hosted (today) ──────────────┐
question ─► guardrail ─► embed ─► FAISS search ─► LLM (Ollama) ─► answer
            FastAPI     E5 model   in the service   on the Fund's GPU
```

On a cloud platform, the *shape* stays exactly the same. What changes is **who runs each box**:

| Step | Self-hosted | Managed cloud equivalent |
|---|---|---|
| API, auth, rate limit, guardrail | FastAPI on the Fund's server | The same FastAPI container on a cloud container service, behind the provider's API gateway |
| Embeddings | E5 model in the service | A provider embedding endpoint, or the same E5 model in the container |
| Vector search | FAISS in memory | FAISS in the container, or a managed search service |
| LLM | Ollama on the Fund's GPU | A hosted model endpoint (billed per token) |
| Documents and index | Fund servers | A cloud storage bucket in the chosen region |

The most important point for the Fund: **the guardrail and the retrieval step decide what text is sent to the LLM.** If the
LLM moves to the cloud, everything in the prompt leaves the building: the question and the retrieved passages. For
handbook questions, the passages are public policy, and that may be acceptable. For a question that includes a member's
details, it is a transfer of personal data.

## Part 2: The three platforms at a glance

All three offer broadly the same building blocks. The names differ.

| | Microsoft Azure | Amazon Web Services | Google Cloud |
|---|---|---|---|
| LLM service | Azure OpenAI Service / Azure AI Foundry | Amazon Bedrock | Vertex AI |
| Typical models | OpenAI GPT family; also Llama, Mistral and others through the model catalogue | Anthropic Claude, Meta Llama, Mistral, Amazon Nova and others | Google Gemini; Llama, Mistral and others through Model Garden |
| Managed vector search | Azure AI Search | OpenSearch Serverless; Bedrock Knowledge Bases | Vertex AI Vector Search |
| Containers for the API | Azure Container Apps / AKS | ECS / Fargate / EKS | Cloud Run / GKE |
| Secrets | Azure Key Vault | AWS Secrets Manager | Secret Manager |
| Private networking | Private Link | PrivateLink | Private Service Connect |
| Nearest data-centre region to Tanzania | South Africa North (Johannesburg) | Africa (Cape Town) | africa-south1 (Johannesburg) |

Two cautions before anyone quotes this table:

- **Model availability varies by region and changes often.** A model offered in Europe or the US may not be offered in the
  South African region, or may run there only through a cross-region service. Check the provider's current region list for
  the exact model you want, before planning around it.
- **There is no hyperscale cloud region in Tanzania today.** Every option above processes data outside the country. That
  brings in the cross-border transfer rules of the **Personal Data Protection Act, 2022** and the guidance of the Personal
  Data Protection Commission. The Fund's data protection officer and legal team decide what's permissible, not the data
  science team.

## Part 3: One adapter, four back ends

Good design makes the choice of LLM provider a configuration setting, not a rewrite. Put the one provider-specific call
behind a single function. Everything else (guardrail, retrieval, prompt, citations, logging) stays identical.

This is the shape of it. The Ollama version is what you already run. The others show what the same call looks like on each
cloud. You don't need to run them.

```python
import os

def generate(system, user, provider=os.environ.get("LLM_PROVIDER", "ollama")):
    if provider == "ollama":                                   # self-hosted (Labs 1-2)
        import requests
        r = requests.post(f"{os.environ['OLLAMA_URL']}/api/chat", json={
            "model": os.environ["OLLAMA_MODEL"], "stream": False, "options": {"temperature": 0},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]})
        return r.json()["message"]["content"]

    if provider == "azure":                                    # Azure OpenAI: pip install openai
        from openai import AzureOpenAI
        client = AzureOpenAI(azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                             api_key=os.environ["AZURE_OPENAI_KEY"], api_version=os.environ["AZURE_OPENAI_API_VERSION"])
        r = client.chat.completions.create(model=os.environ["AZURE_DEPLOYMENT"], temperature=0,
                                           messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
        return r.choices[0].message.content

    if provider == "bedrock":                                  # Amazon Bedrock: pip install boto3
        import boto3
        client = boto3.client("bedrock-runtime", region_name=os.environ["AWS_REGION"])
        r = client.converse(modelId=os.environ["BEDROCK_MODEL_ID"], system=[{"text": system}],
                            messages=[{"role": "user", "content": [{"text": user}]}],
                            inferenceConfig={"temperature": 0})
        return r["output"]["message"]["content"][0]["text"]

    if provider == "vertex":                                   # Vertex AI: pip install google-genai
        from google import genai
        from google.genai import types
        client = genai.Client(vertexai=True, project=os.environ["GCP_PROJECT"], location=os.environ["GCP_LOCATION"])
        r = client.models.generate_content(model=os.environ["VERTEX_MODEL"], contents=user,
                                           config=types.GenerateContentConfig(system_instruction=system, temperature=0))
        return r.text

    raise ValueError(f"unknown provider {provider}")
```

Notice what *isn't* in there: keys in code. Each provider reads its credentials from the environment, which in production
means a secrets manager or, better, the platform's managed identity, so no key exists to leak at all.

**Think about it (5 minutes):** SDK details change from version to version. Where in the Fund's process would you catch a
breaking change before it reached production? (Hint: Day 10's automated tests.)

## Part 4: A walkthrough on one platform

Here's what deploying the Day 9 assistant would involve on Azure, as an example. The steps on AWS and Google Cloud are
equivalent, with the names from Part 2. This is a sketch of the work, not a script to paste: commands and options change,
so follow the provider's current documentation for each step.

1. **Decide the region and check the model.** Confirm the model you want is available where you want it. Record the answer,
   and the date you checked, in the design document.
2. **Create the resources** in a dedicated resource group: an Azure OpenAI (AI Foundry) resource, a model deployment, a Key
   Vault, a Container Apps environment and a storage account for the documents and index.
3. **Lock down the network.** Private endpoints for the model and storage, no public access, and the Fund's network
   connected over VPN or ExpressRoute. Staff reach the assistant through the Fund's network, not the internet.
4. **Build and push the container.** The FastAPI service from Lab 2, with `LLM_PROVIDER=azure`, packaged with Docker (Day 10
   covers this), pushed to the container registry.
5. **Wire up identity.** Give the container a managed identity with permission to call the model and read the secrets. No
   API keys in environment variables.
6. **Load the index.** Either copy `rag_index/` into the image or storage (keeping FAISS), or load the chunks into Azure AI
   Search. Keeping FAISS is simpler and avoids a second managed service while the document set is small.
7. **Monitor.** Send the service's request log and metrics to Application Insights; set alerts on errors, latency and daily
   token spend.
8. **Run the same evaluation.** Rerun Lab 1's end-to-end evaluation and Day 7's scorecard tests against the cloud
   deployment. Compare quality, latency and Swahili with the self-hosted version **on the same questions**.

## Part 5: Side by side

Fill this in yourself, using what you measured today and your cost worksheet (`Lab3_Cost_Worksheet.ipynb`). The
first rows are started for you.

| Criterion | Self-hosted (Ollama + FAISS on Fund servers) | Managed cloud LLM (your chosen provider) |
|---|---|---|
| Where the prompt text is processed | Fund data centre | Outside Tanzania (nearest region: South Africa) |
| Personal data in prompts | Acceptable under Fund controls | Needs a legal basis for cross-border transfer; avoid, or strip it first |
| Answer quality (grounded Q&A, Swahili) | Measured today with small models | Typically much stronger with frontier models. Measure it on your test set. |
| Latency per answer | Measured in Lab 2 | Add the network round trip to the region, then measure |
| Cost at today's volume | From the worksheet | From the worksheet |
| Cost if volume grows tenfold | Mostly fixed (hardware) | Grows with every token |
| Staff and skills needed | GPU servers, patching, model updates | Cloud engineering, cost control, contract management |
| Scaling for a peak (e.g. month-end) | Limited by hardware owned | Elastic, within quota |
| Lock-in | Low (open models, open tools) | Medium: portable if you use the adapter pattern, higher with managed extras |
| Currency and budget | Capital expense in TZS | Operating expense, billed in USD |
| What happens if the internet link goes down? | ... | ... |
| Who can see the prompts? | ... | ... |

## Part 6: It doesn't have to be one or the other

Many institutions end up with a **hybrid**: route each request by how sensitive it is.

```
request ─► classify sensitivity ─┬─ contains personal data or internal-only material ─► self-hosted model
                                 └─ public policy question, no personal data ───────► managed cloud model (optional)
```

The guardrail you built in Lab 1 is already the start of such a classifier. It spots personal-record questions today; it
could route them tomorrow.

## Part 7: Your recommendation

Write five sentences for the ICT steering committee:

1. **For the handbook assistant (public policy text only),** we recommend ... because ...
2. **For any assistant that handles member records,** we recommend ... because ...
3. **The main risks are** ... and we contain them by ...
4. **Cost:** at today's volume ..., and if volume grows ...
5. **Before a final decision we need** (legal review of cross-border transfer, a quality test of the cloud model on our
   Swahili questions, a quotation for GPU servers ...).

Keep it. On Day 10 it goes into the governance pack for your capstone.
