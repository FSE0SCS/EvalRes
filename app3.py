import os
import streamlit as st
import pandas as pd
import io
import requests # Nuevo requisito para MailGun
from dotenv import load_dotenv # ¡Añade esta línea!

load_dotenv() # ¡Añade esta línea para cargar el .env!

# --- Configuración General ---
st.set_page_config(
    page_title="Evaluación de Notas de Residentes 1.0 – F.S.E. – S.C.S.",
    page_icon="🏥",
    layout="wide"
)

# --- Contraseña de Acceso ---
PASSWORD = "residentes2025"

# --- Configuración de MailGun (tomada de variables de entorno) ---
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_SENDER_EMAIL = os.getenv("MAILGUN_SENDER_EMAIL")
MAILGUN_RECIPIENT_EMAIL = "fse.scs.evalres@gmail.com" # Este puede permanecer fijo

# --- Datos Maestros ---
# Mapeo de Direcciones/Gerencias a Códigos para el nombre de la hoja Excel
CODIGOS_DIRECCION = {
    "DIRECCIÓN GERENCIA HOSPITAL DOCTOR NEGRIN": "HUGCNEGRIN",
    "DIRECCIÓN GERENCIA COMPLEJO HOSPITALARIO UNIVERSITARIO Y MATERNO INFANTIL": "CHUIMI",
    "DIRECCIÓN GERENCIA COMPLEJO HOSPITALARIO UNIVERSITARIO DE CANARIAS": "CHUC",
    "DIRECCIÓN GERENCIA HOSPITAL NUESTRA SEÑORA DE CANDELARIA": "HUSNC",
    "GERENCIA DE ATENCIÓN PRIMARIA DE GRAN CANARIA": "GAPGC",
    "GERENCIA DE ATENCIÓN PRIMARIA DE TENERIFE NORTE": "GAPTF_Norte",
    "GERENCIA DE ATENCIÓN PRIMARIA DE TENERIFE SUR": "GAPTF_Sur",
    "GERENCIA DE SERVICIOS SANITARIOS DE FUERTEVENTURA": "GSSFV",
    "GERENCIA DE SERVICIOS SANITARIOS DE LANZAROTE": "GSSLZ",
    "GERENCIA DE SERVICIOS SANITARIOS DE LA PALMA": "GSSLP"
}

# Especialidades por Dirección/Gerencia
ESPECIALIDADES_POR_DIRECCION = {
    "DIRECCIÓN GERENCIA HOSPITAL DOCTOR NEGRIN": [
        "ALERGOLOGÍA", "ANÁLISIS CLÍNICOS", "ANATOMÍA PATOLÓGICA", "ANESTESIOLOGÍA Y REANIMACIÓN",
        "ANGIOLOGÍA Y CIRUGÍA VASCULAR", "APARATO DIGESTIVO", "CARDIOLOGÍA",
        "CIRUGÍA CARDIOVASCULAR", "CIRUGÍA GENERAL Y DEL APARATO DIGESTIVO",
        "CIRUGÍA ORTOPÉDICA Y TRAUMATOLOGÍA", "CIRUGÍA PLÁSTICA ESTÉTICA Y REPARADORA",
        "CIRUGÍA TORÁCICA", "DERMATOLOGÍA MÉDICO-QUIRÚRGICA Y VENEREOLOGÍA",
        "ENDOCRINOLOGÍA Y NUTRICIÓN", "ENFERMERÍA DEL TRABAJO", "FARMACIA HOSPITALARIA",
        "HEMATOLOGÍA Y HEMOTERAPIA", "INMUNOLOGÍA", "MEDICINA FÍSICA Y REHABILITACIÓN",
        "MEDICINA INTENSIVA", "MEDICINA INTERNA", "MICROBIOLOGÍA Y PARASITOLOGÍA",
        "NEFROLOGÍA", "NEUMOLOGÍA", "NEUROCIRUGÍA", "NEUROFISIOLOGÍA CLÍNICA", "NEUROLOGÍA",
        "OFTALMOLOGÍA", "ONCOLOGÍA MÉDICA", "ONCOLOGÍA RADIOTERÁPICA", "OTORRINOLARINGOLOGÍA",
        "RADIODIAGNÓSTICO", "RADIOFÍSICA HOSPITALARIA", "REUMATOLOGÍA", "UROLOGÍA"
    ],
    "DIRECCIÓN GERENCIA COMPLEJO HOSPITALARIO UNIVERSITARIO Y MATERNO INFANTIL": [
        "ANATOMÍA PATOLÓGICA", "ANESTESIOLOGÍA Y REANIMACIÓN", "ANGIOLOGÍA Y CIRUGÍA VASCULAR",
        "APARATO DIGESTIVO", "BIOQUÍMICA CLÍNICA", "CARDIOLOGÍA", "CIRUGÍA GENERAL Y DEL APARATO DIGESTIVO",
        "CIRUGÍA ORTOPÉDICA Y TRAUMATOLOGÍA", "CIRUGÍA PEDIÁTRICA",
        "DERMATOLOGÍA MÉDICO-QUIRÚRGICA Y VENEREOLOGÍA", "ENDOCRINOLOGÍA Y NUTRICIÓN",
        "ENFERMERÍA DEL TRABAJO", "ENFERMERÍA OBSTÉTRICO GINECOLOGICA", "ENFERMERÍA PEDIATRICA",
        "FARMACIA HOSPITALARIA", "HEMATOLOGÍA Y HEMOTERAPIA", "MEDICINA FÍSICA Y REHABILITACIÓN",
        "MEDICINA INTENSIVA", "MEDICINA INTERNA", "MEDICINA NUCLEAR",
        "MICROBIOLOGÍA Y PARASITOLOGÍA", "NEFROLOGÍA", "NEUMOLOGÍA", "NEUROCIRUGÍA",
        "NEUROFISIOLOGÍA CLÍNICA", "NEUROLOGÍA", "OFTALMOLOGÍA", "ONCOLOGÍA MÉDICA",
        "OTORRINOLARINGOLOGÍA", "RADIODIAGNÓSTICO", "REUMATOLOGÍA", "UROLOGÍA"
    ],
    "DIRECCIÓN GERENCIA COMPLEJO HOSPITALARIO UNIVERSITARIO DE CANARIAS": [
        "ANATOMÍA PATOLÓGICA", "ANESTESIOLOGÍA Y REANIMACIÓN", "ANGIOLOGÍA Y CIRUGÍA VASCULAR",
        "APARATO DIGESTIVO", "BIOQUÍMICA CLÍNICA", "CARDIOLOGÍA", "CIRUGÍA GENERAL Y DEL APARATO DIGESTIVO",
        "CIRUGÍA ORAL Y MAXILOFACIAL", "CIRUGÍA ORTOPÉDICA Y TRAUMATOLOGÍA",
        "CIRUGÍA PLÁSTICA ESTÉTICA Y REPARADORA", "DERMATOLOGÍA MÉDICO-QUIRÚRGICA Y VENEREOLOGÍA",
        "ENDOCRINOLOGÍA Y NUTRICIÓN", "ENFERMERÍA DE SALUD MENTAL", "ENFERMERÍA DEL TRABAJO",
        "ENFERMERÍA OBSTÉTRICO GINECOLOGICA", "ENFERMERÍA PEDIATRICA", "FARMACIA HOSPITALARIA",
        "FARMACOLOGÍA CLÍNICA", "HEMATOLOGÍA Y HEMOTERAPIA", "MEDICINA FÍSICA Y REHABILITACIÓN",
        "MEDICINA INTENSIVA", "MEDICINA INTERNA", "MEDICINA NUCLEAR",
        "MICROBIOLOGÍA Y PARASITOLOGÍA", "NEFROLOGÍA", "NEUMOLOGÍA", "NEUROCIRUGÍA", "NEUROLOGÍA",
        "OBSTETRICIA Y GINECOLOGÍA", "OFTALMOLOGÍA", "ONCOLOGÍA MÉDICA",
        "ONCOLOGÍA RADIOTERÁPICA", "OTORRINOLARINGOLOGÍA", "RADIODIAGNÓSTICO",
        "RADIOFÍSICA HOSPITALARIA", "REUMATOLOGÍA", "UROLOGÍA"
    ],
    "DIRECCIÓN GERENCIA HOSPITAL NUESTRA SEÑORA DE CANDELARIA": [
        "ALERGOLOGÍA", "ANÁLISIS CLÍNICOS", "ANESTESIOLOGÍA Y REANIMACIÓN", "APARATO DIGESTIVO",
        "CARDIOLOGÍA", "CIRUGÍA GENERAL Y DEL APARATO DIGESTIVO", "CIRUGÍA ORAL Y MAXILOFACIAL",
        "CIRUGÍA ORTOPÉDICA Y TRAUMATOLOGÍA", "DERMATOLOGÍA MÉDICO-QUIRÚRGICA Y VENEREOLOGÍA",
        "ENDOCRINOLOGÍA Y NUTRICIÓN", "ENFERMERÍA DEL TRABAJO", "ENFERMERÍA OBSTÉTRICO GINECOLOGICA",
        "ENFERMERÍA PEDIATRICA", "FARMACIA HOSPITALARIA", "HEMATOLOGÍA Y HEMOTERAPIA",
        "MEDICINA FÍSICA Y REHABILITACIÓN", "MEDICINA INTENSIVA", "MEDICINA INTERNA",
        "MEDICINA NUCLEAR", "MICROBIOLOGÍA Y PARASITOLOGÍA", "NEFROLOGÍA", "NEUMOLOGÍA",
        "NEUROCIRUGÍA", "NEUROFISIOLOGÍA CLÍNICA", "NEUROLOGÍA", "OBSTETRICIA Y GINECOLOGÍA",
        "OFTALMOLOGÍA", "ONCOLOGÍA MÉDICA", "ONCOLOGÍA RADIOTERÁPICA", "OTORRINOLARINGOLOGÍA",
        "RADIODIAGNÓSTICO", "RADIOFÍSICA HOSPITALARIA", "REUMATOLOGÍA", "UROLOGÍA"
    ],
    "GERENCIA DE ATENCIÓN PRIMARIA DE GRAN CANARIA": [
        "MEDICINA FAMILIAR Y COMUNITARIA", "ENFERMERÍA FAMILIAR Y COMUNITARIA"
    ],
    "GERENCIA DE ATENCIÓN PRIMARIA DE TENERIFE NORTE": [
        "MEDICINA FAMILIAR Y COMUNITARIA", "ENFERMERÍA FAMILIAR Y COMUNITARIA"
    ],
    "GERENCIA DE ATENCIÓN PRIMARIA DE TENERIFE SUR": [
        "MEDICINA FAMILIAR Y COMUNITARIA", "ENFERMERÍA FAMILIAR Y COMUNITARIA"
    ],
    "GERENCIA DE SERVICIOS SANITARIOS DE FUERTEVENTURA": [
        "MEDICINA FAMILIAR Y COMUNITARIA", "ENFERMERÍA FAMILIAR Y COMUNITARIA",
        "ENFERMERÍA OBSTÉTRICO GINECOLOGICA"
    ],
    "GERENCIA DE SERVICIOS SANITARIOS DE LANZAROTE": [
        "CIRUGÍA ORTOPÉDICA Y TRAUMATOLOGÍA", "ENFERMERÍA FAMILIAR Y COMUNITARIA",
        "ENFERMERIA GERIATRICA", "ENFERMERÍA OBSTÉTRICO GINECOLOGICA",
        "ENFERMERÍA PEDIATRICA", "GERIATRIA", "MEDICINA FAMILIAR Y COMUNITARIA",
        "MEDICINA INTERNA", "PEDIATRIA Y AREAS ESPECIFICAS"
    ],
    "GERENCIA DE SERVICIOS SANITARIOS DE LA PALMA": [
        "MEDICINA FAMILIAR Y COMUNITARIA", "ENFERMERÍA FAMILIAR Y COMUNITARIA"
    ]
}

# --- Funciones Auxiliares ---
def calculate_average(notes):
    """
    Calcula la media de una lista de notas, ignorando None, NaN, valores vacíos y ceros.
    Los ceros introducidos se consideran como celdas no rellenadas para el cálculo de la media.
    """
    valid_notes = [float(note) for note in notes if note is not None and pd.notna(note) and note != "" and float(note) != 0.0]
    if not valid_notes:
        return None
    return sum(valid_notes) / len(valid_notes)

def reset_selection_page():
    """Reinicia el estado de la sesión para volver a la página de selección de Área/Dirección."""
    st.session_state.current_step = 2 # Ahora el paso 2 es la página de información
    st.session_state.area_selected = None
    st.session_state.direccion_selected = None
    st.session_state.confirm_selection = False
    st.session_state.info_understood = False # Resetear la comprensión de normas

def login_successful():
    """Marca la sesión como logueada."""
    st.session_state.logged_in = True

def send_email_with_mailgun(recipient_email, subject, text, attachment=None, filename="attachment.xlsx"):
    """
    Envía un correo electrónico a través de Mailgun con un archivo adjunto.
    """
    if not MAILGUN_API_KEY or MAILGUN_API_KEY == "TU_API_KEY_DE_MAILGUN" or \
       not MAILGUN_DOMAIN or MAILGUN_DOMAIN == "TU_DOMINIO_DE_MAILGUN" or \
       not MAILGUN_SENDER_EMAIL or MAILGUN_SENDER_EMAIL == "TU_EMAIL_REMITENTE_DE_MAILGUN":
        st.error("Error: Las credenciales de MailGun no están configuradas. Por favor, contacta al administrador.")
        return False

    request_url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    
    files = []
    if attachment:
        attachment.seek(0) # Asegurarse de que el puntero está al inicio
        files.append(("attachment", (filename, attachment.read(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")))

    try:
        response = requests.post(
            request_url,
            auth=("api", MAILGUN_API_KEY),
            files=files,
            data={"from": MAILGUN_SENDER_EMAIL,
                  "to": recipient_email,
                  "subject": subject,
                  "text": text})
        
        if response.status_code == 200:
            st.success("✅ El informe ha sido enviado por correo electrónico con éxito.")
            return True
        else:
            st.error(f"❌ Error al enviar el correo: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error de conexión al intentar enviar el correo: {e}")
        return False


# --- Inicialización del Estado de Sesión ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'area_selected' not in st.session_state:
    st.session_state.area_selected = None
if 'direccion_selected' not in st.session_state:
    st.session_state.direccion_selected = None
if 'confirm_selection' not in st.session_state:
    st.session_state.confirm_selection = False
if 'info_understood' not in st.session_state: # Nuevo estado para la pantalla de información
    st.session_state.info_understood = False
if 'data_input' not in st.session_state:
    st.session_state.data_input = {}
if 'data_input_direccion' not in st.session_state:
    st.session_state.data_input_direccion = None
if 'total_residentes_r' not in st.session_state:
    st.session_state.total_residentes_r = {f'R{i}': 0 for i in range(1, 6)}
if 'note_entry_summary' not in st.session_state:
    st.session_state.note_entry_summary = pd.DataFrame()


# --- Interfaz de Usuario y Flujo del Programa ---

# Control de Acceso
if not st.session_state.logged_in:
    st.title("🔐 Acceso al Aplicativo de Evaluación de Notas de Residentes")
    st.write("Por favor, introduce la contraseña para continuar.")
    password_input = st.text_input("Contraseña", type="password", key="password_input")
    if st.button("Iniciar Sesión"):
        if password_input == PASSWORD:
            login_successful()
            st.rerun()
        else:
            st.error("Contraseña incorrecta. Por favor, inténtalo de nuevo.")
    st.markdown("---")
    st.markdown("##### Historial de Versiones")
    st.markdown("- **Versión 1.0 (2025-07-11):** Implementación inicial del flujo de trabajo completo, control de acceso y generación de Excel.")
    st.markdown("- **Versión 1.1 (2025-07-13):** Añadida pantalla de información y normas, reestructuración de la entrada de datos por R, resumen de datos introducidos, y preparación para envío de correo con MailGun.")
    st.stop()


# Flujo principal de la aplicación
st.title("Evaluación de Notas de Residentes 1.1 – F.S.E. – S.C.S. 🏥")
st.markdown("---")

# 1º: Pantalla de bienvenida
if st.session_state.current_step == 1:
    st.header("Bienvenido al programa de Evaluación de Notas de Residentes")
    st.write("Haz clic en 'Iniciar Aplicativo' para comenzar el proceso.")
    if st.button("Iniciar Aplicativo"):
        st.session_state.current_step = 2 # Ir a la nueva pantalla de información
        st.rerun()

# 2º: Pantalla de Información y Normas (NUEVO PASO)
elif st.session_state.current_step == 2:
    st.header("Paso 1: Información Importante del Programa")
    st.markdown("""
    **Bienvenidos al programa para calcular las medias de los residentes**

    * Debe seleccionar su **ÁREA** de operación y su **DIRECCIÓN/GERENCIA** para obtener acceso a las especialidades evaluadas.
    * Debe rellenar el **número de residentes evaluados** en el ejercicio en curso, para todas las especialidades y año de residencia.
    * Debe rellenar las notas de los residentes. Los valores aceptados no pueden ser superiores a **10** y pueden contener **2 decimales**.
    * Si no rellena las 3 notas más altas de alguna especialidad, **NO debe poner un 0** en la casilla vacía, simplemente no introduzca ningún valor numérico.
    * **Importante:** Para la introducción de las notas es posible que tenga que hacerlo dos veces por cada celda, **NO es un error**, es un proceso de validación del programa. Disculpe las molestias.
    """)

    st.session_state.info_understood = st.checkbox("He comprendido las normas del programa")

    if st.button("CONTINUAR"):
        if st.session_state.info_understood:
            st.session_state.current_step = 3 # Ir a la selección de Área/Dirección (anteriormente Paso 2)
            st.rerun()
        else:
            st.warning("Debe marcar la casilla 'He comprendido las normas del programa' para continuar.")

# 3º: Selección de Área y Dirección/Gerencia (Ahora Paso 3)
elif st.session_state.current_step == 3:
    st.header("Paso 2: Selección de Área y Dirección/Gerencia")

    area_options = ["HOSPITALARIA", "PRIMARIA"]
    st.session_state.area_selected = st.selectbox(
        "**SELECCIONE ÁREA**",
        options=[""] + area_options,
        index=area_options.index(st.session_state.area_selected) + 1 if st.session_state.area_selected else 0,
        key="area_selector"
    )

    direccion_options = []
    if st.session_state.area_selected == "HOSPITALARIA":
        direccion_options = [
            "DIRECCIÓN GERENCIA HOSPITAL DOCTOR NEGRIN",
            "DIRECCIÓN GERENCIA COMPLEJO HOSPITALARIO UNIVERSITARIO Y MATERNO INFANTIL",
            "DIRECCIÓN GERENCIA COMPLEJO HOSPITALARIO UNIVERSITARIO DE CANARIAS",
            "DIRECCIÓN GERENCIA HOSPITAL NUESTRA SEÑORA DE CANDELARIA"
        ]
    elif st.session_state.area_selected == "PRIMARIA":
        direccion_options = [
            "GERENCIA DE ATENCIÓN PRIMARIA DE GRAN CANARIA",
            "GERENCIA DE ATENCIÓN PRIMARIA DE TENERIFE NORTE",
            "GERENCIA DE ATENCIÓN PRIMARIA DE TENERIFE SUR",
            "GERENCIA DE SERVICIOS SANITARIOS DE FUERTEVENTURA",
            "GERENCIA DE SERVICIOS SANITARIOS DE LANZAROTE",
            "GERENCIA DE SERVICIOS SANITARIOS DE LA PALMA"
        ]

    st.session_state.direccion_selected = st.selectbox(
        "**SELECCIONE DIRECCIÓN / GERENCIA**",
        options=[""] + direccion_options,
        index=direccion_options.index(st.session_state.direccion_selected) + 1 if st.session_state.direccion_selected and st.session_state.direccion_selected in direccion_options else 0,
        key="direccion_selector"
    )

    col_next_step3, col_back_step3 = st.columns(2)
    with col_next_step3:
        if st.button("Siguiente"):
            if st.session_state.area_selected and st.session_state.direccion_selected:
                st.session_state.current_step = 4 # Ir a la confirmación (anteriormente Paso 3)
                st.session_state.confirm_selection = False
                st.rerun()
            else:
                st.warning("Por favor, selecciona un Área y una Dirección/Gerencia para continuar.")
    with col_back_step3:
        if st.button("ATRÁS", key="back_from_step3"):
            st.session_state.current_step = 2 # Volver a la pantalla de información
            st.rerun()

# 4º: Mensaje de confirmación (Ahora Paso 4)
elif st.session_state.current_step == 4:
    st.header("Paso 3: Confirmación de Datos")
    st.markdown(f"**AREA :** <span style='color: #28a745;'>{st.session_state.area_selected}</span>", unsafe_allow_html=True)
    st.markdown(f"**DIRECCION/GERENCIA :** <span style='color: #007bff;'>{st.session_state.direccion_selected}</span>", unsafe_allow_html=True)
    st.markdown("**¿Desea confirmar estos datos?**")

    col_si, col_atras = st.columns(2)
    with col_si:
        if st.button("SI", key="confirm_si"):
            st.session_state.current_step = 5 # Ir a la introducción de datos (anteriormente Paso 5)
            st.session_state.confirm_selection = True
            st.rerun()
    with col_atras:
        if st.button("ATRÁS", key="confirm_atras"):
            st.session_state.current_step = 3 # Volver a la selección de Área/Dirección
            st.rerun()

# 5º: Zona de trabajo - Introducción de datos (Ahora Paso 5)
elif st.session_state.current_step == 5:
    st.header("Paso 4: Introducción de Datos de Residentes")
    st.write(f"Dirección/Gerencia seleccionada: **{st.session_state.direccion_selected}**")

    especialidades_para_rellenar = ESPECIALIDADES_POR_DIRECCION.get(st.session_state.direccion_selected, [])

    if not especialidades_para_rellenar:
        st.warning("No se encontraron especialidades para la Dirección/Gerencia seleccionada. Por favor, vuelve al paso anterior.")
        if st.button("Volver al Paso 2"):
            st.session_state.current_step = 3 # Volver a la selección de Área/Dirección
            st.rerun()
        st.stop()

    # Estructura para almacenar los datos, incluyendo 'num_residentes_R1' a 'num_residentes_R5'
    if 'data_input' not in st.session_state or st.session_state.data_input_direccion != st.session_state.direccion_selected:
        st.session_state.data_input = {
            esp: {
                'num_residentes_R1': None, 'R1': [None, None, None],
                'num_residentes_R2': None, 'R2': [None, None, None],
                'num_residentes_R3': None, 'R3': [None, None, None],
                'num_residentes_R4': None, 'R4': [None, None, None],
                'num_residentes_R5': None, 'R5': [None, None, None]
            }
            for esp in especialidades_para_rellenar
        }
        st.session_state.data_input_direccion = st.session_state.direccion_selected


    st.markdown("### Rellene los campos a continuación para cada especialidad:")
    st.info("💡 **Importante:** Para las notas, si no va a rellenar las 3 notas más altas, deje los campos vacíos. No ponga '0', ya que afectaría a la media. Las notas deben estar entre 0 y 10, con hasta 2 decimales.")

    # Preparar el DataFrame para st.data_editor con la nueva estructura
    input_data_list = []
    for esp in especialidades_para_rellenar:
        data = st.session_state.data_input[esp]
        input_data_list.append({
            "Especialidad": esp,
            "Nº R1 Evaluados": data['num_residentes_R1'],
            "R1 Nota 1": data['R1'][0], "R1 Nota 2": data['R1'][1], "R1 Nota 3": data['R1'][2],
            "Nº R2 Evaluados": data['num_residentes_R2'],
            "R2 Nota 1": data['R2'][0], "R2 Nota 2": data['R2'][1], "R2 Nota 3": data['R2'][2],
            "Nº R3 Evaluados": data['num_residentes_R3'],
            "R3 Nota 1": data['R3'][0], "R3 Nota 2": data['R3'][1], "R3 Nota 3": data['R3'][2],
            "Nº R4 Evaluados": data['num_residentes_R4'],
            "R4 Nota 1": data['R4'][0], "R4 Nota 2": data['R4'][1], "R4 Nota 3": data['R4'][2],
            "Nº R5 Evaluados": data['num_residentes_R5'],
            "R5 Nota 1": data['R5'][0], "R5 Nota 2": data['R5'][1], "R5 Nota 3": data['R5'][2],
            "Nº Residentes Aptos en la Evaluación final de residencia": 0 # Esto se calculará al final
        })
    input_data_df = pd.DataFrame(input_data_list)

    edited_df = st.data_editor(
        input_data_df,
        column_config={
            "Especialidad": st.column_config.Column("Especialidad", disabled=True),
            "Nº R1 Evaluados": st.column_config.NumberColumn("Nº R1 Evaluados", min_value=0, format="%d", help="Número de residentes R1 evaluados en esta especialidad."),
            "R1 Nota 1": st.column_config.NumberColumn("R1 Nota 1", min_value=0.0, max_value=10.0, format="%.2f"),
            "R1 Nota 2": st.column_config.NumberColumn("R1 Nota 2", min_value=0.0, max_value=10.0, format="%.2f"),
            "R1 Nota 3": st.column_config.NumberColumn("R1 Nota 3", min_value=0.0, max_value=10.0, format="%.2f"),
            "Nº R2 Evaluados": st.column_config.NumberColumn("Nº R2 Evaluados", min_value=0, format="%d", help="Número de residentes R2 evaluados en esta especialidad."),
            "R2 Nota 1": st.column_config.NumberColumn("R2 Nota 1", min_value=0.0, max_value=10.0, format="%.2f"),
            "R2 Nota 2": st.column_config.NumberColumn("R2 Nota 2", min_value=0.0, max_value=10.0, format="%.2f"),
            "R2 Nota 3": st.column_config.NumberColumn("R2 Nota 3", min_value=0.0, max_value=10.0, format="%.2f"),
            "Nº R3 Evaluados": st.column_config.NumberColumn("Nº R3 Evaluados", min_value=0, format="%d", help="Número de residentes R3 evaluados en esta especialidad."),
            "R3 Nota 1": st.column_config.NumberColumn("R3 Nota 1", min_value=0.0, max_value=10.0, format="%.2f"),
            "R3 Nota 2": st.column_config.NumberColumn("R3 Nota 2", min_value=0.0, max_value=10.0, format="%.2f"),
            "R3 Nota 3": st.column_config.NumberColumn("R3 Nota 3", min_value=0.0, max_value=10.0, format="%.2f"),
            "Nº R4 Evaluados": st.column_config.NumberColumn("Nº R4 Evaluados", min_value=0, format="%d", help="Número de residentes R4 evaluados en esta especialidad."),
            "R4 Nota 1": st.column_config.NumberColumn("R4 Nota 1", min_value=0.0, max_value=10.0, format="%.2f"),
            "R4 Nota 2": st.column_config.NumberColumn("R4 Nota 2", min_value=0.0, max_value=10.0, format="%.2f"),
            "R4 Nota 3": st.column_config.NumberColumn("R4 Nota 3", min_value=0.0, max_value=10.0, format="%.2f"),
            "Nº R5 Evaluados": st.column_config.NumberColumn("Nº R5 Evaluados", min_value=0, format="%d", help="Número de residentes R5 evaluados en esta especialidad."),
            "R5 Nota 1": st.column_config.NumberColumn("R5 Nota 1", min_value=0.0, max_value=10.0, format="%.2f"),
            "R5 Nota 2": st.column_config.NumberColumn("R5 Nota 2", min_value=0.0, max_value=10.0, format="%.2f"),
            "R5 Nota 3": st.column_config.NumberColumn("R5 Nota 3", min_value=0.0, max_value=10.0, format="%.2f"),
            "Nº Residentes Aptos en la Evaluación final de residencia": st.column_config.NumberColumn("Nº Residentes Aptos en la Evaluación final de residencia", disabled=True, format="%d")
        },
        num_rows="fixed", # Ahora es fijo porque las especialidades ya están predefinidas
        use_container_width=True,
        key="data_input_editor" # Añadir una clave para evitar re-renderizados innecesarios
    )

    # Actualizar st.session_state.data_input con los valores editados y calcular 'Nº Residentes Aptos'
    st.session_state.total_residentes_r = {f'R{i}': 0 for i in range(1, 6)}
    st.session_state.note_entry_summary = [] # Para el nuevo resumen

    for i, esp in enumerate(especialidades_para_rellenar):
        # Actualizar número de residentes evaluados por R
        st.session_state.data_input[esp]['num_residentes_R1'] = edited_df.iloc[i]["Nº R1 Evaluados"]
        st.session_state.data_input[esp]['num_residentes_R2'] = edited_df.iloc[i]["Nº R2 Evaluados"]
        st.session_state.data_input[esp]['num_residentes_R3'] = edited_df.iloc[i]["Nº R3 Evaluados"]
        st.session_state.data_input[esp]['num_residentes_R4'] = edited_df.iloc[i]["Nº R4 Evaluados"]
        st.session_state.data_input[esp]['num_residentes_R5'] = edited_df.iloc[i]["Nº R5 Evaluados"]

        # Actualizar notas
        st.session_state.data_input[esp]['R1'] = [edited_df.iloc[i]["R1 Nota 1"], edited_df.iloc[i]["R1 Nota 2"], edited_df.iloc[i]["R1 Nota 3"]]
        st.session_state.data_input[esp]['R2'] = [edited_df.iloc[i]["R2 Nota 1"], edited_df.iloc[i]["R2 Nota 2"], edited_df.iloc[i]["R2 Nota 3"]]
        st.session_state.data_input[esp]['R3'] = [edited_df.iloc[i]["R3 Nota 1"], edited_df.iloc[i]["R3 Nota 2"], edited_df.iloc[i]["R3 Nota 3"]]
        st.session_state.data_input[esp]['R4'] = [edited_df.iloc[i]["R4 Nota 1"], edited_df.iloc[i]["R4 Nota 2"], edited_df.iloc[i]["R4 Nota 3"]]
        st.session_state.data_input[esp]['R5'] = [edited_df.iloc[i]["R5 Nota 1"], edited_df.iloc[i]["R5 Nota 2"], edited_df.iloc[i]["R5 Nota 3"]]

        # Calcular 'Nº Residentes Aptos en la Evaluación final de residencia' y totales por R
        total_aptos = 0
        note_summary_row = {"Especialidad": esp, "3 Notas": [], "2 Notas": [], "1 Nota": [], "Vacío": []}

        for r_num in range(1, 6):
            num_res_col = f"Nº R{r_num} Evaluados"
            if edited_df.iloc[i][num_res_col] is not None and pd.notna(edited_df.iloc[i][num_res_col]):
                total_aptos += int(edited_df.iloc[i][num_res_col])
                st.session_state.total_residentes_r[f'R{r_num}'] += int(edited_df.iloc[i][num_res_col])
            
            # Contar notas para el resumen
            notes_for_r = [n for n in st.session_state.data_input[esp][f'R{r_num}'] if n is not None and pd.notna(n) and float(n) != 0.0]
            num_filled_notes = len(notes_for_r)

            if num_filled_notes == 3:
                note_summary_row["3 Notas"].append(f"R{r_num}")
            elif num_filled_notes == 2:
                note_summary_row["2 Notas"].append(f"R{r_num}")
            elif num_filled_notes == 1:
                note_summary_row["1 Nota"].append(f"R{r_num}")
            elif num_filled_notes == 0:
                note_summary_row["Vacío"].append(f"R{r_num}")
        
        # Unir las listas para el resumen
        note_summary_row["3 Notas"] = ", ".join(note_summary_row["3 Notas"])
        note_summary_row["2 Notas"] = ", ".join(note_summary_row["2 Notas"])
        note_summary_row["1 Nota"] = ", ".join(note_summary_row["1 Nota"])
        note_summary_row["Vacío"] = ", ".join(note_summary_row["Vacío"])
        st.session_state.note_entry_summary.append(note_summary_row)


    col_next_step5, col_back_step5 = st.columns(2)

    with col_next_step5:
        if st.button("SIGUIENTE"):
            # Validación antes de pasar al resumen
            validation_errors = []
            for esp, data in st.session_state.data_input.items():
                for r_num in range(1, 6):
                    num_res_key = f"num_residentes_R{r_num}"
                    if data[num_res_key] is None or pd.isna(data[num_res_key]) or not isinstance(data[num_res_key], (int, float)) or data[num_res_key] < 0:
                        validation_errors.append(f"En '{esp}', '{num_res_key}' debe ser un número entero no negativo y no puede estar vacío.")

                    # Validar notas (entre 0 y 10, hasta 2 decimales)
                    for i, note in enumerate(data[f'R{r_num}']):
                        if note is not None and pd.notna(note):
                            if not isinstance(note, (int, float)) or not (0 <= note <= 10):
                                validation_errors.append(f"En '{esp}', Nota {i+1} de R{r_num}: El valor '{note}' no es válido. Las notas deben ser números entre 0 y 10.")
            
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
                st.warning("Por favor, corrige los errores para poder continuar.")
            else:
                st.session_state.current_step = 6 # Ir al resumen
                st.rerun()

    with col_back_step5:
        if st.button("ATRÁS", key="back_from_step5"):
            st.session_state.current_step = 4 # Volver a la confirmación
            st.rerun()

# 6º: Resumen datos introducidos (NUEVO PASO)
elif st.session_state.current_step == 6:
    st.header("Paso 5: Resumen datos introducidos")
    st.markdown("Usted ha introducido lo siguiente en este aplicativo:")

    # Cuadro de Número de Residentes Evaluados
    st.markdown("##### Número de residentes evaluados por año")
    residentes_evaluados_df = pd.DataFrame({
        " ": ["Numero de residentes evaluados"],
        "R1": [st.session_state.total_residentes_r['R1']],
        "R2": [st.session_state.total_residentes_r['R2']],
        "R3": [st.session_state.total_residentes_r['R3']],
        "R4": [st.session_state.total_residentes_r['R4']],
        "R5": [st.session_state.total_residentes_r['R5']]
    })
    st.table(residentes_evaluados_df)

    # Cuadro de Rangos de Notas Introducidos
    st.markdown("##### Rangos de notas introducidos por especialidad y R")
    note_summary_df = pd.DataFrame(st.session_state.note_entry_summary)
    st.table(note_summary_df)

    col_accept, col_review = st.columns(2)
    with col_accept:
        if st.button("ACEPTAR y GENERAR"):
            # Calcular medias y preparar DataFrame para Excel
            results = []
            n_residentes_data = []
            for esp, data in st.session_state.data_input.items():
                row = {"Especialidad": esp}
                total_aptos_esp = 0 # Para el total de aptos de la especialidad

                for r_num in range(1, 6):
                    r_key = f"R{r_num}"
                    notes = data[r_key]
                    avg = calculate_average(notes)
                    row[f"Media {r_key}"] = f"{avg:.2f}" if avg is not None else ""

                    # Sumar el número de residentes evaluados para el total aptos
                    num_res_r_key = f"num_residentes_{r_key}"
                    if data[num_res_r_key] is not None and pd.notna(data[num_res_r_key]):
                        total_aptos_esp += int(data[num_res_r_key])
                
                row["Nº Residentes Aptos"] = total_aptos_esp # Agregar esta columna aquí
                results.append(row)

                # Datos para la hoja "N_Residentes" con la nueva estructura
                n_residentes_data.append({
                    "Especialidad": esp,
                    "Nº R1 Evaluados": data['num_residentes_R1'],
                    "Nº R2 Evaluados": data['num_residentes_R2'],
                    "Nº R3 Evaluados": data['num_residentes_R3'],
                    "Nº R4 Evaluados": data['num_residentes_R4'],
                    "Nº R5 Evaluados": data['num_residentes_R5'],
                    "Nº Residentes Aptos en la Evaluación final de residencia": total_aptos_esp
                })


            output_df = pd.DataFrame(results)

            # Reordenar y renombrar columnas para el Excel final (hoja principal)
            output_df_columns = ["Especialidad", "Media R1", "Media R2", "Media R3", "Media R4", "Media R5", "Nº Residentes Aptos"]
            output_df = output_df[output_df_columns]

            # Crear DataFrame para la nueva hoja "N_Residentes" con la estructura solicitada
            n_residentes_df = pd.DataFrame(n_residentes_data)

            # Generar archivo Excel en memoria
            output = io.BytesIO()
            excel_sheet_name = CODIGOS_DIRECCION.get(st.session_state.direccion_selected, "Resultados")
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                output_df.to_excel(writer, sheet_name=excel_sheet_name, index=False)
                n_residentes_df.to_excel(writer, sheet_name="N_Residentes", index=False)
            output.seek(0)

            st.session_state.excel_output = output
            st.session_state.excel_filename = f"Evaluacion_Notas_{excel_sheet_name}.xlsx"
            
            # Enviar por correo (sin el archivo aún, solo el mensaje de éxito/error)
            # Pasamos una copia del BytesIO para que el original no se consuma al leerlo para el adjunto
            email_sent = send_email_with_mailgun(
                MAILGUN_RECIPIENT_EMAIL,
                f"Informe de Evaluación de Notas - {excel_sheet_name}",
                f"Adjunto encontrarás el informe de evaluación de notas para la Dirección/Gerencia: {st.session_state.direccion_selected}.",
                attachment=st.session_state.excel_output,
                filename=st.session_state.excel_filename
            )

            st.session_state.current_step = 7 # Ir a la descarga y mensaje de correo
            st.rerun()

    with col_review:
        if st.button("REVISAR"):
            st.session_state.current_step = 5 # Volver a la introducción de datos
            st.rerun()

# 7º: Descarga y mensaje de envío por correo (Ahora Paso 6)
elif st.session_state.current_step == 7:
    st.header("Paso 6: Descarga del Informe")
    st.success("¡El informe se ha generado con éxito! Puedes descargarlo ahora.")

    if 'excel_output' in st.session_state and 'excel_filename' in st.session_state:
        st.download_button(
            label="Descargar Informe Excel ⬇️",
            data=st.session_state.excel_output,
            file_name=st.session_state.excel_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Haz clic para descargar el archivo Excel generado."
        )
    else:
        st.error("No se encontró el archivo Excel. Por favor, regresa y genera el informe nuevamente.")

    st.markdown("---")
    st.warning("⚠️ **Recordatorio Importante:** Después de descargar el archivo Excel, por favor, asegúrate de enviarlo a **fse.scs@gobiernodecanarias.org** 📧.")
    st.info("💡 **Aclaración:** Streamlit no permite ventanas emergentes que bloqueen la aplicación para confirmaciones directas. Este mensaje es la forma más clara de recordarte la acción post-descarga y de informar si el envío automático fue exitoso o no.")

    if st.button("Volver al Inicio (nueva evaluación)"):
        st.session_state.clear() # Limpiar todo el estado de la sesión para reiniciar
        st.rerun()

# 8º: Botón de salir del aplicativo (Siempre visible en la barra lateral)
st.sidebar.markdown("---")
if st.sidebar.button("Salir del Aplicativo 🚪"):
    st.session_state.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("##### ℹ️ Información del Aplicativo")
st.sidebar.write("Versión: 1.1")
st.sidebar.write("Desarrollado para: F.S.E. – S.C.S.")
st.sidebar.write("Fecha: Julio 2025")