# =========================================================
# APP STREAMLIT — MODELO Blattella germanica + Indoxacarb
# ZODION Servicios Ambientales
# =========================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(
    page_title="Modelo Blattella germanica – Indoxacarb",
    layout="centered"
)

st.title("🪳 Modelo poblacional de *Blattella germanica*")
st.subheader("Control con indoxacarb – ZODION Servicios Ambientales")

st.markdown(
    """
    Esta aplicación simula la **dinámica poblacional funcional** de *Blattella germanica* bajo tratamiento con indoxacarb, 
    considerando condiciones ambientales e inmigración diaria.
    """
)

# =========================================================
# FACTOR AMBIENTAL (Función Biológica)
# =========================================================
def environmental_factor(temp, humidity):
    # La temperatura óptima es 30°C, la humedad óptima 70%
    temp_factor = max(0, 1 - abs(temp - 30) / 20)
    hum_factor = max(0, 1 - abs(humidity - 70) / 40)
    return temp_factor * hum_factor

# =========================================================
# MODELO POBLACIONAL (Motor de cálculo)
# =========================================================
def simulate_population(days, initial_pop, temp, humidity, immigration):
    birth_rate = 0.06
    natural_mortality = 0.01
    palatability = 0.95
    stop_feed_delay = 2
    lethal_delay = 4

    env = environmental_factor(temp, humidity)

    S = np.zeros(days)
    I1 = np.zeros(days)
    I2 = np.zeros(days)
    D = np.zeros(days)

    S[0] = initial_pop
    intox_history = np.zeros(days)

    for d in range(1, days):
        new_intox = palatability * S[d-1]
        intox_history[d] = new_intox

        births = S[d-1] * birth_rate * env * (1 - palatability)
        natural_deaths = S[d-1] * natural_mortality

        to_I2 = intox_history[d - stop_feed_delay] if d >= stop_feed_delay else 0
        toxic_deaths = intox_history[d - lethal_delay] if d >= lethal_delay else 0

        S[d] = max(0, S[d-1] + births - new_intox - natural_deaths + immigration)
        I1[d] = max(0, I1[d-1] + new_intox - to_I2)
        I2[d] = max(0, I2[d-1] + to_I2 - toxic_deaths)
        D[d] = D[d-1] + toxic_deaths

    N_active = S + I1
    return N_active

# =========================================================
# BARRA LATERAL — PARÁMETROS
# =========================================================
st.sidebar.header("⚙️ Parámetros de simulación")

temp = st.sidebar.slider("Temperatura (°C)", 10, 45, 30)
humidity = st.sidebar.slider("Humedad relativa (%)", 20, 100, 70)
initial_pop = st.sidebar.number_input(
    "Población inicial (ind/m²)", min_value=10, value=500
)
immigration = st.sidebar.number_input(
    "Inmigración diaria (ind)", min_value=0, value=10
)
days = st.sidebar.slider("Días de simulación", 10, 180, 60)

# =========================================================
# CUERPO PRINCIPAL — BOTÓN Y RESULTADOS
# =========================================================
st.divider()
run = st.button("🚀 Iniciar Simulación", use_container_width=True)

if run:
    with st.spinner('Calculando dinámica poblacional...'):
        N = simulate_population(
            days, 
            initial_pop, 
            temp, 
            humidity, 
            immigration
        )

        collapse_threshold = initial_pop * 0.05
        days_axis = np.arange(days)

        st.success("Simulación completada ✅")

        # --- GRÁFICA ---
        fig, ax = plt.subplots(figsize=(10, 5))
        
        ax.axhspan(
            0, collapse_threshold, 
            facecolor="lightcoral", alpha=0.3, 
            label="Colonia eliminada (<5%)"
        )
        
        ax.plot(
            days_axis, N, 
            linewidth=3, color="#1f77b4", 
            label="Población funcional activa"
        )

        ax.set_xlabel("Días de tratamiento")
        ax.set_ylabel("Individuos activos / m²")
        ax.set_title("Efectividad del control con Indoxacarb")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)

        st.pyplot(fig)

        # --- INTERPRETACIÓN ---
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Población Final", f"{int(N[-1])} ind/m²")
        with col2:
            efectividad = ((initial_pop - N[-1]) / initial_pop) * 100
            st.metric("Reducción Estimada", f"{efectividad:.1f}%")

        st.info(f"**Criterio técnico:** Se considera riesgo potencial de recuperación y propagación poblacional cuando la población desciende de {int(collapse_threshold)} ind/m².")

else:
    st.info("💡 Ajusta los valores en el panel izquierdo y presiona el botón para ver la proyección.")
    

