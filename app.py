import streamlit as st
import streamlit.components.v1 as components
from google import genai
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="IdeaTuve - Minecraft Shorts Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CARGAR HOJA DE ESTILOS EXTERNA ---
def load_css(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles.css")

# --- FUNCIONES DE PERSISTENCIA (GUARDAR / CARGAR HISTORIAL) ---
HISTORY_FILE = "chat_history.json"

def load_all_chats():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_all_chats(chats):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)

# Inicializar sesión y chats guardados
if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_all_chats()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- API KEY ---
# Reemplaza la línea vieja por esta:
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY)

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("📂 Historial de Chats")
    
    # Botón para iniciar un nuevo chat
    if st.button("➕ Nueva Conversación", use_container_width=True):
        new_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.current_chat_id = new_id
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # Listado de conversaciones guardadas
    if st.session_state.all_chats:
        st.caption("Conversaciones anteriores:")
        for chat_id, chat_data in list(st.session_state.all_chats.items())[::-1]:
            # Usar el primer mensaje del usuario como título de la conversación
            title = chat_data["title"] if "title" in chat_data else chat_id
            if st.button(f"💬 {title[:20]}...", key=chat_id, use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = chat_data["messages"]
                st.rerun()
    else:
        st.caption("No hay chats guardados aún.")

    st.divider()
    
    st.header("🎬 Referencias Virales")
    st.caption("Videos de referencia para la animación:")
    
    st.markdown("**1. Formato 'Expectativa vs Realidad'**")
    components.html(
        '<iframe width="100%" height="200" src="https://www.youtube.com/embed/i0gmQYp549Q" frameborder="0" allowfullscreen></iframe>',
        height=210
    )
    
    st.divider()
    
    st.markdown("**2. Meme de Audio Viral + Minecraft**")
    components.html(
        '<iframe width="100%" height="200" src="https://www.youtube.com/embed/jwX7GuaRGrs" frameborder="0" allowfullscreen></iframe>',
        height=210
    )

# --- ENCABEZADO ---
st.title("🎬 IdeaTuve - Minecraft Short Generator")
st.caption("Asistente de IA para crear animaciones cortas, memes y tendencias sin voz.")

# --- MOSTRAR MENSAJES DEL CHAT ACTUAL ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- CHAT INPUT & PROCESAMIENTO ---
if user_prompt := st.chat_input("Ej: Dame 3 ideas de memes virales para animar en Minecraft esta semana"):
    st.chat_message("user").markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    system_instruction = (
        "Eres un estratega de animación corta para Minecraft sin voz. "
        "Tus ideas se basan en memes virales, audios de tendencia y humor visual absurdo (10-30 seg). "
        "Estructura tus respuestas en: "
        "1. Título llamativo. "
        "2. Audio/Meme de referencia. "
        "3. Gancho inicial (0-3 seg). "
        "4. Guión visual paso a paso."
    )

    contents = []
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    with st.chat_message("assistant"):
        with st.spinner("Pensando ideas virales..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config={"system_instruction": system_instruction}
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

                # --- GUARDAR EN ARCHIVO JSON LOCAL ---
                chat_id = st.session_state.current_chat_id
                first_msg = st.session_state.messages[0]["content"] if st.session_state.messages else "Nuevo Chat"
                
                st.session_state.all_chats[chat_id] = {
                    "title": first_msg,
                    "messages": st.session_state.messages
                }
                save_all_chats(st.session_state.all_chats)

            except Exception as e:
                st.error(f"Error al generar la respuesta: {e}")