# -*- coding: utf-8 -*-
# Tifia - Upcloud
class mt5:
    
    def __init__(self):

        self.fix_newOrder_y = 365
        self.offset_symbol_y = 20
        self.offset_close_y = 20
    
        self.STOP_LOSS={
            'x': 865,
            'y': 385
        }
        
        self.TAKE_PROFIT={
            'x': 1090,
            'y': 385
        }
            
        self.VOLUME={
                'x': 865,
                'y': 360
                }
        
        self.MARKET_BUY= {
            'x': 1065,
            'y': 545
            }
        
        self.MARKET_SELL={
            'x': 850,
            'y': 545
            }
        
        self.ORDER_OK={
            'x': 1165,
            'y': 245
        }
        
        self.COMMENT={
            'x': 1080,
            'y': 415
            }

        self.symbol ={
            'x': 35,
            'y': 155
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


