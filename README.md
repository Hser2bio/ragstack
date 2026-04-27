# RAG LLM Stack: Open WebUI + LiteLLM + Ollama + Serper

Montaje de un stack de LLM con RAG, combinando modelos locales y cloud, con una interfaz tipo ChatGPT.

La idea es tener algo funcional, autocontenido y fácil de levantar, sin depender completamente de APIs externas.

---

## Qué incluye

* Open WebUI como interfaz
* LiteLLM como proxy unificado
* Ollama para modelos locales
* Un servicio RAG en FastAPI
* Búsqueda en Google vía Serper

---

## Cómo funciona

El flujo es básicamente este:

```
WebUI → RAG → (Serper si hace falta) → LiteLLM → modelo
```

* Si la pregunta parece actual (“precio”, “hoy”, etc.), se hace búsqueda
* Se inyecta contexto en el prompt
* El modelo responde con esa info

---

## Requisitos

* Docker
* Docker Compose
* API key de Serper (https://serper.dev)

Opcional:

* API key de OpenRouter (para modelos cloud)

---

## Instalación

### 1. Instalar Docker (Ubuntu)

```bash
apt update
apt install -y docker.io docker-compose
systemctl enable docker
systemctl start docker
```

---

### 2. Clonar el repo

```bash
git clone https://github.com/Hser2bio/ragstack
cd ragstack
```

---

### 3. Configurar variables

Crear `.env`:

```env
SERPER_API_KEY=tu_api_key
OPENROUTER_API_KEY=tu_api_key_opcional
```

---

### 4. Levantar todo

```bash
docker compose up -d
```

---

## Acceso

* WebUI → http://localhost:3000
* API RAG → http://localhost:5000

---

## Uso

Desde la UI puedes seleccionar modelo y preguntar directamente.

Ejemplo típico:

```
precio bitcoin hoy
```

Si detecta que es algo actual:

* hace búsqueda
* añade contexto
* responde con datos recientes

---

## API

Ejemplo básico:

```bash
curl http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt4mini",
    "messages": [{"role":"user","content":"precio bitcoin hoy"}]
  }'
```

---

## Notas

* El RAG es simple (snippets de búsqueda, sin embeddings)
* El cache es en memoria (se pierde al reiniciar)
* LiteLLM permite cambiar de backend sin tocar la UI

---

## Seguridad

Si lo expones en un servidor, mejor cerrar puertos internos:

```bash
ufw allow 3000
ufw deny 4000
ufw deny 5000
```

---

## Mejoras pendientes

* Cache persistente (Redis)
* Mejor ranking de resultados
* Streaming de respuestas
* Routing automático entre modelos

---

## Licencia

MIT
