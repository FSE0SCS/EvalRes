import os
import streamlit as st
import pandas as pd
import io
import requests
from dotenv import load_dotenv

load_dotenv()

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
    st.session_state.current_step = 2
    st.session_state.area_selected = None
    st.session_state.direccion_selected = None
    st.session_state.confirm_selection = False
    st.session_state.info_understood = False

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
        attachment.seek(0)
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
if 'info_understood' not in st.session_state:
    st.session_state.info_understood = False
if 'data_input' not in st.session_state:
    st.session_state.data_input = {}
if 'data_input_direccion' not in st.session_state:
    st.session_state.data_input_direccion = None
if 'total_residentes_r' not in st.session_state:
    st.session_state.total_residentes_r = {f'R{i}': 0 for i in range(1, 6)}
if 'note_entry_summary' not in st.session_state:
    st.session_state.note_entry_summary = pd.DataFrame()
if 'especialidades_para_rellenar' not in st.session_state:
    st.session_state.especialidades_para_rellenar = []
if 'selected_rs_for_input' not in st.session_state:
    st.session_state.selected_rs_for_input = []

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
    st.markdown("- **Versión 1.2 (2025-07-14):** Mejora de la interfaz de entrada de notas, dividiendo la tabla en 5 sub-tablas por R y añadiendo selectores para pre-rellenar con '0'.")
    st.stop()


# Flujo principal de la aplicación
st.title("Evaluación de Notas de Residentes 1.2 – F.S.E. – S.C.S. 🏥")
st.markdown("---")

# 1º: Pantalla de bienvenida
if st.session_state.current_step == 1:
    st.header("Bienvenido al programa de Evaluación de Notas de Residentes")
    st.write("Haz clic en 'Iniciar Aplicativo' para comenzar el proceso.")
    if st.button("Iniciar Aplicativo"):
        st.session_state.current_step = 2
        st.rerun()

# 2º: Pantalla de Información y Normas (NUEVO PASO)
elif st.session_state.current_step == 2:
    st.header("Paso 1: Información Importante del Programa")
    st.markdown("""
    **Bienvenidos al programa para calcular las medias de los residentes**

    * Debe seleccionar su **ÁREA** de operación y su **DIRECCIÓN/GERENCIA** para obtener acceso a las especialidades evaluadas.
    * Debe rellenar el **NUMERO DE RESIDENTES QUE FINALIZAN LA RESIDENCIA** en el ejercicio en curso, para las diferentes especialidades.
    * Debe rellenar las notas de los residentes. Los valores aceptados no pueden ser superiores a **10** y pueden contener **2 decimales**.
    * Si no rellena las 3 notas más altas de alguna especialidad, **NO debe poner un 0** en la casilla vacía, simplemente no introduzca ningún valor numérico.
    * <span style='color: red;'>**IMPORTANTE:** Para la introducción de las notas es posible que tenga que hacerlo dos veces por cada celda, **NO es un error**, es un proceso de validación del programa. Disculpe las molestias.</span>
    """, unsafe_allow_html=True)

    st.session_state.info_understood = st.checkbox("He comprendido las normas del programa")

    if st.button("CONTINUAR"):
        if st.session_state.info_understood:
            st.session_state.current_step = 3
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
                st.session_state.current_step = 4
                st.session_state.confirm_selection = False
                st.rerun()
            else:
                st.warning("Por favor, selecciona un Área y una Dirección/Gerencia para continuar.")
    with col_back_step3:
        if st.button("ATRÁS", key="back_from_step3"):
            st.session_state.current_step = 2
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
            st.session_state.current_step = 5
            st.session_state.confirm_selection = True
            # Almacenar especialidades_para_rellenar en session_state aquí
            st.session_state.especialidades_para_rellenar = ESPECIALIDADES_POR_DIRECCION.get(st.session_state.direccion_selected, [])
            st.rerun()
    with col_atras:
        if st.button("ATRÁS", key="confirm_atras"):
            st.session_state.current_step = 3
            st.rerun()

# 5º: Zona de trabajo - Introducción de datos (Ahora Paso 5)
elif st.session_state.current_step == 5:
    st.header("Paso 4: Introducción de Datos de Residentes")
    st.write(f"Dirección/Gerencia seleccionada: **{st.session_state.direccion_selected}**")

    especialidades_para_rellenar = st.session_state.especialidades_para_rellenar

    if not especialidades_para_rellenar:
        st.warning("No se encontraron especialidades para la Dirección/Gerencia seleccionada. Por favor, vuelve al paso anterior.")
        if st.button("Volver al Paso 2"):
            st.session_state.current_step = 3
            st.rerun()
        st.stop()

    # Inicializar data_input si la dirección ha cambiado o es la primera vez
    # Or if especialidades_para_rellenar has changed (e.g., if user went back and selected a different area)
    if 'data_input' not in st.session_state or \
       st.session_state.data_input_direccion != st.session_state.direccion_selected or \
       set(st.session_state.data_input.keys()) != set(especialidades_para_rellenar):
        
        # Create a new data_input structure, preserving existing data if specialty exists
        new_data_input = {}
        for esp in especialidades_para_rellenar:
            if esp in st.session_state.data_input:
                new_data_input[esp] = st.session_state.data_input[esp]
            else:
                new_data_input[esp] = {
                    'num_residentes_R1': None, 'R1': [None, None, None],
                    'num_residentes_R2': None, 'R2': [None, None, None],
                    'num_residentes_R3': None, 'R3': [None, None, None],
                    'num_residentes_R4': None, 'R4': [None, None, None],
                    'num_residentes_R5': None, 'R5': [None, None, None]
                }
        st.session_state.data_input = new_data_input
        st.session_state.data_input_direccion = st.session_state.direccion_selected
        st.session_state.selected_rs_for_input = [] # Resetear selecciones al cambiar de dirección

    st.markdown("### Seleccione de qué R va a introducir las 3 notas más altas:")

    col_r1, col_r2, col_r3, col_r4, col_r5, col_all = st.columns(6)

    # Use a unique key for each checkbox, and manage their states directly
    r1_checked = col_r1.checkbox("R1", value='R1' in st.session_state.selected_rs_for_input, key="r1_checkbox")
    r2_checked = col_r2.checkbox("R2", value='R2' in st.session_state.selected_rs_for_input, key="r2_checkbox")
    r3_checked = col_r3.checkbox("R3", value='R3' in st.session_state.selected_rs_for_input, key="r3_checkbox")
    r4_checked = col_r4.checkbox("R4", value='R4' in st.session_state.selected_rs_for_input, key="r4_checkbox")
    r5_checked = col_r5.checkbox("R5", value='R5' in st.session_state.selected_rs_for_input, key="r5_checkbox")

    # To prevent infinite reruns, handle 'all_checked' logic carefully.
    # The `value` parameter for checkboxes should ideally be linked directly to st.session_state
    # to allow for programmatic control and prevent unintended reruns from just setting the `value`.

    # Let's create a temporary list of current selections based on direct checkbox values
    temp_selected_rs = []
    if r1_checked: temp_selected_rs.append('R1')
    if r2_checked: temp_selected_rs.append('R2')
    if r3_checked: temp_selected_rs.append('R3')
    if r4_checked: temp_selected_rs.append('R4')
    if r5_checked: temp_selected_rs.append('R5')

    # Handle the "Todos" checkbox separately to avoid direct modification of other checkbox states
    # inside the rendering loop, which can cause issues.
    # Instead, we define a callback for it.

    def toggle_all_rs():
        if st.session_state.all_checkbox:
            st.session_state.selected_rs_for_input = ['R1', 'R2', 'R3', 'R4', 'R5']
            st.session_state.r1_checkbox = True
            st.session_state.r2_checkbox = True
            st.session_state.r3_checkbox = True
            st.session_state.r4_checkbox = True
            st.session_state.r5_checkbox = True
        else:
            st.session_state.selected_rs_for_input = []
            st.session_state.r1_checkbox = False
            st.session_state.r2_checkbox = False
            st.session_state.r3_checkbox = False
            st.session_state.r4_checkbox = False
            st.session_state.r5_checkbox = False

    # Initialize all_checkbox state based on individual checkboxes
    initial_all_checked_value = (
        r1_checked and r2_checked and r3_checked and r4_checked and r5_checked and
        len(temp_selected_rs) == 5 # Ensure no other R's are secretly selected
    )
    all_checked = col_all.checkbox("Todos", value=initial_all_checked_value, key="all_checkbox", on_change=toggle_all_rs)


    # Update st.session_state.selected_rs_for_input based on individual checkboxes
    # This must happen after the 'all_checked' logic if 'all_checked' can override individual selections.
    # If 'all_checked' was just clicked, its on_change callback already handled the state.
    # Otherwise, individual checkbox changes update the selected_rs_for_input.
    if not st.session_state.get('all_checkbox_clicked_this_rerun', False): # Prevent double-updating if 'all_checkbox' triggered the rerun
        current_selected_rs = []
        if st.session_state.r1_checkbox: current_selected_rs.append('R1')
        if st.session_state.r2_checkbox: current_selected_rs.append('R2')
        if st.session_state.r3_checkbox: current_selected_rs.append('R3')
        if st.session_state.r4_checkbox: current_selected_rs.append('R4')
        if st.session_state.r5_checkbox: current_selected_rs.append('R5')
        
        if set(st.session_state.selected_rs_for_input) != set(current_selected_rs):
            st.session_state.selected_rs_for_input = current_selected_rs
            st.rerun() # Rerun to apply changes in disabled states for `Nº Finalizados`


    st.info("💡 **Importante:** Para las notas, si no va a rellenar las 3 notas más altas, deje los campos vacíos. No ponga '0', ya que afectaría a la media. Las notas deben estar entre 0 y 10, con hasta 2 decimales.")
    st.info("Cuando selecciona un R, la tabla de ese R se activa para la edición. Los R no seleccionados tendrán su 'Nº Evaluados' rellenado con 0.")

    # Generar las 5 tablas dinámicamente
    for r_num in range(1, 6):
        r_key = f'R{r_num}'
        
        # Prepare data for the current R's table using st.session_state.data_input
        table_data_list = []
        for esp in especialidades_para_rellenar:
            num_res = st.session_state.data_input[esp][f'num_residentes_{r_key}']
            notes = st.session_state.data_input[esp][r_key]
            
            # Apply the pre-fill logic if this R is not selected for input
            is_num_res_disabled = r_key not in st.session_state.selected_rs_for_input

            table_data_list.append({
                "Especialidad": esp,
                f"Nº {r_key} Finalizados": 0 if is_num_res_disabled else (num_res if pd.notna(num_res) else None),
                f"{r_key} Nota 1": notes[0],
                f"{r_key} Nota 2": notes[1],
                f"{r_key} Nota 3": notes[2]
            })
        
        table_df = pd.DataFrame(table_data_list)

        st.markdown(f"#### Datos para {r_key}")
        
        # Configuration of columns for st.data_editor
        column_config = {
            "Especialidad": st.column_config.Column("Especialidad", disabled=True),
            f"Nº {r_key} Finalizados": st.column_config.NumberColumn(
                f"Nº {r_key} Finalizados",
                min_value=0, format="%d", help=f"Número de residentes {r_key} finalizados en esta especialidad.",
                disabled=is_num_res_disabled # Disable if not selected
            ),
            f"{r_key} Nota 1": st.column_config.NumberColumn(f"{r_key} Nota 1", min_value=0.0, max_value=10.0, format="%.2f"),
            f"{r_key} Nota 2": st.column_config.NumberColumn(f"{r_key} Nota 2", min_value=0.0, max_value=10.0, format="%.2f"),
            f"{r_key} Nota 3": st.column_config.NumberColumn(f"{r_key} Nota 3", min_value=0.0, max_value=10.0, format="%.2f")
        }

        # Use a unique key for each data editor
        edited_df = st.data_editor(
            table_df,
            column_config=column_config,
            num_rows="fixed",
            use_container_width=True,
            key=f"data_input_editor_{r_key}"
        )

        # IMMEDIATELY UPDATE session_state.data_input with the edited values
        # This is the crucial part to prevent double entry due to reruns.
        for i, esp in enumerate(especialidades_para_rellenar):
            # Update num_residentes
            num_res_val = edited_df.iloc[i][f"Nº {r_key} Finalizados"]
            try:
                st.session_state.data_input[esp][f'num_residentes_{r_key}'] = int(num_res_val) if pd.notna(num_res_val) and num_res_val != "" else None
            except ValueError:
                st.session_state.data_input[esp][f'num_residentes_{r_key}'] = None # Set to None if invalid

            # Update notes
            updated_notes = []
            for j in range(1, 4):
                note_val = edited_df.iloc[i][f"{r_key} Nota {j}"]
                try:
                    updated_notes.append(float(note_val) if pd.notna(note_val) and note_val != "" else None)
                except ValueError:
                    updated_notes.append(None) # Set to None if invalid
            st.session_state.data_input[esp][r_key] = updated_notes
        
        st.markdown("---") # Separator between tables

    col_next_step5, col_back_step5 = st.columns(2)

    with col_next_step5:
        if st.button("SIGUIENTE"):
            # Validation before moving to the summary
            validation_errors = []
            for esp in especialidades_para_rellenar:
                data = st.session_state.data_input[esp]
                for r_num in range(1, 6):
                    num_res_key = f"num_residentes_R{r_num}"
                    num_res_value = data[num_res_key]
                    
                    # Validation for 'num_residentes'
                    # It's okay to be None if the R group was not selected (and thus auto-filled to 0)
                    is_num_res_disabled = f'R{r_num}' not in st.session_state.selected_rs_for_input
                    
                    if not is_num_res_disabled: # Only validate if it was expected for user input
                        if num_res_value is None or not isinstance(num_res_value, int) or num_res_value < 0:
                            validation_errors.append(f"En '{esp}', '{num_res_key}': El número de residentes no puede estar vacío, no es un número válido o es negativo.")

                    # Validate notes (between 0 and 10, up to 2 decimals)
                    for k, note in enumerate(data[f'R{r_num}']):
                        if note is not None:
                            if not isinstance(note, float) or not (0 <= note <= 10):
                                validation_errors.append(f"En '{esp}', Nota {k+1} de R{r_num}: El valor '{note}' no es válido. Las notas deben ser números entre 0 y 10.")
            
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
                st.warning("Por favor, corrige los errores para poder continuar.")
            else:
                st.session_state.current_step = 6
                st.rerun()

    with col_back_step5:
        if st.button("ATRÁS", key="back_from_step5"):
            st.session_state.current_step = 4
            st.rerun()

# 6º: Resumen datos introducidos
elif st.session_state.current_step == 6:
    st.header("Paso 5: Resumen datos introducidos")
    st.markdown("Usted ha introducido lo siguiente en este aplicativo:")

    # Recalculate totals and notes summary before display
    st.session_state.total_residentes_r = {f'R{i}': 0 for i in range(1, 6)}
    st.session_state.note_entry_summary = []

    for esp in st.session_state.especialidades_para_rellenar:
        total_aptos_esp = 0
        note_summary_row = {"Especialidad": esp, "3 Notas": [], "2 Notas": [], "1 Nota": [], "Vacío": []}

        for r_num in range(1, 6):
            r_key = f"R{r_num}"
            
            # Sum the number of residents evaluated for the total aptos
            num_res_r_key = f"num_residentes_{r_key}"
            # Ensure the value is treated as 0 if it's disabled for input, even if internally None for validation
            num_res_val_for_sum = 0
            if r_key in st.session_state.selected_rs_for_input: # If it was enabled for input
                if st.session_state.data_input[esp][num_res_r_key] is not None:
                    num_res_val_for_sum = int(st.session_state.data_input[esp][num_res_r_key])
            else: # If it was disabled, it should be treated as 0
                num_res_val_for_sum = 0

            total_aptos_esp += num_res_val_for_sum
            st.session_state.total_residentes_r[r_key] += num_res_val_for_sum
            
            # Count notes for the summary
            notes_for_r = [n for n in st.session_state.data_input[esp][r_key] if n is not None and pd.notna(n) and float(n) != 0.0]
            num_filled_notes = len(notes_for_r)

            if num_filled_notes == 3:
                note_summary_row["3 Notas"].append(f"R{r_num}")
            elif num_filled_notes == 2:
                note_summary_row["2 Notas"].append(f"R{r_num}")
            elif num_filled_notes == 1:
                note_summary_row["1 Nota"].append(f"R{r_num}")
            elif num_filled_notes == 0:
                note_summary_row["Vacío"].append(f"R{r_num}")
        
        note_summary_row["3 Notas"] = ", ".join(note_summary_row["3 Notas"])
        note_summary_row["2 Notas"] = ", ".join(note_summary_row["2 Notas"])
        note_summary_row["1 Nota"] = ", ".join(note_summary_row["1 Nota"])
        note_summary_row["Vacío"] = ", ".join(note_summary_row["Vacío"])
        st.session_state.note_entry_summary.append(note_summary_row)


    # Cuadro de Número de Residentes Evaluados
    st.markdown("##### Número de residentes finalizados por año")
    residentes_finalizados_df = pd.DataFrame({
        " ": ["Numero de residentes finalizados"],
        "R1": [st.session_state.total_residentes_r['R1']],
        "R2": [st.session_state.total_residentes_r['R2']],
        "R3": [st.session_state.total_residentes_r['R3']],
        "R4": [st.session_state.total_residentes_r['R4']],
        "R5": [st.session_state.total_residentes_r['R5']]
    })
    st.table(residentes_finalizados_df)

    # Cuadro de Rangos de Notas Introducidos
    st.markdown("##### Rangos de notas introducidos por especialidad y R")
    note_summary_df = pd.DataFrame(st.session_state.note_entry_summary)
    st.table(note_summary_df)

    col_accept, col_review = st.columns(2)
    with col_accept:
        if st.button("ACEPTAR y GENERAR"):
            # Calculate averages and prepare DataFrame for Excel
            results = []
            n_residentes_data = []
            for esp in st.session_state.especialidades_para_rellenar:
                row = {"Especialidad": esp}
                total_aptos_esp = 0

                for r_num in range(1, 6):
                    r_key = f"R{r_num}"
                    notes = st.session_state.data_input[esp][r_key]
                    avg = calculate_average(notes)
                    row[f"Media {r_key}"] = f"{avg:.2f}" if avg is not None else ""

                    num_res_r_key = f"num_residentes_{r_key}"
                    # Use the value from data_input, ensuring 0 for disabled fields
                    num_res_val = 0
                    if r_key in st.session_state.selected_rs_for_input:
                        if st.session_state.data_input[esp][num_res_r_key] is not None:
                            num_res_val = int(st.session_state.data_input[esp][num_res_r_key])
                    total_aptos_esp += num_res_val
                
                row["Nº Residentes Aptos"] = total_aptos_esp
                results.append(row)

                # Data for the "N_Residentes" sheet with the new structure
                n_residentes_data.append({
                    "Especialidad": esp,
                    "Nº R1 Finalizados": st.session_state.data_input[esp]['num_residentes_R1'] if 'R1' in st.session_state.selected_rs_for_input else 0,
                    "Nº R2 Finalizados": st.session_state.data_input[esp]['num_residentes_R2'] if 'R2' in st.session_state.selected_rs_for_input else 0,
                    "Nº R3 Finalizados": st.session_state.data_input[esp]['num_residentes_R3'] if 'R3' in st.session_state.selected_rs_for_input else 0,
                    "Nº R4 Finalizados": st.session_state.data_input[esp]['num_residentes_R4'] if 'R4' in st.session_state.selected_rs_for_input else 0,
                    "Nº R5 Finalizados": st.session_state.data_input[esp]['num_residentes_R5'] if 'R5' in st.session_state.selected_rs_for_input else 0,
                    "Nº Residentes que finalizan residencia en el año en curso": total_aptos_esp
                })

            output_df = pd.DataFrame(results)

            # Reorder and rename columns for the final Excel (main sheet)
            output_df_columns = ["Especialidad", "Media R1", "Media R2", "Media R3", "Media R4", "Media R5", "Nº Residentes Aptos"]
            output_df = output_df[output_df_columns]

            # Create DataFrame for the new "N_Residentes" sheet with the requested structure
            n_residentes_df = pd.DataFrame(n_residentes_data)

            # Generate Excel file in memory
            output = io.BytesIO()
            excel_sheet_name = CODIGOS_DIRECCION.get(st.session_state.direccion_selected, "Resultados")
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                output_df.to_excel(writer, sheet_name=excel_sheet_name, index=False)
                n_residentes_df.to_excel(writer, sheet_name="N_Residentes", index=False)
            output.seek(0)

            st.session_state.excel_output = output
            st.session_state.excel_filename = f"Evaluacion_Notas_{excel_sheet_name}.xlsx"
            
            # Send by email
            email_sent = send_email_with_mailgun(
                MAILGUN_RECIPIENT_EMAIL,
                f"Informe de Evaluación de Notas - {excel_sheet_name}",
                f"Adjunto encontrarás el informe de evaluación de notas para la Dirección/Gerencia: {st.session_state.direccion_selected}.",
                attachment=st.session_state.excel_output,
                filename=st.session_state.excel_filename
            )

            st.session_state.current_step = 7
            st.rerun()

    with col_review:
        if st.button("REVISAR"):
            st.session_state.current_step = 5
            st.rerun()

# 7º: Descarga y mensaje de envío por correo
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
        st.session_state.clear()
        st.rerun()

# 8º: Botón de salir del aplicativo (Siempre visible en la barra lateral)
st.sidebar.markdown("---")
if st.sidebar.button("Salir del Aplicativo 🚪"):
    st.session_state.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("##### ℹ️ Información del Aplicativo")
st.sidebar.write("Versión: 1.2")
st.sidebar.write("Desarrollado para: F.S.E. – S.C.S.")
st.sidebar.write("Fecha: Julio 2025")