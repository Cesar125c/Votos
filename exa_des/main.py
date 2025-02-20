import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from groq import Groq

# Cargar variables de entorno
load_dotenv()

# Inicializar cliente de IA
qclient = Groq()

# Función para etiquetar los votos
def etiquetar_votos(texto):
    if "Noboa" in texto:
        return "Voto Noboa"
    elif "Luisa" in texto:
        return "Voto Luisa"
    else:
        return "Voto Nulo"  

# Título de la app
st.title('📊 Análisis de Votos')

# Subir archivo XLSX
xlsx_file = st.file_uploader("Sube un archivo XLSX", type="xlsx")

# Verificar si se ha subido un archivo XLSX
if xlsx_file:
    # Leer el archivo XLSX
    df = pd.read_excel(xlsx_file)
    
    # Convertir el contenido del archivo en texto
    text = df.to_string(index=False)

    # Muestra de la data de manera randómica
    sample_size = st.slider("Selecciona el tamaño de la muestra", min_value=1, max_value=len(df), value=10)
    sample_df = df.sample(n=sample_size, random_state=42)

    # Mostrar la muestra
    st.write("Muestra de la data:")
    st.write(sample_df)

    # Etiquetar los votos
    sample_df['Etiqueta'] = sample_df.apply(lambda row: etiquetar_votos(row.to_string()), axis=1)

    # Contar los votos
    conteo_votos = sample_df['Etiqueta'].value_counts()

    # Presentar los resultados en un gráfico de barras
    st.write("Resultados de los votos:")
    fig, ax = plt.subplots()
    conteo_votos.plot(kind='bar', ax=ax)
    ax.set_xlabel("Tipo de Voto")
    ax.set_ylabel("Cantidad de Votos")
    st.pyplot(fig)

    # Mostrar la cantidad de votos nulos y llegar a una conclusión
    votos_nulos = conteo_votos.get("Voto Nulo", 0)
    st.write(f"Cantidad de votos nulos: {votos_nulos}")

    if conteo_votos.idxmax() == "Voto Nulo":
        conclusion = "La mayoría de los votos son nulos."
    else:
        conclusion = f"La mayoría de los votos son para {conteo_votos.idxmax()}."
    st.write("Conclusión:")
    st.write(conclusion)

    # Permitir hacerle preguntas al bot sobre la data examinada
    user_question = st.text_input("Hazle una pregunta al bot sobre la data:")
    
    if user_question:
        # Generar el prompt para la pregunta
        prompt = f"Sobre la siguiente data:\n\n{text}\n\nPregunta: {user_question}"

        # Enviar la solicitud al modelo IA
        response_container = st.chat_message('assistant').empty()
        response_text = ""

        stream_response = qclient.chat.completions.create(
            messages=[{"role": "system", "content": "You will only answer in Spanish"},
                      {"role": "user", "content": prompt}],
            model="llama-3.3-70b-specdec",
            stream=True
        )

        # Mostrar respuesta progresivamente
        for chunk in stream_response:
            if chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content
                response_container.markdown(response_text)