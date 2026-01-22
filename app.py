import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# CONFIGURACIÓN DE PÁGINA
# =========================================================
st.set_page_config(
    page_title="Modelo Blattella germanica – Indoxacarb",
    layout="centered"
)

st.title("🪳 Modelo poblacional Blattella germanica – Indoxacarb")
st.caption("Aplicación científica interactiva · ZODION Servicios Ambientales")

st.markdown("""
Esta herramienta permite simular la dinámica poblacional de *Blattella germanica*
bajo tratamiento con **indoxacarb**, considerando parámetros ambientales y biológicos.
""")

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
    immigration
):

    # Parámetros biológicos
    birth_rate = 0.06
    natural_mortality = 0.01

    # Indoxacarb
    palatability = 0.95
    stop_feed_delay = 2   # días
    lethal_delay = 4      # días

    env = environmental_factor(temp, humidity)

    # Compartimentos
    S = np.zeros(days)
    I1 = np.zeros(days)
    I2 = np.zeros(days)
    D = np.zeros(days)

    S[0] = initial_pop
    intox_history = np.zeros(days)

    for d in range(1, days):

        # Ingestión
        new_intox = palatability * S[d-1]
        intox_history[d] = new_intox

        # Nacimientos (solo susceptibles)
        births = S[d-1] * birth_rate * env * (1 - palatability)

        # Mortalidad natural
        natural_deaths = S[d-1] * natural_mortality

        # Transiciones metabólicas
        to_I2 = intox_history[d - stop_feed_delay] if d >= stop_feed_delay else 0
        toxic_deaths = intox_history[d - lethal_delay] if d >= lethal_delay else 0

        # Actualización
        S[d] = max(0, S[d-1] + births - new_intox - natural_deaths + immigration)
        I1[d] = max(0, I1[d-1] + new_intox - to_I2)
        I2[d] = max(0, I2[d-1] + to_I2 - toxic_deaths)
        D[d] = D[d-1] + toxic_deaths

    # Población funcional activa
    N_active = S + I1

    return N_active, S, I1, I2, D

# =========================================================
# INTERFAZ DE PARÁMETROS
# =========================================================
st.sidebar.header("⚙️ Parámetros de simulación")

temp = st.sidebar.slider("Temperatura (°C)", 15, 40, 30)
humidity = st.sidebar.slider("Humedad relativa (%)", 30, 90, 70)
initial_pop = st.sidebar.slider("Población inicial (ind/m²)", 50, 1000, 500)
immigration = st.sidebar.slider("Inmigración diaria (individuos)", 0, 50, 10)
days = st.sidebar.slider("Días de simulación", 15, 120, 60)

run = st.sidebar.button("▶ Ejecutar simulación")

# =========================================================
# EJECUCIÓN Y VISUALIZACIÓN
# =========================================================
if run:

    N, S, I1, I2, D = simulate_population(
        days, initial_pop, temp, humidity, immigration
    )

    collapse_threshold = initial_pop * 0.05

    collapse_day = None
    for i in range(len(N) - 3):
        if all(N[i:i+3] <= collapse_threshold):
            collapse_day = i
            break

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.axhspan(
        collapse_threshold, initial_pop,
        color="lightblue", alpha=0.4,
        label="Plaga activa"
    )

    ax.axhspan(
        0, collapse_threshold,
        color="lightcoral", alpha=0.45,
        label="Colonia funcionalmente eliminada"
    )

    ax.plot(
        np.arange(days),
        N,
        color="navy",
        linewidth=3,
        label="Población funcional activa"
    )

    if collapse_day is not None:
        ax.axvline(collapse_day, color="black", linestyle="--", linewidth=2)
        ax.text(
            collapse_day + 1,
            initial_pop * 0.6,
            f"Colonia funcionalmente\neliminada\nDía {collapse_day}",
            fontsize=10,
            weight="bold"
        )

    ax.set_xlabel("Días de tratamiento")
    ax.set_ylabel("Individuos activos / m²")
    ax.set_title("Efectividad del control con indoxacarb")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    st.markdown("### 📊 Interpretación")
    st.markdown("""
- La **población funcional activa** representa individuos capaces de alimentarse y reproducirse.  
- La colonia se considera **funcionalmente eliminada** cuando cae por debajo del **5%**.
- El modelo integra **retardo metabólico**, **cese de alimentación** y **efecto secundario** del indoxacarb.
""")


