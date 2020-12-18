# -*- coding: utf-8 -*-
# Tifia - Upcloud
class mt5:
    
    def __init__(self):

        self.fix_newOrder_y = 365
        self.offset_symbol_y = 30
        self.offset_close_y = 30
    
        self.STOP_LOSS={
            'x': 1060,
            'y': 445
        }
        
        self.TAKE_PROFIT={
            'x': 1400,
            'y': 445
        }
            
        self.VOLUME={
                'x': 1060,
                'y': 405
                }
        
        self.MARKET_BUY= {
            'x': 1350,
            'y': 680
            }
        
        self.MARKET_SELL={
            'x': 1035,
            'y': 680
            }
        
        self.ORDER_OK={
            'x': 1510,
            'y': 245
        }
        
        self.COMMENT={
            'x': 1405,
            'y': 485
            }

        self.symbol ={
            'x': 55,
            'y': 180
        }

        self.close = {
            'x': 1900,
            # 'x': 1870,
            'y': 625
        }
        self.offset_newOrder = {
            'x':38,
            'y':15
        }


