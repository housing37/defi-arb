__fname = 'arb_searcher'
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
print('', cStrDivider, f'START _ {__filename}', cStrDivider, sep='\n')
print(f'GO {__filename} -> starting IMPORTs and globals decleration')

#------------------------------------------------------------#
#   IMPORTS                                                  #
#------------------------------------------------------------#
import sys, os, time, traceback
from datetime import datetime
import requests, json
#from web3 import Web3
#import inspect # this_funcname = inspect.stack()[0].function
#parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(parent_dir) # import from parent dir of this file

#------------------------------------------------------------#
#   GLOBALS
#------------------------------------------------------------#
#LST_CHAIN_IDs = ['ethereum', 'pulsechain']
#LST_DEX_IDs_eth = ['uniswap', 'sushiswap', 'balancer', 'pancakeswap']
#LST_DEX_IDs_pc = ['pulsex']
#
#lst_pair_toks_cid = []
#lst_pair_toks = []
NET_CALL_CNT = 0
ARB_OPP_CNT = 0

RUN_TIME_START = None
USD_DIFF = 1000
USD_LIQ_REQ = 10000

#------------------------------------------------------------#
#   FUNCTION SUPPORT                                         #
#------------------------------------------------------------#
def exe_dexscreener_request(url='nil_url'):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json() # data
        else:
            print(f"Request failed with status code {response.status_code}\n returning empty list")
            return []
    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        print_exception(e, debugLvl=0)
        return -1
        
def search_for_arb(t_addr='nil_', t_symb='nil_', t_name='nil_', chain_id='nil_', d_print=True):
    global NET_CALL_CNT
    if d_print: print('', cStrDivider, f'Print symbols for start TOKEN | {t_symb}: {t_addr} _ {get_time_now()}', cStrDivider, sep='\n')
    dict_all_symbs = scrape_dex_recurs(t_addr, t_symb, chain_id, {}, plog=False)

    print(f'... NET_CALL_CNT: {NET_CALL_CNT} | ARB_OPP_CNT: {ARB_OPP_CNT}\n')
    print(f'{chain_id} _ start from {t_symb} _ unique tokens found: {len(dict_all_symbs.keys())} ...')
    [print(k, dict_all_symbs[k][0:5]) for k in dict_all_symbs.keys()]
    print(f'... {chain_id} _ start from {t_symb} _ unique tokens found: {len(dict_all_symbs.keys())}')
    print(f'... NET_CALL_CNT: {NET_CALL_CNT} | ARB_OPP_CNT: {ARB_OPP_CNT}\n')
    return dict(dict_all_symbs)

# scrape dexscreener recursively
def scrape_dex_recurs(tok_addr, tok_symb, chain_id, DICT_ALL_SYMBS={}, plog=True):
    global NET_CALL_CNT, RUN_TIME_START, USD_DIFF, ARB_OPP_CNT
    NET_CALL_CNT += 1

    # API calls are limited to 300 requests per minute
    url = f"https://api.dexscreener.io/latest/dex/tokens/{tok_addr}"
    time.sleep(0.05) # 0.1 = ~200/min | 0.05 = ~240/min
    data = exe_dexscreener_request(url)
    if plog: print('', cStrDivider, f'[{NET_CALL_CNT}] NET_CALL_CNT _ start: [{RUN_TIME_START}] _ now: [{get_time_now()}]', f'   {tok_symb}: {tok_addr} returned {len(data["pairs"])} pairs', cStrDivider, sep='\n')
    else: print('.', end=' ', flush=True)
    
    for k,v in enumerate(data['pairs']):
        pair_addr = v['pairAddress']
        liquid = -1.0 if 'liquidity' not in v else v['liquidity']['usd']
        _chain_id = v['chainId']
        dex_id = v['dexId']
        labels = ['-1'] if 'labels' not in v else v['labels']
        price_usd = '-1.0' if 'priceUsd' not in v else v['priceUsd']
        base_tok_addr = v['baseToken']['address']
        base_tok_symb = v['baseToken']['symbol']
        base_tok_name = v['baseToken']['name']
        quote_tok_addr = v['quoteToken']['address']
        quote_tok_symb = v['quoteToken']['symbol']
        quote_tok_name = v['quoteToken']['name']
        
        # check liquidity requirement
        if liquid < USD_LIQ_REQ:
            continue
            
        # ignore usd price errors
        if price_usd == '-1.0':
            continue
            
        # ignore uniswap v3 (compatible w/ v2 code?)
        if dex_id == 'uniswap' and 'v3' in labels:
            continue
            
        if _chain_id == chain_id:
            if v['baseToken']['address'] and v['baseToken']['address'] not in DICT_ALL_SYMBS:
                addr = v['baseToken']['address']
                symb = v['baseToken']['symbol']
                DICT_ALL_SYMBS[addr] = [0, symb, v['chainId'], v['dexId'], labels, [[pair_addr, quote_tok_symb, quote_tok_addr, liquid, price_usd]]]
                #[print(k, DICT_ALL_SYMBS[k]) for k in DICT_ALL_SYMBS.keys()]
                scrape_dex_recurs(addr, symb, chain_id, DICT_ALL_SYMBS, plog=plog)
            elif v['baseToken']['address'] in DICT_ALL_SYMBS:
                addr = v['baseToken']['address']
                symb = v['baseToken']['symbol']
                DICT_ALL_SYMBS[addr][0] = DICT_ALL_SYMBS[addr][0] + 1
                
                lst_symbs = DICT_ALL_SYMBS[addr]
                lst_quotes = lst_symbs[-1]
                append_qoute = True
                for quote in lst_quotes:
                    # if this BT symbol is not stored already
                    #   and the price is diffrent than whats stored
                    #   and price is not set to -1
                    if symb != quote[1] and float(quote[-1]) != float(price_usd) and float(quote[-1]) != -1:
                        # check for price diff than what we've logged so far
                        diff = float(quote[-1]) - float(price_usd)
                        if diff >= USD_DIFF or diff <= -USD_DIFF:
                            ARB_OPP_CNT += 1
                            print(f'\n[r{NET_CALL_CNT}] _ T | {tok_symb}: {tok_addr} returned {len(data["pairs"])} pairs _ start: [{RUN_TIME_START}] _ now: [{get_time_now()}]')
                            print(f'FOUND arb-opp #{ARB_OPP_CNT} ... PRICE-DIFF = ${diff:,.2f}')
                            print(f'  base_tok | {lst_symbs[1]}: {addr} | {lst_symbs[2:5]}')
                            print(f'  quote_tok | {quote[1]}: {quote[2]} _ price: ${float(quote[-1]):,.2f}')
                            print(f'  pair_addr: {quote[0]}')
                            print(f'  LIQUIDITY: ${quote[3]:,.2f}')
                            print('\n  cross-dex ...')
                            print(f'   base_tok | {base_tok_symb}: {base_tok_addr} | {_chain_id}, {dex_id}, {labels}')
                            print(f'   quote_tok | {quote_tok_symb}: {quote_tok_addr} _ price: ${float(price_usd):,.2f}')
                            print(f'   pair_addr: {pair_addr}')
                            print(f'   LIQUIDITY: ${liquid:,.2f}')
                            print(f'\n  PRICE-DIFF = ${diff:,.2f}\n')
                    if pair_addr == quote[0]:
                        append_qoute = False
                if append_qoute: DICT_ALL_SYMBS[addr][-1].append([pair_addr, quote_tok_symb, quote_tok_addr, liquid, price_usd])
                #[print(k, DICT_ALL_SYMBS[k]) for k in DICT_ALL_SYMBS.keys()]

            if v['quoteToken']['address'] and v['quoteToken']['address'] not in DICT_ALL_SYMBS:
                addr = v['quoteToken']['address']
                symb = v['quoteToken']['symbol']
                DICT_ALL_SYMBS[addr] = [0, symb, v['chainId'], v['dexId'], labels, [['', '', '', -1, '-1']]]
                #[print(k, DICT_ALL_SYMBS[k]) for k in DICT_ALL_SYMBS.keys()]
                scrape_dex_recurs(addr, symb, chain_id, DICT_ALL_SYMBS, plog=plog)
            elif v['quoteToken']['address'] in DICT_ALL_SYMBS:
                addr = v['quoteToken']['address']
                DICT_ALL_SYMBS[addr][0] = DICT_ALL_SYMBS[addr][0] + 1
                #[print(k, DICT_ALL_SYMBS[k]) for k in DICT_ALL_SYMBS.keys()]
                
    return DICT_ALL_SYMBS

#------------------------------------------------------------#
#   DEFAULT SUPPORT                                          #
#------------------------------------------------------------#
READ_ME = f'''
    *DESCRIPTION*
        search for arbitrage opportunites via dexscreener
         - loop through each chain ID
         - for each token address,
            log token value diffs between dex routers

    *NOTE* INPUT PARAMS...
        nil
        
    *EXAMPLE EXECUTION*
        $ python3 {__filename} -<nil> <nil>
        $ python3 {__filename}
'''
#ref: https://stackoverflow.com/a/1278740/2298002
def print_exception(e, debugLvl=0):
    #print type(e)       # the exception instance
    #print e.args        # arguments stored in .args
    #print e             # __str__ allows args to be printed directly
    print('', cStrDivider, f' Exception Caught _ e: {e}', cStrDivider, sep='\n')
    if debugLvl > 0:
        print('', cStrDivider, f' Exception Caught _ type(e): {type(e)}', cStrDivider, sep='\n')
    if debugLvl > 1:
        print('', cStrDivider, f' Exception Caught _ e.args: {e.args}', cStrDivider, sep='\n')

    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #print(traceback.format_exc())
    strTrace = traceback.format_exc()
    #print(exc_type, fname, exc_tb.tb_lineno)
    print('', cStrDivider, f' type: {exc_type}', f' file: {fname}', f' line_no: {exc_tb.tb_lineno}', f' traceback: {strTrace}', cStrDivider, sep='\n')
    
def wait_sleep(wait_sec : int, b_print=True, bp_one_line=True): # sleep 'wait_sec'
    print(f'waiting... {wait_sec} sec')
    for s in range(wait_sec, 0, -1):
        if b_print and bp_one_line: print(wait_sec-s+1, end=' ', flush=True)
        if b_print and not bp_one_line: print('wait ', s, sep='', end='\n')
        time.sleep(1)
    if bp_one_line and b_print: print() # line break if needed
    print(f'waiting... {wait_sec} sec _ DONE')
        
def get_time_now(dt=True):
    if dt: return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[0:-4]
    return datetime.now().strftime("%H:%M:%S.%f")[0:-4]
    
def read_cli_args():
    print(f'\nread_cli_args...\n # of args: {len(sys.argv)}\n argv lst: {str(sys.argv)}')
    for idx, val in enumerate(sys.argv): print(f' argv[{idx}]: {val}')
    print('read_cli_args _ DONE\n')
    return sys.argv, len(sys.argv)

def go_main():
#    addr_bond = '0x25d53961a27791B9D8b2d74FB3e937c8EAEadc38'
#    addr_wpls = '0xA1077a294dDE1B09bB078844df40758a5D0f9a27'
#    addr_bear = '0xd6c31bA0754C4383A41c0e9DF042C62b5e918f6d'
#    addr_a1a = '0x697fc467720B2a8e1b2F7F665d0e3f28793E65e8'
#
#    addr_legal = '0x0b1307dc5D90a0B60Be18D2634843343eBc098AF' # 1 LEGAL (LegalContract) _ 'LEGAL'
#    addr_ojeon = '0xFa4d9C6E012d946853386113ACbF166deC5465Bb' # 500 ã (OjeonContract) _ (ã = E3889D)
#    addr_ying = '0x271197EFe41073681577CdbBFD6Ee1DA259BAa3c'
#    addr_lol = '0xA63F8061A67ecdbf147Cd1B60f91Cf95464E868D' # 999 LOL (LOLContract) _ (Þ = DE8D)
#    addr_treas = '0x463413c579D29c26D59a65312657DFCe30D545A1' # 100,000 Treasury (TreasuryBillContract) _ 'TREASURY BILL'
#    addr_bul8 = '0x2959221675bdF0e59D0cC3dE834a998FA5fFb9F4' # (1311 * 9**18) / 10**18 Bullion (Bullion8Contract) _ (â§ = E291A7)
#
#    addr_write = '0x26D5906c4Cdf8C9F09CBd94049f99deaa874fB0b' # ޖޮޔިސްދޭވޯހީ (write) $M price token
#    addr_r = '0x557F7e30aA6D909Cfe8a229A4CB178ab186EC622'
#    addr_bear9 = '0x1f737F7994811fE994Fe72957C374e5cD5D5418A'
#
#    addr_wenti = '0xA537d6F4c1c8F8C41f1004cc34C00e7Db40179Cc' # '问题 (问题) _ wenti'
#
#    addr_atrop = '0xCc78A0acDF847A2C1714D2A925bB4477df5d48a6' # 313 Atropa (AtropaContract) _ 'ATROPA'
#    addr_tsfi = '0x4243568Fa2bbad327ee36e06c16824cAd8B37819'
#    addr_caw = '0xf3b9569F82B18aEf890De263B84189bd33EBe452'
    #addr_wenti = '0xA537d6F4c1c8F8C41f1004cc34C00e7Db40179Cc' # '问题 (问题) _ wenti'
#    addr_bond = '0x25d53961a27791B9D8b2d74FB3e937c8EAEadc38'
#    st0_addr = '0x52a4682880E990ebed5309764C7BD29c4aE22deB' # 2,000,000 유 (YuContract) _ (ì = EC9CA0)
#    st1_addr = '0x347BC40503E0CE23fE0F5587F232Cd2D07D4Eb89' # 1 Di (DiContract) _ (ç¬¬ä½ = E7ACACE4BD9C)
#    liq_tok_0 = '0xE63191967735C52f5de78CE2471759a9963Ce118' # 清导
#    liq_tok_1 = '0x26D5906c4Cdf8C9F09CBd94049f99deaa874fB0b' # ޖޮޔިސްދޭވޯހީ (write)
    addr_pdai = '0x6B175474E89094C44Da98b954EedeAC495271d0F'
    addr_weth_eth = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
    addr_wpls_pc = '0xA1077a294dDE1B09bB078844df40758a5D0f9a27'
    #========================================================#

#    choose = input('\n Scrape dexscreener for unique tokens? [y/n]: ')
#    assert choose == 'y', "  didn't pick 'y', exiting..."
    
    c0 = 'ethereum'
    s0 = 'WETH (on ethereum)'
    d0 = search_for_arb(t_addr=addr_weth_eth,
                        t_symb=s0,
                        chain_id=c0,
                        d_print=True)

    
#    c1 = 'pulsechain'
#    s1 = 'WPLS'
#    d1 = search_for_arb(t_addr=addr_wpls_pc,
#                        t_symb=s1,
#                        chain_id=c1,
#                        d_print=True)
#
#    print()
#    [print(k, d0[k][0:5]) for k in d0.keys()]
#    print(f'{c0} _ start from {s0} _ unique tokens found: {len(d0.keys())} ...\n')
#    [print(k, d1[k][0:5]) for k in d1.keys()]
#    print(f'{c1} _ start from {s1} _ unique tokens found: {len(d1.keys())} ...\n')

if __name__ == "__main__":
    ## start ##
    RUN_TIME_START = get_time_now()
    print(f'\n\nRUN_TIME_START: {RUN_TIME_START}\n'+READ_ME)
    lst_argv_OG, argv_cnt = read_cli_args()
    
    ## exe ##
    try:
        go_main()
    except Exception as e:
        print_exception(e, debugLvl=0)
    
    ## end ##
    print(f'\n\nRUN_TIME_START: {RUN_TIME_START}\nRUN_TIME_END:   {get_time_now()}\n')

print('', cStrDivider, f'# END _ {__filename}', cStrDivider, sep='\n')
