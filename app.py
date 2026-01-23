# =========================================================
# MODELO POBLACIONAL Blattella germanica – Indoxacarb
# Versión corregida, escalable y bio-realista
# ZODION Servicios Ambientales
# =========================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# CONFIGURACIÓN STREAMLIT
# =========================================================
st.set_page_config(
    page_title="Modelo Blattella germanica – Indoxacarb",
    layout="centered"
)

st.title("Modelo poblacional de Blattella germanica")
st.subheader("Control con indoxacarb – Enfoque bio-realista")
st.caption("Desarrollado por ZODION Servicios Ambientales")

# =========================================================
# FACTOR AMBIENTAL
# =========================================================
def environmental_factor(temp, humidity):
    temp_factor = max(0, 1 - abs(temp - 30) / 20)
    hum_factor = max(0, 1 - abs(humidity - 70) / 40)
    return temp_factor * hum_factor


# =========================================================
# MODELO POBLACIONAL CORREGIDO
# =========================================================
def simulate_population(
    days,
    initial_pop,
    temp,
    humidity,
    reinfestation_rate
):

    # --- Parámetros biológicos ---
    birth_rate = 0.04            # reproducción diaria efectiva
    natural_mortality = 0.01     # mortalidad natural
    exposure_rate = 0.05         # % máximo expuesto por día
    saturation_alpha = 0.75      # saturación del consumo

    stop_feed_delay = 2          # días (48h)
    lethal_delay = 4             # días (96h)

    env = environmental_factor(temp, humidity)

    # --- Compartimentos ---
    S = np.zeros(days)   # Susceptibles
    I1 = np.zeros(days)  # Intoxicados tempranos
    I2 = np.zeros(days)  # Intoxicados tardíos
    D = np.zeros(days)   # Muertos acumulados

    S[0] = initial_pop
    intox_history = np.zeros(days)

    for d in range(1, days):

        # ---- Saturación de ingestión ----
        max_exposed = exposure_rate * (S[d-1] ** saturation_alpha)
        new_intox = min(max_exposed, S[d-1])
        intox_history[d] = new_intox

        # ---- Reproducción ----
        births = S[d-1] * birth_rate * env

        # ---- Mortalidad natural ----
        natural_deaths = S[d-1] * natural_mortality

        # ---- Transiciones metabólicas ----
        to_I2 = intox_history[d - stop_feed_delay] if d >= stop_feed_delay else 0
        toxic_deaths = intox_history[d - lethal_delay] if d >= lethal_delay else 0

        # ---- Reinfestación condicionada ----
        if S[d-1] < 25:
            immigration = reinfestation_rate * S[d-1]
        else:
            immigration = 0

        # ---- Actualización ----
        S[d] = max(0, S[d-1] + births - new_intox - natural_deaths + immigration)
        I1[d] = max(0, I1[d-1] + new_intox - to_I2)
        I2[d] = max(0, I2[d-1] + to_I2 - toxic_deaths)
        D[d] = D[d-1] + toxic_deaths

    N_active = S + I1

    return N_active, S, I1, I2, D


# =========================================================
# INTERFAZ DE ENTRADA
# =========================================================
st.sidebar.header("Parámetros de simulación")

temp = st.sidebar.slider("Temperatura (°C)", 15, 40, 30)
humidity = st.sidebar.slider("Humedad relativa (%)", 30, 90, 70)
initial_pop = st.sidebar.number_input(
    "Población inicial (ind/m²)",
    min_value=1,
    max_value=1_000_000,
    value=500,
    step=100
)
reinfestation_rate = st.sidebar.slider(
    "Tasa de reinfestación",
    0.000, 0.01, 0.002,
    help="Activada solo cuando la población es crítica"
)
days = st.sidebar.slider("Días de simulación", 30, 180, 60)

run = st.sidebar.button("Ejecutar simulación")

# =========================================================
# EJECUCIÓN Y VISUALIZACIÓN
# =========================================================
if run:

    N, S, I1, I2, D = simulate_population(
        days,
        initial_pop,
        temp,
        humidity,
        reinfestation_rate
    )

    days_axis = np.arange(days)

    # --- Umbrales técnicos ---
    elimination_threshold = 5
    risk_threshold = 25

    # --- Gráfico ---
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.axhspan(
        risk_threshold, initial_pop,
        color="lightblue", alpha=0.3,
        label="Plaga activa"
    )
    ax.axhspan(
        elimination_threshold, risk_threshold,
        color="khaki", alpha=0.4,
        label="Riesgo de recuperación"
    )
    ax.axhspan(
        0, elimination_threshold,
        color="lightcoral", alpha=0.5,
        label="Colonia funcionalmente eliminada"
    )

    ax.plot(
        days_axis, N,
        color="navy", linewidth=3,
        label="Población funcional activa"
    )

    ax.set_xlabel("Días de tratamiento")
    ax.set_ylabel("Individuos activos / m²")
    ax.set_title("Dinámica poblacional bajo tratamiento con indoxacarb")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # --- Indicadores claros ---
    final_pop = int(N[-1])

    st.subheader("Resultados clave")

    st.write(f"**Población inicial:** {initial_pop} ind/m²")
    st.write(f"**Población activa final:** {final_pop} ind/m²")

    if final_pop < elimination_threshold:
        st.success("Colonia funcionalmente eliminada")
    elif final_pop < risk_threshold:
        st.warning("Control parcial – Riesgo de recuperación")
    else:
        st.error("Actividad activa – Tratamiento insuficiente")

    st.caption(
        "Criterios técnicos basados en biología reproductiva de Blattella germanica. "
        "Una sola hembra fértil puede reiniciar la infestación."
    )

