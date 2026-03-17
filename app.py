import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# CONFIGURACIÓN Y ESTILO ZODION
# =========================================================
st.set_page_config(page_title="ZODION - Modelo Blattella Pro", layout="centered")

st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #1f77b4;
        color: white;
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
    }
    .main { background-color: #f9f9f9; }
    </style>
    """, unsafe_allow_html=True)

st.title("🪳 Modelo Biológico: *Blattella germanica*")
st.subheader("Simulación de Persistencia de Juveniles – ZODION")

# =========================================================
# FUNCIONES ECOLÓGICAS
# =========================================================
def factor_ambiental(T, H):
    # Temperatura óptima 28-30°C
    fT = 1.0 if 25 <= T <= 33 else max(0.1, 1 - abs(T - 30) / 15)
    # Humedad óptima 60-70%
    fH = 1.0 if 50 <= H <= 80 else max(0.2, 1 - abs(H - 65) / 35)
    return fT, fH

# =========================================================
# BARRA LATERAL (INPUTS)
# =========================================================
st.sidebar.header("⚙️ Parámetros de Campo")
temp = st.sidebar.slider("Temperatura promedio (°C)", 10, 45, 28)
hum = st.sidebar.slider("Humedad Relativa (%)", 20, 100, 60)
st.sidebar.divider()
n_ini = st.sidebar.number_input("Ninfas iniciales (estimadas)", value=500)
a_ini = st.sidebar.number_input("Adultos iniciales (estimados)", value=200)
trat = st.sidebar.select_slider("Intensidad de Tratamiento (Indoxacarb)", 
                               options=[0.1, 0.3, 0.5, 0.8, 1.0], value=0.8)
dias_sim = st.sidebar.slider("Días de seguimiento", 30, 180, 120)

# =========================================================
# MOTOR DE SIMULACIÓN (LÓGICA DE PERSISTENCIA)
# =========================================================
def ejecutar_modelo(dias, n_inicial, a_inicial, T, H, intensidad):
    N = np.zeros(dias)
    A = np.zeros(dias)
    banco_ootecas = np.zeros(dias + 60)
    
    N[0] = n_inicial
    A[0] = a_inicial
    
    fT, fH = factor_ambiental(T, H)
    
    # El calor acelera la eclosión (biología real)
    retraso_eclosion = int(28 / (0.6 + 0.4 * fT))
    
    # Carga inicial de ootecas ya presentes en el sitio
    for i in range(retraso_eclosion):
        banco_ootecas[i] = (a_inicial * 0.25) * 35 # 25% hembras con ooteca

    for t in range(dias - 1):
        # 1. Nuevas Ootecas (Puestas por adultos vivos)
        futura_eclosion = t + retraso_eclosion
        if futura_eclosion < len(banco_ootecas):
            banco_ootecas[futura_eclosion] += A[t] * (0.12 * fT * fH) * 35

        # 2. Eclosión (Ninfas nuevas hoy)
        emergentes = banco_ootecas[t]

        # 3. Mortalidad (Diferenciada según tu observación)
        # Adultos mueren más rápido. Juveniles resisten por refugio/coprofagia.
        m_adultos = intensidad * 0.12 * fT
        m_ninfas = intensidad * 0.04 * fT # Tasa menor para ninfas

        # 4. Maduración (Ninfas pasan a Adultos)
        maduracion = N[t] * (0.02 * fT)

        # 5. Evolución poblacional
        N[t+1] = max(0, N[t] + emergentes - (m_ninfas + 0.01) * N[t] - maduracion)
        A[t+1] = max(0, A[t] + maduracion - (m_adultos + 0.005) * A[t])
        
    return N, A

# =========================================================
# RESULTADOS
# =========================================================
if st.button("🚀 Iniciar Simulación Biológica"):
    N, A = ejecutar_modelo(dias_sim, n_ini, a_ini, temp, hum, trat)
    t_axis = np.arange(dias_sim)

    # Gráfica Profesional
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.fill_between(t_axis, N, color="orange", alpha=0.2, label="Área de Juveniles")
    ax.plot(t_axis, N, color="darkorange", linewidth=2.5, label="Ninfas (Reposición)")
    ax.plot(t_axis, A, color="green", linewidth=2, label="Adultos")
    
    ax.set_title(f"Dinámica Poblacional - ZODION\n(Persistencia detectada a {temp}°C)")
    ax.set_xlabel("Días post-tratamiento")
    ax.set_ylabel("Cantidad de individuos")
    ax.legend()
    ax.grid(True, alpha=0.2)
    st.pyplot(fig)

    # Alerta Técnica
    if N[-1] > (n_ini * 0.1):
        st.warning(f"⚠️ **Observación Técnica:** A los {dias_sim} días persiste un {int((N[-1]/n_ini)*100)}% de juveniles. Esto coincide con la reposición por eclosión de ootecas protegidas.")
    else:
        st.success("✅ Control proyectado exitoso bajo estas condiciones.")
    
    st.info("💡 **Nota de ZODION:** El Indoxacarb elimina eficazmente adultos, pero la eclosión de ninfas requiere monitoreo continuo hasta agotar el banco de ootecas.")
