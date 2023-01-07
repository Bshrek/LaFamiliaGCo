#main commands


from cgitb import text
from datetime import date, datetime
from email import message
from gc import callbacks
from itertools import product
import logging
from operator import index
from os import stat
from random import Random, random
from sqlite3 import Date
#from sre_parse import State
import time ,sched
from tkinter import Button
from typing import Awaitable
from unicodedata import name
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton,InlineKeyboardMarkup
from decouple import config
#################
##import DBConnect 
##import MangmentBot

BOT_TOKEN = config('BOT_TOKEN')

APPLICATION_ID = config('X_PARSE_APPLICATION_ID')
REST_API_KEY = config('X_PARSE_REST_API_KEY')

Storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot,storage=Storage)

BOT_TOKEN_MANGER = config('MANGER_BOT_TOKEN')

Storage_MANGER = MemoryStorage()
bot_MANGER = Bot(token=BOT_TOKEN)
dp_MANGER = Dispatcher(bot,storage=Storage)


##----------------------------- StartCom -----------------------------##

@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):

    checktext = DBConnect.checkIfYouHaveAccount(str(message.from_user.id))

    if checktext == 'don`t have':
        await message.answer("عظيم..😍😍\nيبدو أن هناك من يحاول ان يكون فرد جديد في العائلة\n أهلا "+message.from_user.first_name)
        time.sleep(1)
        await message.answer("تستطيع دائما الأطلاع على العروض الخاصة بنا بدون تسجيل"+
                        " الحساب الخاص لكن لن تستطيع القيام بعمليات الشراء بدون حساب\n"
                        +"/SingIn : لتسجيل حساب جديد\n"
                        +"/OurProdecuts : لعرض المنتجات مباشرتََ بدون أنشاء حساب جديد")
    else : 
        await message.answer("عظيم..😍😍\nيبدو أن هناك  فرد من العائلة قد عاد\n أهلا بك مجددا "+message.from_user.first_name)
        time.sleep(4)
        await message.answer("/OurProdecuts : لعرض المنتجات ")
       
##----------------------------- SingIN -----------------------------##
"""
class SingUPClass(StatesGroup):
    FirstName = State()
    LastName = State()
    TeleNum = State()
    LastNews = State()

@dp.message_handler(commands=['SingIn'])
async def SingInUserUserName(message: types.Message, state:FSMContext):
    
    checktext = DBConnect.checkIfYouHaveAccount(str(message.from_user.id))
    if checktext == 'don`t have':

        await message.answer('الخطوة الأولى لتسجيل الدخول \n أسم المستخدم المسجل في تلغرام : \n'+ str(message.from_user.first_name +' '+ message.from_user.last_name)+' .. ')

        async with state.proxy() as singInData:
            singInData['userTeleID'] = str(message.from_user.id)
            singInData['userName'] = message.from_user.first_name +' '+ message.from_user.last_name
        
        time.sleep(4)

        await SingUPClass.FirstName.set()
        await message.answer('الخطوة الثانية أدخل الأسم الأول الخاص بك')
    else :
        await message.answer('لديك حساب موجود مسبقا\nان كنت تريد معرفة تفاصيل حساب يمكنك النقر هنا /MyProfile')


@dp.message_handler(state=SingUPClass.FirstName)    
async def SingInUserFirstname(message: types.Message, state:FSMContext):

    async with state.proxy() as singInData:
        singInData['firstName'] = message.text
    await SingUPClass.next()
    await message.answer('أدخل الأسم الأخير الخاص بك')

@dp.message_handler(state=SingUPClass.LastName)    
async def SingInUserLastname(message: types.Message, state:FSMContext):

    async with state.proxy() as singInData:
        singInData['lastName'] = message.text
    await SingUPClass.next()
    await message.answer('الخطوة الثالثة رقم الجوال الخاص بك\n يرجى التأكد من أن الرقم يملك حساب واتس + تلغرام\n يرجى أدخال الرقم بدون الرمز الدولي مثال : 0991234567')

@dp.message_handler(state=SingUPClass.TeleNum)    
async def SingInUserTeleNum(message: types.Message, state:FSMContext):

    async with state.proxy() as singInData:
        singInData['teleNum'] = message.text
    await SingUPClass.next()
    
    markupLastNews = types.ReplyKeyboardMarkup(resize_keyboard=True,selective=True,one_time_keyboard=True)

    markupLastNews.add('الحصول على أخر الأخبار')
    markupLastNews.add('عدم الحصول')

    await message.answer('أخيرا هل تريد أن تصلك أخر الأشعارات الخاصة بنا \n ما هي الأشعارات ؟؟ \n' +
        '1. أكثر 10 قمصان مبيعاََ لهذا الأسبوع  \n 2. اخر العروض الخاصة بنا (تخفيضات ,عروض صيف وشتاء خريف وربيع) '+
           ' \n 3. أخر أفراد العائلة في مجتمعنا وما الذي يقدمونه \n 4. تعديل الأسعار أن وجد',reply_markup = markupLastNews)


@dp.message_handler(state=SingUPClass.LastNews)    
async def SingInUserLastNews(message: types.Message, state:FSMContext):

    #markupLastNews = types.ReplyKeyboardRemove()

    if message.text == 'الحصول على أخر الأخبار' :
        async with state.proxy() as singInData:
            singInData['lastNews'] = True
    
    if message.text == 'عدم الحصول' :
        async with state.proxy() as singInData:
            singInData['lastNews'] = False
            
    DBConnect.SingupUser(singInData['userName'],singInData['firstName'],singInData['lastName'],int(singInData['teleNum']),False,singInData['lastNews'],str(singInData['userTeleID']))

    await message.answer('تمت العملية بنجاح , يبدو ان مجتمع La Familia قد أكتسب فرداََ جديد')

    await state.finish()

    if singInData['lastNews'] == True:
        await message.answer('البيانات الخاصة بك :\n الأسم الأول : '+singInData['firstName']
                        +'\nالأسم الأخير : '+singInData['lastName']+'\nرقم الهاتف : '+singInData['teleNum']
                        +'\nولقد وافقت على أستلام أخر الأشعارات')
    else : 
        await message.answer('البيانات الخاصة بك :\n الأسم الأول : '+singInData['firstName']
                        +'\nالأسم الأخير : '+singInData['lastName']+'\nرقم الهاتف : '+singInData['teleNum']
                        +'\nولم توافق على أستلام الأشعارات')


@dp.message_handler(state = SingUPClass, commands='cancelSingUp')
@dp.message_handler(state = SingUPClass)
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return
 
    logging.info('تم ألغاء عملية تسجيل الدخول %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('تم الألغاء.', reply_markup=types.ReplyKeyboardRemove())
 
##----------------------------- MyProfile -----------------------------##
                                    #
                                    #
                                    #
                                    #
                                    #
                                    #
##----------------------------- OurProducts -----------------------------##
@dp.message_handler(commands=['OurProdecuts'])
async def setType(message: types.Message):
 
    cur = DBConnect.GetType()
    inlineKeyboradType = InlineKeyboardMarkup(resize_keyboard=True)   

    for row in cur.fetchall():
        inlineKeyboradType.add(InlineKeyboardButton(text = str(row[1]),callback_data = row[1])) 

    await message.answer('أولا ماهو نوع المنتج الذي تبحث عنه',reply_markup=inlineKeyboradType)

                #
               ###
               ###
                #

curProductsType = DBConnect.GetType()
listTypeProducts = []
for row in curProductsType.fetchall():
     listTypeProducts.append(row[1])


listCatProducts = []

                #
                #

@dp.callback_query_handler(text = listTypeProducts)
async def setCatogre(call : types.CallbackQuery, state:FSMContext):

    async with state.proxy() as setConditonForProducts:
        setConditonForProducts['Type'] = call.data
 
    cur = DBConnect.GetCategorie(setConditonForProducts['Type'])
    inlineKeyboradCat = InlineKeyboardMarkup(resize_keyboard=True)   

    for row in cur.fetchall():
        inlineKeyboradCat.add(InlineKeyboardButton(text = str(row[1])+" : يعني بلعربي "+str(row[2]),callback_data = row[1])) 
        listCatProducts.append(row[1])

    await call.message.answer('ثانيا ماهي فئة المنتج ...',reply_markup=inlineKeyboradCat)
                
                #
               ###
               ###
                #

@dp.callback_query_handler(text = listCatProducts)
async def GetOurProdecuts(call : types.CallbackQuery, state:FSMContext):
   
    async with state.proxy() as setConditonForProducts:
        setConditonForProducts['Categories'] = call.data
    
    cur = DBConnect.GetProductsWithTypeANDCat(setConditonForProducts['Type'],setConditonForProducts['Categories'])
    inlineKeyboradType = InlineKeyboardMarkup(resize_keyboard=True)   
  
    for row in cur.fetchall():
        await call.message.answer_photo(photo=open(row[6],"rb"))
        inlineKeyboradType = InlineKeyboardMarkup(resize_keyboard=True)   

        inlineKeyboradType.add(InlineKeyboardButton(text = 'أضف إلى قائمة المشتريات' ,callback_data = row[5]))

        if (DBConnect.checkIfYouHaveAccount(str(call.from_user.id)) == 'have account'):

            await call.message.answer('الكود الخاص بلمنتج : '+str(row[0])+
                                    '\nنوع المنتج : '+str(row[1])+'\nصفة المنتج : '+str(row[2])+'\nالمتجر : '+
                                    str((row[3]))+'\nالسعر : '+str(('{:,}'.format(int(row[7])))),reply_markup= inlineKeyboradType) 

        else: await call.message.answer('الكود الخاص بلمنتج : '+str(row[0])+
                                    '\nنوع المنتج : '+str(row[1])+'\nصفة المنتج : '+str(row[2])+'\nالمتجر : '+
                                    str((row[3]))+'\nالسعر : '+str(('{:,}'.format(int(row[7])))))

curProductsID = DBConnect.GetAllProducts('ProductsCode')
listIDProducts = []
for row in curProductsID.fetchall():
     listIDProducts.append(str(row[0]))

                #
                #

@dp.callback_query_handler(text = listIDProducts)
async def GetOurProdecuts(call : types.CallbackQuery, state:FSMContext):
    cur = DBConnect.GetProductsWithProductsCode(str(call.data))
    
    for row in cur.fetchall():
        DBConnect.ADDToUserCart(str(call.from_user.id),str(row[0]),str(row[7]),str(datetime.now()),str(row[6]))

    await call.answer('تم أضافة العنصر')



class CheckoutProcess(StatesGroup):
    showMyCart = State()
    checkIFDelete = State()
    setLocation = State()
    checkNUM = State()


class DeleteAndStartCart(StatesGroup):
    goToCart = State()

@dp.message_handler(commands=['MyCart'])

#ينتج الخطاء عند تفعيل دالة الكارت المشكلة هنا 
async def MyCart(message: types.Message, state:FSMContext):
    
    #await CheckoutProcess.showMyCart.set()
    if (DBConnect.checkIfYouHaveAccount(str(message.from_user.id)) == 'have account'):

        if (DBConnect.checkIfYouHaveCartANDAccount(str(message.from_user.id)) == 'have account'):
            cur = DBConnect.GetMyCart(str(message.from_user.id),False)

            for row in cur.fetchall():
                async with state.proxy() as theCart:
                    theCart['ProductsList'] = row[1].split(",")
                    theCart['PriceList'] = row[2].split(",")
                    theCart['DateList'] = row[3].split(",")
                    theCart['IMGPath'] = row[6].split(",")
                    theCart['typeMediaGroup'] = types.MediaGroup()
                    theCart['ItemIndex'] = 0
                    theCart['PriceTotal'] = 0.0
                    theCart['deleteItem'] = 'empty'


                    for i in theCart['IMGPath']:
                        theCart['typeMediaGroup'].attach_photo(types.InputFile(str(i)))

                    await message.answer_media_group(media = theCart['typeMediaGroup'])

                    for i in theCart['ProductsList']:
                        inlineKeyborad = InlineKeyboardMarkup(resize_keyboard=True)   
                        inlineKeyborad.add(InlineKeyboardButton(text = 'حذف العنصر',callback_data = str(f'DeleItem,{str(i)}')))

                        await message.answer('رمز العنصر : '+str(i)+'\nسعر العنصر : '+
                                            str(('{:,}'.format(int(theCart['PriceList'][theCart['ItemIndex']]))))+
                                            '\nتاريخ الإضافة : '+theCart['DateList'][theCart['ItemIndex']],reply_markup=inlineKeyborad)


                        theCart['ItemIndex'] = theCart['ItemIndex'] + 1     
                    replyKeyborad = ReplyKeyboardMarkup(resize_keyboard = True ,one_time_keyboard = True).add('أنهاء عملية الشراء')

                    for i in theCart['PriceList']:
                        theCart['PriceTotal'] = int(theCart['PriceTotal']) + int(i)
                    await message.answer('مجموع الفاتورة : '+ str(('{:,}'.format(int(theCart['PriceTotal'])))),reply_markup=replyKeyborad)

        else: await message.answer('قائمة مشترياتك فارغة تستطيع أستعراض المنتجات من هنا\n/OurProdecuts')

    else: await message.answer('عليك تسجيل الدخول للوصول إلى هنا ..')



curDeleteItem = DBConnect.GetAllProducts('ProductsID')
listDeleteID = []
for row in curDeleteItem.fetchall():
    listDeleteID.append(str(f'DeleItem,{str(row[0])}'))

@dp.callback_query_handler(text = listDeleteID)
async def DeleteFromCart(call : types.CallbackQuery, state:FSMContext):
    await bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id=call.message.message_id ,reply_markup = None)

    deleteItemCart = call.data.split(',')
    cur = DBConnect.GetMyCart(str(call.from_user.id),False)
    for row in cur.fetchall():
        async with state.proxy() as theCart:
            theCart['PopItem'] = row[1].split(',').index(deleteItemCart[1])
            theCart['ProductsList'] = row[1].split(",")
            print(len(theCart['ProductsList']))
            if (len(theCart['ProductsList']) > 1): 
                del theCart['ProductsList'][theCart['PopItem']-1]

                theCart['PriceList'] = row[2].split(",")
                del theCart['PriceList'][theCart['PopItem']-1]
                
                theCart['DateList'] = row[3].split(",")
                del theCart['DateList'][theCart['PopItem']-1]
                
                theCart['IMGPath'] = row[6].split(",")
                del theCart['IMGPath'][theCart['PopItem']-1]
                
                DBConnect.DeleteFromUserCart(str(call.from_user.id),','.join(theCart['ProductsList'])
                                            ,','.join(theCart['PriceList']),','.join(theCart['DateList']),','.join(theCart['IMGPath']))   

            else:
                DBConnect.DeleteAllRecordFromCart(str(call.from_user.id))
                
    await call.message.answer(text='تم ألغاء العنصر للعودة للسلة \n/MyCart')    

@dp.message_handler(text='أنهاء عملية الشراء')    
async def DeleteOrComplate(message: types.Message, state:FSMContext):

    cur = DBConnect.GetLoc()
    inlineKeyborad = InlineKeyboardMarkup(resize_keyboard=True)   
    for row in cur.fetchall():
        inlineKeyborad.add(InlineKeyboardButton(text = f'{str(row[1])} - {str(row[3])}',callback_data = str(row[1])))
    await message.answer('حدد موقع التسليم الأقرب لك',reply_markup=inlineKeyborad)

curLoc = DBConnect.GetLoc()
listLoc = []          
for row in curLoc.fetchall():
     listLoc.append(str(row[1]))

@dp.callback_query_handler(text = listLoc)
async def FinshOrderAndSendToRunedOrder(call : types.CallbackQuery, state:FSMContext):
    await bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id=call.message.message_id ,reply_markup = None)

    phoneNum = '0'
    cur = DBConnect.GetAccountInfo(str(call.from_user.id))
    
    for row in cur.fetchall():
        phoneNum = str(row[4])   
    
    async with state.proxy() as DateOrder:

        DateOrder['orderDate'] = str(datetime.now().strftime("%D--%H:%M:%S"))

        DBConnect.sendToOrderList(str(call.from_user.id),str(call.data),str(phoneNum),DateOrder['orderDate'])
        
        await bot.edit_message_text(text = f'تمت العملية بنجاح وسوف يتم التواصل معك من خلال الرقم {phoneNum} عند أنجاز الطلب',
                                    chat_id = call.message.chat.id, message_id=call.message.message_id)
        
        await MangmentBot.sendToManger(str(call.from_user.id),DateOrder['orderDate'])

    #call.message.answer(text = f'تمت العملية بنجاح وسوف يتم التواصل معك من خلال الرقم {phoneNum} عند أنجاز الطلب')

async def sendToUser(userID:str,loc:str):
    await bot.send_message(int(userID),text = f'تم أنجاز الطلب ,تستطيع الذهاب للمندوب التالي : {loc}')


@dp.message_handler(commands=['FastCommand'])
async def FCommand(message: types.Message):

    await message.answer('قائمة الوصول السريع \n\
/AboutUS: للمزيد من المعلومات عن المشروع الخاص بنا\n\
/ConnectUS: للتواصل مع إدارة المشروع والمطورين\n\
/OurProdecuts: منتجاتنا\n\
/MyCart: حقيبة المشتريات الخاصة بك\n\
/MyOrder: الفواتير الخاصة بك (قيد التنفيذ)\n\
/OurLocation: افراد العائلة المساهمين\n\
/MyProfile: معلومات عنك')


s = sched.scheduler(time.time, time.sleep)
def loopRoom(target:str):
    #print('agien')
    global curProductsType
    global listTypeProducts
    
    global curProductsID
    global listIDProducts
        
    global curDeleteItem
    global listDeleteID
        
    global curLoc
    global listLoc
    
    curProductsType = DBConnect.GetType()
    listTypeProducts = []
    for row in curProductsType.fetchall():
            listTypeProducts.append(row[1])
    listCatProducts = []
    
    curProductsID = DBConnect.GetAllProducts('ProductsCode')
    listIDProducts = []
    for row in curProductsID.fetchall():
            listIDProducts.append(str(row[0]))

    curDeleteItem = DBConnect.GetAllProducts('ProductsID')
    listDeleteID = []
    for row in curDeleteItem.fetchall():
        listDeleteID.append(str(f'DeleItem,{str(row[0])}'))
        
    curLoc = DBConnect.GetLoc()
    listLoc = []          
    for row in curLoc.fetchall():
            listLoc.append(str(row[1]))
            
    s.enter(0.5, 1, loopRoom, (s,))
"""

if __name__ == '__main__':
    executor.start_polling(dp)
    executor.start_polling(dp_MANGER)
    s.enter(0.5, 1, loopRoom, (s,))
    s.run()

