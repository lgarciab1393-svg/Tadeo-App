import streamlit as st
import google.generativeai as genai

# --- Configuración Inicial ---
st.set_page_config(page_title="Tadeo - Coach Ciclista", page_icon="🚴")

# --- BUSCAR LA LLAVE SECRETA ---
try:
    # Tadeo busca la llave en la caja fuerte de Streamlit
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ No se encontró la llave secreta. Configúrala en Streamlit Cloud > Settings > Secrets.")
    st.stop()

# Configurar Google Gemini
genai.configure(api_key=api_key)
# Usamos el modelo rápido que sabemos que funciona en tu cuenta
model = genai.GenerativeModel("gemini-2.0-flash", system_instruction="""
Eres Tadeo, un entrenador experto en ciclismo amateur.
Tu tono es motivador, técnico pero accesible, y muy enfocado en datos.
Responde siempre en español. Ayuda a crear planes, explicar métricas (FTP, VAM) y dar consejos de nutrición.
""")

# --- Interfaz Gráfica ---
st.title("🚴 Hola, soy Tadeo")
st.write("Tu entrenador inteligente. Listo para rodar contigo.")

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "model", "content": "¡Hola! Ya tengo mis sensores listos y calibrados. ¿Qué entrenamiento tienes en mente para hoy?"})

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capturar input del usuario
if prompt := st.chat_input("Escribe aquí (Ej: Mañana quiero subir Patios en 25 min)..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generar respuesta
    with st.chat_message("model"):
        with st.spinner("Analizando ruta y vatios... ⚡"):
            try:
                chat = model.start_chat(history=[
                    {"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]
                ])
                response = chat.send_message(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "model", "content": response.text})
            except Exception as e:
                st.error(f"Hubo un error de conexión: {e}")
