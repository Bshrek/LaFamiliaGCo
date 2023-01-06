#start in 6/9/2022 11:33 PM

from ast import Str
#from asyncio.windows_events import NULL
from contextlib import nullcontext
from dataclasses import dataclass
from datetime import date
from email.mime import image
from re import I
from sqlite3 import Date
from tokenize import String
from webbrowser import get
from xmlrpc.client import Boolean
import pyodbc

try:
    #Get Access file ### ODBC Driver 13 for SQL Server
    #con_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=opt/render/project/src/laFamiliaDB.accdb;'
    con_string = r'DRIVER={/usr/local/lib/libmsodbcsql.13.dylib}; (*.mdb, *.accdb)};DBQ=opt/render/project/src/laFamiliaDB.accdb;'
    #File Connection
    conn = pyodbc.connect(con_string)
    #create cursor to fetch Data
    cur = conn.cursor()

    #To cheick if user have or no and Sing up if no
    """
    يتم التأكد من وجود الحساب مسبقا وذلك من خلال من تطابق الرقم والأسم مع المدخلات
    انشاء متغير اول بقيمة أفتراضية هي تسجيل حساب جديد
    اذا وجد حساب سوف يكون تسجيل دخول فقط
    """
##----------------------------- CheckAccount -----------------------------##

    def checkIfYouHaveAccount(UserID:str):
        dataList = []
        Checktext = 'don`t have'
        cur.execute('SELECT UserTeleID FROM Users WHERE UserTeleID = ?',UserID)
        for row in cur.fetchall():
            dataList.append(row[0])
            Checktext = 'have account'

        return Checktext
##----------------------------- CheckAccount -----------------------------##

    def checkIfYouHaveCartANDAccount(UserID:str):
        dataList = []
        Checktext = 'don`t have'
        cur.execute('SELECT UserID FROM UserCart WHERE UserID = ?',UserID)
        for row in cur.fetchall():
            dataList.append(row[0])
            Checktext = 'have account'

        return Checktext
##----------------------------- CheckAccount -----------------------------##

    def sendToOrderList(UserID:str,Loc:str,phoneNum:str,productsDateForItem:str):

        print(UserID)

        Products = ''
        Price = ''
        productsDate = ''
        imagePath = ''

        cur.execute('SELECT * FROM UserCart WHERE UserID = ?',str(UserID))
        
        for row in cur.fetchall():
            Products = str(row[1]) 
            Price = str(row[2])
            productsDate = str(row[3])
            imagePath = str(row[6])
   
        cur.execute('INSERT INTO [Order] (Products ,Price ,DateOfProducts , UserID, ImagePath ,DoneOrder ,[Location] ,PhoneNum,ProductsDate)\
                     VALUES (?,?,?,?,?,?,?,?,?)',(Products ,Price ,productsDate ,UserID ,imagePath ,'قيد التنفيذ' ,Loc ,phoneNum ,productsDateForItem))
        
        conn.commit()
        return 'Data Sended'
##----------------------------- GetAccountInfo -----------------------------##

    def GetAccountInfo(UserID:str):
        cur.execute('SELECT * FROM Users WHERE UserTeleID = ?',UserID)

        return cur
##----------------------------- DeleteCartIfEmpty -----------------------------##

    def DeleteAllRecordFromCart(UserID:str):
        cur.execute('DELETE FROM UserCart WHERE UserID = ?',UserID)
        conn.commit()

        return cur
##----------------------------- GetOrderInfo -----------------------------##

    def GetOrderInfo(UserID:str,DateProducts:str):
        cur.execute('SELECT * FROM [Order] WHERE UserID = ? AND ProductsDate = ?',UserID,DateProducts)

        return cur
##----------------------------- GetOrderIDANDDate -----------------------------##

    def GetIDANDDateFromOrder():
        listOrder = [] 
        cur.execute('SELECT * FROM [Order]')
        for row in cur.fetchall():
            listOrder.append(str(row[4])+','+str(row[9]))
        
        return listOrder
##----------------------------- UpdateDateOrder -----------------------------##

    def UpdateDateOrder(theState:str,productsDate:str,UserID:str):
        cur.execute('UPDATE [Order] SET DoneOrder = ? WHERE ProductsDate = ? AND UserID = ?',theState,productsDate,UserID)
        conn.commit()
        return 'Updated'
##----------------------------- SingIN -----------------------------##

    #To cheick if user have or no and Sing up if no
    """
    يتم التأكد من وجود الحساب مسبقا وذلك من خلال من تطابق الرقم والأسم مع المدخلات
    انشاء متغير اول بقيمة أفتراضية هي تسجيل حساب جديد
    اذا وجد حساب سوف يكون تسجيل دخول فقط
    """

    def SingupUser(Username:str,FirstName:str,LastName:str,Telphone:int,Investor:bool,LastNews:bool,UserTeleID:str):
        cur.execute('INSERT INTO Users (UserName ,FirstName ,LastName , Tele_Wh_Num, Investor ,LastNews,UserTeleID)\
                 VALUES (?,?,?,?,?,?,?)',(Username,FirstName,LastName,Telphone,Investor,LastNews,UserTeleID))

        conn.commit()
        print('Data Inserted')

        
##----------------------------- GetAllProducts -----------------------------##

    def GetAllProducts(targetTable:str):
        cur.execute('SELECT '+targetTable+' FROM Prroducts')

        return cur
##----------------------------- GetProductsWithID -----------------------------##

    def GetProductsWithProductsCode(Code:str):
        cur.execute('SELECT * FROM Prroducts WHERE ProductsCode = ?',Code)

        return cur
##----------------------------- GetProductsWithConditon -----------------------------##

    def GetProductsWithTypeANDCat(ConditionType:str,ConditionCat:str):
        cur.execute('SELECT * FROM Prroducts WHERE ProductsType = ? AND ProductsCat = ?',ConditionType,ConditionCat)
    
        return cur
##----------------------------- GetTypeItem -----------------------------##

    def GetType():
        cur.execute('SELECT * FROM ProductsType')
    
        return cur
##----------------------------- GetCatItem -----------------------------##

    def GetCategorie(Type:str):
        cur.execute('SELECT * FROM Categories WHERE TypeFather = ?',Type)
    
        return cur
##----------------------------- GetCatItem -----------------------------##

    def GetOrderToMang(UserID:str):
        cur.execute('SELECT * FROM Order WHERE UserID = ?',UserID)
    
        return cur
##----------------------------- GetProductsItemWithLimit -----------------------------##

    def GetItemWithLimit(limit:int):
        limitNum = 1 
        cur.execute('SELECT * FROM Prroducts')
        for row in cur.fetchall():
            if limitNum <= limit :
                print (row)
                limitNum = limitNum + 1
            else : break
##----------------------------- AddToUserCart -----------------------------##

    def ADDToUserCart(UserID:str,Products:str,Price:str,DataOfCart:str,IMGPath:str):
        Checktext = 'new cart'
        privateCur = conn.cursor()
        cur.execute('SELECT * FROM UserCart WHERE UserID = ?',UserID)
        privateCur.execute('SELECT * FROM UserCart')

        for row in cur.fetchall():
            Checktext = 'have cart'

        if (Checktext == 'have cart'):
            for row in privateCur.fetchall():

                privateCur.execute('UPDATE UserCart SET Prodects = ?,Price = ?,DateOfCart = ? ,ImagePath = ?\
                    WHERE UserID = ?',(str(row[1])+','+Products,str(row[2])+','+Price,str(row[3])+','+DataOfCart,str(row[6])+','+IMGPath,UserID))
                conn.commit()

        else :
            cur.execute('INSERT INTO UserCart (Prodects ,Price ,DateOfCart , UserID ,ImagePath)\
                 VALUES (?,?,?,?,?)',(Products,Price,DataOfCart,UserID,IMGPath))
            conn.commit()
        return ('تمت الأضافة للسلة الخاصة بك')
##----------------------------- DeleteFromUserCart -----------------------------##

    def DeleteFromUserCart(UserID:str,Products:str,Price:str,DataOfCart:str,IMGPath:str):
        cur.execute('UPDATE UserCart SET Prodects = ?,Price = ?,DateOfCart = ? ,ImagePath = ?\
                    WHERE UserID = ?',(Products,Price,DataOfCart,IMGPath,UserID))
        conn.commit()
        
        return ('تمت الأضافة للسلة الخاصة بك')
##-----------------------------GetMyUserCart -----------------------------##

    def ADDPhoneToCart(UserID:str,PhoneNum:str):
        cur.execute('UPDATE UserCart SET Loc = ? WHERE UserID = ?',(PhoneNum,UserID))
        return cur
##-----------------------------GetMyUserCart -----------------------------##

    def GetMyCart(UserID:str,Close:bool):
        cur.execute('SELECT * FROM UserCart WHERE UserID = ?',UserID)   
        #if (Close):
        #else : 

        return cur

##-----------------------------GetUserInfo -----------------------------##

    def GetUserInfo(target:str,type:str): 
        if (target == '*'):
            cur.execute('SELECT * FROM Users')   
        else:
            if (type == 'NUM'):
                cur.execute('SELECT * FROM Users WHERE UserID = ?',(target))   
            else:
                cur.execute('SELECT * FROM Users WHERE FirstName AND LastName = ?',(target.split(' ')))   

        return cur
##-----------------------------GetLoc -----------------------------##

    def GetLoc():
        cur.execute('SELECT * FROM LocitonCode ')   


        return cur
##----------------------------- SearchForProducts -----------------------------##

    def SearchOfItem(Code:str):
        cur.execute('SELECT * FROM Prroducts WHERE ProductsID = ?',Code)

        return cur
    
    def test():
        print('test')
        return 'test'
    
    #cur.execute('SELECT * FROM Users WHERE UserID = ? AND UserName = ?',(1,"admin"))
 
#    for row in cur.fetchall():
    #print(sendToOrderList('1256','test','test'))
 
except pyodbc.Error as e:
    print(e)
