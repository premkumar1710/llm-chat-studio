import json
import time
from datetime import datetime
import requests
import streamlit as st

BASE_URL = "http://localhost:11434"

st.set_page_config(page_title="LLM Chat Studio", page_icon="💬", layout="wide")

def installed_models():
    try:
        r = requests.get(f"{BASE_URL}/api/tags", timeout=5)
        r.raise_for_status()
        return [m["name"] for m in r.json().get("models", [])]
    except requests.RequestException:
        return []

def chat(model, messages, temperature, max_tokens, json_mode):
    payload = {
        "model": model, "messages": messages, "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens}
    }
    if json_mode:
        payload["format"] = "json"
    r = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=300)
    r.raise_for_status()
    return r.json()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "stats" not in st.session_state:
    st.session_state.stats = []

models = installed_models()
with st.sidebar:
    st.title("⚙️ Chat settings")
    model = st.selectbox("Installed Ollama model", models) if models else st.text_input("Model name", "llama3.2:3b")
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
    max_tokens = st.slider("Maximum response tokens", 128, 4096, 700, 64)
    json_mode = st.checkbox("Request JSON response")
    system_prompt = st.text_area(
        "System prompt",
        "You are a helpful, accurate AI assistant. Explain clearly and do not invent facts.",
        height=120
    )
    custom = st.text_area("Custom instructions", "", height=90)
    if st.button("🔄 Refresh models", use_container_width=True):
        st.rerun()
    if st.button("🧹 Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.stats = []
        st.rerun()
    st.caption("Local Ollama inference. No OpenAI API key required.")

st.title("💬 LLM Chat Studio — Ollama Edition")
st.write("Chat with locally running language models using Python, Streamlit, and Ollama.")

if models:
    st.success(f"Ollama connected · {len(models)} local model(s) found")
else:
    st.warning("Ollama is not reachable or no models are installed. Install/start Ollama, then run: ollama pull llama3.2:3b")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Message your local AI…")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            sys_text = system_prompt.strip()
            if custom.strip():
                sys_text += "\n\nAdditional instructions:\n" + custom.strip()
            messages = [{"role": "system", "content": sys_text}] + st.session_state.messages[-21:]
            with st.spinner(f"Generating with {model}…"):
                start = time.time()
                result = chat(model.strip(), messages, temperature, max_tokens, json_mode)
                elapsed = time.time() - start
            answer = result.get("message", {}).get("content", "") or "(Empty response)"
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            p_tokens = result.get("prompt_eval_count", 0)
            o_tokens = result.get("eval_count", 0)
            st.session_state.stats.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "model": model, "input_tokens": p_tokens,
                "output_tokens": o_tokens, "response_seconds": round(elapsed, 2)
            })
            st.caption(f"Input tokens: {p_tokens} · Output tokens: {o_tokens} · Response time: {elapsed:.2f}s · Local inference (no per-token API charge)")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to Ollama. Open the Ollama desktop app, or run `ollama serve`.")
        except requests.exceptions.Timeout:
            st.error("The model timed out. Try a smaller model or shorter prompt.")
        except requests.exceptions.HTTPError as e:
            detail = e.response.text if e.response is not None else str(e)
            st.error(f"Ollama API error: {detail}")
            st.info(f"If the model is missing, install it with: ollama pull {model}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

with st.expander("📊 Usage and performance"):
    if st.session_state.stats:
        st.dataframe(st.session_state.stats, use_container_width=True, hide_index=True)
        rows = ["time,model,input_tokens,output_tokens,response_seconds"]
        rows += [f'{x["time"]},{x["model"]},{x["input_tokens"]},{x["output_tokens"]},{x["response_seconds"]}' for x in st.session_state.stats]
        st.download_button("Download performance log (CSV)", "\n".join(rows), "ollama_usage_log.csv", "text/csv")
    else:
        st.caption("Token counts and response times appear after your first chat.")

with st.expander("⬇️ Export conversation"):
    data = {"provider": "Ollama local", "model": model, "messages": st.session_state.messages}
    st.download_button("Download chat history (JSON)", json.dumps(data, indent=2, ensure_ascii=False), "chat_history.json", "application/json")
