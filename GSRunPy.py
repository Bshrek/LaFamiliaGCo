# import libraries
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from IPython.display import display

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import asyncio

# connect to MetaTrader5 platform
if not mt5.initialize():
    print("فشل في الاتصال بـ MT5")

current_time = datetime.today()
loop = asyncio.get_event_loop()
userID = 5104035032

async def send_custom_message(user_id, message):
    # تعيين معرف البوت والحصول على معرف مطور البوت من موقع BotFather
    bot_token = '6181282756:AAGEEsVvwvH-gLXTl-yb6B34M-C4KDrqo8E'
    bot = Bot(token=bot_token)

    # إنشاء مسار التوجيه
    dp = Dispatcher(bot)

    try:
        # إرسال رسالة مخصصة إلى المستخدم المحدد
        await bot.send_message(chat_id=user_id, text=message)
        print("تم إرسال الرسالة بنجاح")
    except Exception as e:
        print(f"حدث خطأ أثناء إرسال الرسالة: {e}")

    # إغلاق الاتصال بـ Telegram
    await bot.close()

async def open_position(pair, order_type, size, tp_distance=None, stop_distance=None):

    symbol_info = mt5.symbol_info(pair)

    # قيمة السبريد
    spread = symbol_info.spread

    if spread < (26): # ex:26

        if symbol_info is None:
            # تشغيل الدالة في مهمة غير متزامنة باستخدام `asyncio`
            await send_custom_message(userID, str(pair)+" not found")
            print(pair, "not found")
            return

        if not symbol_info.visible:
            print(pair, "is not visible, trying to switch on")
            if not mt5.symbol_select(pair, True):
                print("symbol_select({}}) failed, exit",pair)
                return
        await send_custom_message(userID, str(pair)+" found!")
        print(pair, "found!")

        point = symbol_info.point
        
        if(order_type == "BUY"):
            order = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(pair).ask
            if(stop_distance):
                sl = price - (stop_distance * point)
            if(tp_distance):
                tp = price + (tp_distance * point)
                
        if(order_type == "SELL"):
            order = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(pair).bid
            if(stop_distance):
                sl = price + (stop_distance * point)
            if(tp_distance):
                tp = price - (tp_distance * point)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pair,
            "volume": float(size),
            "type": order,
            "price": price,
            "sl": sl,
            "tp": tp,
            "magic": 234000,
            "comment": "",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            await send_custom_message(userID," Failed to send order :(")
            print("Failed to send order :(")
        else:
            await send_custom_message(userID," Order successfully placed!")
            print ("Order successfully placed!")

        # استرداد جميع المراكز المفتوحة
        positions = mt5.positions_get()

        # المعلومات الأساسية للصفقة
        symbol = "EURUSD"  # الرمز التجاري للأداة المالية

        # البحث عن الصفقة المفتوحة باستخدام الرمز التجاري
        for position in positions:
            if position.symbol == symbol:
                ticket = position.ticket
                await send_custom_message(userID, "الصفقة مفتوحة. رقم التذكرة:"+str(ticket))
                print("الصفقة مفتوحة. رقم التذكرة:", ticket)
                return(ticket)
                
        else:
            await send_custom_message(userID, "لا توجد صفقة مفتوحة للرمز التجاري المحدد")
            print("لا توجد صفقة مفتوحة للرمز التجاري المحدد")
    else:
        await send_custom_message(userID, f"high spread {spread}")
        print(f"high spread {spread}")


def positions_get(symbol=None):

    if(symbol is None):
	    res = mt5.positions_get()
    else:
        res = mt5.positions_get(symbol=symbol)

    if(res is not None and res != ()):
        df = pd.DataFrame(list(res),columns=res[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    
    return pd.DataFrame()

async def close_position(deal_id):
    open_positions = positions_get()
    open_positions = open_positions[open_positions['ticket'] == deal_id]
    order_type  = open_positions["type"][0]
    symbol = open_positions['symbol'][0]
    volume = open_positions['volume'][0]

    if(order_type == mt5.ORDER_TYPE_BUY):
        order_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    else:
        order_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
	
    close_request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": order_type,
        "position": deal_id,
        "price": price,
        "magic": 234000,
        "comment": "Close trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(close_request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        await send_custom_message(userID, "Failed to close order :(")
        print("Failed to close order :(")
    else:
        await send_custom_message(userID, "Order successfully closed!")
        print ("Order successfully closed!")

async def close_positons_by_symbol(symbol):
    loop = asyncio.get_event_loop()
    open_positions = positions_get(symbol)
    if  not open_positions.empty:
        open_positions['ticket'].apply(lambda x: close_position(x))
    else:
        await send_custom_message(userID, "لا توجد صفقات مفتوحة")
        print("لا توجد صفقات مفتوحة")

def specify_candle_type(open_price, close_price):

    if close_price > open_price:
        return 'BUY'
    elif close_price < open_price:
        return 'SELL'
    else:
        return 'doji'


# لتحضير الساعة الحالية وتجهيز الوقت المناسب للدخول
def getLastCandle(current_time_value):
    # settings
    SYMBOL = "EURUSD"
    TIMEFRAME = mt5.TIMEFRAME_H1
    TIMEFRAME1M = mt5.TIMEFRAME_M1
    start_dt = datetime(current_time_value.year, current_time_value.month,current_time_value.day)
    end_dt = datetime.now()

    # request ohlc data a save them in a pandas DataFrame
    bars = mt5.copy_rates_range(SYMBOL, TIMEFRAME, start_dt, end_dt)
    df = pd.DataFrame(bars)[['time', 'open', 'high', 'low', 'close','spread']]
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # df = df.drop(df.index[-1])    

    df['candle_type'] = np.vectorize(specify_candle_type)(df['open'], df['close'])
    last_candle = df.iloc[-1]

    lenOfCandle = last_candle['open'] - last_candle['close']

    return([last_candle['candle_type'],lenOfCandle])


async def run():
    while True:
            # احصل على الوقت الحالي
        current_time = datetime.today()

        # عدد الدقائق والثواني للتوقف
        minutes = (current_time.minute+1 - 60)*-1
        seconds = (current_time.second - 60)*-1

        # حساب إجمالي الوقت بالثواني
        total_time = (minutes * 60) + seconds

        print(f"الوقت الحالي الدقيقة : {current_time.minute} الثواني : {current_time.second}")
        print(f"الوقت المتبقي لفتح الصفقة الدقيقة : {minutes} الثواني : {seconds}")
        await send_custom_message(userID, f"الوقت الحالي الدقيقة : {current_time.minute} الثواني : {current_time.second}")
        await send_custom_message(userID, f"الوقت المتبقي لفتح الصفقة الدقيقة : {current_time.minute} الثواني : {current_time.second}")


        # التوقف للوقت المحدد
        time.sleep(total_time)
        time.sleep(2)


        # تنفيذ العمليات بعد انتهاء الانتظار

        # الحصول على تاريخ اليوم
        today = datetime.today()
        # الحصول على اسم اليوم
        day_name = today.strftime("%A")
        if day_name != "Sunday" or day_name != "Saturday":
            candleTypeP = getLastCandle(current_time)

            #للتأكد من أن السوق يحمل سيولة عالية
            if candleTypeP[1] > 0.00035 or candleTypeP[1] < -0.00035:
                open_position("EURUSD",candleTypeP[0],0.01,70,25)
                await send_custom_message(userID, "تم تنفيذ العمليات بعد التوقف المحدد" + str(datetime.now()))
                print("تم تنفيذ العمليات بعد التوقف المحدد" + str(datetime.now()))
            else:
                await send_custom_message(userID, "لا يوجد سيولة")
                print("لا يوجد سيولة")

            time.sleep(3540)
            close_positons_by_symbol("EURUSD")

        else:
            await send_custom_message(userID, "اليوم عطلة")
            print("اليوم عطلة")




#From we strat the ....
run()