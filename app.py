import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------
# CONFIGURACIÓN GENERAL
# --------------------------------------------------
st.set_page_config(
    page_title="Modelo poblacional Blattella germanica – Indoxacarb",
    layout="wide"
)

st.title("🪳 Modelo poblacional de Blattella germanica")
st.caption(
    "Modelo ecológico aplicado al control poblacional con indoxacarb\n"
    "Basado en biología, ecología y experiencia de campo – ZODION Servicios Ambientales"
)

# --------------------------------------------------
# FUNCIONES ECOLÓGICAS
# --------------------------------------------------

def factor_temperatura(T):
    if T < 10:
        return 0.0
    elif 10 <= T < 25:
        return (T - 10) / 15
    elif 25 <= T <= 33:
        return 1.0
    elif 33 < T <= 38:
        return max(0.3, 1 - (T - 33) / 6)
    else:
        return 0.0


def factor_humedad(H):
    if H < 30:
        return 0.2
    elif 30 <= H <= 70:
        return 1.0
    else:
        return max(0.4, 1 - (H - 70) / 40)


def fraccion_accesible(poblacion):
    """
    Límite biológico: fracción máxima diaria de individuos
    que pueden entrar en contacto efectivo con el tratamiento
    """
    if poblacion < 50:
        return 0.30
    elif poblacion < 500:
        return 0.18
    elif poblacion < 2000:
        return 0.10
    elif poblacion < 5000:
        return 0.05
    else:
        return 0.03


def factor_proinsecticida(dia):
    """
    Indoxacarb: activación metabólica progresiva
    """
    if dia < 5:
        return 0.15
    elif 5 <= dia < 15:
        return 0.15 + (dia - 5) * 0.05
    else:
        return 0.65


# --------------------------------------------------
# SIMULACIÓN PRINCIPAL
# --------------------------------------------------

def simular_poblacion(
    dias,
    poblacion_inicial,
    temperatura,
    humedad,
    intensidad_tratamiento
):

    P = np.zeros(dias)
    R = np.zeros(dias)

    P[0] = poblacion_inicial
    R[0] = 1.0

    fT = factor_temperatura(temperatura)
    fH = factor_humedad(humedad)

    for t in range(dias - 1):

        if P[t] < 1:
            P[t + 1] = 0
            continue

        # ------------------------------
        # REPRODUCCIÓN LIMITADA
        # ------------------------------
        tasa_reproductiva = 0.0015 * fT * fH * R[t]
        nuevos = P[t] * tasa_reproductiva

        # ------------------------------
        # MORTALIDAD POR INDOXACARB
        # ------------------------------
        Fa = fraccion_accesible(P[t])
        efecto_metabolico = factor_proinsecticida(t)

        mortalidad_indox = (
            P[t]
            * Fa
            * intensidad_tratamiento
            * efecto_metabolico
        )

        # ------------------------------
        # MORTALIDAD NATURAL
        # ------------------------------
        mortalidad_natural = 0.004 * P[t]

        # ------------------------------
        # ACTUALIZACIÓN
        # ------------------------------
        P[t + 1] = max(
            0,
            P[t] + nuevos - mortalidad_indox - mortalidad_natural
        )

        # ------------------------------
        # CONSUMO DE RECURSOS
        # ------------------------------
        consumo = 0.0000012 * P[t]
        R[t + 1] = max(0.2, R[t] - consumo)

    return P


# --------------------------------------------------
# INTERFAZ STREAMLIT
# --------------------------------------------------

st.sidebar.header("🔧 Parámetros del escenario")

poblacion_inicial = st.sidebar.number_input(
    "Población inicial estimada (individuos)",
    min_value=5,
    max_value=5000,
    value=500
)

temperatura = st.sidebar.slider(
    "Temperatura (°C)",
    min_value=5,
    max_value=38,
    value=28
)

humedad = st.sidebar.slider(
    "Humedad relativa (%)",
    min_value=20,
    max_value=90,
    value=60
)

intensidad = st.sidebar.slider(
    "Intensidad del tratamiento (indoxacarb)",
    min_value=0.10,
    max_value=0.85,
    value=0.60
)

dias = st.sidebar.slider(
    "Duración del tratamiento (días)",
    min_value=30,
    max_value=240,
    value=120
)

# --------------------------------------------------
# EJECUCIÓN
# --------------------------------------------------

if st.sidebar.button("▶ Ejecutar simulación"):

    P = simular_poblacion(
        dias,
        poblacion_inicial,
        temperatura,
        humedad,
        intensidad
    )

    t = np.arange(dias)

    # ------------------------------
    # GRÁFICA INTEGRADA
    # ------------------------------
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(t, P, linewidth=3, color="darkred")
    ax.set_xlabel("Días")
    ax.set_ylabel("Individuos")
    ax.set_title("📉 Respuesta poblacional integrada al tratamiento")
    ax.grid(True)

    st.pyplot(fig)

    # ------------------------------
    # EVALUACIÓN CUANTITATIVA
    # ------------------------------
    eliminacion = (1 - P[-1] / poblacion_inicial) * 100

    st.subheader("📊 Evaluación del tratamiento")

    st.metric(
        "Eliminación poblacional alcanzada",
        f"{eliminacion:.2f} %"
    )

    if eliminacion >= 99:
        st.success("✅ Eliminación poblacional efectiva – descontaminación lograda")
    elif eliminacion >= 95:
        st.success("🟢 Control avanzado – colapso poblacional")
    elif eliminacion >= 80:
        st.warning("🟡 Control funcional – población residual activa")
    elif eliminacion >= 50:
        st.warning("🟠 Reducción significativa – tratamiento en fase madura")
    else:
        st.error("🔴 Presión insuficiente – tratamiento en fase temprana")


