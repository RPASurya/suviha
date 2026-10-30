import json, httpx

PROVIDERS = {
    "gemini": {"label": "Google Gemini", "model": "gemini-3.8-flash", "key_label": "Gemini API key", "base_url": "https://generativelanguage.googleapis.com/v1beta"},
    "openai": {"label": "OpenAI API (GPT models)", "model": "gpt-4.1", "key_label": "OpenAI API key", "base_url": "https://api.openai.com/v1"},
    "anthropic": {"label": "Anthropic Claude", "model": "claude-sonnet-4-20250514", "key_label": "Anthropic API key", "base_url": "https://api.anthropic.com/v1"},
    "openrouter": {"label": "OpenRouter (multiple models)", "model": "google/gemini-3.8-flash", "key_label": "OpenRouter API key", "base_url": "https://openrouter.ai/api/v1"},
    "azure_openai": {"label": "Azure OpenAI", "model": "", "key_label": "Azure OpenAI key", "base_url": ""},
    "ollama": {"label": "Ollama (local model)", "model": "qwen2.5-coder:14b", "key_label": "Optional Ollama key", "base_url": "http://localhost:11434/v1"},
    "custom_openai": {"label": "Custom OpenAI-compatible API", "model": "", "key_label": "Provider API key", "base_url": ""},
}

class ProviderError(Exception):
    pass

async def generate(provider: str, api_key: str, model: str, prompt: str, settings: dict) -> str:
    timeout = httpx.Timeout(240.0, connect=30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        if provider == "gemini":
            url = f"{settings.get('base_url') or PROVIDERS[provider]['base_url']}/models/{model}:generateContent"
            response = await client.post(url, params={"key": api_key}, json={"contents":[{"parts":[{"text":prompt}]}], "generationConfig":{"temperature":0.1, "responseMimeType":"application/json"}})
            if response.is_error: raise ProviderError(f"Gemini API error {response.status_code}: {response.text[:1200]}")
            data = response.json()
            try: return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as exc: raise ProviderError("Gemini returned no text. Check model access and API quota.") from exc
        if provider == "anthropic":
            url = (settings.get("base_url") or PROVIDERS[provider]["base_url"]).rstrip("/") + "/messages"
            response = await client.post(url, headers={"x-api-key":api_key,"anthropic-version":"2023-06-01","content-type":"application/json"}, json={"model":model,"max_tokens":16000,"temperature":0.1,"messages":[{"role":"user","content":prompt}]})
            if response.is_error: raise ProviderError(f"Anthropic API error {response.status_code}: {response.text[:1200]}")
            data=response.json(); return "\n".join(x.get("text","") for x in data.get("content",[]) if x.get("type")=="text")
        base = settings.get("base_url") or PROVIDERS[provider]["base_url"]
        if provider == "azure_openai":
            # Azure endpoint is the full resource endpoint; model field is the deployment name.
            if not base or not settings.get("api_version"):
                raise ProviderError("Azure OpenAI requires an endpoint URL and API version in Admin Settings.")
            url = base.rstrip("/") + f"/openai/deployments/{model}/chat/completions?api-version={settings['api_version']}"
            headers={"api-key":api_key,"content-type":"application/json"}
        else:
            if not base: raise ProviderError("Provider base URL is required.")
            url=base.rstrip("/") + "/chat/completions"
            headers={"Authorization":f"Bearer {api_key}" if api_key else "Bearer local-ollama","content-type":"application/json"}
        payload={"model":model,"messages":[{"role":"system","content":"You are an expert automation migration engineer. Return only valid JSON when asked."},{"role":"user","content":prompt}],"temperature":0.1}
        response=await client.post(url,headers=headers,json=payload)
        if response.is_error: raise ProviderError(f"{PROVIDERS[provider]['label']} API error {response.status_code}: {response.text[:1200]}")
        data=response.json()
        try: return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc: raise ProviderError("LLM response did not contain a text completion.") from exc
