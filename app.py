import streamlit as st
import websocket
import json
import threading

st.set_page_config(page_title="Deriv Bot GPT", layout="centered")

st.title("🤖 Deriv Bot - WebSocket")
token = st.text_input("Token da Deriv", type="password")
symbol = st.selectbox("Símbolo", ["R_10", "R_25", "R_50", "R_75", "R_100"], index=0)
stake = st.number_input("Stake Inicial", value=0.35)
martingale = st.checkbox("Ativar Martingale", value=True)
factor = st.number_input("Fator Martingale", value=1.65)
profit_limit = st.number_input("Limite de Lucro", value=10.0)
loss_limit = st.number_input("Limite de Perda", value=10.0)
analysis_ticks = st.selectbox("Análise dos últimos ticks", [10, 33, 50, 100], index=1)

if st.button("Iniciar Robô"):
    st.success("Robô iniciado (simulação).")