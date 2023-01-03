from collections import UserList
from decouple import config
#from asyncio.windows_events import NULL
from cgitb import text
from datetime import datetime
from email import message
from gc import callbacks
from itertools import product
import logging
from operator import index
from os import stat
from random import Random, random
from sre_parse import State
import time
from tkinter import Button
from typing import Awaitable
from unicodedata import name
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton,InlineKeyboardMarkup

import DBConnect
import main



BOT_TOKEN = config('MANGER_BOT_TOKEN')

Storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot,storage=Storage)

async def sendToManger(userID:str,dateOrder:str):
    print(str(userID)+','+str(dateOrder))

    inlineKeyboradType = InlineKeyboardMarkup(resize_keyboard=True)   
    inlineKeyboradType.add(InlineKeyboardButton(text = 'تم الأنجاز' ,callback_data = f'{userID},{dateOrder}'))

    cur = DBConnect.GetOrderInfo(userID,dateOrder)

    for row in cur.fetchall():
        await bot.send_message(5104035032,text = f'OrderID : {row[0]}\nUserID : {row[4]}\nProducts List : {row[1]}\nPriceList : {row[2]}\nDate Of Order : {row[3]}\nPhone Number : {row[8]}\nLoc : {row[7]}',reply_markup=inlineKeyboradType)


print(DBConnect.GetIDANDDateFromOrder())

@dp.callback_query_handler(text = DBConnect.GetIDANDDateFromOrder())
async def OrderDone(call : types.CallbackQuery, state:FSMContext):
    loc = ''
    await bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id=call.message.message_id ,reply_markup = None)
    IDList = call.data.split(",")
    cur = DBConnect.GetOrderInfo(str(IDList[0]),str(IDList[1]))
    for row in cur:
        loc = str(row[7])

    DBConnect.UpdateDateOrder('تم العملية',str(IDList[1]),str(IDList[0]))
    await main.sendToUser(str(IDList[0]),loc)

class GetIDOfItem(StatesGroup):
    IDInsert = State()

@dp.message_handler(commands=['GetItem'])
async def getItemID(message : types.Message, state:FSMContext):

    inlineKeyboradType = InlineKeyboardMarkup(resize_keyboard=True)  
    inlineKeyboradType.add(InlineKeyboardButton(text = 'إلغاء' ,callback_data = 'إلغاء'))
    await message.answer('يرجى إدخال الرمز الخاص بلعنصر',reply_markup=inlineKeyboradType)

    await GetIDOfItem.IDInsert.set()

@dp.callback_query_handler(text = 'إلغاء')
async def CansleItemSearch(call : types.CallbackQuery, state:FSMContext):
        await call.message.answer('تم ألغاء العملية')
        await state.finish()



@dp.message_handler(state=GetIDOfItem.IDInsert)
async def getItemWithID(message : types.Message, state:FSMContext):
    
    inlineKeyboradType = InlineKeyboardMarkup(resize_keyboard=True)  
    inlineKeyboradType.add(InlineKeyboardButton(text = 'إلغاء' ,callback_data = 'إلغاء'))

    await message.answer('يرجى إدخال الرمز الخاص بلعنصر')

    if (str(message.text) == 'إلغاء'):
        await message.answer('تم ألغاء العملية')
        await state.finish()


    ItemReturn = 'الرمز خطأ يرجى التأكد من رمز المنتج او الخروج من الوضع من خلال أرسال إلغاء'

    cur = DBConnect.SearchOfItem(str(message.text))
    for row in cur.fetchall():
        ItemReturn = 'الكود الخاص بلمنتج : '+str(row[0])+'\nنوع المنتج : '+str(row[1])+'\nصفة المنتج : '+str(row[2])+'\nالمتجر : '+str((row[3]))+'\nالسعر : '+str(('{:,}'.format(int(row[7]))))
        await message.answer_photo(photo=open(row[6],"rb"))
        await message.answer(ItemReturn)
        await state.finish()

    if (ItemReturn == 'الرمز خطأ يرجى التأكد من رمز النتج او الخروج من الوضع من خلال أرسال إلغاء'):
        await GetIDOfItem.IDInsert.set()
        await message.answer(ItemReturn,reply_markup=inlineKeyboradType)

@dp.message_handler(commands=['GetUsers'])
async def getUsers(message : types.Message, state:FSMContext):
        
        inlineKeyboradType = InlineKeyboardMarkup(resize_keyboard=True)  
        inlineKeyboradType.add(InlineKeyboardButton(text = 'أعداد المستخدمين' ,callback_data = 'عداد المستخدمين'))
        inlineKeyboradType.add(InlineKeyboardButton(text = 'كل المستخدمين' ,callback_data = 'كل المستخدمين'))
        inlineKeyboradType.add(InlineKeyboardButton(text = 'البحث عن مستخدم' ,callback_data = 'البحث عن مستخدم'))

        await message.answer('ماالذي تحتاجه بضبط',inlineKeyboradType)

@dp.callback_query_handler(text = ['عداد المستخدمين','كل المستخدمين'])
async def GetUserANDCount(call : types.CallbackQuery, state:FSMContext):
    cur = DBConnect.GetUserInfo('*')
    countUser = 0
    teleUserList = []
    for row in cur.fetchall():
        countUser + 1
        teleUserList.append(str(row[2]))
    if (call.data == 'عداد المستخدمين'):
        await call.message.answer(f'عدد المستخدمين : {str(countUser)}')
    else:
        textMessage = ''
        for i in teleUserList:
            textMessage = textMessage+'\n'+str(i)
        await call.message.answer(f'المستخدمين : {str(countUser)}')

@dp.callback_query_handler(text = ['البحث عن مستخدم'])
async def SearchUser(call : types.CallbackQuery, state:FSMContext):    
    inlineKeyboradType = InlineKeyboardMarkup(resize_keyboard=True)  
    inlineKeyboradType.add(InlineKeyboardButton(text = 'إلغاء' ,callback_data = 'إلغاء البحث عن المستخدم'))

    await call.message.answer('البحث من خلال الأسم أو الرمز\nأدخل البيانات.',reply_markup=inlineKeyboradType)
    

if __name__ == '__main__':
    executor.start_polling(dp)

