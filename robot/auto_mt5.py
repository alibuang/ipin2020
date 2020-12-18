import pyautogui
# from .mt5_upcloud import mt5
from .mt5_laptop import mt5
import time
import sys
import keyboard

pyautogui.FAILSAFE=False
BUY = 0
SELL= 1

class Auto_Robot:

    def __init__(self):
        self.loc =  mt5()

    def close_order(self, index:int):

        if keyboard.is_pressed('ctrl + q'): sys.exit()

        print("Close order for index {}".format(index))

        try:
            loc_x = self.loc.close['x']
            loc_y = self.loc.close['y'] + (index * self.loc.offset_close_y)

            print("symbol location", loc_x, loc_y)
            pyautogui.leftClick(loc_x, loc_y)

        except Exception as err:
            print("Exception in click new order: {}".format(err))
        else:
            print("Close open position index '{}' success...".format(index))


    def new_order_mm(self, index:int):

        if keyboard.is_pressed('ctrl + q'): sys.exit()

        try:
            loc_symbol_x = self.loc.symbol['x']
            loc_symbol_y = self.loc.symbol['y'] + (index * self.loc.offset_symbol_y)

            loc_newOrder_x = loc_symbol_x + self.loc.offset_newOrder['x']
            loc_newOrder_y = loc_symbol_y + self.loc.offset_newOrder['y']

            loc_fixed_newOrder_y = self.loc.fix_newOrder_y

            print("symbol location", loc_symbol_x, loc_symbol_y)
            pyautogui.rightClick(loc_symbol_x, loc_symbol_y)

            # Only in my laptop
            # if index <=5: pyautogui.leftClick(loc_newOrder_x, loc_newOrder_y)
            # else: pyautogui.leftClick(loc_newOrder_x, loc_fixed_newOrder_y)
            pyautogui.leftClick(loc_newOrder_x, loc_newOrder_y)


        except Exception as err:
            print("Exception in click new order: {}".format(err))
        else:
            print("clicked new order success...")

    def place_open_position_mm(self,trade_type:int,
                               pair_idx:int,
                               stop_loss:str= None,
                               take_profit:str=None,
                               volume:str="0.1",
                               comment:str="test123 sell"):
        print("Trade Type: {} \nSymbol: {} \nStop Loss: {} \nTake Profit: {} \nVolume: {} \nComment: {}".format(
            trade_type, pair_idx, stop_loss, take_profit, volume, comment
        ))

        try:
            self.new_order_mm(pair_idx)
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

        if keyboard.is_pressed('ctrl + q'): sys.exit()

        try:
            pyautogui.leftClick(self.loc.STOP_LOSS['x'], self.loc.STOP_LOSS['y'])
            pyautogui.write(sl)

        except Exception as err:
            print("Exception in set stop loss: {}".format(err))
        else:
            print("set stop loss success...")

    def take_profit(self, tp):

        if keyboard.is_pressed('ctrl + q'): sys.exit()

        try:
            pyautogui.leftClick(self.loc.TAKE_PROFIT['x'], self.loc.TAKE_PROFIT['y'])
            pyautogui.write(tp)

        except Exception as err:
            print("Exception in set take profit: {}".format(err))
        else:
            print("set take profit success...")

    def change_volume(self, volume="1.0"):

        if keyboard.is_pressed('ctrl + q'): sys.exit()

        try:
            pyautogui.leftClick(self.loc.VOLUME['x'], self.loc.VOLUME['y'])
            pyautogui.write(volume)

        except Exception as err:
            print("Exception in set volume: {}".format(err))
        else:
            print("set volume success...")


    def market_buy(self):

        if keyboard.is_pressed('ctrl + q'): sys.exit()

        try:
            pyautogui.leftClick(self.loc.MARKET_BUY['x'], self.loc.MARKET_BUY['y'], 0.25)

        except Exception as err:
            print("Exception in click buy market: {}".format(err))
        else:
            print("clicked market buy success...")

    def market_sell(self):

        if keyboard.is_pressed('ctrl + q'): sys.exit()

        try:
            pyautogui.leftClick(self.loc.MARKET_SELL['x'], self.loc.MARKET_SELL['y'],0.25)

        except Exception as err:
            print("Exception in click sell market: {}".format(err))
        else:
            print("clicked market sell success...")

    def write_comment(self,comment):

        if keyboard.is_pressed('ctrl + q'): sys.exit()

        try:
            pyautogui.leftClick(self.loc.COMMENT['x'], self.loc.COMMENT['y'])
            pyautogui.write(comment)

        except Exception as err:
            print("Exception in write comment: {}".format(err))
        else:
            print("write comment success ...")


    def order_ok(self):

        if keyboard.is_pressed('ctrl + q'): sys.exit()

        try:
            pyautogui.leftClick(self.loc.ORDER_OK['x'], self.loc.ORDER_OK['y'])

        except Exception as err:
            print("Exception in click OK: {}".format(err))
        else:
            print("click OK success ...")

def main():

    auto = Auto_Robot()
    isOpen = False
    # auto.place_open_position_mm(SELL, 4)
    # auto.close_order(0)
    # sys.exit()

    print("Syntax: python auto_mt4.py <symbol> <order> <volume> <order_comment>")
    print("sys argv length: {}".format(len(sys.argv)))
    time.sleep(1)

    if(len(sys.argv)==1):

        if isOpen:

            trade_type = SELL

            for i in range(0, 10):
                print("testing ...")
                pair_index = i
                auto.place_open_position_mm(trade_type, pair_index)

        else:
            for i in range(9,-1,-1):
                print("Close testing ...")
                auto.close_order(i)

    else:
        symbol = sys.argv[1]
        order= sys.argv[2]
        volume = sys.argv[3]
        order_comment = sys.argv[4]


if __name__ =="__main__":
    main()