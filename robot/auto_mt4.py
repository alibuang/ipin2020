import pyautogui
from .mt4_locater import mt4
import time
import sys

pyautogui.FAILSAFE=False
BUY = 0
SELL= 1

class Auto_Robot:

    def __init__(self):
        self.loc =  mt4()

    def pair_loc(self,symbol):
        return {
            'EURUSD': self.loc.eurusd,
            'AUDUSD': self.loc.audusd,
            'GBPUSD': self.loc.gbpusd,
            'NZDUSD': self.loc.nzdusd,
            'USDJPY': self.loc.usdjpy,
            'USDCAD': self.loc.usdcad,
            'EURJPY': self.loc.eurjpy,
            'GBPJPY': self.loc.gbpjpy

        }[symbol]

    def new_order_mm(self, symbol):
        try:
            sc = self.pair_loc(symbol)
            pyautogui.rightClick(sc['x'],sc['y'])
            pyautogui.leftClick(sc['x']+38, sc['y']+15)

        except Exception as err:
            print("Exception in click new order: {}".format(err))
        else:
            print("clicked new order success...")



    def place_open_position_mm(self,trade_type:int,
                               symbol:str,
                               stop_loss:str= None,
                               take_profit:str=None,
                               volume:str="1",
                               comment:str="test123 sell"):
        print("Trade Type: {} \nSymbol: {} \nStop Loss: {} \nTake Profit: {} \nVolume: {} \nComment: {}".format(
            trade_type, symbol, stop_loss, take_profit, volume, comment
        ))

        try:
            self.new_order_mm(symbol)
            self.change_volume(volume)
            if stop_loss is not None: self.stop_loss(stop_loss)
            if take_profit is not None: self.take_profit(take_profit)
            self.write_comment(comment)

            if trade_type == BUY:
                self.market_buy()
            elif trade_type == SELL:
                self.market_sell()
            else:
                print("Trade type '{}' not valid".format(trade_type))
            self.order_ok()

        except Exception as err:
            print("Exception in place_open_position_mm: {}".format(err))

    def stop_loss(self, sl):

        try:
            pyautogui.leftClick(self.loc.STOP_LOSS['x'], self.loc.STOP_LOSS['y'])
            pyautogui.write(sl)

        except Exception as err:
            print("Exception in set stop loss: {}".format(err))
        else:
            print("set stop loss success...")

    def take_profit(self, tp):

        try:
            pyautogui.leftClick(self.loc.TAKE_PROFIT['x'], self.loc.TAKE_PROFIT['y'])
            pyautogui.write(tp)

        except Exception as err:
            print("Exception in set take profit: {}".format(err))
        else:
            print("set take profit success...")

    def change_volume(self, volume="1.0"):

        try:
            pyautogui.leftClick(self.loc.VOLUME['x'], self.loc.VOLUME['y'])
            pyautogui.write(volume)

        except Exception as err:
            print("Exception in set volume: {}".format(err))
        else:
            print("set volume success...")


    def market_buy(self):

        try:
            pyautogui.leftClick(self.loc.MARKET_BUY['x'], self.loc.MARKET_BUY['y'], 0.25)

        except Exception as err:
            print("Exception in click buy market: {}".format(err))
        else:
            print("clicked market buy success...")

    def market_sell(self):

        try:
            pyautogui.leftClick(self.loc.MARKET_SELL['x'], self.loc.MARKET_SELL['y'],0.25)

        except Exception as err:
            print("Exception in click sell market: {}".format(err))
        else:
            print("clicked market sell success...")

    def write_comment(self,comment):

        try:
            pyautogui.leftClick(self.loc.COMMENT['x'], self.loc.COMMENT['y'])
            pyautogui.write(comment)

        except Exception as err:
            print("Exception in write comment: {}".format(err))
        else:
            print("write comment success ...")


    def order_ok(self):

        try:
            pyautogui.leftClick(self.loc.ORDER_OK['x'], self.loc.ORDER_OK['y'])

        except Exception as err:
            print("Exception in click OK: {}".format(err))
        else:
            print("click OK success ...")

def main():

    auto = Auto_Robot()

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
                auto.place_buy_order_mm(symbol, volume, order_comment)
            elif order == "sell":
                auto.place_sell_order_mm(symbol, volume, order_comment)
            else:
                print("Only receive 'buy' or ''sell'")
            time.sleep(3)
    else:
        symbol = sys.argv[1]
        order= sys.argv[2]
        volume = sys.argv[3]
        order_comment = sys.argv[4]

        if order == "buy":
            auto.place_buy_order_mm(symbol, volume, order_comment)
        elif order == "sell":
            auto.place_sell_order_mm(symbol, volume, order_comment)
        else:
            print("Only receive 'buy' or ''sell'")

if __name__ =="__main__":
    main()