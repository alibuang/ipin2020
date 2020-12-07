from ipin_modules.Broker import Broker
# from PyQt5 import QtWidgets
from ipin_modules.si_ui import Ui_MainWindow  # importing our generated file
from ipin_modules.setting import Ui_SettingWindow
# from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from ipin_modules.SaveConfig import SaveFile
import sys
from ipin_modules import ReadConfig4
import os
import datetime as dt
from shutil import copyfile

BUY = 0
SELL= 1

DOWN = 1
UP = 2
NO_SIGNAL = 99

cfg_file = '../config/superipin.cfg'


class Cfg_Data:

    def __init__(self):
    # Read from config file
    # ----------------------------------------------
        self.symbols = ""
        self.master_ip = ""
        self.slave_ip = ""
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

class mywindow(QMainWindow):

    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.cfg = Cfg_Data()

        self.main_program()


        #initiate broker HERE

        self.setting_screen = Setting()
        self.display_cfg()
        self.ui.actionSetting.triggered.connect(self.setting_screen.show)

        self.setting_screen.setting.pbLoad.clicked.connect(self.display_cfg)
        self.setting_screen.setting.pbSave.clicked.connect(self.save_setting)

    def save_setting(self):

        buttonReply = QMessageBox.question(self, 'Configuration', "Do you want to save the configuration?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.No:
            print('Not Save the configuration')
            self.setting_screen.activateWindow()
            self.setEnabled(True)
            return
        else:
            print('Save the configuration')


        config_file = cfg_file
        dest = config_file[:-3] + 'bak'

        if os.path.exists(config_file):
            copyfile(config_file, dest)
            os.remove(config_file)

        save = SaveFile(config_file)
        save.save_config(';master_ip = ' + self.setting_screen.setting.master_ip.text())
        save.save_config(';slave_ip = ' + self.setting_screen.setting.slave_ip.text())
        save.save_config(';master_lot = ' + self.setting_screen.setting.master_lot.text())
        save.save_config(';slave_lot = ' + self.setting_screen.setting.slave_lot.text())
        save.save_config(';master_min_lot = ' + self.setting_screen.setting.master_min_lot.text())
        save.save_config(';slave_min_lot = ' + self.setting_screen.setting.slave_min_lot.text())
        save.save_config(';master_slippage = ' + self.setting_screen.setting.master_slip.text())
        save.save_config(';slave_slippage = ' + self.setting_screen.setting.slave_slip.text())
        save.save_config(';master_sl = ' + self.setting_screen.setting.master_stopLoss.text())
        save.save_config(';slave_sl = ' + self.setting_screen.setting.slave_stoploss.text())
        save.save_config(';master_suffix = ' + self.setting_screen.setting.master_suffix.text())
        save.save_config(';slave_suffix = ' + self.setting_screen.setting.slave_suffix.text())

        #common setting
        save.save_config(';magic_number = ' + self.setting_screen.setting.magic_number.text())
        save.save_config(';token = ' + self.setting_screen.setting.token.text())
        save.save_config(';chat_id = ' + self.setting_screen.setting.chat_id.text())
        save.save_config(';risk = ' + self.setting_screen.setting.risk.text())
        save.save_config(';arbitrage_open = ' + self.setting_screen.setting.arb_open.text())
        save.save_config(';arbitrage_close = ' + self.setting_screen.setting.arb_close.text())
        save.save_config(';scalping_rule = ' + self.setting_screen.setting.scalping_rule.text())
        save.save_config(';pip_step = ' + self.setting_screen.setting.pip_step.text())

        #for symbol check box
        setting = self.setting_screen.setting

        try:
            symbols = []
            if setting.cbEurUsd.isChecked(): symbols.append(setting.cbEurUsd.text())
            if setting.cbAudUsd.isChecked(): symbols.append(setting.cbAudUsd.text())
            if setting.cbGbpUsd.isChecked(): symbols.append(setting.cbGbpUsd.text())
            if setting.cbNzdUsd.isChecked(): symbols.append(setting.cbNzdUsd.text())
            if setting.cbUsdJpy.isChecked(): symbols.append(setting.cbUsdJpy.text())
            if setting.cbUsdCad.isChecked(): symbols.append(setting.cbUsdCad.text())
            if setting.cbUsdChf.isChecked(): symbols.append(setting.cbUsdChf.text())
            if setting.cbEurJpy.isChecked(): symbols.append(setting.cbEurJpy.text())
            if setting.cbGbpJpy.isChecked(): symbols.append(setting.cbGbpJpy.text())
            if setting.cbAudJpy.isChecked(): symbols.append(setting.cbAudJpy.text())
            if setting.cbNzdJpy.isChecked(): symbols.append(setting.cbNzdJpy.text())
            if setting.cbCadJpy.isChecked(): symbols.append(setting.cbCadJpy.text())
            if setting.cbChfJpy.isChecked(): symbols.append(setting.cbChfJpy.text())
            if setting.cbEurGbp.isChecked(): symbols.append(setting.cbEurGbp.text())

            str_symbols = ';symbols = '
            for symbol in symbols:
                str_symbols = str_symbols + symbol + ','

            str_symbols = str_symbols[:-1]
            print(str_symbols)
            save.save_config(str_symbols)

        except Exception as e:
            print(e)

        print('save to file')
        self.setting_screen.hide()

    def read_cfg_file(self):
        cfg_read = ReadConfig4.config(cfg_file)

        self.cfg.symbols = cfg_read.symbols
        self.cfg.master_ip = cfg_read.m_ip
        self.cfg.slave_ip = cfg_read.s_ip
        self.cfg.magic_number = cfg_read.magic_number
        self.cfg.token = cfg_read.token
        self.cfg.chat_id = cfg_read.chat_id
        self.cfg.risk = cfg_read.risk
        self.cfg.arb_open = cfg_read.arbitrage_open
        self.cfg.arb_close = cfg_read.arbitrage_close
        self.cfg.pip_step = cfg_read.pip_step
        self.cfg.scalping_rule = cfg_read.scalping_rule
        self.cfg.master_lot = cfg_read.master_lot
        self.cfg.slave_lot = cfg_read.slave_lot
        self.cfg.master_min_lot = cfg_read.master_min_lot
        self.cfg.slave_min_lot = cfg_read.slave_min_lot
        self.cfg.master_slip = cfg_read.master_slippage
        self.cfg.slave_slip = cfg_read.slave_slippage
        self.cfg.master_sl = cfg_read.master_sl
        self.cfg.slave_sl = cfg_read.slave_sl
        self.cfg.master_suffix = cfg_read.m_suffix
        self.cfg.slave_suffix = cfg_read.s_suffix

    def display_cfg(self):

        self.read_cfg_file()

        #Common
        self.setting_screen.setting.magic_number.setText(str(self.cfg.magic_number))
        self.setting_screen.setting.token.setText(self.cfg.token)
        self.setting_screen.setting.chat_id.setText(str(self.cfg.chat_id))
        self.setting_screen.setting.risk.setText(self.cfg.risk)
        self.setting_screen.setting.arb_open.setText(str(self.cfg.arb_open))
        self.setting_screen.setting.arb_close.setText(str(self.cfg.arb_close))
        self.setting_screen.setting.pip_step.setText(str(self.cfg.pip_step))
        self.setting_screen.setting.scalping_rule.setText(str(self.cfg.scalping_rule))

        for s in self.cfg.symbols:
            if s == 'EURUSD': self.setting_screen.setting.cbEurUsd.setChecked(True);
            if s == 'AUDUSD': self.setting_screen.setting.cbAudUsd.setChecked(True);
            if s == 'GBPUSD': self.setting_screen.setting.cbGbpUsd.setChecked(True);
            if s == 'NZDUSD': self.setting_screen.setting.cbNzdUsd.setChecked(True);
            if s == 'USDJPY': self.setting_screen.setting.cbUsdJpy.setChecked(True);
            if s == 'USDCAD': self.setting_screen.setting.cbUsdCad.setChecked(True);
            if s == 'USDCHF': self.setting_screen.setting.cbUsdChf.setChecked(True);
            if s == 'EURJPY': self.setting_screen.setting.cbEurJpy.setChecked(True);
            if s == 'GBPJPY': self.setting_screen.setting.cbGbpJpy.setChecked(True);
            if s == 'AUDJPY': self.setting_screen.setting.cbAudJpy.setChecked(True);
            if s == 'NZDJPY': self.setting_screen.setting.cbNzdJpy.setChecked(True);
            if s == 'CADJPY': self.setting_screen.setting.cbCadJpy.setChecked(True);
            if s == 'CHFJPY': self.setting_screen.setting.cbChfJpy.setChecked(True);
            if s == 'EURGBP': self.setting_screen.setting.cbEurGbp.setChecked(True);

        #     print(s)
        #     self.setting_screen.setting.cbEurUsd.setChecked(True) if s == "EURUSD" else  self.setting_screen.setting.cbEurUsd.setChecked(False)

        #Master
        self.setting_screen.setting.master_ip.setText(self.cfg.master_ip)
        self.setting_screen.setting.master_lot.setText(str(self.cfg.master_lot))
        self.setting_screen.setting.master_min_lot.setText(str(self.cfg.master_min_lot))
        self.setting_screen.setting.master_slip.setText(str(self.cfg.master_slip))
        self.setting_screen.setting.master_stopLoss.setText(str(self.cfg.master_sl))
        self.setting_screen.setting.master_suffix.setText(str(self.cfg.master_suffix))

        #Slave
        self.setting_screen.setting.slave_ip.setText(self.cfg.slave_ip)
        self.setting_screen.setting.slave_lot.setText(str(self.cfg.slave_lot))
        self.setting_screen.setting.slave_min_lot.setText(str(self.cfg.slave_min_lot))
        self.setting_screen.setting.slave_slip.setText(str(self.cfg.slave_slip))
        self.setting_screen.setting.slave_stoploss.setText(str(self.cfg.slave_sl))
        self.setting_screen.setting.slave_suffix.setText(str(self.cfg.slave_suffix))

    def main_program(self):
        # self.ui.lblBrokerAName.setText(broker_A)

        self.timer = QTimer()

        self.ui.pbRun.clicked.connect(self.btn_Run_pressed)
        self.ui.pbStop.clicked.connect(self.btn_Stop_pressed)
        self.ui.pbReset.clicked.connect(self.btn_Reset_pressed)
        self.ui.pbTestOpen.clicked.connect(self.btn_TestOpen_pressed)
        self.ui.pbTestClose.clicked.connect(self.btn_Close_pressed)

    def btn_TestOpen_pressed(self):
        # slave.send_order(BUY, slave.symbols[i], slave.ask[i], slave.lots, slave.SLIP, slave.stop_loss, mt4_comments)

        for i in range(len(self.cfg.symbols)):

            self.broker_master.send_order(BUY, self.cfg.symbols[i],self.broker_master.ask[i],1.0, 10 )
            self.broker_slave.send_order(SELL, self.cfg.symbols[i], self.broker_slave.bid[i], 1.0, 10)

    def btn_Close_pressed(self):
        self.broker_master.order_close(self.broker_master.symbols)
        self.broker_slave.order_close(self.broker_slave.symbols)

    def btn_Reset_pressed(self):
        self.ui.pbRun.setEnabled(True)
        self.ui.pbStop.setEnabled(True)
        self.ui.tableWidget.clearContents()
        self.ui.lblBrokerAName.clear()
        self.ui.lblBrokerBName.clear()

    def btn_Stop_pressed(self):
        self.ui.pbRun.setEnabled(True)
        self.ui.pbStop.setDisabled(True)
        self.timer.stop()

    def btn_Run_pressed(self):

        self.ui.pbRun.setDisabled(True)
        self.ui.pbStop.setEnabled(True)

        self.read_cfg_file()
        self.gap_down = []
        self.gap_up = []
        for i in range(len(self.cfg.symbols)):
            self.gap_down.append(0)
            self.gap_up.append(0)


        # initialize broker .........
        self.broker_master = Broker('tcp://' + self.cfg.master_ip, self.cfg.magic_number, \
                                    self.cfg.symbols, self.cfg.master_suffix)
        self.broker_master.get_acct_info()
        self.ui.lblBrokerAName.setText(self.broker_master.company)

        self.broker_slave = Broker('tcp://' + self.cfg.slave_ip, self.cfg.magic_number, \
                                   self.cfg.symbols, self.cfg.slave_suffix)
        self.broker_slave.get_acct_info()
        self.ui.lblBrokerBName.setText(self.broker_slave.company)

        print('master:', self.broker_master.symbols, '\nslave:', self.broker_slave.symbols)

        self.broker_master.init_symbol()
        self.broker_slave.init_symbol()

        self.timer.timeout.connect(self.run_2Leg_arb)
        self.timer.start(1000)

    def run_2Leg_arb(self):

        self.broker_master.get_price(self.broker_master.symbols)
        self.broker_slave.get_price(self.broker_slave.symbols)

        self.broker_master.get_profit(self.broker_master.symbols)
        self.broker_slave.get_profit(self.broker_slave.symbols)

        # debug-----------------
        self.broker_master.get_order_status(self.broker_master.symbols)
        # print('Trade count is master ', self.broker_master.trade_count)
        # debug-----------------

        for i in range(len(self.cfg.symbols)):

            digit = self.broker_master.digits[i] if self.broker_master.digits[i] > self.broker_slave.digits[i] else \
            self.broker_slave.digits[i]

            # calculate gap between brokers
            self.gap_up[i] = pow(10, digit) * (self.broker_master.ask[i] - self.broker_slave.bid[i])
            self.gap_down[i] = pow(10, digit) * (self.broker_slave.ask[i] - self.broker_master.bid[i])

            # Open position management
            signal = self.get_signal(self.gap_up[i], self.gap_down[i], self.cfg.arb_open)

            if signal == DOWN and self.broker_master.ask[i] != 0 and self.broker_slave.ask[i] !=0 :
                self.broker_master.send_order(SELL, self.cfg.symbols[i], self.broker_master.bid[i], 1.0, 10)
                self.broker_slave.send_order(BUY, self.cfg.symbols[i], self.broker_slave.ask[i], 1.0, 10)

            elif signal == UP and self.broker_master.ask[i] != 0 and self.broker_slave.ask[i] !=0 :
                self.broker_master.send_order(BUY, self.cfg.symbols[i], self.broker_master.ask[i], 1.0, 10)
                self.broker_slave.send_order(SELL, self.cfg.symbols[i], self.broker_slave.bid[i], 1.0, 10)


                #Close position management

                #check for any open position
                #check gap is lee than arb_close ie 20 pip
                #check for time > sclaping rule ie 15 minits

            if self.chk_closeValid(self.broker_master,self.broker_master.symbols[i]) and \
                    self.gap_down[i] > - self.cfg.arb_close and \
                    self.broker_master.trade_count[i] > 0:
                self.broker_master.order_close([self.broker_master.symbols[i]])
                self.broker_slave.order_close([self.broker_slave.symbols[i]])

        self.update_table()

    def update_table(self):

        # print('up to update table')


        pro_fmt = "{0:0." + str(2) + "f}"
        gap_fmt = '{:d}'

        # print('up to update table 2')


        for i in range(len(self.cfg.symbols)):


            # print(i)
            digit = self.broker_master.digits[i] if self.broker_master.digits[i] > self.broker_slave.digits[i] else \
            self.broker_slave.digits[i]

            m_fmt = "{0:0." + str(digit) + "f}"
            s_fmt = "{0:0." + str(digit) + "f}"

            net_profit = self.broker_master.profit[i] + self.broker_slave.profit[i]
            pl = 'PROFIT' if net_profit > 0 else 'LOSS' if net_profit < 0 else 'NA'

            self.ui.tableWidget.setItem(i, 0, QTableWidgetItem(self.cfg.symbols[i]))
            self.ui.tableWidget.setItem(i, 1, QTableWidgetItem(m_fmt.format(self.broker_master.ask[i])))
            self.ui.tableWidget.setItem(i, 2, QTableWidgetItem(s_fmt.format(self.broker_master.bid[i])))
            self.ui.tableWidget.setItem(i, 3, QTableWidgetItem(m_fmt.format(self.broker_slave.ask[i])))
            self.ui.tableWidget.setItem(i, 4, QTableWidgetItem(s_fmt.format(self.broker_slave.bid[i])))
            self.ui.tableWidget.setItem(i, 5, QTableWidgetItem(gap_fmt.format(int(self.gap_up[i]))))
            self.ui.tableWidget.setItem(i, 6, QTableWidgetItem(gap_fmt.format(int(self.gap_down[i]))))
            self.ui.tableWidget.setItem(i, 7, QTableWidgetItem(pro_fmt.format(self.broker_master.profit[i])))
            self.ui.tableWidget.setItem(i, 8, QTableWidgetItem(pro_fmt.format(self.broker_slave.profit[i])))
            self.ui.tableWidget.setItem(i, 9, QTableWidgetItem(pro_fmt.format(net_profit)))
            self.ui.tableWidget.setItem(i, 10, QTableWidgetItem(pl))

        self.ui.tableWidget.repaint()
        # print('update table !')

    def get_signal(self, gap_up, gap_down, arb_open):

        signal = DOWN if gap_down < - arb_open else NO_SIGNAL
        signal = UP if gap_up < - arb_open else NO_SIGNAL

        return signal

    def chk_closeValid(self, broker, symbol):
        closeValid = False

        openTime, mt4ServerTime = broker.get_openTime(symbol)
        allowedCloseTime = openTime + dt.timedelta(seconds= self.cfg.scalping_rule)

        if mt4ServerTime > allowedCloseTime:
                closeValid=True

        return closeValid


class Setting(QMainWindow):

    def __init__(self):
        super(Setting, self).__init__()
        self.setting = Ui_SettingWindow()
        self.setting.setupUi(self)

# ------------- main program ----------------

app = QApplication([])
application = mywindow()
application.show()
sys.exit(app.exec())