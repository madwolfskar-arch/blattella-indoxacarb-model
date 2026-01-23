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
    "Simulación ecológica del control poblacional con indoxacarb\n"
    "Desarrollado bajo criterios biológicos y de campo – ZODION Servicios Ambientales"
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
        return max(0.2, 1 - (T - 33) / 5)
    else:
        return 0.0


def factor_humedad(H):
    if H < 30:
        return 0.1
    elif 30 <= H <= 70:
        return 1.0
    else:
        return max(0.3, 1 - (H - 70) / 30)


# --------------------------------------------------
# SIMULACIÓN PRINCIPAL
# --------------------------------------------------

def simular_poblacion(
    dias,
    ninfas_inicial,
    adultos_inicial,
    temperatura,
    humedad,
    intensidad_tratamiento
):

    N = np.zeros(dias)
    A = np.zeros(dias)
    R = np.zeros(dias)

    N[0] = ninfas_inicial
    A[0] = adultos_inicial
    R[0] = 1.0  # recursos iniciales normalizados

    fT = factor_temperatura(temperatura)
    fH = factor_humedad(humedad)

    for t in range(dias - 1):

        poblacion_total = N[t] + A[t]
        if poblacion_total < 1:
            break

        # ------------------------------
        # REPRODUCCIÓN (limitada)
        # ------------------------------
        tasa_reproductiva_diaria = 0.002  # equivalente biológico estable
        ninfas_nuevas = (
            A[t]
            * tasa_reproductiva_diaria
            * fT
            * fH
            * R[t]
        )

        # ------------------------------
        # MORTALIDAD POR INDOXACARB
        # ------------------------------
        efecto_gregario = np.log(1 + poblacion_total)
        mortalidad_indox_ninfas = intensidad_tratamiento * 0.015 * efecto_gregario
        mortalidad_indox_adultos = intensidad_tratamiento * 0.010 * efecto_gregario

        # ------------------------------
        # MORTALIDAD NATURAL
        # ------------------------------
        mortalidad_nat_ninfas = 0.008
        mortalidad_nat_adultos = 0.005

        # ------------------------------
        # TRANSICIÓN NINFA → ADULTO
        # ------------------------------
        tasa_maduracion = 0.02
        nuevos_adultos = N[t] * tasa_maduracion

        # ------------------------------
        # ACTUALIZACIÓN POBLACIONAL
        # ------------------------------
        N[t + 1] = max(
            0,
            N[t]
            + ninfas_nuevas
            - (mortalidad_indox_ninfas + mortalidad_nat_ninfas) * N[t]
            - nuevos_adultos
        )

        A[t + 1] = max(
            0,
            A[t]
            + nuevos_adultos
            - (mortalidad_indox_adultos + mortalidad_nat_adultos) * A[t]
        )

        # ------------------------------
        # CONSUMO DE RECURSOS
        # ------------------------------
        consumo = 0.0000015 * A[t] + 0.0000008 * N[t]
        R[t + 1] = max(0, R[t] - consumo)

    return N, A, R


# --------------------------------------------------
# INTERFAZ STREAMLIT
# --------------------------------------------------

st.sidebar.header("🔧 Parámetros del escenario")

ninfas_inicial = st.sidebar.number_input(
    "Ninfas iniciales",
    min_value=0,
    max_value=1_000_000,
    value=500
)

adultos_inicial = st.sidebar.number_input(
    "Adultos iniciales",
    min_value=0,
    max_value=1_000_000,
    value=200
)

temperatura = st.sidebar.slider(
    "Temperatura (°C)",
    min_value=5,
    max_value=38,
    value=28
)

humedad = st.sidebar.slider(
    "Humedad relativa (%)",
    min_value=10,
    max_value=90,
    value=60
)

intensidad = st.sidebar.slider(
    "Intensidad del tratamiento (indoxacarb)",
    min_value=0.1,
    max_value=1.0,
    value=0.8
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

    N, A, R = simular_poblacion(
        dias,
        ninfas_inicial,
        adultos_inicial,
        temperatura,
        humedad,
        intensidad
    )

    t = np.arange(dias)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(t, N, label="Ninfas", linewidth=2)
    ax.plot(t, A, label="Adultos", linewidth=2)
    ax.set_xlabel("Días")
    ax.set_ylabel("Individuos")
    ax.set_title("Dinámica poblacional de Blattella germanica")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    if N[-1] + A[-1] < 1:
        st.success("✅ Control poblacional completo logrado")
    elif R[-1] < 0.1:
        st.warning("⚠️ Recursos agotados – riesgo bajo de recuperación")
    else:
        st.info("ℹ️ Población controlada pero aún activa")

