__fname = 'gastracker' # ported from 'altcointools' (121023)
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
print('', cStrDivider, f'GO _ {__filename} -> starting IMPORTs & declaring globals', cStrDivider, sep='\n')
cStrDivider_1 = '#----------------------------------------------------------------#'

'''
    # 1 =
    $ python3 gastracker.py 1
'''
#ref: https://docs.etherscan.io/api-endpoints/gas-tracker
#ref: https://etherscan.io/apis
from pprint import *
import requests
import time
import appscript
import sys
import os
import threading
from simple_email import *
import time
from datetime import datetime


ETHERSCAN_API_KEY = '2BXII1MZ6SQRFENYRSZIVZG42IUT8H22CE'
GET_URL = f'https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={ETHERSCAN_API_KEY}'
#GET_URL = f'https://scan.pulsechain.com/api?module=gastracker&action=gasoracle&apikey={ETHERSCAN_API_KEY}'

# ref: https://scan.pulsechain.com/api-docs
#GET_URL = f'https://scan.pulsechain.com/api'


# global static
bENABLE_ALERT_EMAIL = False
iSEC_REFRESH = 3 # note_022522: 2 sec interval started returning server rate limit error
iGWEI_ALERT = 25
iALERT_INTER = 15 # track | sec cnt (for triggered alerts)
pHEAD = '  time   _ [cnt] low   |   avg   |   high  |   SBF    | meta'

# global dynamics
iGWEI_LOW = -1
iGWEI_HIGH = -1
iTRACK_CNT = 0
LAST_ALERT_SEC = 0


def go_tracker(enable_alert=False):
    global iSEC_REFRESH, iSEC_REFRESH, iGWEI_LOW, iGWEI_HIGH, iTRACK_CNT, LAST_ALERT_SEC, bENABLE_ALERT_EMAIL
    time_now = get_time_now(timeconv=True, timeonly=False)
    print()
    print(f'gastracker.py _ GO ... [{time_now}]', f'(inter: {iSEC_REFRESH}sec, alert: {iGWEI_ALERT}gwei, alert_inter: {iALERT_INTER}sec)', '\n')
    print(f'{pHEAD}')
    print('---------------------------------------------------------------------------------')

    while True:
        try:
            response = requests.get(GET_URL)
            dict_resp = response.json()
        except Exception as e:
            print('!! Exception hit...', e, type(e), e.args, '\n')
            continue

        if dict_resp['message'].lower() == 'ok':
            results = dict_resp['result']
            high = int(results['FastGasPrice'])
            avg = int(results['ProposeGasPrice'])
            low = int(results['SafeGasPrice'])
            sbf = float(results['suggestBaseFee'])
            b_new_low = b_new_high = False
            
            #iGWEI_LOW = f'{low} {[iTRACK_CNT]}' if low < iGWEI_LOW or iGWEI_LOW == -1 else iGWEI_LOW
            if low < iGWEI_LOW or iGWEI_LOW == -1:
                iGWEI_LOW = low
                str_gwei_low = f'lo{[iTRACK_CNT]}: {low}'
                b_new_low = True
            
            #iGWEI_HIGH = f'{high} {[iTRACK_CNT]}' if high > iGWEI_HIGH else iGWEI_HIGH
            if high > iGWEI_HIGH:
                iGWEI_HIGH = high
                str_gwei_high = f'hi{[iTRACK_CNT]}: {high}'
                b_new_high = True
                
            time_now = get_time_now(timeconv=True, timeonly=True)
            p_data = f'{time_now} _ [{iTRACK_CNT}*]   {low}   |   {avg}   |   {high}   |   {sbf:.2f} | alert: {iGWEI_ALERT}gwei, {str_gwei_low}, {str_gwei_high}'
            print(f'{p_data}')
            if enable_alert:
                #valid_time_passed = iTRACK_CNT % iALERT_INTER == 0
                valid_time_passed = LAST_ALERT_SEC + iALERT_INTER < int(get_time_now())
                less_than_alert = low < iGWEI_ALERT
                if less_than_alert and valid_time_passed:
                    # launch new terminal
                    #pyPath = f'~/devzndlabs/git/zndlabs/etherscan.io/gastracker.py'
                    #appscript.app('Terminal').do_script(f'python3 {pyPath} {0}')
                    
                    msg = f"etherscan: trans price {low} <= '{iGWEI_ALERT}' : )"
                    notify(msg, p_data) # OSx notification
                    if bENABLE_ALERT_EMAIL:
                        THREAD_send_alert_email(low,msg+'\n'+p_data) # threaded
                    os.system(f"say 'low gas detected @ {low} gwi'") # gwei
                    LAST_ALERT_SEC = int(get_time_now())

                # audio alert on new all-time low (if lower than alert)
                if less_than_alert and b_new_low:
                    msg = f"_ etherscan: trans price {low} <= '{iGWEI_ALERT}' : )"
                    notify(msg, p_data) # OSx notification
                    os.system(f"say 'new low detected @ {low} gwi'") # gwei
                    
        
        iTRACK_CNT += 1
        time.sleep(iSEC_REFRESH)

def THREAD_send_alert_email(low,msg):
    thread = threading.Thread(target = email_send_gas_price, args = (37, low, msg))
    thread.start()
    
#ref: https://stackoverflow.com/a/41318195/2298002
def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))
    
def get_time_now(timeconv=False, timeonly=False):
    timenow = '%s' % int(round(time.time()))
    if timeconv:
        timenow = datetime.fromtimestamp(int(timenow))
        if timeonly:
            timenow = str(timenow).split(' ')[1]
    return timenow

str_help = (
"""
 -- required: 1 = enable alerts | 0 = disable",
 -- optional: set num GWEI price alert (iGWEI_ALERT)',
 -- example: "$ python3 gastracker.py 1",
 -- example: "$ python3 gastracker.py 1 20"
""")
if __name__ == "__main__":
    try:
        if len(sys.argv) == 2 and sys.argv[1] == '--help':
            print('\n --help detected... ', str_help, '\nexit...')
            exit()
        argv = int(sys.argv[1]) # 1 = enable alerts | 0 = disable
        if len(sys.argv) == 3:
            iGWEI_ALERT = int(sys.argv[2]) # sets GWEI price alert (iGWEI_ALERT)
    except Exception as e:
        print('\n -- ERROR detecte: invalid args...', f'\n -- Exception e.args: {e.args}', str_help, '\nexit...')
        exit()
        
    go_tracker(argv)
    
