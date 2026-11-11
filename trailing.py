# trailing.py - HIGH SPEED Trailing for XAUUSD / JustMarkets
# Reads login from GitHub Secrets, YOU control with control.txt

import MetaTrader5 as mt5
import os
import time

TRAILING_START = 100
TRAILING_DISTANCE = 60

def connect():
    login = int(os.environ.get("MT5_LOGIN", "0"))
    password = os.environ.get("MT5_PASSWORD", "")
    server = os.environ.get("MT5_SERVER", "")
    if not mt5.initialize(login=login, password=password, server=server):
        print("MT5 login failed, retrying...")
        time.sleep(5)
        return False
    print("Connected to JustMarkets MT5!")
    return True

def check_control():
    # If control.txt says STOP, bot pauses
    try:
        if os.path.exists("control.txt"):
            return open("control.txt").read().strip().upper()
    except:
        pass
    return "RUN"

def do_trailing():
    positions = mt5.positions_get(symbol="XAUUSD")
    if not positions:
        return
    tick = mt5.symbol_info_tick("XAUUSD")
    if tick is None:
        return
    for pos in positions:
        price = tick.bid if pos.type == 0 else tick.ask
        point = mt5.symbol_info("XAUUSD").point
        if pos.type == 0: # BUY
            profit = (price - pos.price_open) / point
            if profit > TRAILING_START:
                new_sl = price - (TRAILING_DISTANCE * point)
                if new_sl > pos.sl:
                    mt5.order_send({"action": mt5.TRADE_ACTION_SLTP, "position": pos.ticket, "symbol": "XAUUSD", "sl": new_sl, "tp": pos.tp, "deviation": 10})
                    print(f"BUY Trail: {pos.sl} -> {new_sl}")
        if pos.type == 1: # SELL
            profit = (pos.price_open - price) / point
            if profit > TRAILING_START:
                new_sl = price + (TRAILING_DISTANCE * point)
                if new_sl < pos.sl or pos.sl == 0:
                    mt5.order_send({"action": mt5.TRADE_ACTION_SLTP, "position": pos.ticket, "symbol": "XAUUSD", "sl": new_sl, "tp": pos.tp, "deviation": 10})
                    print(f"SELL Trail: {pos.sl} -> {new_sl}")

if __name__ == "__main__":
    print("HIGH SPEED Trailing Started...")
    if not connect():
        print("Could not connect. Check Secrets.")
    else:
        while True:
            if check_control() == "STOP":
                print("Paused by YOU - control.txt = STOP")
                time.sleep(5)
                continue
            do_trailing()
            time.sleep(0.01)
