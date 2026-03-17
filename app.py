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

# Estilo personalizado para botones y tarjetas de métricas
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

st.info("Este modelo simula la eclosión de ootecas protegidas, explicando por qué la actividad de ninfas persiste tras el tratamiento inicial.")

# =========================================================
# FUNCIONES ECOLÓGICAS (Lógica Biológica)
# =========================================================
def factor_ambiental(T, H):
    # La temperatura afecta la velocidad del metabolismo y desarrollo
    fT = 1.0 if 25 <= T <= 33 else max(0.1, 1 - abs(T - 30) / 15)
    # La humedad afecta la viabilidad de las ootecas y ninfas
    fH = 1.0 if 50 <= H <= 80 else max(0.2, 1 - abs(H - 65) / 35)
    return fT, fH

# =========================================================
# BARRA LATERAL (INPUTS)
# =========================================================
st.sidebar.header("⚙️ Parámetros de Campo")
temp = st.sidebar.slider("Temperatura promedio (°C)", 10, 45, 28)
hum = st.sidebar.slider("Humedad Relativa (%)", 20, 100, 60)
st.sidebar.divider()
n_ini = st.sidebar.number_input("Ninfas iniciales estimadas", min_value=0, value=500)
a_ini = st.sidebar.number_input("Adultos iniciales estimados", min_value=0, value=200)
st.sidebar.divider()
trat = st.sidebar.select_slider("Intensidad de Tratamiento (Indoxacarb)", 
                               options=[0.1, 0.3, 0.5, 0.8, 1.0], value=0.8)
dias_sim = st.sidebar.slider("Días de seguimiento", 30, 180, 120)

# =========================================================
# MOTOR DE SIMULACIÓN (Persistencia y Ootecas)
# =========================================================
def ejecutar_modelo(dias, n_inicial, a_inicial, T, H, intensidad):
    N = np.zeros(dias)
    A = np.zeros(dias)
    # El banco de ootecas representa ninfas que nacerán en el futuro (protegidas del cebo)
    banco_ootecas = np.zeros(dias + 60)
    
    N[0] = n_inicial
    A[0] = a_inicial
    fT, fH = factor_ambiental(T, H)
    
    # El calor acelera la eclosión: a 30°C tardan ~28 días; a 20°C tardan ~45 días.
    retraso_eclosion = int(28 / (0.6 + 0.4 * fT))
    
    # Carga inicial de ootecas ya depositadas en el ambiente antes de llegar nosotros
    for i in range(retraso_eclosion):
        banco_ootecas[i] = (a_inicial * 0.25) * 35 

    for t in range(dias - 1):
        # 1. Producción de nuevas ootecas por adultos que aún no han muerto
        futura_eclosion = t + retraso_eclosion
        if futura_eclosion < len(banco_ootecas):
            banco_ootecas[futura_eclosion] += A[t] * (0.12 * fT * fH) * 35

        # 2. Eclosión diaria (Ninfas que "aparecen" hoy del banco protegido)
        emergentes = banco_ootecas[t]

        # 3. Tasas de mortalidad (Indoxacarb)
        # Los adultos consumen más cebo. Las ninfas recién nacidas tienen refugio/coprofagia.
        m_adultos = intensidad * 0.12 * fT
        m_ninfas = intensidad * 0.04 * fT 
        
        # 4. Maduración (Ninfas pasan a fase adulta)
        maduracion = N[t] * (0.02 * fT)

        # 5. Evolución de las poblaciones
        N[t+1] = max(0, N[t] + emergentes - (m_ninfas + 0.01) * N[t] - maduracion)
        A[t+1] = max(0, A[t] + maduracion - (m_adultos + 0.005) * A[t])
        
    return N, A

# =========================================================
# RENDERIZADO DE RESULTADOS
# =========================================================
if st.button("🚀 Iniciar Simulación Biológica"):
    N, A = ejecutar_modelo(dias_sim, n_ini, a_ini, temp, hum, trat)
    t_axis = np.arange(dias_sim)

    # Cálculos de Éxito (%)
    pob_inicial = n_ini + a_ini
    pob_final = N[-1] + A[-1]
    porcentaje_exito = max(0, (1 - (pob_final / pob_inicial)) * 100)

    # Bloque de Métricas Superiores
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Población Final", f"{int(pob_final)} ind.")
    m2.metric("Éxito del Tratamiento", f"{porcentaje_exito:.1f}%", delta=f"{porcentaje_exito:.1f}%")
    m3.metric("Ninfas Residuales", f"{int(N[-1])} ind.")

    # Generación de la Gráfica
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.fill_between(t_axis, N, color="orange", alpha=0.15, label="Carga de Juveniles")
    ax.plot(t_axis, N, color="darkorange", linewidth=2.5, label="Ninfas (Reposición)")
    ax.plot(t_axis, A, color="green", linewidth=2, label="Adultos")
    
    ax.set_title(f"Efectividad Proyectada: {porcentaje_exito:.1f}%", fontsize=14, fontweight='bold')
    ax.set_xlabel("Días post-tratamiento")
    ax.set_ylabel("Individuos activos")
    ax.legend(loc='upper right')
    ax.grid(True, linestyle='--', alpha=0.3)
    
    st.pyplot(fig)

    # Interpretación Técnica para el Cliente
    if porcentaje_exito > 95:
        st.success(f"✅ **Control Exitoso:** Se ha reducido la población en un {porcentaje_exito:.1f}%. La colonia está funcionalmente colapsada.")
    else:
        st.warning(f"⚠️ **Actividad Residual:** La reducción es del {porcentaje_exito:.1f}%. Se detecta persistencia de juveniles debido a la eclosión escalonada de ootecas.")
    
    st.write("---")
    st.caption("© ZODION Servicios Ambientales - Simulación basada en dinámicas de eclosión y metabolismo dependiente de temperatura.")

else:
    st.write("### ⬅️ Configure los parámetros y presione el botón para simular.")





