import pyautogui
from mt4_locater import mt4
import time
import sys

loc =  mt4()


def pair_loc(symbol):
    return {
        'EURUSD': loc.eurusd,
        'AUDUSD': loc.audusd,
        'GBPUSD': loc.gbpusd,
        'NZDUSD': loc.nzdusd,
        'USDJPY': loc.usdjpy,
        'USDCAD': loc.usdcad,
        'EURJPY': loc.eurjpy,
        'GBPJPY': loc.gbpjpy

    }[symbol]

def new_order_mm(symbol):

    sc = pair_loc(symbol)
    pyautogui.rightClick(sc['x'],sc['y'])
    pyautogui.leftClick(sc['x']+38, sc['y']+15)


def place_buy_order_mm(symbol, volume="1", comment="test123"):
    new_order_mm(symbol)
    change_volume(volume)
    write_comment(comment)
    market_buy()
    order_ok()


def place_sell_order_mm(symbol, volume="1", comment="test123"):
    new_order_mm(symbol)
    change_volume(volume)
    write_comment(comment)
    market_sell()
    order_ok()

def new_order():
    pyautogui.leftClick(loc.NEW_ORDER['x'], loc.NEW_ORDER['y'])
    
def change_volume(volume="1.0"):
    pyautogui.leftClick(loc.VOLUME['x'], loc.VOLUME['y'])
    pyautogui.write(volume)
    
def market_buy():
    pyautogui.leftClick(loc.MARKET_BUY['x'], loc.MARKET_BUY['y'], 0.25)
    
def market_sell():
    pyautogui.leftClick(loc.MARKET_SELL['x'], loc.MARKET_SELL['y'],0.25)
    
def write_comment(comment):
    pyautogui.leftClick(loc.COMMENT['x'], loc.COMMENT['y'])
    pyautogui.write(comment)
    
def order_ok():
    pyautogui.leftClick(loc.ORDER_OK['x'], loc.ORDER_OK['y'])
    
def place_sell_order(volume="1", comment="Alhamdulillah"):    
    new_order()
    change_volume(volume)
    write_comment(comment)
    market_sell()
    order_ok()
    
def place_buy_order(volume="1", comment="Alhamdulillah"):    
    new_order()
    change_volume(volume)
    write_comment(comment)
    market_buy()
    order_ok()

def main():

    print("Syntax: python auto_mt4.py <symbol> <order> <volume> <order_comment>")
    print("sys argv length: {}".format(len(sys.argv)))
    time.sleep(5)

    if(len(sys.argv)==1):
        symbols = [
                    'EURUSD',
                    'AUDUSD',
                    'GBPUSD',
                    'NZDUSD',
                    'USDJPY',
                    'USDCAD',
                    'EURJPY',
                    'GBPJPY'
                   ]
        order="buy"
        volume="1.23"
        order_comment="test123"

        for symbol in symbols:
            if order == "buy":
                place_buy_order_mm(symbol, volume, order_comment)
            elif order == "sell":
                place_sell_order_mm(symbol, volume, order_comment)
            else:
                print("Only receive 'buy' or ''sell'")
            time.sleep(3)
    else:
        symbol = sys.argv[1]
        order= sys.argv[2]
        volume = sys.argv[3]
        order_comment = sys.argv[4]

        if order == "buy":
            place_buy_order_mm(symbol, volume, order_comment)
        elif order == "sell":
            place_sell_order_mm(symbol, volume, order_comment)
        else:
            print("Only receive 'buy' or ''sell'")

if __name__ =="__main__":
    main()