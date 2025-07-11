import streamlit as st
import pandas as pd
import io

# --- Configuración General ---
st.set_page_config(
    page_title="Evaluación de Notas de Residentes 1.0 – F.S.E. – S.C.S.",
    page_icon="🏥",
    layout="wide"
)

# --- Contraseña de Acceso ---
PASSWORD = "residentes2025"

# --- Datos Maestros ---
# Mapeo de Direcciones/Gerencias a Códigos para el nombre de la hoja Excel
CODIGOS_DIRECCION = {
    "DIRECCIÓN GERENCIA HOSPITAL DOCTOR NEGRIN": "HUGCNEGRIN",
    "DIRECCIÓN GERENCIA COMPLEJO HOSPITALARIO UNIVERSITARIO Y MATERNO INFANTIL": "CHUIMI",
    "DIRECCIÓN GERENCIA COMPLEJO HOSPITALARIO UNIVERSITARIO DE CANARIAS": "CHUC",
    "DIRECCIÓN GERENCIA HOSPITAL NUESTRA SEÑORA DE CANDELARIA": "HUSNC",
    "GERENCIA DE ATENCIÓN PRIMARIA DE GRAN CANARIA": "GAPGC",
    "GERENCIA DE ATENCIÓN PRIMARIA DE TENERIFE NORTE": "GAPTF Norte",
    "GERENCIA DE ATENCIÓN PRIMARIA DE TENERIFE SUR": "GAPTF Sur",
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
    """Calcula la media de una lista de notas, ignorando None, NaN o valores vacíos."""
    # Filter out None, NaN, and empty strings. Convert to float if not already.
    valid_notes = [float(note) for note in notes if note is not None and pd.notna(note) and note != ""]
    if not valid_notes:
        return None
    return sum(valid_notes) / len(valid_notes)

def reset_selection_page():
    """Reinicia el estado de la sesión para volver a la página de selección."""
    st.session_state.current_step = 2
    st.session_state.area_selected = None
    st.session_state.direccion_selected = None
    st.session_state.confirm_selection = False

def login_successful():
    """Marca la sesión como logueada."""
    st.session_state.logged_in = True

# --- Interfaz de Usuario ---

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

# --- Control de Acceso ---
if not st.session_state.logged_in:
    st.title("🔐 Acceso al Aplicativo de Evaluación de Notas")
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
    st.stop()


# --- Flujo del Programa ---
st.title("Evaluación de Notas de Residentes 1.0 – F.S.E. – S.C.S. 🏥")
st.markdown("---")

# 1º: Pantalla de bienvenida
if st.session_state.current_step == 1:
    st.header("Bienvenido al programa de Evaluación de Notas de Residentes")
    st.write("Haz clic en 'Iniciar Aplicativo' para comenzar el proceso.")
    if st.button("Iniciar Aplicativo"):
        st.session_state.current_step = 2
        st.rerun()

# 2º: Selección de Área y Dirección/Gerencia
elif st.session_state.current_step == 2:
    st.header("Paso 1: Selección de Área y Dirección/Gerencia")

    # Primer campo desplegable: SELECCIONE AREA
    area_options = ["HOSPITALARIA", "PRIMARIA"]
    st.session_state.area_selected = st.selectbox(
        "**SELECCIONE ÁREA**",
        options=[""] + area_options,
        index=area_options.index(st.session_state.area_selected) + 1 if st.session_state.area_selected else 0,
        key="area_selector"
    )

    # Segundo campo desplegable: SELECCIONE DIRECCION / GERENCIA
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

    if st.button("Siguiente"):
        if st.session_state.area_selected and st.session_state.direccion_selected:
            st.session_state.current_step = 3
            st.session_state.confirm_selection = False # Reset confirmation for next step
            st.rerun()
        else:
            st.warning("Por favor, selecciona un Área y una Dirección/Gerencia para continuar.")

# 3º: Mensaje de confirmación
elif st.session_state.current_step == 3:
    st.header("Paso 2: Confirmación de Datos")
    # Modificación para colorear el texto
    st.markdown(f"**AREA :** <span style='color: #28a745;'>{st.session_state.area_selected}</span>", unsafe_allow_html=True) # Verde
    st.markdown(f"**DIRECCION/GERENCIA :** <span style='color: #007bff;'>{st.session_state.direccion_selected}</span>", unsafe_allow_html=True) # Azul
    st.markdown("**¿Desea confirmar estos datos?**")

    col_si, col_atras = st.columns(2)
    with col_si:
        if st.button("SI", key="confirm_si"):
            st.session_state.current_step = 5
            st.session_state.confirm_selection = True
            st.rerun()
    with col_atras:
        if st.button("ATRÁS", key="confirm_atras"):
            reset_selection_page()
            st.rerun()

# 4º: Volver al paso 2 (manejado por el botón "ATRÁS" en el paso 3)
# Este paso se maneja directamente cambiando st.session_state.current_step a 2.

# 5º: Zona de trabajo - Introducción de datos
elif st.session_state.current_step == 5:
    st.header("Paso 3: Introducción de Datos de Residentes")
    st.write(f"Dirección/Gerencia seleccionada: **{st.session_state.direccion_selected}**")

    especialidades_para_rellenar = ESPECIALIDADES_POR_DIRECCION.get(st.session_state.direccion_selected, [])

    if not especialidades_para_rellenar:
        st.warning("No se encontraron especialidades para la Dirección/Gerencia seleccionada. Por favor, vuelve al paso anterior.")
        if st.button("Volver al Paso 2"):
            reset_selection_page()
            st.rerun()
        st.stop()

    # Estructura para almacenar los datos
    # {'Especialidad': {'num_residentes': val, 'R1': [n1,n2,n3], 'R2': [n1,n2,n3], ...}}
    if 'data_input' not in st.session_state or st.session_state.data_input_direccion != st.session_state.direccion_selected:
        st.session_state.data_input = {
            esp: {'num_residentes': None, 'R1': [None, None, None], 'R2': [None, None, None],
                  'R3': [None, None, None], 'R4': [None, None, None], 'R5': [None, None, None]}
            for esp in especialidades_para_rellenar
        }
        st.session_state.data_input_direccion = st.session_state.direccion_selected


    st.markdown("### Rellene los campos a continuación para cada especialidad:")
    st.info("💡 **Importante:** Para las notas, si no va a rellenar las 3 notas más altas, deje los campos vacíos. No ponga '0', ya que afectaría a la media. Las notas deben estar entre 0 y 10, con hasta 2 decimales.")

    # Crear una tabla interactiva para la entrada de datos
    input_data_df = pd.DataFrame(
        {
            "Especialidad": especialidades_para_rellenar,
            "Nº Residentes Aptos": [st.session_state.data_input[esp]['num_residentes'] for esp in especialidades_para_rellenar],
            "R1 Nota 1": [st.session_state.data_input[esp]['R1'][0] for esp in especialidades_para_rellenar],
            "R1 Nota 2": [st.session_state.data_input[esp]['R1'][1] for esp in especialidades_para_rellenar],
            "R1 Nota 3": [st.session_state.data_input[esp]['R1'][2] for esp in especialidades_para_rellenar],
            "R2 Nota 1": [st.session_state.data_input[esp]['R2'][0] for esp in especialidades_para_rellenar],
            "R2 Nota 2": [st.session_state.data_input[esp]['R2'][1] for esp in especialidades_para_rellenar],
            "R2 Nota 3": [st.session_state.data_input[esp]['R2'][2] for esp in especialidades_para_rellenar],
            "R3 Nota 1": [st.session_state.data_input[esp]['R3'][0] for esp in especialidades_para_rellenar],
            "R3 Nota 2": [st.session_state.data_input[esp]['R3'][1] for esp in especialidades_para_rellenar],
            "R3 Nota 3": [st.session_state.data_input[esp]['R3'][2] for esp in especialidades_para_rellenar],
            "R4 Nota 1": [st.session_state.data_input[esp]['R4'][0] for esp in especialidades_para_rellenar],
            "R4 Nota 2": [st.session_state.data_input[esp]['R4'][1] for esp in especialidades_para_rellenar],
            "R4 Nota 3": [st.session_state.data_input[esp]['R4'][2] for esp in especialidades_para_rellenar],
            "R5 Nota 1": [st.session_state.data_input[esp]['R5'][0] for esp in especialidades_para_rellenar],
            "R5 Nota 2": [st.session_state.data_input[esp]['R5'][1] for esp in especialidades_para_rellenar],
            "R5 Nota 3": [st.session_state.data_input[esp]['R5'][2] for esp in especialidades_para_rellenar],
        }
    )

    edited_df = st.data_editor(
        input_data_df,
        column_config={
            "Especialidad": st.column_config.Column("Especialidad", disabled=True),
            "Nº Residentes Aptos": st.column_config.NumberColumn(
                "Nº Residentes Aptos en la Evaluación final de residencia",
                min_value=1,
                format="%d",
                help="Valor entero, positivo y obligatorio."
            ),
            "R1 Nota 1": st.column_config.NumberColumn("R1 Nota 1", min_value=0.0, max_value=10.0, format="%.2f"),
            "R1 Nota 2": st.column_config.NumberColumn("R1 Nota 2", min_value=0.0, max_value=10.0, format="%.2f"),
            "R1 Nota 3": st.column_config.NumberColumn("R1 Nota 3", min_value=0.0, max_value=10.0, format="%.2f"),
            "R2 Nota 1": st.column_config.NumberColumn("R2 Nota 1", min_value=0.0, max_value=10.0, format="%.2f"),
            "R2 Nota 2": st.column_config.NumberColumn("R2 Nota 2", min_value=0.0, max_value=10.0, format="%.2f"),
            "R2 Nota 3": st.column_config.NumberColumn("R2 Nota 3", min_value=0.0, max_value=10.0, format="%.2f"),
            "R3 Nota 1": st.column_config.NumberColumn("R3 Nota 1", min_value=0.0, max_value=10.0, format="%.2f"),
            "R3 Nota 2": st.column_config.NumberColumn("R3 Nota 2", min_value=0.0, max_value=10.0, format="%.2f"),
            "R3 Nota 3": st.column_config.NumberColumn("R3 Nota 3", min_value=0.0, max_value=10.0, format="%.2f"),
            "R4 Nota 1": st.column_config.NumberColumn("R4 Nota 1", min_value=0.0, max_value=10.0, format="%.2f"),
            "R4 Nota 2": st.column_config.NumberColumn("R4 Nota 2", min_value=0.0, max_value=10.0, format="%.2f"),
            "R4 Nota 3": st.column_config.NumberColumn("R4 Nota 3", min_value=0.0, max_value=10.0, format="%.2f"),
            "R5 Nota 1": st.column_config.NumberColumn("R5 Nota 1", min_value=0.0, max_value=10.0, format="%.2f"),
            "R5 Nota 2": st.column_config.NumberColumn("R5 Nota 2", min_value=0.0, max_value=10.0, format="%.2f"),
            "R5 Nota 3": st.column_config.NumberColumn("R5 Nota 3", min_value=0.0, max_value=10.0, format="%.2f"),
        },
        num_rows="dynamic",
        use_container_width=True
    )

    # Actualizar st.session_state.data_input con los valores editados
    for i, esp in enumerate(especialidades_para_rellenar):
        st.session_state.data_input[esp]['num_residentes'] = edited_df.iloc[i]["Nº Residentes Aptos"]
        st.session_state.data_input[esp]['R1'] = [edited_df.iloc[i]["R1 Nota 1"], edited_df.iloc[i]["R1 Nota 2"], edited_df.iloc[i]["R1 Nota 3"]]
        st.session_state.data_input[esp]['R2'] = [edited_df.iloc[i]["R2 Nota 1"], edited_df.iloc[i]["R2 Nota 2"], edited_df.iloc[i]["R2 Nota 3"]]
        st.session_state.data_input[esp]['R3'] = [edited_df.iloc[i]["R3 Nota 1"], edited_df.iloc[i]["R3 Nota 2"], edited_df.iloc[i]["R3 Nota 3"]]
        st.session_state.data_input[esp]['R4'] = [edited_df.iloc[i]["R4 Nota 1"], edited_df.iloc[i]["R4 Nota 2"], edited_df.iloc[i]["R4 Nota 3"]]
        st.session_state.data_input[esp]['R5'] = [edited_df.iloc[i]["R5 Nota 1"], edited_df.iloc[i]["R5 Nota 2"], edited_df.iloc[i]["R5 Nota 3"]]

    col_generate, col_back_step5 = st.columns(2)

    with col_generate:
        if st.button("GENERAR"):
            # Validación antes de generar
            validation_errors = []
            for esp, data in st.session_state.data_input.items():
                # Validar Nº Residentes Aptos
                if data['num_residentes'] is None or pd.isna(data['num_residentes']) or not isinstance(data['num_residentes'], (int, float)) or data['num_residentes'] <= 0:
                    validation_errors.append(f"En '{esp}', el 'Nº Residentes Aptos' debe ser un número entero positivo y no puede estar vacío.")

                # Validar notas (entre 0 y 10, hasta 2 decimales)
                for r_key in ['R1', 'R2', 'R3', 'R4', 'R5']:
                    for i, note in enumerate(data[r_key]):
                        # Only validate if the note is not None/NaN (i.e., if a value was entered)
                        if note is not None and pd.notna(note):
                            if not isinstance(note, (int, float)) or not (0 <= note <= 10):
                                validation_errors.append(f"En '{esp}', Nota {i+1} de {r_key}: El valor '{note}' no es válido. Las notas deben ser números entre 0 y 10.")

            if validation_errors:
                for error in validation_errors:
                    st.error(error)
                st.warning("Por favor, corrige los errores para poder generar el informe.")
            else:
                # Calcular medias y preparar DataFrame para Excel
                results = []
                n_residentes_data = [] # Data for the new sheet
                for esp, data in st.session_state.data_input.items():
                    row = {"Especialidad": esp}
                    for r_num in range(1, 6):
                        r_key = f"R{r_num}"
                        notes = data[r_key]
                        avg = calculate_average(notes)
                        row[f"Media {r_key}"] = f"{avg:.2f}" if avg is not None else "" # Formatear a 2 decimales

                    results.append(row)
                    n_residentes_data.append({"Especialidad": esp, "Nº Residentes Aptos": data['num_residentes']}) # Collect data for new sheet

                output_df = pd.DataFrame(results)

                # Renombrar columnas para el Excel final
                output_df.columns = ["Especialidad", "Media R1", "Media R2", "Media R3", "Media R4", "Media R5"]

                # Crear DataFrame para la nueva hoja "N_Residentes"
                n_residentes_df = pd.DataFrame(n_residentes_data)

                # Generar archivo Excel en memoria
                output = io.BytesIO()
                excel_sheet_name = CODIGOS_DIRECCION.get(st.session_state.direccion_selected, "Resultados")
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # Escribir la primera hoja (la original)
                    output_df.to_excel(writer, sheet_name=excel_sheet_name, index=False)
                    # Escribir la nueva hoja "N_Residentes"
                    n_residentes_df.to_excel(writer, sheet_name="N_Residentes", index=False)
                output.seek(0) # Rewind to the beginning of the stream

                st.session_state.excel_output = output
                st.session_state.excel_filename = f"Evaluacion_Notas_{excel_sheet_name}.xlsx"
                st.session_state.current_step = 6
                st.rerun()

    with col_back_step5:
        if st.button("ATRÁS", key="back_from_step5"):
            st.session_state.current_step = 3
            st.rerun()


# 6º: Descarga y mensaje de envío por correo
elif st.session_state.current_step == 6:
    st.header("Paso 4: Descarga del Informe")
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
    # Nuevo mensaje más prominente para el envío por correo
    st.warning("⚠️ **Recordatorio Importante:** Después de descargar el archivo Excel, debes enviarlo a **fse.scs** 📧.")
    st.info("💡 **Aclaración:** Streamlit no permite ventanas emergentes que bloqueen la aplicación para confirmaciones directas. Este mensaje es la forma más clara de recordarte la acción post-descarga.")


    if st.button("Volver al Inicio (nueva evaluación)"):
        st.session_state.clear() # Clear all session state to restart
        st.rerun()

# 7º: Botón de salir del aplicativo
# Este se podría integrar en el footer o en un botón de "Cerrar Sesión" si se quiere una funcionalidad de logout explícita.
# Por ahora, un simple "Salir" desde cualquier punto reinicia la sesión (cierra la "sesión" de Streamlit).
st.sidebar.markdown("---")
if st.sidebar.button("Salir del Aplicativo 🚪"):
    st.session_state.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("##### ℹ️ Información del Aplicativo")
st.sidebar.write("Versión: 1.0")
st.sidebar.write("Desarrollado para: F.S.E. – S.C.S.")
st.sidebar.write("Fecha: Julio 2025")