
import streamlit as st
import websocket
import json
import threading
import time

# Variáveis globais
ws = None
connected = False
running = False
loss_count = 0
profit = 0.0
loss_limit = 10
profit_limit = 10
martingale = True
factor = 1.65
initial_stake = 0.35
current_stake = initial_stake
ticks = []

# Função de análise 6em7Digit
def analyze_ticks_and_trade():
    global running, ws, current_stake, loss_count, profit
    if len(ticks) >= 8:
        últimos = ticks[-8:]
        abaixo_de_4 = [d for d in últimos if d < 4]
        if len(abaixo_de_4) >= 6:
            contract = {
                "buy": 1,
                "price": round(current_stake, 2),
                "parameters": {
                    "amount": round(current_stake, 2),
                    "basis": "stake",
                    "contract_type": "DIGITOVER",
                    "currency": "USD",
                    "duration": 1,
                    "duration_unit": "t",
                    "symbol": "R_10",
                    "barrier": "3"
                },
                "passthrough": {},
                "req_id": 1
            }
            ws.send(json.dumps(contract))

def on_message(wsapp, message):
    global connected, running, ticks, profit, loss_count, current_stake
    data = json.loads(message)
    if "msg_type" in data:
        if data["msg_type"] == "authorize":
            connected = True
        elif data["msg_type"] == "tick":
            digit = int(str(data["tick"]["quote"])[-1])
            ticks.append(digit)
            if len(ticks) > 100:
                ticks.pop(0)
            if running:
                analyze_ticks_and_trade()
        elif data["msg_type"] == "buy":
            st.session_state.log.append(f"🎯 Ordem enviada: Digit Over 3 com stake ${current_stake}")
        elif data["msg_type"] == "proposal_open_contract":
            if data["proposal_open_contract"]["is_sold"]:
                pnl = data["proposal_open_contract"]["profit"]
                profit += pnl
                if pnl > 0:
                    st.session_state.log.append(f"✅ Ganhou ${pnl:.2f}")
                    current_stake = initial_stake
                    loss_count = 0
                else:
                    st.session_state.log.append(f"❌ Perdeu ${abs(pnl):.2f}")
                    loss_count += 1
                    if martingale:
                        current_stake *= factor
                if profit >= profit_limit:
                    st.session_state.log.append("🏁 Limite de lucro atingido. Robô parado.")
                    stop_bot()
                elif abs(profit) >= loss_limit:
                    st.session_state.log.append("🛑 Limite de perda atingido. Robô parado.")
                    stop_bot()

def on_open(wsapp):
    wsapp.send(json.dumps({"authorize": st.session_state.token}))
    wsapp.send(json.dumps({"ticks": "R_10", "subscribe": 1}))

def on_close(wsapp, close_status_code, close_msg):
    global connected
    connected = False

def run_ws():
    global ws
    ws = websocket.WebSocketApp("wss://ws.derivws.com/websockets/v3",
                                on_message=on_message,
                                on_open=on_open,
                                on_close=on_close)
    ws.run_forever()

def start_bot():
    global running, current_stake, loss_count, profit
    running = True
    current_stake = initial_stake
    loss_count = 0
    profit = 0.0
    st.session_state.log.append("🤖 Robô iniciado")

def stop_bot():
    global running
    running = False
    st.session_state.log.append("⛔ Robô parado")

# Interface
st.title("🤖 Deriv Bot - Estratégia 6em7Digit")
st.markdown("Conecte-se com seu token Deriv para iniciar.")

if "log" not in st.session_state:
    st.session_state.log = []

st.session_state.token = st.text_input("🔑 Token da API Deriv", type="password")
if st.session_state.token:
    if not connected:
        threading.Thread(target=run_ws).start()
        time.sleep(2)
    st.success("✅ Conectado à Deriv" if connected else "❌ Não conectado")
    st.markdown("---")
    st.markdown("### 🎯 Estratégia ativa: 6em7Digit (Digit Over 3 com base nos últimos 8 ticks)")
    st.write(f"📈 Stake inicial: ${initial_stake} | 🎲 Martingale: {'Sim' if martingale else 'Não'}")
    st.write(f"💰 Limite de lucro: ${profit_limit} | 📉 Limite de perda: ${loss_limit}")
    if st.button("▶️ Iniciar Robô"):
        start_bot()
    if st.button("⏹ Parar Robô"):
        stop_bot()
    st.markdown("### 📊 Relatório ao vivo:")
    for log in st.session_state.log[-15:][::-1]:
        st.write(log)
else:
    st.warning("Insira seu token da API para iniciar.")
