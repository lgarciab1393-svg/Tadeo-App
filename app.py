import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Tadeo - Entrenador Ciclismo", page_icon="🚴", layout="centered")

# --- BARRA LATERAL (API KEY) ---
with st.sidebar:
    st.title("⚙️ Configuración")
    st.markdown("Para activar a Tadeo, pega tu API Key de Google aquí.")
    # Input para la clave
    api_key = st.text_input("Tu API Key:", type="password")
    st.markdown("[👉 Consigue tu API Key gratis aquí](https://aistudio.google.com/app/apikey)")
    st.divider()
    st.info("Versión Beta - Compatible con Garmin, Xiaomi, Huawei y Samsung.")

# --- CABECERA ---
st.title("🚴 Hola, soy Tadeo")
st.markdown("**Tu entrenador inteligente.** Especializado en ciclistas amateurs de Bogotá.")

# --- CEREBRO DE TADEO (EL PROMPT) ---
SYSTEM_PROMPT = """
Eres "Tadeo", un entrenador de ciclismo experto, flexible y empático para amateurs en Bogotá.
TU OBJETIVO: Adaptar el entreno a la fatiga y contexto real del usuario.

REGLAS DE ORO:
1. ONBOARDING: Si el usuario saluda, pide: Edad, Dispositivo (Garmin/Xiaomi/Huawei/Strava), Pulso (Si/No) y Nivel.
2. DISPOSITIVOS:
   - Garmin: Pregunta por "Body Battery".
   - Xiaomi/Huawei/Samsung: Pregunta por "Carga", "Energy Score" o "Recuperación".
   - Solo Strava: NUNCA hables de pulso/vatios. Habla de RPE (Sensación de ahogo).
3. FATIGA: Si el usuario dice "estoy cansado/me costó", PROHIBIDO Z4/Z5. Manda Z1 (Recuperación) o Descanso.
4. ZONAS (Dinámicas - Calcula mentalmente):
   - Z1 (Recuperación): <75% FCM.
   - Z2 (Fondo): 75-83% FCM.
   - Z3 (Tempo): 84-90% FCM.
   - Z4 (Umbral): 91-95% FCM.
   - Z5 (VO2): >95% FCM.

CONTEXTO BOGOTÁ: Patios (6km subida), Virgilio (Plano), Sabana (Fondo/Viento).
"""

# --- GESTIÓN DEL CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LÓGICA DE RESPUESTA ---
if prompt := st.chat_input("Escribe aquí (Ej: Hola Tadeo, quiero entrenar mañana)..."):
    
    # Mostrar mensaje usuario
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Validar que puso la clave
    if not api_key:
        st.error("⚠️ ¡Falta la llave! Por favor pega tu API Key en el menú de la izquierda.")
        st.stop()

    # Llamar a Google
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=SYSTEM_PROMPT)
        
        # Preparar historial
        chat_history = []
        for m in st.session_state.messages:
            if m["role"] != "system":
                chat_history.append({"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]})

        # Generar respuesta
        chat = model.start_chat(history=chat_history[:-1])
        response = chat.send_message(prompt)
        
        # Mostrar respuesta IA
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Error de conexión: {e}")