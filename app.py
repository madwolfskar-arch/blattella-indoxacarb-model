import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# CONFIGURACIÓN Y ESTILO ZODION
# =========================================================
st.set_page_config(
    page_title="ZODION - Modelo Blattella Pro", 
    layout="centered",
    page_icon="🪳"
)

st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #1f77b4;
        color: white;
        border-radius: 10px;
        font-weight: bold;
        height: 3em;
        width: 100%;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #efefef;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🪳 Modelo Biológico: *Blattella germanica*")
st.subheader("Simulación de Persistencia de Juveniles – ZODION")

# =========================================================
# FUNCIONES ECOLÓGICAS
# =========================================================
def factor_ambiental(T, H):
    fT = 1.0 if 25 <= T <= 33 else max(0.1, 1 - abs(T - 30) / 15)
    fH = 1.0 if 50 <= H <= 80 else max(0.2, 1 - abs(H - 65) / 35)
    return fT, fH

# =========================================================
# BARRA LATERAL (INPUTS)
# =========================================================
st.sidebar.header("⚙️ Parámetros de Campo")
temp = st.sidebar.slider("Temperatura promedio (°C)", 10, 45, 28)
hum = st.sidebar.slider("Humedad Relativa (%)", 20, 100, 60)
st.sidebar.divider()
n_ini = st.sidebar.number_input("Ninfas iniciales estimadas", min_value=1, value=500)
a_ini = st.sidebar.number_input("Adultos iniciales estimados", min_value=1, value=200)
st.sidebar.divider()
trat = st.sidebar.select_slider("Intensidad de Tratamiento (Indoxacarb)", 
                               options=[0.1, 0.3, 0.5, 0.8, 1.0], value=0.8)
dias_sim = st.sidebar.slider("Días de seguimiento", 30, 180, 120)

# =========================================================
# MOTOR DE SIMULACIÓN
# =========================================================
def ejecutar_modelo(dias, n_inicial, a_inicial, T, H, intensidad):
    N = np.zeros(dias)
    A = np.zeros(dias)
    banco_ootecas = np.zeros(dias + 60)
    
    N[0] = n_inicial
    A[0] = a_inicial
    fT, fH = factor_ambiental(T, H)
    
    # El calor acelera la eclosión
    retraso_eclosion = int(28 / (0.6 + 0.4 * fT))
    
    # Carga inicial de ootecas
    for i in range(retraso_eclosion):
        banco_ootecas[i] = (a_inicial * 0.25) * 35 

    for t in range(dias - 1):
        futura_eclosion = t + retraso_eclosion
        if futura_eclosion < len(banco_ootecas):
            banco_ootecas[futura_eclosion] += A[t] * (0.12 * fT * fH) * 35

        emergentes = banco_ootecas[t]
        # AJUSTE DE MORTALIDAD: Ahora el tratamiento SI afecta el éxito
        m_adultos = intensidad * 0.15 * fT
        m_ninfas = intensidad * 0.05 * fT 
        
        maduracion = N[t] * (0.02 * fT)

        N[t+1] = max(0, N[t] + emergentes - (m_ninfas + 0.01) * N[t] - maduracion)
        A[t+1] = max(0, A[t] + maduracion - (m_adultos + 0.005) * A[t])
        
    return N, A

# =========================================================
# RENDERIZADO DE RESULTADOS
# =========================================================
if st.button("🚀 Iniciar Simulación Biológica"):
    # Ejecutamos el modelo
    n_resultado, a_resultado = ejecutar_modelo(dias_sim, n_ini, a_ini, temp, hum, trat)
    t_axis = np.arange(dias_sim)

    # CÁLCULO CRÍTICO DEL ÉXITO
    pob_inicial_total = n_ini + a_ini
    pob_final_total = n_resultado[-1] + a_resultado[-1]
    
    # Cálculo corregido: (Inicial - Final) / Inicial * 100
    reduccion = pob_inicial_total - pob_final_total
    porcentaje_exito = (reduccion / pob_inicial_total) * 100
    
    # Asegurar que el éxito no sea negativo si la población crece
    porcentaje_exito = max(0, porcentaje_exito)

    # Bloque de Métricas
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Población Final", f"{int(pob_final_total)} ind.")
    m2.metric("Éxito del Tratamiento", f"{porcentaje_exito:.1f}%")
    m3.metric("Ninfas Residuales", f"{int(n_resultado[-1])} ind.")

    # Gráfica
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.fill_between(t_axis, n_resultado, color="orange", alpha=0.15, label="Carga de Juveniles")
    ax.plot(t_axis, n_resultado, color="darkorange", linewidth=2.5, label="Ninfas (Reposición)")
    ax.plot(t_axis, a_resultado, color="green", linewidth=2, label="Adultos")
    
    ax.set_title(f"Efectividad Proyectada: {porcentaje_exito:.1f}%", fontsize=14, fontweight='bold')
    ax.set_xlabel("Días post-tratamiento")
    ax.set_ylabel("Individuos activos")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.3)
    
    st.pyplot(fig)

    # Alertas
    if porcentaje_exito > 90:
        st.success(f"✅ **Control Efectivo:** Reducción del {porcentaje_exito:.1f}%.")
    else:
        st.warning(f"⚠️ **Control Parcial:** Éxito del {porcentaje_exito:.1f}%. Persistencia por ootecas.")

else:
    st.info("### ⬅️ Configure los parámetros y presione el botón.")




