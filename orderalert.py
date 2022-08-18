import config  #first do login run
from datetime import datetime, time as TT
import time
import pandas as pd
import requests
import traceback

from NorenApi import NorenApi    #tweaked for our purpose 


shoonya=NorenApi()  #shoonya is api name
shoonya.set_token()   #setting the token


# while True :
#     aim=float(shoonya.get_quotes('NSE','ITC-EQ')['lp'])
#     # b=a-1
#     print(aim) #to Get LTP
#     aimq=aim+1
#     print(aimq)


# type in telegram search “@RawDataBot” and hit “Enter.” and select telegram bot raw in orange color or Botfather
#Telegram Bot token

BOT_TOKEN = ''AAHO8NsccbWqtIRsvY8buEgOUD6Cu81EMTg”
BOT_CHAT_ID =''5301769958”

def getOrderDf(shoonya):
    ret = shoonya.get_order_book()
    orderdf = pd.DataFrame(ret)
    if ret is not None and 'avgprc' in orderdf.columns :
        orderdf = orderdf[['norenordno','tsym','qty','trantype','prd','prctyp','status','avgprc','fillshares']]
    return orderdf


def telegram_bot_sendtext(bot_message):
    try:
        bot_message = bot_message.replace('&','')
        print(bot_message)
        send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + BOT_CHAT_ID + '&parse_mode=HTML&text=' + bot_message
        res = requests.get(send_text)
        #logger.info(f'Telegram response : {res.json()}')
        time.sleep(1)
    except Exception as e:
        #logger.exception(f'Error in sending Telegram msg {e}')   
        print(e)

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://shoonyatrade.finvasia.com/NorenWClientTP/', websocket='wss://shoonyatrade.finvasia.com/NorenWSTP/', eodhost='https://shoonya.finvasia.com/chartApi/getdata/')

def startScan(api):
    telegram_bot_sendtext('Order Alert Started')
    orderdf1 = getOrderDf(api)
    while datetime.now().time() < TT(15,30)   :
        try:
            orderdf2 = getOrderDf(api)
            
            if orderdf2 is None or len(orderdf2) == 0:
                time.sleep(5)
                continue
            
            
            if len(orderdf2) > len(orderdf1): # New Order Entry 
                if len(orderdf1) == 0:
                    newOrderList = orderdf2
                else:    
                    newOrderList = orderdf2[~orderdf2.norenordno.isin(orderdf1.norenordno)]
                telegram_bot_sendtext(f'New Order Detected  {newOrderList.to_json(orient="records")}')
            
            if len(orderdf1) > 0  and len(orderdf2) > 0 :
                mergeDf = orderdf2.merge(orderdf1,how='inner', on='norenordno',suffixes=('_n', '_o'))
                #mergeDf.fillna({'fillshares_o':0,'fillshares_n':0},inplace = True)
                for i in mergeDf.index:
                    order = mergeDf.loc[i]
                    if order['status_o'] != order['status_n']:
                        telegram_bot_sendtext(f'Status Changed {order.to_json()}')

                    """elif order['fillshares_o'] != order['fillshares_n']:
                        telegram_bot_sendtext(f'Filled Qty Changed {order.to_json()}')"""


            orderdf1 = orderdf2.copy()
            time.sleep(5)
        except Exception as e:
            print('error in scan',e)
            traceback.print_exc()
    telegram_bot_sendtext('Order Alert Stopped')




def login():
    api = ShoonyaApiPy()
    res=api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei)
    print(res['prarr'])
    return api


if __name__ == "__main__":
    api = login()
    startScan(api)

