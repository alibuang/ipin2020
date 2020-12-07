//+------------------------------------------------------------------+
//|                                       ZeroMQ_MT4_EA_Template.mq4 |
//|                                    Copyright 2017, Darwinex Labs |
//|                                        https://www.darwinex.com/ |
//+------------------------------------------------------------------+
#property copyright "Copyright 2017, Darwinex Labs."
#property link      "https://www.darwinex.com/"
#property version   "1.00"
#property strict

// Required: MQL-ZMQ from https://github.com/dingmaotu/mql-zmq
#include <Zmq/Zmq.mqh>

string PROJECT_NAME = "Ali ZMQ";
input string ZEROMQ_PROTOCOL = "tcp";
input string HOSTNAME = "127.0.0.101";
input int REP_PORT = 5555;
input int PUSH_PORT = 5556;
input int MILLISECOND_TIMER = 1;  // 1 millisecond

input string t0 = "--- Trading Parameters ---";
input int MagicNumber = 123456;
input int MaximumOrders = 1;
input double MaximumLotSize = 0.01;

// CREATE ZeroMQ Context
Context context(PROJECT_NAME);

// CREATE ZMQ_REP SOCKET
Socket repSocket(context,ZMQ_REP);

// CREATE ZMQ_PUSH SOCKET
Socket pushSocket(context,ZMQ_PUSH);

// VARIABLES FOR LATER
uchar data[];
ZmqMsg request;

string ea_ver = "mt4zeromq_1.0";
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
//---

   EventSetMillisecondTimer(MILLISECOND_TIMER);     // Set Millisecond Timer to get client socket input
   
   Print("[REP] Binding MT4 Server to Socket on Port " + REP_PORT + "..");   
   Print("[PUSH] Binding MT4 Server to Socket on Port " + PUSH_PORT + "..");
   
   repSocket.bind(StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, HOSTNAME, REP_PORT));
   pushSocket.bind(StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, HOSTNAME, PUSH_PORT));
   
   /*
       Maximum amount of time in milliseconds that the thread will try to send messages 
       after its socket has been closed (the default value of -1 means to linger forever):
   */
   
   repSocket.setLinger(1000);  // 1000 milliseconds
   
   /* 
      If we initiate socket.send() without having a corresponding socket draining the queue, 
      we'll eat up memory as the socket just keeps enqueueing messages.
      
      So how many messages do we want ZeroMQ to buffer in RAM before blocking the socket?
   */
   
   repSocket.setSendHighWaterMark(5);     // 5 messages only.
   
//---
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
//---
   Print("[REP] Unbinding MT4 Server from Socket on Port " + REP_PORT + "..");
   repSocket.unbind(StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, HOSTNAME, REP_PORT));
   
   Print("[PUSH] Unbinding MT4 Server from Socket on Port " + PUSH_PORT + "..");
   pushSocket.unbind(StringFormat("%s://%s:%d", ZEROMQ_PROTOCOL, HOSTNAME, PUSH_PORT));
   
}
//+------------------------------------------------------------------+
//| Expert timer function                                            |
//+------------------------------------------------------------------+
void OnTimer()
{
//---

   /*
      For this example, we need:
      1) socket.recv(request,true)
      2) MessageHandler() to process the request
      3) socket.send(reply)
   */
   
   // Get client's response, but don't wait.
   repSocket.recv(request,true);
   //Print("Okay 1");
   // MessageHandler() should go here.   
   ZmqMsg reply = MessageHandler(request);
   
   // socket.send(reply) should go here.
   repSocket.send(reply);
}
//+------------------------------------------------------------------+

ZmqMsg MessageHandler(ZmqMsg &request) {
   
   // Output object
   ZmqMsg reply;
   string data2send;
   
   // Message components for later.
   string components[];
   
    
      if(request.size() > 0) {
//@debug-    if(request.size() == 0) {
   
      // Get data from request   
      ArrayResize(data, request.size());
      request.getData(data);
      
      string dataStr = CharArrayToString(data);
      //PrintFormat("Data received are %s ",dataStr);
           
      // Process data
      ParseZmqMessage(dataStr, components);
//@debug-      string dataStrDebug = "LASTOPENTIME|0|GBPUSD_";
//@debug-      ParseZmqMessage(dataStrDebug, components);
      
      // Interpret data
      InterpretZmqMessage(&pushSocket, components);
      
      // Construct response
      data2send = StringSubstr(dataStr,0,27);
      ZmqMsg ret(StringFormat("[SERVER]: %s", data2send));
     
      reply = ret;
      
   }
   else {
      // NO DATA RECEIVED
   }
   
   return(reply);
}

// Interpret Zmq Message and perform actions
void InterpretZmqMessage(Socket &pSocket, string& compArray[]) {

   //Print("ZMQ: Interpreting Message..");
   //Print("Okay 5");   
   string broker="", comments="", symbol[],retStr[];
   int switch_action = 0, magic_number = 0,  order_type = 9, err_cd=0, stop_loss=0, take_profit=0, slip=0, retCount[], shift;
   ENUM_TIMEFRAMES timeframe;
   double open_price=0.0, lot=0.0;
   datetime timestamp = TimeLocal(), tm;
   string time_str = TimeToString(timestamp,TIME_DATE|TIME_SECONDS);
   int magNumRead[];
   string symbolsRead;
   
   if(compArray[0] == "TRADE" && compArray[1] == "OPEN"){
      switch_action = 1;
      order_type = StringToInteger(compArray[2]);
      ArrayResize(symbol,1);
      symbol[0] = compArray[3];
      open_price = StringToDouble(compArray[4]);
      lot = StringToDouble(compArray[5]);
      stop_loss = StringToInteger(compArray[6]);
      take_profit = StringToInteger(compArray[7]);
      slip = StringToInteger(compArray[8]);
      comments = compArray[9];
      magic_number = StringToInteger(compArray[10]);
   }
   
   else if(compArray[0] == "RATES"){
      //Print("Okay 6 ... ");
      switch_action = 2;
      
      //Print(ArraySize(compArray));
      ArrayResize(symbol,ArraySize(compArray)-1);
      for(int j=0; j < ArraySize(compArray)-1;j++)
         symbol[j] = compArray[j+1];
      
      //Print("Okay 7...");
      }
      
   else if(compArray[0] == "TRADE" && compArray[1] == "CLOSE"){
      switch_action = 3;
      magic_number =StringToInteger(compArray[2]);
      
      ArrayResize(symbol,ArraySize(compArray)-3);
      for(int j=0; j < ArraySize(compArray)-3;j++)
         symbol[j] = compArray[j+3];
      
      
   }
   else if(compArray[0] == "DATA")
      switch_action = 4;
      
   else if(compArray[0] == "COMPANY")
      switch_action = 5;
   
   else if(compArray[0] == "COUNT"){
      switch_action = 6;
      magic_number = compArray[1];
      
      ArrayResize(symbol,ArraySize(compArray)-2);
      for(int j=0; j < ArraySize(compArray)-2;j++)
         symbol[j] = compArray[j+2];
    }
    
    else if(compArray[0] == "STATUS"){
      switch_action = 7;
      magic_number = compArray[1];
      
      ArrayResize(symbol,ArraySize(compArray)-2);
      for(int j=0; j < ArraySize(compArray)-2;j++)
         symbol[j] = compArray[j+2];
    }
    
    else if(compArray[0] == "ACCTINFO"){
         switch_action = 8;
    }
    
    else if(compArray[0] == "EAVERSION"){
         switch_action = 9;
    }
    
    else if(compArray[0] == "LASTOPENTIME"){
         switch_action = 10;
         magic_number = compArray[1];        
         
         ArrayResize(symbol,1);
         symbol[0] = compArray[2];
    }
    else if(compArray[0] == "INITIALIZE"){
         switch_action = 11;
         
         ArrayResize(symbol,ArraySize(compArray)-1);
         for(int j=0; j < ArraySize(compArray)-1;j++)
            symbol[j] = compArray[j+1];
    }    
    else if(compArray[0] == "OHLC"){
         switch_action = 12;
         timeframe = compArray[1];
         shift = compArray[2];
         
         ArrayResize(symbol,ArraySize(compArray)-3);
         for(int j=0; j < ArraySize(compArray)-3;j++)
            symbol[j] = compArray[j+3];
    
    }
   
   else if(compArray[0] == "PROFIT"){
         switch_action = 13;
         magic_number = StringToInteger(compArray[1]);
         
         ArrayResize(symbol,ArraySize(compArray)-2);
         for(int j=0; j < ArraySize(compArray)-2;j++)
            symbol[j] = compArray[j+2];
               
    }

   else if(compArray[0] == "MAGIC_NUMBER"){
         switch_action = 14;
                      
    }
    
    else if(compArray[0] == "PROFIT2"){
         switch_action = 15;
                  
         ArrayResize(magNumRead,ArraySize(compArray)-1);
         for(int j=0; j < ArraySize(compArray)-1;j++)
            magNumRead[j] = compArray[j+1];
               
    }
    
     else if(compArray[0] == "CLOSE2"){
         switch_action = 16;
         magic_number = compArray[1];
    }

    else if(compArray[0] == "SYMBOLS"){
         switch_action = 17;
         
         ArrayResize(magNumRead,ArraySize(compArray)-1);
         for(int j=0; j < ArraySize(compArray)-1;j++)
            magNumRead[j] = compArray[j+1];
         
    }
    else if(compArray[0] == "LASTOPENTIME_MAGIC"){
         switch_action = 18;
         magic_number = compArray[1];
     }
     else if(compArray[0] == "LASTOPENTIME_SYMBOL"){
         switch_action = 19;
         symbolsRead = compArray[1];
         }
   
   
   
   string ret = "";
   int ticket = -1;
   bool ans = false;
   double price_array[];
   ArraySetAsSeries(price_array, true);
   int count = 0, last_order = 9;
   double last_price = 0.0;
   int price_count = 0;
   int space= 0;
   string company ;
   double balance ;
   string name ;
   int accountNumber;
   double profit;
   datetime last_openOrderTime, serverTime ;
   bool connection = false;
   string mag_nums, profitRead;
            
   
   switch(switch_action) 
   {
      case 1: 
         
         err_cd = send_Order(order_type, symbol[0], open_price, lot ,stop_loss, take_profit, slip, comments, magic_number, 101);
         ret = StringFormat("%d", err_cd);
                  
         //InformPullClient(pSocket, ret);
         //InformPullClient(pSocket,"OPEN TRADE Instruction Received");
         // IMPLEMENT OPEN TRADE LOGIC HERE
         break;
      case 2: 
         ret = time_str; 
        
         ArrayResize(retStr,ArraySize(symbol));
         
         //RefreshRates();
         
         if(ArraySize(compArray) > 1) 
            for(int i=0;i<ArraySize(symbol);i++){
               retStr[i]=GetBidAsk(symbol[i]);
               ret = ret + "|" + retStr[i];
         }
         
         //Print(ret);
         InformPullClient(pSocket, ret); 
         break;
      case 3:
        // InformPullClient(pSocket,"CLOSE TRADE Instruction Received");
         
         for (int c=0; c<ArraySize(symbol); c++)
               err_cd = CloseAll(symbol[c], magic_number);
         
         ret = StringFormat("%d", err_cd);
         //InformPullClient(pSocket, ret);
         
         break;
      /*
      case 4:
         InformPullClient(pSocket, "HISTORICAL DATA Instruction Received");
         
         // Format: DATA|SYMBOL|TIMEFRAME|START_DATETIME|END_DATETIME
         price_count = CopyClose(compArray[1], StringToInteger(compArray[2]), 
                        StringToTime(compArray[3]), StringToTime(compArray[4]), 
                        price_array);
         
         if (price_count > 0) {
            
            ret = "";
            
            // Construct string of price|price|price|.. etc and send to PULL client.
            for(int i = 0; i < price_count; i++ ) {
               
               if(i == 0)
                  ret = compArray[1] + "|" + DoubleToString(price_array[i], 5);
               else if(i > 0) {
                  ret = ret + "|" + DoubleToString(price_array[i], 5);
               }   
            }
            
            Print("Sending: " + ret);
            
            // Send data to PULL client.
            InformPullClient(pSocket, StringFormat("%s", ret));
            // ret = "";
         }
            
         break;
         */
      case 5: 
         space = StringFind(AccountInfoString(ACCOUNT_COMPANY)," ",0);
         broker = StringSubstr(AccountInfoString(ACCOUNT_COMPANY),0, space);
         InformPullClient(pSocket, broker);
         
         break;
         
      case 6:
         
         ret = "COUNT"; 
         ArrayResize(retCount,ArraySize(symbol));
         
         if(ArraySize(compArray) > 1) 
            for(int i=0;i<ArraySize(symbol);i++){
               retCount[i]=CountTrades(symbol[i],magic_number);
               ret = ret + "|" + retCount[i];
              // Print("Count is ",ret,"\nsymbol is ",symbol[i]);
         }
         //Print(ret);
      
         InformPullClient(pSocket, ret);
         break;
         
      case 7:
         
         ret = ""; 
         
         if(ArraySize(compArray) > 1) 
            for(int i=0;i<ArraySize(symbol);i++){
            
               count = CountTrades(symbol[i],magic_number); 
               
               if(count >0){          
               last_order = get_lastOrder_type(symbol[i],magic_number);
               last_price = get_lastPrice_NEW(symbol[i],magic_number);
               }
               else{
                  last_order = 9;
                  last_price = 0.0;               
               }
               
               ret = ret + count + "|" + last_order + "|" + last_price +"|";
         }
         //Print(ret);
      
         InformPullClient(pSocket, ret);
         break;
         
      case 8:
      
            ret = "";
            company = AccountInfoString(ACCOUNT_COMPANY);
            balance = AccountInfoDouble(ACCOUNT_BALANCE);
            name = AccountInfoString(ACCOUNT_NAME);
            accountNumber = AccountInfoInteger(ACCOUNT_LOGIN);
            profit = AccountInfoDouble(ACCOUNT_PROFIT);
            connection = TerminalInfoInteger(TERMINAL_CONNECTED);
            
            ret = company + "|"+ name + "|" + IntegerToString(accountNumber) + "|" + DoubleToString(balance,2)+ "|" + DoubleToString(profit,2)
                  + "|" + connection; 
            //Print("info is : ",ret);
            
            InformPullClient(pSocket, ret);     
            break;
            
      case 9:
      
            ret = ea_ver;
            Print(ea_ver);
            InformPullClient(pSocket, ret);     
            break;        
            
      case 10:
            ret = "";
           
            serverTime = TimeCurrent();
           
            last_openOrderTime = get_lastDateTime(symbol[0], magic_number);
            ret = TimeToString(last_openOrderTime, TIME_DATE|TIME_SECONDS) + "|" + TimeToString(serverTime, TIME_DATE|TIME_SECONDS);
            InformPullClient(pSocket, ret);
                        
            break;
            
      case 11:
            
            //PrintFormat("Okay HERE ----------> ");
            //break;
            get_Symbols(symbol);
            break;
            
      case 12: 
         
         tm = iTime(symbol[0], timeframe, shift);
         time_str = TimeToString(tm,TIME_DATE|TIME_SECONDS);
         ret = time_str; 
         
         ArrayResize(retStr,ArraySize(symbol));
         //RefreshRates();
         
         if(ArraySize(compArray) > 1) 
            for(int i=0;i<ArraySize(symbol);i++){
               retStr[i]=Get_OHLC(symbol[i], timeframe, shift);
               ret = ret + "|" + retStr[i];
               //Print(symbol[i]+" "+ timeframe +" "+ shift);
         }
         
         //Print(ret);
         InformPullClient(pSocket, ret); 
         break;
         
      
      case 13:
      
         ret = "PROFIT"; 
         ArrayResize(retCount,ArraySize(symbol));
         
         if(ArraySize(compArray) > 1) 
            for(int i=0;i<ArraySize(symbol);i++){
               retCount[i]=CountProfit(symbol[i],magic_number);
               ret = ret + "|" + retCount[i];
              // Print("Count is ",ret,"\nsymbol is ",symbol[i]);
         }
         //Print(ret);
      
         InformPullClient(pSocket, ret);
         break;
         
      case 14:
      
         ret = "MAGIC_NUMBER";
         
         mag_nums = GetMagicNumbers();         
         ret = ret + mag_nums;
         
         InformPullClient(pSocket, ret);
               
         break;
                     
      
   
      case 15:
      
         ret = "PROFIT"; 
         ArrayResize(retCount,ArraySize(magNumRead));
         
         if(ArraySize(compArray) > 1) 
            for(int i=0;i<ArraySize(magNumRead);i++){
               profitRead = GetProfit2(magNumRead[i]);
               ret = ret + "|" + profitRead;
              // Print("Count is ",ret,"\nsymbol is ",symbol[i]);
         }
         //Print(ret);
      
         InformPullClient(pSocket, ret);
         break;
   
  // Print(ret);
  
      case 16:
         
        err_cd = CloseByMagicNumber( magic_number );
         
         ret = StringFormat("%d", err_cd);
         //InformPullClient(pSocket, ret);
         
         break;
  
      case 17:
      
         ret = "SYMBOLS"; 
         
         //ArrayResize(retCount,ArraySize(magNumRead));
         
         //PrintFormat("The first magic number is %d and the size of array is %d", magNumRead[0], ArraySize(magNumRead) );
         if(ArraySize(compArray) > 1) 
            for(int i=0;i<ArraySize(magNumRead);i++){
               //PrintFormat("Magic number is %d", magNumRead[i]);
                ret = ret + "|" + GetSymbolByMagic(magNumRead[i]);
            }         
         
         //PrintFormat("Symbols retrieved are : %s ", ret);
                  
         InformPullClient(pSocket, ret);
               
         break;
         
       case 18:
            ret = "";
           
            serverTime = TimeCurrent();
           
            last_openOrderTime = get_lastTimeByMagic(magic_number);
            ret = TimeToString(last_openOrderTime, TIME_DATE|TIME_SECONDS) + "|" + TimeToString(serverTime, TIME_DATE|TIME_SECONDS);
            InformPullClient(pSocket, ret);
                        
            break; 
        
        case 19:
            ret = "";
           
            serverTime = TimeCurrent();
           
            last_openOrderTime = get_lastTimeBySymbol(symbolsRead);
            ret = TimeToString(last_openOrderTime, TIME_DATE|TIME_SECONDS) + "|" + TimeToString(serverTime, TIME_DATE|TIME_SECONDS);
            InformPullClient(pSocket, ret);
                        
            break;
         
  
       default: 
            break;   
         
   }
}

//----------------------------------------------------------
// This function is to enable list of symbols in marketwatch
//----------------------------------------------------------
bool get_Symbols(string& listSymbols[]){

   bool success = false;
   string symbolName;
     
   int totalSymbol= SymbolsTotal(true);
  // Print(totalSymbol);
   
   //Print("Here --------------> 456");
   
   for(int i=totalSymbol-1 ; i >= 0 ; i--){
      symbolName = SymbolName(i, true);
      //Print(symbolName);
      SymbolSelect(symbolName, false);
      
   }     

   int listsize = ArraySize(listSymbols);
   for(int j=0; j<listsize ; j++){
       SymbolSelect(listSymbols[j], true);               
       //Print(listSymbols[j], j);
       success = true;
   }  
   
   return success;
}

//+------------------------------------------------------------------+
//|  this subroutine is to find the last datetime for the open position                                                          |
//+------------------------------------------------------------------+
datetime get_lastDateTime(string symbol, int magic_number){
     
      datetime oldOrderTime=NULL, orderTime = NULL;
      int cnt, oldticketnumber=0, ticketnumber;
      int order_total = OrdersTotal();
      int order_chk;
      int trade;
      
      
      for(trade=PositionsTotal()-1;trade>=0;trade--){
         PositionSelectByTicket(PositionGetTicket(trade));
               
          if(PositionGetString(POSITION_SYMBOL)!=symbol ||PositionGetInteger(POSITION_MAGIC)!=magic_number)
              continue;
               
          if(PositionGetString(POSITION_SYMBOL)==symbol && PositionGetInteger(POSITION_MAGIC)== magic_number)
               if(PositionGetInteger(POSITION_TYPE)== POSITION_TYPE_SELL || PositionGetInteger(POSITION_TYPE)== POSITION_TYPE_BUY)  
                     orderTime = PositionGetInteger(POSITION_TIME) ; 
       }
          
   return(orderTime);
}


//+------------------------------------------------------------------+
//|  this subroutine is to find the last datetime for the open position                                                          |
//+------------------------------------------------------------------+
datetime get_lastTimeByMagic(int magic_number){
     
      datetime oldOrderTime=NULL, orderTime = NULL;
      int cnt, oldticketnumber=0, ticketnumber;
      int order_total = OrdersTotal();
      int order_chk;
      int trade;
      
      
      for(trade=PositionsTotal()-1;trade>=0;trade--){
         PositionSelectByTicket(PositionGetTicket(trade));
               
          if(PositionGetInteger(POSITION_MAGIC)!=magic_number)
              continue;
               
          if(PositionGetInteger(POSITION_MAGIC)== magic_number)
               if(PositionGetInteger(POSITION_TYPE)== POSITION_TYPE_SELL || PositionGetInteger(POSITION_TYPE)== POSITION_TYPE_BUY)  
                     orderTime = PositionGetInteger(POSITION_TIME) ; 
      }               
       
   return(orderTime);
}

datetime get_lastTimeBySymbol(string symbol){
     
      datetime prevTime = NULL, currentTime = NULL, wantedTime = NULL;
      int cnt, oldticketnumber=0, ticketnumber;
      int order_total = OrdersTotal();
      int order_chk;
      int trade;
      
      for(trade=PositionsTotal()-1;trade>=0;trade--){
         PositionSelectByTicket(PositionGetTicket(trade));
               
          if(PositionGetString(POSITION_SYMBOL)!=symbol)
              continue;
               
          if(PositionGetString(POSITION_SYMBOL)==symbol)
               if(PositionGetInteger(POSITION_TYPE)== POSITION_TYPE_SELL || PositionGetInteger(POSITION_TYPE)== POSITION_TYPE_BUY){  
                     
                     currentTime = PositionGetInteger(POSITION_TIME) ; 
                    
                    // PrintFormat("%s 1: order time is %s and older time is %s ",symbol, TimeToString(orderTime, TIME_DATE|TIME_SECONDS), TimeToString(oldOrderTime, TIME_DATE|TIME_SECONDS));
                     if (wantedTime == NULL){
                           wantedTime = currentTime;
                          // PrintFormat("%s: trade :%d (L1) , wanted time is %s and current time is %s ",symbol, trade, TimeToString(wantedTime, TIME_DATE|TIME_SECONDS), TimeToString(currentTime, TIME_DATE|TIME_SECONDS));
                      }
                     else if (wantedTime < currentTime) {                          
                           wantedTime = currentTime;     
                          // PrintFormat("%s: trade :%d (L2), wanted time is %s and current time is %s ",symbol, trade, TimeToString(wantedTime, TIME_DATE|TIME_SECONDS), TimeToString(currentTime, TIME_DATE|TIME_SECONDS));
                     }                     
                                                    
               }
      }               
       
   return(wantedTime);
}



//+------------------------------------------------------------------+
//|  this subroutine is to find the last buy price                                                                |
//+------------------------------------------------------------------+
double get_lastPrice_NEW(string symbol, int magic_number){
     
      double oldorderopenprice=0, orderprice=0.0;
      int cnt, oldticketnumber=0, ticketnumber;
      int order_total = OrdersTotal();
      int order_chk;

      for(cnt= order_total - 1 ;cnt>=0;cnt--){
               order_chk = OrderSelect(OrderGetTicket(cnt));
            if(OrderGetString(ORDER_SYMBOL)!= symbol || OrderGetInteger(ORDER_MAGIC)!=magic_number) continue;
            if(OrderGetString(ORDER_SYMBOL)== symbol && OrderGetInteger(ORDER_MAGIC)==magic_number){
                  ticketnumber=OrderGetInteger(ORDER_TICKET);
                  if(ticketnumber>oldticketnumber){
                        orderprice=OrderGetDouble(ORDER_PRICE_OPEN);
                        oldorderopenprice=orderprice;
                        oldticketnumber=ticketnumber;
                  }
            }
         }
       
   return(orderprice);
}




//----------------------------------------------------
int get_lastOrder_type(string symbol, int magic_number)
{
   int o_type = 9;
   int order_total = OrdersTotal();


   for (int y = order_total - 1 ; y >=0; y--)
   {
      int order_chk = OrderSelect (OrderGetTicket(y));
      if(OrderGetString(ORDER_SYMBOL)!=symbol || OrderGetInteger(ORDER_MAGIC)!=magic_number) continue;
      if(OrderGetInteger(ORDER_MAGIC)==magic_number && OrderGetString(ORDER_SYMBOL)==symbol)
      {
            o_type=OrderGetInteger(ORDER_TYPE); 
            break;                     
      }   
   } 

//------------------
   return(o_type);
}

//----------------------------------------------------------------------
// Parse Zmq Message
void ParseZmqMessage(string& message, string& retArray[]) {
   
   //Print("Parsing: " + message);
  // Print("Okay 4");
   
   string sep = "|";
   ushort u_sep = StringGetCharacter(sep,0);
   
   int splits = StringSplit(message, u_sep, retArray);
  // Print("splits=",splits);
   
  // for(int i = 0; i < splits; i++) {
  //    Print(i + ") " + retArray[i]);
   //}
}


//+------------------------------------------------------------------+
// Generate string for Bid/Ask by symbol
string GetBidAsk(string symbol) {

   //datetime timestamp = TimeLocal();
  // string time_str = TimeToString(timestamp,TIME_DATE|TIME_SECONDS);
   string ret_string;
   
   double bid = SymbolInfoDouble(symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(symbol, SYMBOL_ASK);
   double spread = SymbolInfoInteger(symbol,SYMBOL_SPREAD);
   double digits = SymbolInfoInteger(symbol, SYMBOL_DIGITS);
   
   ret_string = StringFormat("%f|%f|%f|%f", bid, ask, spread, digits);
   //Print(ret_string);
   return(ret_string);
}

// Inform Client
void InformPullClient(Socket& pushSocket, string message) {

   ZmqMsg pushReply(StringFormat("%s", message));
   pushSocket.send(pushReply,true);
   //pushSocket.send(pushReply,true,false);
   
}

//+------------------------------------------------------------------+
//|   This function is to Count number of trades                                                               |e
//+------------------------------------------------------------------+
string CountTrades(string symbol, int magic_number)
{
            int count=0;
            int trade;
            
            //PrintFormat("Order Total is %d ", OrdersTotal());
            //PrintFormat("Position total is %d ", PositionsTotal());
            
            
            for(trade=PositionsTotal()-1;trade>=0;trade--)
              {
               PositionSelectByTicket(PositionGetTicket(trade));
               
              // PrintFormat("count Trade: Ticket # is %d for trade %d ", PositionGetTicket(trade), trade);
               
               if(PositionGetString(POSITION_SYMBOL)!=symbol ||PositionGetInteger(POSITION_MAGIC)!=magic_number)
                  continue;
               if(PositionGetString(POSITION_SYMBOL)==symbol && PositionGetInteger(POSITION_MAGIC)== magic_number)
                  if(PositionGetInteger(POSITION_TYPE)== POSITION_TYPE_SELL || PositionGetInteger(POSITION_TYPE)== POSITION_TYPE_BUY)
                     count++;
               
              }//for
            return(StringFormat("%d",count));
}


string GetMagicNumbers()
{
            int trade;
            string str_magic_no;
                       
            for(trade=PositionsTotal()-1;trade>=0;trade--){
            
               PositionSelectByTicket(PositionGetTicket(trade));
               str_magic_no = str_magic_no + "|" + IntegerToString(PositionGetInteger(POSITION_MAGIC));
            }//for
             
            return(str_magic_no);             
}

string GetSymbolByMagic(int magic_number)
{
            string symbols;
            int trade;
                        
            //Print("Position Total is " + PositionsTotal() );
            for(trade=PositionsTotal()-1;trade>=0;trade--){
             
               PositionSelectByTicket(PositionGetTicket(trade));
              // PrintFormat("count Profit: Ticket # is %d for trade %d ", PositionGetTicket(trade), trade);
               
               if(PositionGetInteger(POSITION_MAGIC)!=magic_number)
                  continue;
               
               if( PositionGetInteger(POSITION_MAGIC)== magic_number)
                  if(PositionGetInteger(POSITION_TYPE)== POSITION_TYPE_SELL || PositionGetInteger(POSITION_TYPE)== POSITION_TYPE_BUY){
                     symbols = PositionGetSymbol(trade);
                    // PrintFormat("Symbol is %s", symbols);
                     break;
                   }
             } 
            
            return(symbols);            
}



//+------------------------------------------------------------------+
//|   This function is to Count profit of trades                                                               |e
//+------------------------------------------------------------------+
string CountProfit(string symbol, int magic_number)
{
            double profit = 0;
            int trade;
            
            
            //Print("Position Total is " + PositionsTotal() );
            for(trade=PositionsTotal()-1;trade>=0;trade--){
             
               PositionSelectByTicket(PositionGetTicket(trade));
              // PrintFormat("count Profit: Ticket # is %d for trade %d ", PositionGetTicket(trade), trade);
               
               if(PositionGetString(POSITION_SYMBOL)!=symbol ||PositionGetInteger(POSITION_MAGIC)!=magic_number)
                  continue;
               
               if(PositionGetString(POSITION_SYMBOL)==symbol && PositionGetInteger(POSITION_MAGIC)== magic_number)
                  if(PositionGetInteger(POSITION_TYPE)== POSITION_TYPE_SELL || PositionGetInteger(POSITION_TYPE)== POSITION_TYPE_BUY)
                     profit += PositionGetDouble(POSITION_PROFIT);
                     //PrintFormat("Profit for ticket # %d is %.2f ",PositionGetTicket(trade), PositionGetDouble(POSITION_PROFIT));
            } 
            //PrintFormat("Total Profit is %.3f ",profit);
            return(StringFormat("%.2f",profit));
            
}

string GetProfit2(int magic_number)
{
            double profit = 0;
            int trade;
                        
            //Print("Position Total is " + PositionsTotal() );
            for(trade=PositionsTotal()-1;trade>=0;trade--){
             
               PositionSelectByTicket(PositionGetTicket(trade));
              // PrintFormat("count Profit: Ticket # is %d for trade %d ", PositionGetTicket(trade), trade);
               
               if(PositionGetInteger(POSITION_MAGIC)!=magic_number)
                  continue;
               
               if( PositionGetInteger(POSITION_MAGIC)== magic_number)
                  if(PositionGetInteger(POSITION_TYPE)== POSITION_TYPE_SELL || PositionGetInteger(POSITION_TYPE)== POSITION_TYPE_BUY){
                     profit = PositionGetDouble(POSITION_PROFIT);
                     break;
                   }
                     
                     //PrintFormat("Profit for ticket # %d is %.2f ",PositionGetTicket(trade), PositionGetDouble(POSITION_PROFIT));
            } 
            //PrintFormat("Total Profit is %.3f ",profit);
            return(StringFormat("%.2f",profit));
            
}


//+----------------------------------------------------------------
// This function is to execute buy command
//+----------------------------------------------------------------
bool send_Order(int order_type,string iSymbol, double iOpenPrice, double iLot,int iStopLoss, int iTakeProfit, int iSlip, string comments, int iMagicNumber, int err_type){

   bool order_status = false;
   int ticket, retry = 1;
   double lot= iLot;
   double open_price = iOpenPrice;
   double stop_loss=0.0;
   double take_profit=0.0;
   int slip = iSlip;
   //string comment_level=comments;
   string str_order_type, err_msg, text_msg;
   int spread_price= 0;
   double point = SymbolInfoDouble(iSymbol,SYMBOL_POINT);
   //Print("Open Price = ",open_price);
   
   if(order_type == ORDER_TYPE_BUY ){
      str_order_type = "Buy";
      if(iStopLoss != 0) stop_loss = open_price - (iStopLoss * point); 
      if(iTakeProfit != 0) take_profit = open_price + (iTakeProfit * point);           
   }    
   else if(order_type == ORDER_TYPE_SELL){
      str_order_type = "Sell"; 
      if(iStopLoss != 0) stop_loss = open_price + (iStopLoss * point);  
      if(iTakeProfit != 0) take_profit = open_price - (iTakeProfit * point);     
   }
    
      //--- declare and initialize the trade request and result of trade request
      MqlTradeRequest request={0};
      MqlTradeResult  result={0};
       //--- parameters of request
            request.action   =TRADE_ACTION_DEAL;                     // type of trade operation
            request.symbol   =iSymbol;                              // symbol
            request.volume   =lot;                                   // volume of 0.1 lot
            request.type     =order_type;                        // order type
            request.price    =open_price; // price for opening
         request.deviation=slip;                                     // allowed deviation from the price
         request.magic    =iMagicNumber;                          // MagicNumber of the order
         request.type_filling = ORDER_FILLING_IOC;
         request.comment = comments;
      //--- send the request
      
         PrintFormat("%s: open price is %f", request.symbol, request.price);
         if(!OrderSend(request,result))
            PrintFormat("%s: OrderSend error %d",request.symbol, GetLastError());     // if unable to send the request, output the error code
             
      //--- information about the operation
        //@alib PrintFormat("retcode=%u  deal=%I64u  order=%I64u",result.retcode,result.deal,result.order);
         
   return order_status;
  }
//+----------------------------------------------------------------
// END
//+----------------------------------------------------------------

//---------------------------------------------------------
// This function is to close all open position
//---------------------------------------------------------
//bool CloseAll(string symbol, int magic_number){
//
//   bool closed=false;
//   int order_type;
//   int slip = 1;
//   bool err_flag;
//   int total_order = OrdersTotal();
//   string err_msg;
//   
//  // Print("Order Total=",total_order);
//   
//   for (int i = total_order - 1; i >= 0; i--) {  //#
//         OrderSelect(OrderGetTicket(i));
//      
//         if (OrderGetInteger(ORDER_MAGIC)== magic_number && OrderGetString(ORDER_SYMBOL)==symbol&&(OrderGetInteger(ORDER_TYPE)== ORDER_TYPE_BUY||OrderGetInteger(ORDER_TYPE)==ORDER_TYPE_SELL)) 
//         {
//            order_type = OrderGetInteger(ORDER_TYPE);
//            err_flag = false;
//            //retry loop if there is error to close position
//            
//               for(int j = 3; j>0 ;j--){   
//                     //RefreshRates();           
//                    
//                      if( order_type == ORDER_TYPE_BUY){
//                           err_flag = OrderClose(OrderGetInteger(ORDER_TYPE), OrderGetDouble(ORDER_VOLUME_CURRENT), SymbolInfoString(OrderGetString(ORDER_SYMBOL),MODE_BID), slip, CLR_NONE);
//                           if(err_flag) {
//                              closed = true;
//                              break;
//                              
//                           }
//                      }
//                      if(order_type == OP_SELL){
//                           err_flag = OrderClose(OrderTicket(), OrderLots(), MarketInfo(OrderGetString(ORDER_SYMBOL), MODE_ASK), slip, CLR_NONE);
//                           if(err_flag) {
//                              closed = true;
//                              break;
//                              
//                           }
//                      }              
//                     else if(err_flag == false){
//                           err_msg = "OrderClose failed with error #" + GetLastError();
//                           Print(err_msg); 
//                           write_error_file(err_msg);
//                           
//                           err_msg = "Line546|CloseAll()|OrderTicket="+OrderTicket()+"|OrderLots="+OrderLots();
//                           Print(err_msg); 
//                           write_error_file(err_msg);                          
//                     }       
//               }                      
//            }                
//    } 
//    
//    return closed;
//    
//}

//+----------------------------------------------------------------
// END
//+----------------------------------------------------------------

bool CloseAll(string symbol, int magic_number){

   bool closeSucess = true;
//--- declare and initialize the trade request and result of trade request
   MqlTradeRequest request;
   MqlTradeResult  result;
   int total=PositionsTotal(); // number of open positions   
//--- iterate over all open positions
   for(int i=total-1; i>=0; i--)
     {
      //--- parameters of the order
      ulong  position_ticket=PositionGetTicket(i);                                      // ticket of the position
      string position_symbol=PositionGetString(POSITION_SYMBOL);                        // symbol 
      int    digits=(int)SymbolInfoInteger(position_symbol,SYMBOL_DIGITS);              // number of decimal places
      ulong  magic=PositionGetInteger(POSITION_MAGIC);                                  // MagicNumber of the position
      double volume=PositionGetDouble(POSITION_VOLUME);                                 // volume of the position
      ENUM_POSITION_TYPE type=(ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);    // type of the position
      //--- output information about the position
      PrintFormat("#%I64u %s  %s  %.2f  %s [%I64d]",
                  position_ticket,
                  position_symbol,
                  EnumToString(type),
                  volume,
                  DoubleToString(PositionGetDouble(POSITION_PRICE_OPEN),digits),
                  magic);
      //--- if the MagicNumber matches
      if(magic==magic_number)
        {
         //--- zeroing the request and result values
         ZeroMemory(request);
         ZeroMemory(result);
         //--- setting the operation parameters
         request.action   =TRADE_ACTION_DEAL;        // type of trade operation
         request.position =position_ticket;          // ticket of the position
         request.symbol   =position_symbol;          // symbol 
         request.volume   =volume;                   // volume of the position
         request.deviation=5;                        // allowed deviation from the price
         request.magic    =magic_number;             // MagicNumber of the position
         request.type_filling = ORDER_FILLING_IOC;
         //--- set the price and order type depending on the position type
         if(type==POSITION_TYPE_BUY)
           {
            request.price=SymbolInfoDouble(position_symbol,SYMBOL_BID);
            request.type =ORDER_TYPE_SELL;
           }
         else
           {
            request.price=SymbolInfoDouble(position_symbol,SYMBOL_ASK);
            request.type =ORDER_TYPE_BUY;
           }
         //--- output information about the closure
         PrintFormat("Close #%I64d %s %s",position_ticket,position_symbol,EnumToString(type));
         //--- send the request
         if(!OrderSend(request,result)){
            PrintFormat("OrderSend error %d",GetLastError());  // if unable to send the request, output the error code
            closeSucess = false;
            }
         //--- information about the operation   
         PrintFormat("retcode=%u  deal=%I64u  order=%I64u",result.retcode,result.deal,result.order);
         //---
        }
     }
     return closeSucess;
  }

bool CloseByMagicNumber(int magic_number){

   bool closeSucess = true;
//--- declare and initialize the trade request and result of trade request
   MqlTradeRequest request;
   MqlTradeResult  result;
   int total=PositionsTotal(); // number of open positions   
//--- iterate over all open positions
   for(int i=total-1; i>=0; i--)
     {
      //--- parameters of the order
      ulong  position_ticket=PositionGetTicket(i);                                      // ticket of the position
      string position_symbol=PositionGetString(POSITION_SYMBOL);                        // symbol 
      int    digits=(int)SymbolInfoInteger(position_symbol,SYMBOL_DIGITS);              // number of decimal places
      ulong  magic=PositionGetInteger(POSITION_MAGIC);                                  // MagicNumber of the position
      double volume=PositionGetDouble(POSITION_VOLUME);                                 // volume of the position
      ENUM_POSITION_TYPE type=(ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);    // type of the position
      //--- output information about the position
    /*  PrintFormat("#%I64u %s  %s  %.2f  %s [%I64d]",
                  position_ticket,
                  position_symbol,
                  EnumToString(type),
                  volume,
                  DoubleToString(PositionGetDouble(POSITION_PRICE_OPEN),digits),
                  magic);
                  */
      //--- if the MagicNumber matches
      if (magic != magic_number)
         continue;
      else if(magic==magic_number){
      
         //--- zeroing the request and result values
         ZeroMemory(request);
         ZeroMemory(result);
         //--- setting the operation parameters
         request.action   =TRADE_ACTION_DEAL;        // type of trade operation
         request.position =position_ticket;          // ticket of the position
         request.symbol   =position_symbol;          // symbol 
         request.volume   =volume;                   // volume of the position
         request.deviation=5;                        // allowed deviation from the price
         request.magic    =magic_number;             // MagicNumber of the position
         request.type_filling = ORDER_FILLING_IOC;
         //--- set the price and order type depending on the position type
         if(type==POSITION_TYPE_BUY)
           {
            request.price=SymbolInfoDouble(position_symbol,SYMBOL_BID);
            request.type =ORDER_TYPE_SELL;
           }
         else
           {
            request.price=SymbolInfoDouble(position_symbol,SYMBOL_ASK);
            request.type =ORDER_TYPE_BUY;
           }
         //--- output information about the closure
         PrintFormat("Close #%I64d %s %s",position_ticket,position_symbol,EnumToString(type));
         //--- send the request
         if(!OrderSend(request,result)){
            PrintFormat("%s: OrderSend error %d", request.symbol, GetLastError());  // if unable to send the request, output the error code
            closeSucess = false;
            }
         //--- information about the operation   
        //@alib PrintFormat("retcode=%u  deal=%I64u  order=%I64u",result.retcode,result.deal,result.order);
         //---
        }
     }
     return closeSucess;
  }

//-------------------------------------------------
// This function is to log error into filr
//--------------------------------------------------
bool write_error_file (string error_msg){
   
   bool write_status = false;
   ulong pos[];
   
   string InpFileName = "error_msg.log";
   
   string time_log = TimeToString(TimeLocal(),TIME_DATE|TIME_SECONDS);
   string pair_log = Symbol();
   string error_log = time_log+","+pair_log+","+error_msg;
   
   //--- reset error value 
   ResetLastError(); 
   //--- open the file 
   int file_handle=FileOpen(InpFileName,FILE_READ|FILE_WRITE|FILE_TXT); 
   if(file_handle!=INVALID_HANDLE) 
     { 
         FileSeek(file_handle,0,SEEK_END);
         FileWrite(file_handle,error_log);
      
      
          //--- close the file
         FileClose(file_handle);
        // PrintFormat("%s file is closed",InpFileName);    
         
     } 
   else {
      PrintFormat("Error, code = %d",GetLastError()); 
      write_status = false;
      }
   
   return write_status;
}


//+------------------------------------------------------------------+
// Generate string for Bid/Ask by symbol
string Get_OHLC(string symbol, ENUM_TIMEFRAMES tf, int shift) {

   //datetime timestamp = TimeLocal();
  // string time_str = TimeToString(timestamp,TIME_DATE|TIME_SECONDS);
   string ret_string;
   
   //RefreshRates();
   double open = iOpen(symbol, tf, shift);
   double high = iHigh(symbol, tf, shift);
   double low = iLow(symbol, tf, shift);
   double close = iClose(symbol, tf, shift);
   
   //retry if value is zero
   if (open == 0.0 || high == 0.0 || low == 0.0 || close == 0.0){
         open = iOpen(symbol, tf, shift);
         high = iHigh(symbol, tf, shift);
         low = iLow(symbol, tf, shift);
         close = iClose(symbol, tf, shift);
   }
     
   ret_string = StringFormat("%f|%f|%f|%f", open, high, low, close);
   //Print(ret_string);
   return(ret_string);
}