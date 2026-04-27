from fastapi import FastAPI
import requests
import os
import time

app = FastAPI()

LITELLM_URL = "http://litellm:4000/v1/chat/completions"
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# cache simple
cache = {}


# decidir si buscar
def needs_search(prompt: str) -> bool:
    trigger_words = [
        "hoy", "actual", "precio", "noticia",
        "último", "ahora", "reciente", "2026"
    ]
    return any(word in prompt.lower() for word in trigger_words)


# búsqueda SERPER
def search_serper(query: str) -> str:
    if query in cache:
        print("⚡ CACHE HIT")
        return cache[query]

    if not SERPER_API_KEY:
        print("❌ SERPER_API_KEY missing")
        return ""

    try:
        res = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY},
            json={"q": query},
            timeout=5
        )

        print("SERPER STATUS:", res.status_code)

        if res.status_code != 200:
            print("❌ Serper error:", res.text)
            return ""

        results = res.json()

        snippets = []
        for r in results.get("organic", [])[:3]:
            snippet = r.get("snippet")
            if snippet:
                snippets.append(snippet)

        context = "\n".join(snippets)
        context = context[:800]

        cache[query] = context
        return context

    except Exception as e:
        print("❌ Serper exception:", str(e))
        return ""


# llamada robusta a LiteLLM
def call_litellm(payload):
    last_error = None

    for i in range(3):
        try:
            response = requests.post(
                LITELLM_URL,
                headers={
                    "Authorization": "Bearer dummy",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=60
            )

            print("STATUS:", response.status_code)
            print("RAW:", response.text)

            if response.status_code != 200:
                raise Exception(response.text)

            # si viene vacío
            if not response.text.strip():
                raise Exception("Empty response from LiteLLM")

            return response.json()

        except Exception as e:
            print(f"❌ intento {i} fallo:", str(e))
            last_error = e
            time.sleep(1)

    return {
        "id": "error",
        "object": "chat.completion",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": f"Error interno: {str(last_error)}"
                }
            }
        ]
    }


# endpoint modelos
@app.get("/v1/models")
def models():
    try:
        res = requests.get("http://litellm:4000/v1/models", timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}


# endpoint principal
@app.post("/v1/chat/completions")
def chat(payload: dict):

    # soportar formato prompt
    if "messages" not in payload and "prompt" in payload:
        payload["messages"] = [
            {"role": "user", "content": payload["prompt"]}
        ]

    # 🔥 CLAVE: desactivar streaming
    payload["stream"] = False

    try:
        user_msg = payload["messages"][-1]["content"]
    except Exception:
        return {"error": "Invalid payload format"}

    context = ""

    if needs_search(user_msg):
        context = search_serper(user_msg)

    print("USER:", user_msg)
    print("CONTEXT:", context)

    # inyectar contexto si hay
    if context.strip():
        payload["messages"].insert(0, {
            "role": "system",
            "content": f"Usa esta información actual:\n{context}"
        })

    return call_litellm(payload)


# compatibilidad
@app.post("/v1/completions")
def completions(payload: dict):
    return chat(payload)
