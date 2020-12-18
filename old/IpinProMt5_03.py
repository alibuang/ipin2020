# 29 May 2019

# Random magic number
# 1. magic number randomly created - done
# 2. open position with random magic_number
# 3. trade count with random magic number
# 4. count proft with random magic number
#
# 1. telegram msg for gap up and down decimal point not set - done
# 2. put comment (debug and live)
# 3. open next pos and use pip step
# 4. send telegram msg when close (with net profit)
# 5. display total equity
# 6. create log file when open
# 7. ea close position after 3 hours
# 8. open new position after 5 min previous open position

# 10. if there is open position either at master or slave but the other pair no open position, and already passed 30 sec
#    then the position will be closed.

from ipin_modules.Broker import Broker
from robot.auto_mt5 import Auto_Robot
from ipin_modules.ipinPro_ui import Ui_MainWindow  # importing our generated file
from ipin_modules.setting_ui import Ui_SettingWindow
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from ipin_modules.SaveConfig import SaveFile
from ipin_modules import ReadConfig4
import os
import datetime as dt
import sys
from shutil import copyfile
import telegram
from datetime import datetime
from time import sleep
from random import randint
import keyboard
import math



BUY = 0
SELL= 1
DOWN = 1
UP = 2
NO_SIGNAL = 99

cfg_file = 'config/superipin.cfg'
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
        self.slave_tp= 0
        self.slave_comment=""
        self.master_suffix = ""
        self.slave_suffix = ""
        self.open_time_gap = 0
        self.weekend_off = 0

class mywindow(QMainWindow):

    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()

        self.ui.setupUi(self)
        self.cfg = Cfg_Data()

        self.main_program()
        self.setting_ui()

    def setting_ui(self):

        self.setting_screen = Setting()
        self.display_cfg()


        self.ui.actionSetting.triggered.connect(self.setting_screen.show)

        self.setting_screen.setting.pbLoad.clicked.connect(self.display_cfg)
        self.setting_screen.setting.pbSave.clicked.connect(self.save_setting)
        self.setting_screen.setting.pbExit.clicked.connect(self.setting_screen.close)
        self.setting_screen.setting.pbSendTeleg.clicked.connect(self.debug_telegram)

    def debug_telegram(self):
        self.send_telegram_msg('FxCitizen Market Capital', 'Ipin Pro 2019', 'FxOpen Private Limited' \
                               ,'Abdullah Bin Razak', 'EURGBP',12.00123, -60.00456, 'test ONLY')

    def send_debug_msg(self):
        bot = telegram.Bot(token=self.cfg.token)
        bot.send_message(chat_id=self.cfg.chat_id, text="Hello There", timeout=50)

    def send_telegram_robotStart(self, master_comp, master_accName, slave_comp, slave_accName):
        bot = telegram.Bot(token=self.cfg.token)

        timestamp = str(datetime.now().replace(microsecond=0))

        # generate text message for telegram
        text_msg = 'Robot Ipin Start\n'\
                   +'timestamp: ' + timestamp + '\n' \
                   + 'broker Master: ' + master_comp[:20] + '\n' \
                   + 'acct Master: ' + master_accName[:20] + '\n' \
                   + 'broker Slave: ' + slave_comp[:20] + '\n' \
                   + 'acct Slave: ' + slave_accName[:20] + '\n' \

        try:
            bot.send_message(chat_id=self.cfg.chat_id, text=text_msg, timeout=50)
        except Exception as error:
            print(error)

    def send_telegram_msg(self, master_comp, master_accName, slave_comp, slave_accName, symbol, gap_up, gap_down, comments):
        bot = telegram.Bot(token=self.cfg.token)

        timestamp = str(datetime.now().replace(microsecond=0))

        # generate text message for telegram
        text_msg = 'timestamp: ' + timestamp + '\n' \
                   + 'broker Master: ' + master_comp[:20] + '\n' \
                   + 'acct Master: ' + master_accName[:20] + '\n' \
                   + 'broker Slave: ' + slave_comp[:20] + '\n' \
                   + 'acct Slave: ' + slave_accName[:20] + '\n' \
                   + 'symbol: ' + symbol + '\n' \
                   + 'Gap UP: ' + str(int(gap_up)) + '\n' \
                   + 'Gap DOWN: ' + str(int(gap_down)) + '\n' \
                   + comments

        try:
            bot.send_message(chat_id=self.cfg.chat_id, text=text_msg, timeout=50)
        except Exception as error:
            print(error)

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
        save.save_config(';slave_tp = ' + self.setting_screen.setting.slave_takeprofit.text())
        save.save_config(';slave_comment = ' + self.setting_screen.setting.slave_comment.text())
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
        save.save_config(';next_open_duration =' + self.setting_screen.setting.next_open_duration.text())

        if self.setting_screen.setting.weekendOFFCheckBox.isChecked():
            save.save_config(';weekend_off = 1')
        else:
            save.save_config(';weekend_off = 0')

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
        self.cfg.slave_tp = cfg_read.slave_tp
        self.cfg.slave_comment =  cfg_read.slave_comment
        self.cfg.weekend_off = cfg_read.weekend_off
        self.cfg.master_suffix = cfg_read.m_suffix
        self.cfg.slave_suffix = cfg_read.s_suffix
        self.cfg.open_time_gap = cfg_read.open_time_gap

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
        self.setting_screen.setting.next_open_duration.setText(str(self.cfg.open_time_gap))
        if self.cfg.weekend_off == 1:
            self.setting_screen.setting.weekendOFFCheckBox.setChecked(True)
        else:
            self.setting_screen.setting.weekendOFFCheckBox.setChecked(False)

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
        self.setting_screen.setting.slave_takeprofit.setText(str(self.cfg.slave_tp))
        self.setting_screen.setting.slave_comment.setText(str(self.cfg.slave_comment))
        self.setting_screen.setting.slave_suffix.setText(str(self.cfg.slave_suffix))

    def main_program(self):

        self.timer = QTimer()
        self.isTest= False

        self.ui.pbRun.clicked.connect(self.btn_Run_pressed)
        self.ui.pbStop.clicked.connect(self.btn_Stop_pressed)
        self.ui.pbReset.clicked.connect(self.btn_Reset_pressed)
        self.ui.pbTestOpen.clicked.connect(self.btn_TestOpen_pressed)
        self.ui.pbTestClose.clicked.connect(self.btn_Close_pressed)
        self.ui.pbTestExit.clicked.connect(self.close)
        self.ui.pbDebug.clicked.connect(self.debug)

        self.ui.pbTestOpen.setDisabled(True)
        self.ui.pbStop.setDisabled(True)

    def debug(self):

        isTestOpen=True

        if isTestOpen:
            self.isTest = True
            self.btn_Run_pressed()

        else:
            auto_close = Auto_Robot()

            try:

                self.read_cfg_file()
                master = Broker('tcp://' + self.cfg.master_ip, self.cfg.magic_number, \
                                self.cfg.symbols, self.cfg.master_suffix)
                slave = Broker('tcp://' + self.cfg.slave_ip, self.cfg.magic_number, \
                                           self.cfg.symbols, self.cfg.slave_suffix)
                slave.get_acct_info()
                print(slave.acctName)
                trade = slave.get_total_count(self.cfg.slave_comment)
                print("total count : {}".format(trade["total"]))

                for ticket in trade["ticket"]:

                    trade_details = slave.get_fx_details(ticket)
                    print("symbol:{} ,idx:{} ticket: {}".format(trade_details['symbol'], trade_details['idx'], ticket))

                    master_detail = slave.get_master_details(trade_details['symbol'])
                    # print("master details: {}".format(master_detail))

                    digit = master_detail['digits'] if master_detail['digits'] > trade_details['digits'] else trade_details['digits']

                    gap_up = round(pow(10, digit) * (trade_details['ask'] - master_detail['bid']))
                    gap_down = round(pow(10, digit) * (master_detail['ask'] - trade_details['bid']))

                    close_signal = self.get_close_signal(trade_details['op_type'], gap_up, gap_down, self.cfg.arb_close)
                    close_time_valid = self.chk_closeTimeValid(trade_details['lastOpenTime'], trade_details['mt4ServerTime'])

                    if close_signal and close_time_valid:
                        print("close trade ticket {} , index '{}'".format(ticket,trade_details['idx']))
                        auto_close.close_order(trade_details['idx'])
                        sleep(1)


            except Exception as err_msg:
                print('Error : {}'.format(err_msg))

    def btn_TestOpen_pressed(self):
        # slave.send_order(BUY, slave.symbols[i], slave.ask[i], slave.lots, slave.SLIP, slave.stop_loss, mt4_comments)
        master = self.broker_master
        slave = self.broker_slave

        for i in range(len(self.cfg.symbols)):

            magic_number = self.generate_magicno()

            master.send_order2(order_type= BUY, symbol=master.symbols[i], price=master.ask[i], lot=self.cfg.master_lot,\
                               slip=self.cfg.master_slip, magic_number=magic_number, comments=str(magic_number) )
            slave.send_order2(order_type= SELL, symbol=slave.symbols[i], price=slave.bid[i], lot=self.cfg.slave_lot, \
                               slip=self.cfg.slave_slip, magic_number=magic_number, comments=str(magic_number))

            # master.send_order(BUY, master.symbols[i], master.ask[i],self.cfg.master_lot, self.cfg.master_slip)
            # slave.send_order(SELL, slave.symbols[i], slave.bid[i], self.cfg.slave_lot, self.cfg.slave_slip)

    def btn_Close_pressed(self):

        self.read_cfg_file()

        self.broker_master = Broker('tcp://' + self.cfg.master_ip, self.cfg.magic_number, \
                                    self.cfg.symbols, self.cfg.master_suffix)
        m_magnums = self.broker_master.get_magnums()

        self.broker_slave = Broker('tcp://' + self.cfg.slave_ip, self.cfg.magic_number, \
                                   self.cfg.symbols, self.cfg.slave_suffix)
        s_magnums = self.broker_slave.get_magnums()

        for mn in m_magnums:
            self.broker_master.order_close2(magic_number= mn)

        for mn in s_magnums:
            self.broker_slave.order_close2(magic_number=mn)

    def btn_Reset_pressed(self):
        self.ui.pbRun.setEnabled(True)
        self.ui.pbStop.setDisabled(True)
        self.ui.tableWidget.clearContents()
        # self.ui.tw_Open_Position.clearContents()
        self.ui.lblBrokerAName.clear()
        self.ui.lblBrokerBName.clear()

    def btn_Stop_pressed(self):
        self.ui.pbRun.setEnabled(True)
        self.ui.pbStop.setDisabled(True)
        self.timer.stop()

    def btn_Run_pressed(self):

        self.ui.pbRun.setDisabled(True)
        self.ui.pbStop.setEnabled(True)
        self.ui.pbTestOpen.setEnabled(True)

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
        self.send_telegram_robotStart(self.broker_master.company, self.broker_master.acctName, \
                                      self.broker_slave.company, self.broker_slave.acctName)

        if self.isTest:
            self.test_arbitrage()
        else:
            self.broker_master.init_symbol()
            self.broker_slave.init_symbol()
            self.timer.timeout.connect(self.test_arbitrage)
            self.timer.start(900)

    def test_arbitrage(self):

        try:
            self.manage_closearbit(self.broker_master, self.broker_slave)

            if self.isTest:
                #Only FOR testing purpose
                self.broker_master.get_test_price(self.broker_master.symbols, "MASTER")
                self.broker_slave.get_test_price(self.broker_slave.symbols, "SLAVE")
                print("\n{} \nMaster price \nask:{} \nbid:{} \nspread:{}".format(self.broker_master.symbols,
                                                                       self.broker_master.ask,
                                                                       self.broker_master.bid,
                                                                       self.broker_master.spread))
                print("\n{} \nSlave price \nask:{} \nbid:{} \nspread:{}".format(self.broker_slave.symbols,
                                                                       self.broker_slave.ask,
                                                                       self.broker_slave.bid,
                                                                       self.broker_slave.spread))
            else:
                self.broker_master.get_price(self.broker_master.symbols)
                self.broker_slave.get_price(self.broker_slave.symbols)

            self.opennew_arbitposition(self.broker_master, self.broker_slave)
            self.update_table()

        except Exception as err:
            print("The exception in test_arbitrage: {}".format(err))

    def manage_closearbit(self, master:Broker, slave:Broker):

        auto_close = Auto_Robot()

        try:

            trade = slave.get_total_count(self.cfg.slave_comment)
            # print("total count : {}".format(trade["total"]))

            for ticket in trade["ticket"]:

                trade_details = slave.get_fx_details(ticket)
                print("symbol:{} ,idx:{} ticket: {}".format(trade_details['symbol'], trade_details['idx'], ticket))

                master_detail = master.get_master_details(trade_details['symbol'])
                # print("master details: {}".format(master_detail))

                digit = master_detail['digits'] if master_detail['digits'] > trade_details['digits'] else trade_details[
                    'digits']

                gap_up = round(pow(10, digit) * (trade_details['ask'] - master_detail['bid']))
                gap_down = round(pow(10, digit) * (master_detail['ask'] - trade_details['bid']))

                close_signal = self.get_close_signal(trade_details['op_type'], gap_up, gap_down, self.cfg.arb_close)
                close_time_valid = self.chk_closeTimeValid(trade_details['lastOpenTime'],
                                                           trade_details['mt4ServerTime'])

                if close_signal and close_time_valid:
                    print("close trade ticket {} , index '{}'".format(ticket, trade_details['idx']))
                    auto_close.close_order(trade_details['idx'])
                    sleep(1)

        except Exception as err_msg:
            print('Error : {}'.format(err_msg))



    def opennew_arbitposition(self, master, slave):

        auto_trade = Auto_Robot()

        try:
            for i in range(len(self.cfg.symbols)):
                volume = str(self.cfg.slave_lot)
                order_comment= self.cfg.slave_comment
                trade_type=None

                digit = master.digits[i] if master.digits[i] > slave.digits[i] else slave.digits[i]

                # calculate gap between brokers
                self.gap_up[i] = pow(10, digit) * (slave.ask[i] - master.bid[i])
                self.gap_down[i] = pow(10, digit) * (master.ask[i] - slave.bid[i])

                # Open position management
                open_signal = self.get_open_signal(self.gap_up[i], self.gap_down[i], self.cfg.arb_open)

                if open_signal == DOWN and \
                        master.ask[i] != 0 and \
                        slave.ask[i] != 0  and \
                        self.is_next_position(slave, slave.symbols[i], open_signal, self.gap_up[i],
                                              self.gap_down[i]) and \
                        self.chk_open_valid(slave, slave.symbols[i], order_comment):
                    trade_type = SELL

                elif open_signal == UP and \
                        master.ask[i] != 0 and \
                        slave.ask[i] != 0 and \
                        self.is_next_position(slave, slave.symbols[i], open_signal, self.gap_up[i],
                                              self.gap_down[i]) and \
                        self.chk_open_valid(slave, slave.symbols[i], order_comment):
                    trade_type = BUY

                if trade_type is not None:
                    if self.isTest:
                        slave_test= slave
                        slave_test.get_price(slave_test.symbols)
                        print("isTest is :",self.isTest)
                        stop_loss = str(self.get_stop_loss(
                            trade_type,
                            slave_test.ask[i],
                            slave_test.bid[i],
                            slave_test.digits[i],
                            self.cfg.slave_sl))
                        take_profit = str(self.get_take_profit(
                            trade_type,
                            slave_test.ask[i],
                            slave_test.bid[i],
                            slave_test.digits[i],
                            self.cfg.slave_tp))

                    else:

                        trade_comment = 'SLAVE BUY' if trade_type == BUY else 'SLAVE SELL'
                        self.send_telegram_msg(
                            master.company,
                            master.acctName,
                            slave.company,
                            slave.acctName,
                            self.cfg.symbols[i],
                            self.gap_up[i],
                            self.gap_down[i],
                            trade_comment)
                        stop_loss = str(self.get_stop_loss(
                            trade_type,
                            slave.ask[i],
                            slave.bid[i],
                            slave.digits[i],
                            self.cfg.slave_sl))
                        take_profit = str(self.get_take_profit(
                            trade_type,
                            slave.ask[i],
                            slave.bid[i],
                            slave.digits[i],
                            self.cfg.slave_tp))
                    auto_trade.place_open_position_mm(trade_type,
                                                      i,
                                                      stop_loss,
                                                      take_profit,
                                                      volume,
                                                      order_comment)
            if self.isTest:
                self.isTest = False
                print("Test Mode completed ...")

        except Exception as err:
            print("The exception in opennew_arbitposition: {}".format(err))

    def is_next_position(self, slave:Broker, symbol:str, signal:int, gap_up:float, gap_down:float):

        #print("Get the status whether nex position is allowed ...")

        #get pip_step from cfg
        pip_step = self.cfg.pip_step
        comment = self.cfg.slave_comment
        arbit_open = self.cfg.arb_open
        next_step = {}

        #get trade count from MT5 based on the comments
        trade_count = slave.get_trade_count(symbol, comment)
        next_step['buy'] = arbit_open + (trade_count['buy'] * pip_step)
        next_step['sell'] = arbit_open + (trade_count['sell'] * pip_step)

        #calc the allowed open price for BUY and SELL
        if trade_count['buy'] == 0 and trade_count['sell'] == 0:
            return True
        else:
            if signal == UP and gap_up < -next_step['buy']: return True
            elif signal == DOWN and gap_down < -next_step['sell']: return True
            else: return False

    def get_stop_loss(self, trade_type:int, ask:float, bid:float, digits:int, sl_pip:int):

        try:
            if(trade_type == BUY):
                return round(ask - (sl_pip / math.pow(10, digits)), digits)
            elif(trade_type == SELL):
                return round(bid + (sl_pip / math.pow(10, digits)), digits)
            else:
                return 0

        except Exception as err:
            print("The exception in get_stop_loss: {}".format(err))

    def get_take_profit(self, trade_type:int, ask:float, bid:float, digits:int, tp_pip:int):

        try:
            if (trade_type == BUY):
                return round(ask + (tp_pip / math.pow(10, digits)), digits)
            elif (trade_type == SELL):
                return round(bid - (tp_pip / math.pow(10, digits)), digits)
            else:
                return 0

        except Exception as err:
            print("The exception in get_take_profit: {}".format(err))

    def clean_open_position(self):

        master = self.broker_master
        slave = self.broker_slave

        try:
            m_magnums = master.get_magnums()
            s_magnums = slave.get_magnums()


            diff_a = list(set(m_magnums).difference(s_magnums))
            diff_b = list(set(s_magnums).difference(m_magnums))

            if len(diff_a) != 0 or len(diff_b) != 0:
                print('diff A is {}, and fiff B is {}'.format(diff_a, diff_b))

            for magnum in diff_a:
                master.order_close2(magic_number=magnum)

            for magnum in diff_b:
                slave.order_close2(magic_number=magnum)

        except Exception as err:
            print(err)

    def open_position_handling(self):

        m_magnums = self.broker_master.get_magnums()
        s_magnums = self.broker_slave.get_magnums()
        magnums = list(set(m_magnums).intersection(s_magnums))

        m_symbols = self.broker_master.get_symbols(magnums)
        s_symbols = self.broker_slave.get_symbols(magnums)

        m_profit = self.broker_master.get_profit2(magnums)
        s_profit = self.broker_slave.get_profit2(magnums)

        # print('master : {} and slave : {} and common {}'.format(m_magnums, s_magnums, magnums))
        # print('master symbol : {}'.format(m_symbols))

        net_profits = []
        pnl = []
        if len(m_profit) == len(s_profit):
            for i in range(len(m_profit)):
                net_profits.append(m_profit[i] + s_profit[i])
                profit_or_loss = 'PROFIT' if net_profits[i] >= 0 else 'LOSS'
                pnl.append(profit_or_loss)

        self.update_op_table(symbols=m_symbols, magnums=magnums, m_profit=m_profit, s_profit=s_profit, \
                             net_profits=net_profits, pnl=pnl)

    def update_table(self):

        self.ui.tableWidget.clearContents()

        pro_fmt = "{0:0." + str(2) + "f}"
        gap_fmt = '{:d}'

        for i in range(len(self.cfg.symbols)):


            # print(i)
            digit = self.broker_master.digits[i] if self.broker_master.digits[i] > self.broker_slave.digits[i] else \
            self.broker_slave.digits[i]

            m_fmt = "{0:0." + str(digit) + "f}"
            s_fmt = "{0:0." + str(digit) + "f}"

            # net_profit = self.broker_master.profit[i] + self.broker_slave.profit[i]
            # pl = 'PROFIT' if net_profit > 0 else 'LOSS' if net_profit < 0 else 'NA'

            self.ui.tableWidget.setItem(i, 0, QTableWidgetItem(self.cfg.symbols[i]))
            self.ui.tableWidget.setItem(i, 1, QTableWidgetItem(m_fmt.format(self.broker_master.ask[i])))
            self.ui.tableWidget.setItem(i, 2, QTableWidgetItem(s_fmt.format(self.broker_master.bid[i])))
            self.ui.tableWidget.setItem(i, 3, QTableWidgetItem(m_fmt.format(self.broker_slave.ask[i])))
            self.ui.tableWidget.setItem(i, 4, QTableWidgetItem(s_fmt.format(self.broker_slave.bid[i])))
            self.ui.tableWidget.setItem(i, 5, QTableWidgetItem(gap_fmt.format(int(self.gap_up[i]))))
            self.ui.tableWidget.setItem(i, 6, QTableWidgetItem(gap_fmt.format(int(self.gap_down[i]))))
            # self.ui.tableWidget.setItem(i, 7, QTableWidgetItem(pro_fmt.format(self.broker_master.profit[i])))
            # self.ui.tableWidget.setItem(i, 8, QTableWidgetItem(pro_fmt.format(self.broker_slave.profit[i])))
            # self.ui.tableWidget.setItem(i, 9, QTableWidgetItem(pro_fmt.format(net_profit)))
            # self.ui.tableWidget.setItem(i, 10, QTableWidgetItem(pl))

        self.ui.tableWidget.repaint()
        # print('update table !')

    def update_op_table(self, **kwargs):

        self.ui.tw_Open_Position.clearContents()

        symbols = kwargs.pop('symbols')
        magnums = kwargs.pop('magnums')
        m_profit = kwargs.pop('m_profit')
        s_profit = kwargs.pop('s_profit')
        net_profits = kwargs.pop('net_profits')
        pnl = kwargs.pop('pnl')

        p_fmt = "{0:0.2f}"

        for i in range(len(magnums)):

            self.ui.tw_Open_Position.setItem(i, 0, QTableWidgetItem(symbols[i]))
            self.ui.tw_Open_Position.setItem(i, 1, QTableWidgetItem(str(magnums[i])))
            self.ui.tw_Open_Position.setItem(i, 2, QTableWidgetItem(p_fmt.format(m_profit[i])))
            self.ui.tw_Open_Position.setItem(i, 3, QTableWidgetItem(p_fmt.format(s_profit[i])))
            self.ui.tw_Open_Position.setItem(i, 4, QTableWidgetItem(p_fmt.format(net_profits[i])))
            self.ui.tw_Open_Position.setItem(i, 5, QTableWidgetItem(pnl[i]))

        self.ui.tw_Open_Position.repaint()

    def get_close_signal(self, trade_type:int,  gap_up, gap_down, arb_close):

        if trade_type == BUY and gap_up > - arb_close:
            return True
        elif trade_type == SELL and gap_down > -arb_close:
            return True
        else:
            return False

    def get_open_signal(self, gap_up, gap_down, arb_open):

        signal = NO_SIGNAL

        if gap_down < -arb_open :
            signal = DOWN
            return signal

        elif gap_up < -arb_open:
            signal = UP
            # print('signal is {}'.format(signal))
            return signal

        else:
            signal = NO_SIGNAL

        # print ('get open signal is {}'.format(signal))
        return signal

    def chk_closeValid(self, broker, magic_number):
        closeValid = False

        openTime, mt4ServerTime = broker.get_opentime_bymagnum(magic_number)
        allowedCloseTime = openTime + dt.timedelta(seconds= self.cfg.scalping_rule)

        if mt4ServerTime > allowedCloseTime:
                closeValid=True

        return closeValid

    def chk_closeTimeValid(self, openTime, mt4ServerTime):
        closeValid = False

        allowedCloseTime = openTime + dt.timedelta(seconds= self.cfg.scalping_rule)

        if mt4ServerTime > allowedCloseTime:
                closeValid=True

        return closeValid

    def chk_open_valid(self, broker, symbol, order_comment):
        open_valid = False

        openTime, mt4ServerTime = broker.get_lastopentime_bysymbol(symbol, order_comment)
        # print("Last position open time: {} , and mt4 server time: {}".format(openTime, mt4ServerTime))

        allowed_open_time = openTime + dt.timedelta(seconds=self.cfg.open_time_gap)

        if mt4ServerTime > allowed_open_time:
            open_valid = True

        # print('Open valid is {}, Server Time is {} and allowed open time is {} and open time is {}'.format(open_valid, mt4ServerTime, allowed_open_time, openTime))

        return open_valid

    def generate_magicno(self):
        r1 = randint(0,9)
        r2 = randint(0,9) * 10
        r3 = randint(0,9) * 100
        r4 = randint(0,9) * 1000
        r5 = randint(1,9) * 10000

        magic_number = r1 + r2 + r3 + r4 + r5
        # print('magic_number is {} '.format(magic_number))
        return magic_number
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