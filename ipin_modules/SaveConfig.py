import os

class Cfg_Data:

    def __init__(self):
    # Read from config file
    # ----------------------------------------------
        self.symbols = ""
        self.master_ip=""
        self.slave_ips  = ""
        self.magic_number = ""
        self.token = ""
        self.chat_id = ""
        self.risk = ""
        self.arb_open = 0
        self.arb_close = 0
        self.pip_step = 0
        self.scalping_rule = 0
        self.master_lot = 0.0
        self.slave_lot = 0.0
        self.master_min_lot = 0.0
        self.slave_min_lot = 0.0
        self.master_slip = 0
        self.slave_slip = 0
        self.master_sl = 0
        self.slave_sl = 0
        self.master_suffix = ""
        self.slave_suffix = ""

class SaveFile:

    def __init__(self, configFile):
        self.filename = configFile
        # self.cfg = Cfg_Data()

    def save_config(self, content):

        f = open(self.filename, 'a')
        f.writelines(content + '\n' + '\n')
        f.close()

    def write_symbol(self, symbols):

        sym = ';symbols = '
        for s in symbols:
            sym = sym + s + ','

        self.save_config(sym)




if __name__ == "__main__":

    symbols = ['GBPJPY', 'XXXXXX', 'GBPUSD']

    if os.path.exists("test123.cfg"):
        os.remove("test123.cfg")

    cfgData = SaveFile('test123.cfg')
    cfgData.write_symbol(symbols)
    cfgData.save_config(';master_ip= 888.99.90.12')




