import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# CONFIGURACIÓN ZODION
# =========================================================
st.set_page_config(page_title="ZODION - Modelo Blattella Pro", layout="centered")

st.title("🪳 Modelo Biológico: *Blattella germanica*")
st.subheader("Simulación de Persistencia de Juveniles – ZODION")

# =========================================================
# BARRA LATERAL
# =========================================================
st.sidebar.header("⚙️ Parámetros de Campo")
temp = st.sidebar.slider("Temperatura promedio (°C)", 15, 40, 28)
hum = st.sidebar.slider("Humedad Relativa (%)", 20, 100, 60)
st.sidebar.divider()
n_ini = st.sidebar.number_input("Ninfas iniciales", min_value=10, value=500)
a_ini = st.sidebar.number_input("Adultos iniciales", min_value=10, value=200)
st.sidebar.divider()
# Aumentamos el impacto del tratamiento para que el % se mueva
trat = st.sidebar.select_slider("Intensidad de Tratamiento (Indoxacarb)", 
                               options=[0.1, 0.2, 0.4, 0.6, 0.8, 1.0], value=0.8)
dias_sim = st.sidebar.slider("Días de seguimiento", 30, 180, 120)

# =========================================================
# MOTOR DE SIMULACIÓN
# =========================================================
def ejecutar_modelo(dias, n_inicial, a_inicial, T, H, intensidad):
    N = np.zeros(dias)
    A = np.zeros(dias)
    banco_ootecas = np.zeros(dias + 100)
    
    N[0] = n_inicial
    A[0] = a_inicial
    
    # Factores ambientales (0.0 a 1.0)
    fT = 1.0 if 25 <= T <= 32 else max(0.2, 1 - abs(T - 28) / 15)
    fH = 1.0 if 50 <= H <= 80 else max(0.4, 1 - abs(H - 65) / 40)
    
    # Tiempo de eclosión (biología real)
    retraso = int(28 / (0.7 + 0.3 * fT))
    
    # Ootecas iniciales (la "herencia" de la plaga antes del servicio)
    for i in range(retraso):
        banco_ootecas[i] = (a_inicial * 0.4) * 30 # 40% hembras cargadas

    for t in range(dias - 1):
        # 1. Eclosión (Nuevas ninfas hoy)
        emergentes = banco_ootecas[t]

        # 2. Mortalidad por Indoxacarb (AJUSTADA)
        # Indoxacarb es potente: Adultos mueren 25% diario, ninfas 12% con intensidad 1.0
        m_adultos = intensidad * 0.25 * fT
        m_ninfas = intensidad * 0.12 * fT
        
        # 3. Natalidad (Nuevas ootecas puestas hoy)
        # Solo adultos que sobreviven al veneno pueden poner ootecas
        futura = t + retraso
        if futura < len(banco_ootecas):
            banco_ootecas[futura] += A[t] * (0.05 * fT * fH) * 30

        # 4. Maduración (Ninfas a adultos)
        maduracion = N[t] * (0.015 * fT)

        # 5. Evolución
        N[t+1] = max(0, N[t] + emergentes - (m_ninfas + 0.01) * N[t] - maduracion)
        A[t+1] = max(0, A[t] + maduracion - (m_adultos + 0.005) * A[t])
        
    return N, A

# =========================================================
# RESULTADOS
# =========================================================
if st.button("🚀 Iniciar Simulación Biológica"):
    n_res, a_res = ejecutar_modelo(dias_sim, n_ini, a_ini, temp, hum, trat)
    
    pob_ini = n_ini + a_ini
    pob_fin = n_res[-1] + a_res[-1]
    
    # Cálculo de éxito basado en la población máxima alcanzada vs final
    # (Para evitar el error de 0% si la plaga crece al principio por las ootecas)
    pob_maxima = max(pob_ini, np.max(n_res + a_res))
    exito = max(0, (1 - (pob_fin / pob_maxima)) * 100)

    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Población Final", f"{int(pob_fin)} ind.")
    # El delta muestra cuánto bajó respecto al máximo
    c2.metric("Éxito del Control", f"{exito:.1f}%", delta=f"{int(pob_maxima - pob_fin)} eliminados")
    c3.metric("Ninfas Activas", f"{int(n_res[-1])}")

    # Gráfica
    t = np.arange(dias_sim)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(t, n_res, label="Ninfas (Eclosión)", color="orange", lw=2)
    ax.plot(t, a_res, label="Adultos", color="green", lw=2)
    ax.fill_between(t, n_res + a_res, color="gray", alpha=0.1, label="Carga Total")
    ax.set_title(f"Análisis de Control ZODION - Éxito: {exito:.1f}%")
    ax.legend()
    st.pyplot(fig)

    if exito < 50:
        st.error("🚨 **Alerta:** La tasa de eclosión supera la velocidad del tratamiento.")
    elif exito < 90:
        st.warning("⚠️ **Control en proceso:** Se requiere persistencia del biocida.")
    else:
        st.success("✅ **Control Exitoso:** Población bajo umbral crítico.")

else:
    st.info("Configure parámetros y ejecute la simulación.")




