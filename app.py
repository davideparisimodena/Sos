import streamlit as st
import google.generativeai as genai
import time

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="SOS Calma",
    page_icon="🌿",
    layout="centered"
)

# --- CSS PER PULIZIA VISIVA (Opzionale) ---
# Nasconde il menu hamburger e il footer di Streamlit per un look più da "app"
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- TITOLO E DISCLAIMER ---
st.title("SOS Calma 🌿")
st.markdown("### Un respiro alla volta.")

st.info("⚠️ **Nota Importante:** Questo è un supporto di auto-aiuto basato sull'IA. Non sostituisce un medico. In caso di emergenza o pericolo, chiama il **112** o il Telefono Amico **199.284.284**.")

# --- GESTIONE API KEY ---
# In produzione userai i "Secrets" di Streamlit. 
# Per ora, per testare, la chiediamo nella barra laterale se non c'è.
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Inserisci Google API Key", type="password")

# --- PROMPT DI SISTEMA (IL "CERVELLO") ---
SYSTEM_PROMPT = """
SEI "SOS CALMA", UN ASSISTENTE PER IL GROUNDING.
OBIETTIVO: Guidare l'utente attraverso la tecnica 5-4-3-2-1 per ridurre l'ansia.
REGOLE:
1. Tono calmo, lento, empatico. Usa frasi brevi.
2. NON dare consigli medici. Se rilevi intenti suicidi, fornisci SOLO i numeri di emergenza.
3. Segui RIGIDAMENTE questi step, uno alla volta, aspettando la risposta dell'utente:
   - STEP 0: Saluta, presentati brevemente e chiedi di fare un respiro profondo.
   - STEP 1: Chiedi di scrivere 5 cose che vede.
   - STEP 2: Chiedi 4 cose che può toccare.
   - STEP 3: Chiedi 3 cose che può sentire (udito).
   - STEP 4: Chiedi 2 cose che può annusare.
   - STEP 5: Chiedi 1 cosa che può gustare o il suo cibo preferito.
   - FINE: Chiedi come si sente.
NON passare allo step successivo se l'utente non ha risposto a quello corrente.
"""

# --- INIZIALIZZAZIONE SESSIONE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Messaggio di benvenuto finto (l'AI lo genererà davvero alla prima chiamata)
    # ma per l'UI iniziamo puliti o lasciamo che sia l'utente o l'AI a partire.
    # Per forzare l'AI a iniziare, aggiungiamo un messaggio "invisibile" dell'utente che dice "Aiutami"
    st.session_state.first_run = True

# --- LOGICA DELL'AI ---
if api_key:
    genai.configure(api_key=api_key)
    
    # Configurazione del modello (usiamo Flash perché è veloce ed economico)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )

    # Ricostruiamo la chat history per Gemini
    chat_history = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        chat_history.append({"role": role, "parts": [msg["content"]]})

    chat = model.start_chat(history=chat_history)

    # Se è la prima volta che apri la pagina, l'AI deve parlare per prima
    if "first_run" in st.session_state and st.session_state.first_run:
        with st.chat_message("assistant"):
            with st.spinner("Respirando con te..."):
                response = chat.send_message("L'utente ha appena aperto l'app ed è agitato. Inizia la procedura.")
                st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.session_state.first_run = False

    # Mostra la cronologia a video
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- INTERAZIONE UTENTE ---
    if prompt := st.chat_input("Scrivi qui come ti senti o rispondi all'esercizio..."):
        # 1. Mostra messaggio utente
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 2. Risposta AI
        with st.chat_message("assistant"):
            with st.spinner("..."):
                try:
                    # Inviamo il messaggio a Gemini
                    response = chat.send_message(prompt)
                    
                    # Effetto "dattilografo" per sembrare più umano e calmo
                    full_response = response.text
                    message_placeholder = st.empty()
                    displayed_response = ""
                    
                    # Simula la scrittura lenta (calmante)
                    for chunk in full_response.split():
                        displayed_response += chunk + " "
                        message_placeholder.markdown(displayed_response + "▌")
                        time.sleep(0.05) 
                    message_placeholder.markdown(displayed_response)
                    
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                except Exception as e:
                    st.error(f"Qualcosa non va nella connessione. Riprova. Errore: {e}")

else:
    st.warning("Per iniziare, inserisci la tua Google API Key nella barra laterale a sinistra.")
    st.write("Non hai una chiave? [Ottienila qui gratis](https://aistudio.google.com/).")

