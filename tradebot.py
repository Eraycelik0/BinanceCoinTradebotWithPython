import websocket, json, pprint, talib, numpy
from binance.client import Client
from binance.enums import *

API_KEY = 'yourbinanceApikey'
API_SCRIPT = 'yourbinancescript'

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANTITY = 0.01

closes = []
in_position = False

def binance_order(symbol, side, quantity, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending binance order")
        order = Client.create_order(symbol=symbol, side=side, quantity=quantity, type=order_type)
        print(order)
    except Exception as e:
        print("an exception - {}".format(e))
        return False

def check_sell_or_buy(last_rsi):
    global in_position
    
    if last_rsi > RSI_OVERBOUGHT:
        if in_position:
            print("overbought! SELL!")
            order_statu = binance_order(TRADE_SYMBOL, SIDE_SELL, TRADE_QUANTITY)
            if order_statu:
                in_position = False
        else:
            print("it is overbought we don't have any")
    if last_rsi < RSI_OVERSOLD:
        if  in_position:
            print("it is oversold but we already have it")
        else:
            print("oversold! BUY!")
            order_statu = binance_order(TRADE_SYMBOL, SIDE_BUY, TRADE_QUANTITY)
            if order_statu:
                in_position = True

def on_open(ws):
    print("Opened connection")

def on_close(ws):
    print("Closed connection")

def on_message(ws, message):
    print("received message")
    json_message = json.loads(message)
    #pprint.pprint(json_message)
    candle = json_message['k']
    close = candle['c']
    is_candle_closed = candle['x']
    if is_candle_closed:
        print("candle closed at: ", close)
        closes.append(float(close))
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all RSIs calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print("the current rsi value is ", last_rsi)
            check_sell_or_buy(last_rsi)


ws = websocket.WebSocketApp(SOCKET, on_open = on_open, on_close = on_close, on_message = on_message)
ws.run_forever()