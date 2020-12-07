import zmq
from datetime import datetime

class Broker:
    tms = None
    trade_count = None
    err_msg = None
    req_socket = None
    pull_socket = None
    symbol = None
    magic_number = None

    def __init__(self, broker_ip, magic_no, symbols, suffix, risk='manual', ratio=1, offsets=None):
        self.ip = broker_ip
        self.get_socket(broker_ip)
        self.magic_number = magic_no
        self.risk = risk
        self.lot2usd_ratio = ratio
        self.var_initialization(symbols, suffix, offsets)

    def var_initialization(self, symbols, suffix, offsets):
        self.pos = []
        self.neg = []
        self.gap = []
        self.cnt_arb = []
        self.symbols = []
        self.offsets = []


        for symbol in (symbols):
            self.pos.append(0.0)
            self.neg.append(0.0)
            self.gap.append(0.0)
            self.cnt_arb.append(0)
            self.symbols.append(symbol + suffix)

        if offsets != None:
            for offset in offsets:
                self.offsets.append(offset)

    # To initialize limit that depend on broker digits
    def limit_digit_dep(self, arbitrage_open_param, arbitrage_close_param, pip_step_param, SLIP_param, stop_loss_param  ):

        if self.digits == 2 or self.digits == 4:
            self.arbitrage_open = arbitrage_open_param / 10
            self.arbitrage_close = arbitrage_close_param / 10
            self.pip_step = pip_step_param / 10
            self.SLIP = SLIP_param / 10
            self.stop_loss = stop_loss_param / 10

        else:
            self.arbitrage_open = arbitrage_open_param
            self.arbitrage_close = arbitrage_close_param
            self.pip_step = pip_step_param
            self.SLIP = SLIP_param
            self.stop_loss = stop_loss_param

    def get_socket(self, broker_ip):
        context = zmq.Context()

        socket_req = broker_ip + ':5555'
        socket_pull = broker_ip + ':5556'
        # print("Socket Req is {}".format(socket_req))

        # Create REQ Socket
        reqSocket = context.socket(zmq.REQ)
        reqSocket.connect(socket_req)
        self.req_socket = reqSocket

        # Create PULL Socket
        pullSocket = context.socket(zmq.PULL)
        pullSocket.connect(socket_pull)
        self.pull_socket = pullSocket

    # Function to send commands to ZeroMQ MT4 EA
    def remote_send(self, socket, data):
        msg = None
        try:

            socket.send_string(data)
            socket.setsockopt(zmq.RCVTIMEO, 5000)
            msg = socket.recv_string()

        # except zmq.ZMQError as e:
        except zmq.Again as e:
            print("1.Waiting for PUSH from MetaTrader 4.. :", e)

    def remote_pull(self, socket):

        msg = None
        try:
            socket.setsockopt(zmq.RCVTIMEO, 5000)
            msg = socket.recv_string()
            # msg = socket.recv(flags=zmq.NOBLOCK)

        # except zmq.ZMQError as e:
        except zmq.Again as e:
            print("2.Waiting for PUSH from MetaTrader 4... '{}': {}".format(self.ip,e))

        return msg

    def get_price(self, symbols):
        # print(symbols)

        sym = ''
        for symbol in symbols:
            sym = sym + '|' + symbol

        # print (sym)
        get_rates = "RATES" + sym
        # print (get_rates)

        self.remote_send(self.req_socket, get_rates)
        msg = self.remote_pull(self.pull_socket)

        self.bid = []
        self.ask = []
        self.spread = []
        self.digits = []
        self.avg_price = []
        for i in range(len(symbols)):
            self.bid.append(0.0)
            self.ask.append(0.0)
            self.spread.append(0.0)
            self.digits.append(0)
            self.avg_price.append(0.0)

        # print (msg)
        if msg is not None:
            quote = msg.split('|')
            self.tms = datetime.strptime(quote[0], '%Y.%m.%d %H:%M:%S')

            for i in range(len(symbols)):
                self.bid[i] = float(quote[(i * 4) + 1])
                self.ask[i] = float(quote[(i * 4) + 2])
                self.spread[i] = float(quote[(i * 4) + 3])
                self.digits[i] = int(float(quote[(i * 4) + 4]))
                self.avg_price[i] = round((self.bid[i] + self.ask[i]) / 2, self.digits[i])
            # print i

            # print self.bid, self.ask, self.avg_price

    def get_test_price(self, symbols, master_slave):
        # print(symbols)

        sym = ''
        for symbol in symbols:
            sym = sym + '|' + symbol

        # print (sym)
        get_rates = "TESTRATES|" + master_slave + sym
        # print ("Outgoing get test rates : '{}'".format(get_rates))

        self.remote_send(self.req_socket, get_rates)
        msg = self.remote_pull(self.pull_socket)

        self.bid = []
        self.ask = []
        self.spread = []
        self.digits = []
        self.avg_price = []
        for i in range(len(symbols)):
            self.bid.append(0.0)
            self.ask.append(0.0)
            self.spread.append(0.0)
            self.digits.append(0)
            self.avg_price.append(0.0)

        # print ("Incoming get test rates : '{}'".format(msg))
        if msg is not None:
            quote = msg.split('|')
            self.tms = datetime.strptime(quote[0], '%Y.%m.%d %H:%M:%S')

            for i in range(len(symbols)):
                self.bid[i] = float(quote[(i * 4) + 1])
                self.ask[i] = float(quote[(i * 4) + 2])
                self.spread[i] = float(quote[(i * 4) + 3])
                self.digits[i] = int(float(quote[(i * 4) + 4]))
                self.avg_price[i] = round((self.bid[i] + self.ask[i]) / 2, self.digits[i])
            # print i

            # print self.bid, self.ask, self.avg_price


    def get_count(self, symbols):

        sym = ''
        for s in symbols:
            sym = sym + '|' + s

        self.trade_count = []
        for a in range(len(symbols)):
            self.trade_count.append(0)

        req_count = "COUNT|" + str(self.magic_number) + sym

        self.remote_send(self.req_socket, req_count)
        msg = self.remote_pull(self.pull_socket)

        # msg = 'COUNT|1|2|3|4|5|6'
        # print msg

        if msg is not None:
            quote = msg.split('|')
            for i in range(len(symbols)):
                # print i, '\t', quote[i + 1]
                self.trade_count[i] = int(float(quote[i + 1]))

            # print self.trade_count

    def get_test_OP(self, order_comment):

        req_count = "TEST_OPEN_POSITION|" + order_comment

        self.remote_send(self.req_socket, req_count)
        msg = self.remote_pull(self.pull_socket)

        if msg is not None:
            quote = msg.split('|')
            timestamp= quote[0]
            test_activate = quote[1]

        return test_activate

    def get_openTime(self, symbol):

        lastOpenTime = None
        mt4ServerTime = None
        req_OpenTime = "LASTOPENTIME|" + str(self.magic_number) + "|" + symbol

        self.remote_send(self.req_socket, req_OpenTime)
        msg = self.remote_pull(self.pull_socket)
        # print(msg)

        if msg is not None:
            quote = msg.split('|')
            lastOpenTime = datetime.strptime(quote[0], '%Y.%m.%d %H:%M:%S')
            mt4ServerTime = datetime.strptime(quote[1], '%Y.%m.%d %H:%M:%S')

        return lastOpenTime, mt4ServerTime

    def get_opentime_bymagnum(self, magic_number):

        lastOpenTime = None
        mt4ServerTime = None
        req_OpenTime = "LASTOPENTIME_MAGIC|" + str(magic_number)

        self.remote_send(self.req_socket, req_OpenTime)
        msg = self.remote_pull(self.pull_socket)
        # print(msg)

        if msg is not None:
            quote = msg.split('|')
            lastOpenTime = datetime.strptime(quote[0], '%Y.%m.%d %H:%M:%S')
            mt4ServerTime = datetime.strptime(quote[1], '%Y.%m.%d %H:%M:%S')

        return lastOpenTime, mt4ServerTime

    # this function will return trade count, order type  and  last price
    def get_order_status(self, symbols):
        sym = ''
        for symbol in self.symbols:
            sym = sym + '|' + symbol

        get_status = "STATUS|" + str(self.magic_number) + sym
        # print get_status

        self.remote_send(self.req_socket, get_status)
        msg = self.remote_pull(self.pull_socket)

        # print msg

        self.trade_count = []
        self.order_type = []
        self.last_price = []
        for i in range(len(symbols)):
            self.trade_count.append(0.0)
            self.order_type.append(None)
            self.last_price.append(0.0)

        # print msg
        if msg is not None:
            quote = msg.split('|')

            for i in range(len(symbols)):
                self.trade_count[i] = int(float(quote[(i * 3) + 0]))
                self.order_type[i] = int(float(quote[(i * 3) + 1]))
                self.last_price[i] = float(quote[(i * 3) + 2])

            # print self.trade_count, self.order_type, self.last_price

    # this function will return trade count, order type  and  last price
    def get_open_price(self, symbol):

        get_price = "OPENPRICE|" + str(self.magic_number) + symbol
        # print get_status

        self.remote_send(self.req_socket, get_price)
        msg = self.remote_pull(self.pull_socket)

        # print msg

        trade_count = 0
        order_type = None
        price = []

        # print msg
        if msg is not None:
            quote = msg.split('|')
            trade_count = int(float(quote[0]))
            order_type = quote[1]
            for i in range(trade_count):
                price.append(quote[1 + i])

        return trade_count, order_type, price

    def get_profit(self, symbols):

        sym = ''
        for s in symbols:
            sym = sym + '|' + s

        self.profit = []
        for a in range(len(symbols)):
            self.profit.append(0.0)

        req_count = "PROFIT|" + str(self.magic_number) + sym

        # print('send request profit : ' + req_count)
        self.remote_send(self.req_socket, req_count)
        #        sys.exit()

        msg = self.remote_pull(self.pull_socket)

        # print('received read profit : ' + msg)

        if msg is not None:
            quote = msg.split('|')
            for i in range(len(symbols)):
                # print i, '\t', quote[i + 1]
                self.profit[i] = int(float(quote[i + 1]))

        # print(self.profit)

    def get_profit2(self, magnums):

        req_profit = 'PROFIT2'
        for magnum in magnums:
            req_profit = req_profit + '|' + str(magnum)
        # print('send request profit : ' + req_count)

        self.remote_send(self.req_socket, req_profit)
        msg = self.remote_pull(self.pull_socket)

        if msg is not None:
            quote = msg.split('|')
            str_profit = quote[1:]

        profit = [float(p) for p in str_profit]

        return profit

    def send_order(self, order_type, symbol, price, lot=0.01, slip=10, stop_loss=0, comments="no comments"):

        # format 'TRADE|OPEN|ordertype|symbol|openprice|lot|SL|TP|Slip|comments|magicnumber'

        order = "TRADE|OPEN|" + str(order_type) + "|" + symbol + "|" + str(price) + "|" + str(lot) + "|" + str(
            stop_loss) + "|0|" + str(slip) + "|" + comments + "|" + str(self.magic_number)
        print(order)

        self.remote_send(self.req_socket, order)

    def send_order2(self, **kwargs):

        # format 'TRADE|OPEN|ordertype|symbol|openprice|lot|SL|TP|Slip|comments|magicnumber'

        order = "TRADE|OPEN|" \
                + str(kwargs.pop('order_type')) + "|" \
                + kwargs.pop('symbol') + "|" \
                + str(kwargs.pop('price')) + "|" \
                + str(kwargs.pop('lot', 0.01)) + "|" \
                + str(kwargs.pop('stop_loss', 0)) + "|0|" \
                + str(kwargs.pop('slip', 10)) + "|" \
                + kwargs.pop('comments','no comment') + "|" \
                + str(kwargs.pop('magic_number'))
        print(order)

        self.remote_send(self.req_socket, order)

    def order_close(self, symbols):

        str_symb = ''
        # print symbols
        for s in symbols:
            str_symb = str_symb + '|' + s
        # print str_symb

        # format 'TRADE|CLOSE|magicnumber|symbol1, symbol2, ..'
        close_order = 'TRADE|CLOSE|' + str(self.magic_number) + str_symb

        print(close_order)
        # sys.exit()

        self.remote_send(self.req_socket, close_order)

    def order_close2(self, **kwargs):

        close_order = 'CLOSE2|' + str(kwargs.get('magic_number'))
        print(close_order)

        self.remote_send(self.req_socket, close_order)

    def get_zmq_ver(self):

        chk_ver = 'EAVERSION'
        print('Check ZMQ version')
        self.remote_send(self.req_socket, chk_ver)
        msg = self.remote_pull(self.pull_socket)

        self.zmq_mt4_ver = msg

    def get_acct_info(self):

        acct_info = 'ACCTINFO'
        # print 'Check account info'
        self.remote_send(self.req_socket, acct_info)
        msg = self.remote_pull(self.pull_socket)
        # print('message is :',msg)

        if msg is not None:
            quote = msg.split('|')
            self.company = quote[0]
            self.acctName = quote[1]
            self.acctNumber = int(float(quote[2]))
            self.balance = float(quote[3])
            self.profit = float(quote[4])

            if quote[5] == 'true' or quote[5] == 'True':
                self.connection = True
            else:
                self.connection = False

    def init_symbol(self):

        str_symb = ''
        for s in self.symbols:
            str_symb = str_symb + '|' + s

        init_symbols = 'INITIALIZE' + str_symb
        print('Initialize MT4 Symbols ...')

        self.remote_send(self.req_socket, init_symbols)

    def get_lots(self, minLOT, LOTS):
        self.lots = 0.0

        # ----------------------
        if minLOT == 0.01:
            rounders = 2
        elif minLOT == 0.1:
            rounders = 1
        else:
            rounders = 0

        # ------------------------
        if self.risk == 'HIGH':
            pipRisk = 200
        elif self.risk == 'MEDIUM':
            pipRisk = 500
        elif self.risk == 'LOW':
            pipRisk = 1000

        # ----------------------------
        if self.risk != 'manual':
            usdPerPip = self.balance / pipRisk
            self.lots = round((usdPerPip / self.lot2usd_ratio), rounders)
        elif self.risk == 'manual':
            self.lots = LOTS * self.lot2usd_ratio

    def get_magnums(self):

        magic = 'MAGIC_NUMBER'
        self.remote_send(self.req_socket, magic)
        msg = self.remote_pull(self.pull_socket)

        if msg is not None:
            quote = msg.split('|')
            key_word = quote[0]
            magic_number = quote[1:]

        magic_number = [int(m) for m in magic_number]
        # print(magic_number)

        return magic_number

    def get_symbols(self, magnums):

        req_symbols = 'SYMBOLS'
        for magnum in magnums:
            req_symbols = req_symbols + "|" + str(magnum)

        self.remote_send(self.req_socket, req_symbols)
        msg = self.remote_pull(self.pull_socket)

        if msg is not None:
            quote = msg.split('|')
            key_word = quote[0]
            symbols = quote[1:]

        return symbols

    def get_lastopentime_bysymbol(self, symbol, order_comment="test123"):

        lastOpenTime = None
        mt4ServerTime = None
        req_OpenTime = "LASTOPENTIME_SYMBOL|" + symbol + "|" + order_comment

        self.remote_send(self.req_socket, req_OpenTime)
        msg = self.remote_pull(self.pull_socket)
        # print(msg)

        if msg is not None:
            quote = msg.split('|')
            lastOpenTime = datetime.strptime(quote[0], '%Y.%m.%d %H:%M:%S')
            mt4ServerTime = datetime.strptime(quote[1], '%Y.%m.%d %H:%M:%S')


        return lastOpenTime, mt4ServerTime

    def get_lastprice_bysymbol(self, symbol, trade_type):

        req_OpenTime = "LASTPRICE_SYMBOL|" + symbol + "|" + str(trade_type)

        self.remote_send(self.req_socket, req_OpenTime)
        msg = self.remote_pull(self.pull_socket)
        # print(msg)

        if msg is not None:
            quote = msg.split('|')
            price = float(quote[0])
            digits = int(quote[1])

        # print('open price   = {}'.format(price))

        return price

if __name__ == "__main__":
    master_ip = '10.0.0.1'
    magic_number = 12345
    master_symbol ='USDJPY'
    suffix = ''
    master_broker = Broker('tcp://' + master_ip, magic_number, master_symbol, suffix)
