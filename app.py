import streamlit as st
import websocket
import threading
import json
import time
import winsound

st.set_page_config(page_title="Deriv Bot - Estratégia 6em7Digit", layout="centered")

# Variáveis globais de controle
tick_history = []
loss_streak = 0
profit = 0.0
loss = 0.0
running = False
ws = None

def play_sound(win=True):
    frequency = 1000 if win else 500
    duration = 400
    try:
        winsound.Beep(frequency, duration)
    except:
        pass  # winsound só funciona no Windows

def send_buy_contract(token, symbol, stake, contract_type):
    global ws
    if not ws: return
    data = {
        "buy": 1,
        "price": stake,
        "parameters": {
            "amount": stake,
            "basis": "stake",
            "contract_type": contract_type,
            "currency": "USD",
            "duration": 1,
            "duration_unit": "t",
            "symbol": symbol
        }
    }
    ws.send(json.dumps(data))

def on_message(wsapp, message):
    global tick_history, running, loss_streak, profit, loss
    data = json.loads(message)

    if 'tick' in data:
        tick = int(str(data['tick']['quote'])[-1])
        tick_history.append(tick)
        if len(tick_history) > selected_analysis:
            tick_history.pop(0)
        if running:
            analyze_and_trade()

    if 'buy' in data:
        st.session_state.log.append(f"🎯 Ordem enviada: ID {data['buy']['buy_id']}")

    if 'proposal_open_contract' in data:
        if data['proposal_open_contract']['is_sold']:
            result = data['proposal_open_contract']['profit']
            if result > 0:
                st.session_state.log.append("✅ Lucro: $" + str(round(result, 2)))
                profit += result
                loss_streak = 0
                play_sound(True)
            else:
                st.session_state.log.append("❌ Prejuízo: $" + str(round(result, 2)))
                loss += abs(result)
                loss_streak += 1
                play_sound(False)

def analyze_and_trade():
    global tick_history, ws, running, stake, loss_streak, profit, loss

    if len(tick_history) < 8: return
    small_digits = [d for d in tick_history[-8:] if d < 4]
    if len(small_digits) >= 6 and loss_streak < 4:
        send_buy_contract(token, symbol, stake, "DIGITOVER")
        st.session_state.log.append(f"📈 Entrada com DIGITOVER 3 (Stake: ${stake})")

def run_bot():
    global ws, running
    running = True
    ws = websocket.WebSocketApp(
        "wss://ws.derivws.com/websockets/v3",
        on_message=on_message
    )
    ws.on_open = lambda ws: ws.send(json.dumps({"authorize": token}))
    ws.run_forever()

def stop_bot():
    global ws, running
    running = False
    if ws:
        try:
            ws.close()
        except:
            pass

st.title("🤖 Deriv Bot - Estratégia 6em7Digit")

token = st.text_input("Token da Deriv", type="password")
symbol = st.selectbox("Símbolo", ["R_10", "R_25", "R_50", "R_75", "R_100"], index=0)
stake = st.number_input("Stake Inicial", value=0.35)
martingale = st.checkbox("Ativar Martingale", value=True)
factor = st.number_input("Fator Martingale", value=1.65)
profit_limit = st.number_input("Limite de Lucro ($)", value=10.0)
loss_limit = st.number_input("Limite de Perda ($)", value=10.0)
selected_analysis = st.selectbox("Analisar últimos dígitos", [10, 33, 50, 100], index=1)

if "log" not in st.session_state:
    st.session_state.log = []

col1, col2 = st.columns(2)

if col1.button("▶️ Iniciar Robô"):
    threading.Thread(target=run_bot).start()
    st.success("Robô iniciado!")

if col2.button("⏹ Parar Robô"):
    stop_bot()
    st.warning("Robô parado.")

st.subheader("📋 Registro de Operações")
for item in st.session_state.log[-20:]:
    st.write(item)

st.markdown("---")
st.caption("Desenvolvido com ❤️ para operar com WebSocket na Deriv.com")