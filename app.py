import streamlit as st
import google.generativeai as genai

# --- Configuración de la Página ---
st.set_page_config(page_title="Tadeo - Coach Ciclista", page_icon="🚴")

# --- BUSCAR LA LLAVE SECRETA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⚠️ Falta la API Key. Configúrala en Streamlit Cloud > Settings > Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# Instrucciones del Cerebro (Tadeo)
system_instruction = """
Eres Tadeo, un entrenador experto en ciclismo amateur.
Tu tono es motivador, técnico pero accesible (usando jerga ciclista como vatios, cadencia, 'chupar rueda').
SIEMPRE responde en español.
Tu objetivo es ayudar a crear planes, explicar métricas (FTP, V/Km) y dar consejos.
Si el usuario es nuevo, pregúntale su edad, dispositivo (Garmin/Wahoo) y nivel.
"""

# Cambiamos "gemini-2.0-flash" por este que aguanta más tráfico:
model = genai.GenerativeModel("gemini-1.5-flash-latest", system_instruction=system_instruction)

# --- Interfaz Gráfica ---
st.title("🚴 Hola, soy Tadeo")
st.markdown("Tu entrenador de **Inteligencia Artificial**. _Déjame ayudarte a romper tus PRs._")

# Inicializar historial con un saludo estructurado
if "messages" not in st.session_state:
    st.session_state.messages = []
    # El saludo inicial del Robot
    welcome_msg = """
    ¡Hola! Ya tengo mis sensores calibrados ⚡.
    
    Para darte el mejor consejo, cuéntame un poco de ti:
    1. ¿Qué edad tienes?
    2. ¿Qué dispositivo usas? (Garmin, Wahoo, Celular...)
    3. ¿Cuánto tiempo llevas montando bici?
    """
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# Mostrar historial (Con iconos correctos)
for message in st.session_state.messages:
    # Si es "assistant" ponemos avatar de robot, si es usuario ponemos un ciclista o default
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Capturar input del usuario
if prompt := st.chat_input("Escribe aquí (Ej: Tengo 40 años y uso Garmin)..."):
    # Guardar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generar respuesta
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Analizando datos... ⚙️"):
            try:
                # Traducir historial para Gemini (assistant -> model)
                gemini_history = []
                for m in st.session_state.messages[:-1]:
                    role = "model" if m["role"] == "assistant" else "user"
                    gemini_history.append({"role": role, "parts": [m["content"]]})

                chat = model.start_chat(history=gemini_history)
                response = chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Se rompió la cadena: {e}")

