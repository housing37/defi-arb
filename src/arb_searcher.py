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
addr_weth_eth = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
addr_wpls_pc = '0xA1077a294dDE1B09bB078844df40758a5D0f9a27'
LST_CHAIN_PARAMS = []
LST_CHAIN_PARAMS.append(['ethereum','WETH',addr_weth_eth])
#LST_CHAIN_PARAMS.append(['pulsechain','WPLS',addr_wpls_pc])
#LST_DEX_ROUTERS = ['solidlycom', 'kyberswap', 'pancakeswap', 'sushiswap']
NET_CALL_CNT = 0
ARB_OPP_CNT = 0

RUN_TIME_START = None
USD_DIFF = 100
USD_LIQ_REQ = 1000

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
        
        # set conditional for printing quote
        #   ignore uniswap v3, usd price errors, low liquidity
        #   NOTE: but don't want to ignore them for recursive calls
        #   NOTE_2: this logic allows cought cases to be stored
        #            but they won't be printed and have their quote list updated
        #       HENCE, skip_quote & non-hi_liq cases will indeed be printed
        #               when they are compared against non-skip_quote & hi_liq cases
        skip_quote = (dex_id == 'uniswap' and 'v3' in labels) or price_usd == '-1.0' or liquid < USD_LIQ_REQ
        hi_liq = liquid > float(price_usd)
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

                # NOTE: hi_liq 'should' still let the low liquidity pairs get stored
                #   but they won't be printed and have their quote list updated
                if hi_liq and not skip_quote:
                    quote = lst_quotes[-1]
                    # if this BT symbol is not stored already
                    #   and the price is diffrent than whats stored
                    #   and price is not set to -1
                    if symb != quote[1] and float(quote[-1]) != float(price_usd) and float(quote[-1]) != -1:
                        # check for price diff than what we've logged so far
                        diff = float(price_usd) - float(quote[-1])
                        diff_perc = abs(1 - (float(quote[-1]) / float(price_usd))) * 100
                        if diff >= USD_DIFF or diff <= -USD_DIFF:
                            ARB_OPP_CNT += 1
                            print(f'\n[r{NET_CALL_CNT}] _ T | {tok_symb}: {tok_addr} returned {len(data["pairs"])} pairs _ start: [{RUN_TIME_START}] _ now: [{get_time_now()}]')
                            print(f'FOUND arb-opp #{ARB_OPP_CNT} ... PRICE-DIFF = ${diff:,.2f} _ {diff_perc}%')
                            print(f'  base_tok | {lst_symbs[1]}: {addr} | {lst_symbs[2:5]}')
                            print(f'  quote_tok | {quote[1]}: {quote[2]} _ price: ${float(quote[-1]):,.2f}')
                            print(f'  pair_addr: {quote[0]}')
                            print(f'  LIQUIDITY: ${quote[3]:,.2f}')
                            print('\n  cross-dex ...')
                            print(f'   base_tok | {base_tok_symb}: {base_tok_addr} | {_chain_id}, {dex_id}, {labels}')
                            print(f'   quote_tok | {quote_tok_symb}: {quote_tok_addr} _ price: ${float(price_usd):,.2f}')
                            print(f'   pair_addr: {pair_addr}')
                            print(f'   LIQUIDITY: ${liquid:,.2f}')
                            print(f'\n  PRICE-DIFF = ${diff:,.2f} _ {diff_perc:,.2f}% diff\n')

                    DICT_ALL_SYMBS[addr][-1].append([pair_addr, quote_tok_symb, quote_tok_addr, liquid, price_usd])
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
    lst_d = []
    addr = symb = chain = 'nil'
    for c in LST_CHAIN_PARAMS:
        addr = c[2]
        symb = c[1]
        chain = c[0]
        d0 = search_for_arb(t_addr=addr,
                            t_symb=symb,
                            chain_id=chain,
                            d_print=True)
        lst_d.append([d0, addr, symb, chain])
                            
    print()
    for v in lst_d:
        d0 = v[0]
        print(f'{v[3]} _ start from token: {v[2]} _ unique tokens found: {len(v[0].keys())} ...')
        [print(k, d0[k][0:5]) for k in d0.keys()]
        print(f'{v[3]} _ start from token: {v[2]} _ unique tokens found: {len(v[0].keys())}\n')
        print(f'... NET_CALL_CNT: {NET_CALL_CNT} | ARB_OPP_CNT: {ARB_OPP_CNT}\n')

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
