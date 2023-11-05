__fname = 'arb_searcher'
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
print('', cStrDivider, f'GO _ {__filename} -> starting IMPORTs & declaring globals', cStrDivider, sep='\n')

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
#LST_CHAIN_PARAMS.append(['ethereum','WETH',addr_weth_eth])
#LST_CHAIN_PARAMS.append(['pulsechain','WPLS',addr_wpls_pc])
#LST_DEX_ROUTERS = ['solidlycom', 'kyberswap', 'pancakeswap', 'sushiswap']
NET_CALL_CNT = 0
ARB_OPP_CNT = 0

RUN_TIME_START = None
USD_DIFF = 100
USD_LIQ_REQ = 1000

# for net requests:
#   0.1 = ~200/min | 0.05 = ~240/min (stalls sometimes)
#   0.25 (doesn't seem to stall)
SLEEP_TIME = 0.25

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
    if d_print: print('', cStrDivider, f'Searching pairs recursively _ start T|{t_symb}: {t_addr} _ [{get_time_now()}]', cStrDivider, sep='\n')
    dict_all_symbs = scrape_dex_recurs(t_addr, t_symb, chain_id, {}, plog=False)
    #dict_all_symbs = scrape_dex_recurs_1(t_addr, t_symb, chain_id, {}, plog=False)

    print(f'... NET_CALL_CNT: {NET_CALL_CNT} | ARB_OPP_CNT: {ARB_OPP_CNT}\n')
    print(f'{chain_id} _ start from {t_symb} _ unique tokens found: {len(dict_all_symbs.keys())} ...')
    [print(idx, k, v[0:5]) for idx, (k,v) in enumerate(dict_all_symbs.items())]
    print(f'... {chain_id} _ start from {t_symb} _ unique tokens found: {len(dict_all_symbs.keys())}')
    print(f'... NET_CALL_CNT: {NET_CALL_CNT} | ARB_OPP_CNT: {ARB_OPP_CNT}\n')
    return dict(dict_all_symbs)

# house_102923: new algorithm attempt (not working at all)
# scrape dexscreener recursively
def scrape_dex_recurs_1(tok_addr, tok_symb, chain_id, DICT_ALL_SYMBS={}, plog=True):
    global NET_CALL_CNT, RUN_TIME_START, USD_DIFF, ARB_OPP_CNT, SLEEP_TIME
    NET_CALL_CNT += 1

    # API calls are limited to 300 requests per minute
    url = f"https://api.dexscreener.io/latest/dex/tokens/{tok_addr}"
    time.sleep(SLEEP_TIME) # 0.1 = ~200/min | 0.05 = ~240/min
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
        price_nat = '-1.0' if 'priceNative' not in v else v['priceNative']
        base_tok_addr = v['baseToken']['address']
        base_tok_symb = v['baseToken']['symbol']
        base_tok_name = v['baseToken']['name']
        quote_tok_addr = v['quoteToken']['address']
        quote_tok_symb = v['quoteToken']['symbol']
        quote_tok_name = v['quoteToken']['name']
        
#        base_tok_addr = v['baseToken']['address'] if v['baseToken']['address'] > 0 else 'nil_str'
#        base_tok_addr = 'nil_str'
        if len(base_tok_addr) < 1: base_tok_addr = 'nil_str'
        if len(base_tok_symb) < 1: base_tok_symb = 'nil_str'
        if len(base_tok_name) < 1: base_tok_name = 'nil_str'
        if len(quote_tok_addr) < 1: quote_tok_addr = 'nil_str'
        if len(quote_tok_symb) < 1: quote_tok_symb = 'nil_str'
        if len(quote_tok_name) < 1: quote_tok_name = 'nil_str'
        
#        if price_usd == '-1.0':
#            import pprint
#            pp = pprint.PrettyPrinter(indent=4)
#            pp.pprint(v)
#            print('exiting...')
#            exit(1)
#        print(f'checking liquidity: {liquid}')
        if liquid < 0:
            continue
        
#        if addr not in DICT_ALL_SYMBS:
        
        if _chain_id == chain_id:
            # recursive call to 'scrape_dex_recurs', until all QTs are found as BTs
            if tok_addr == base_tok_addr:
                addr = v['baseToken']['address']
                symb = v['baseToken']['symbol']
                if addr not in DICT_ALL_SYMBS:
                    DICT_ALL_SYMBS[addr] = [0, symb, v['chainId'], v['dexId'], labels, [[pair_addr, quote_tok_symb, quote_tok_addr, liquid, price_nat, price_usd]]]
                else:
                    DICT_ALL_SYMBS[addr][-1].append([pair_addr, quote_tok_symb, quote_tok_addr, liquid, price_nat, price_usd])
                    DICT_ALL_SYMBS[addr][0] = DICT_ALL_SYMBS[addr][0] + 1
                    
                    lst_symbs = DICT_ALL_SYMBS[addr] # legacy support
                    
                    # check for arb opp between OG pair addr and this new pair addr
                    dexid = DICT_ALL_SYMBS[addr][3]
                    lst_addr_info = DICT_ALL_SYMBS[addr]
                    lst_q = lst_addr_info[-1]
#                    found_qt = False
#                    for q in lst_q:
#                        q_addr = q[2]
#                        if q_addr == addr_quote:
#                            found_qt = True

                    # set conditional for printing quote
                    #   usd price errors and low liquidity
                    #   NOTE: but don't want to ignore them for recursive calls
                    #    this logic allows all cases to be stored & recursively assessed
                    #    but they won't be printed and have their quote list updated
                    #   HENCE, skip_quote & non-hi_liq cases will indeed be printed
                    #    when they are compared against non-skip_quote & hi_liq cases
                    skip_quote = price_usd == '-1.0' or liquid < USD_LIQ_REQ or dexid == dex_id
                    hi_liq = liquid > float(price_usd)
                    
                    # NOTE: hi_liq still lets the low liq pairs get stored
                    #   but low liq pairs not printed & have no quote list updates
#                    if not found_qt and not skip_quote and hi_liq:
                    if hi_liq and not skip_quote:
                        print(' | ')
                        #quote = lst_quotes[-1]
                        # if this BT symbol is not stored already
                        #   and the price is diffrent than whats stored
                        #   and price is not set to -1
                        #if symb != quote[1] and float(quote[-1]) != float(price_usd) and float(quote[-1]) != -1:
                        
                        quote = lst_q[0] # original BT quote info array
                        if float(quote[-1]) != float(price_usd):
                            print(' || ')

                            # check for native price diff and quoteTokens match
                            diff_nat = diff_perc_nat = log_diff_nat = -1
#                            if addr_quote == quote[2]:
#                                diff_nat = float(price_nat) - float(quote[-2])
#                                diff_perc_nat = abs(1 - (float(quote[-2]) / float(price_nat))) * 100
#                                log_diff_nat = f'{diff_nat:,.4f} {quote_tok_symb} _ {diff_perc_nat:,.2f}% diff _ {lst_symbs[3]} <-> {dex_id}'
                                
                            diff_nat = float(price_nat) - float(quote[-2])
                            diff_perc_nat = abs(1 - (float(quote[-2]) / float(price_nat))) * 100
                            log_diff_nat = f'{diff_nat:,.4f} {quote_tok_symb} _ {diff_perc_nat:,.2f}% diff _ {lst_symbs[3]} <-> {dex_id}'
                            
                            # check for usd price diff than what we've logged so far
                            diff_usd = float(price_usd) - float(quote[-1])
                            diff_perc = abs(1 - (float(quote[-1]) / float(price_usd))) * 100
                            usd_diff_ok = diff_usd >= USD_DIFF or diff_usd <= -USD_DIFF
                            nat_diff_ok = diff_nat
                            if usd_diff_ok:
                                print(' .. .. .. ')
                                ARB_OPP_CNT += 1
                                print(f'\n[r{NET_CALL_CNT}] _ T | {tok_symb}: {tok_addr} returned {len(data["pairs"])} pairs _ start: [{RUN_TIME_START}] _ now: [{get_time_now()}]')
                                print(f'FOUND arb-opp #{ARB_OPP_CNT} ... PRICE-DIFF = ${diff_usd:,.2f} _ {diff_perc:,.2f}%')
                                print(f'  base_tok | {lst_symbs[1]}: {addr} | {lst_symbs[2:5]}')
                                print(f'  quote_tok | {quote[1]}: {quote[2]} _ price: ${float(quote[-1]):,.2f} ({float(quote[-2])} {quote[1]})')
                                print(f'  pair_addr: {quote[0]}')
                                print(f'  LIQUIDITY: ${quote[3]:,.2f}')
                                print('\n  cross-dex ...')
                                print(f'   base_tok | {base_tok_symb}: {base_tok_addr} | {_chain_id}, {dex_id}, {labels}')
                                print(f'   quote_tok | {quote_tok_symb}: {quote_tok_addr} _ price: ${float(price_usd):,.2f} ({float(price_nat)} {quote_tok_symb})')
                                print(f'   pair_addr: {pair_addr}')
                                print(f'   LIQUIDITY: ${liquid:,.2f}')
                                print(f'\n  PRICE-DIFF-USD = ${diff_usd:,.2f} _ {diff_perc:,.2f}% diff _ {lst_symbs[3]} <-> {dex_id}')
                                print(f'  PRICE-DIFF-NAT = {log_diff_nat}\n')

#                        DICT_ALL_SYMBS[addr][-1].append([pair_addr, quote_tok_symb, quote_tok_addr, liquid, price_nat, price_usd])
                        #[print(k, DICT_ALL_SYMBS[k]) for k in DICT_ALL_SYMBS.keys()]
            else: # tok_addr == quote_tok_addr
#                scrape_dex_recurs_1(base_tok_addr, base_tok_symb, chain_id, DICT_ALL_SYMBS, plog=plog)
                scrape_dex_recurs_1(quote_tok_addr, quote_tok_symb, chain_id, DICT_ALL_SYMBS, plog=plog)
                
    return DICT_ALL_SYMBS
                
# scrape dexscreener recursively
def scrape_dex_recurs(tok_addr, tok_symb, chain_id, DICT_ALL_SYMBS={}, plog=True):
    global NET_CALL_CNT, RUN_TIME_START, USD_DIFF, ARB_OPP_CNT, SLEEP_TIME
    NET_CALL_CNT += 1

    # API calls are limited to 300 requests per minute
    url = f"https://api.dexscreener.io/latest/dex/tokens/{tok_addr}"
    time.sleep(SLEEP_TIME) # 0.1 = ~200/min | 0.05 = ~240/min
    data = exe_dexscreener_request(url)
    if plog: print('', cStrDivider, f'[{NET_CALL_CNT}] NET_CALL_CNT _ start: [{RUN_TIME_START}] _ now: [{get_time_now()}]', f'   {tok_symb}: {tok_addr} returned {len(data["pairs"])} pairs', cStrDivider, sep='\n')
    else: print(' .', end='', flush=True)
    
    for k,v in enumerate(data['pairs']):
        pair_addr = v['pairAddress']
        liquid = -1.0 if 'liquidity' not in v else v['liquidity']['usd']
        _chain_id = v['chainId']
        dex_id = v['dexId']
        labels = ['-1'] if 'labels' not in v else v['labels']
        price_usd = '-1.0' if 'priceUsd' not in v else v['priceUsd']
        price_nat = '-1.0' if 'priceNative' not in v else v['priceNative']
        base_tok_addr = v['baseToken']['address']
        base_tok_symb = v['baseToken']['symbol']
        base_tok_name = v['baseToken']['name']
        quote_tok_addr = v['quoteToken']['address']
        quote_tok_symb = v['quoteToken']['symbol']
        quote_tok_name = v['quoteToken']['name']
        
        if _chain_id == chain_id:
            if v['baseToken']['address'] and v['baseToken']['address'] not in DICT_ALL_SYMBS:
                addr = v['baseToken']['address']
                symb = v['baseToken']['symbol']
                DICT_ALL_SYMBS[addr] = [0, symb, v['chainId'], v['dexId'], labels, [[pair_addr, quote_tok_symb, quote_tok_addr, liquid, price_nat, price_usd]]]
                #[print(k, DICT_ALL_SYMBS[k]) for k in DICT_ALL_SYMBS.keys()]
                scrape_dex_recurs(addr, symb, chain_id, DICT_ALL_SYMBS, plog=plog)
            elif v['baseToken']['address'] in DICT_ALL_SYMBS:
                addr = v['baseToken']['address']
                symb = v['baseToken']['symbol']
                addr_quote = v['quoteToken']['address']
                DICT_ALL_SYMBS[addr][0] = DICT_ALL_SYMBS[addr][0] + 1
                
                lst_symbs = DICT_ALL_SYMBS[addr]
                lst_quotes = lst_symbs[-1]

                # set conditional for printing quote
                #   usd price errors and low liquidity
                #   NOTE: but don't want to ignore them for recursive calls
                #    this logic allows all cases to be stored & recursively assessed
                #    but they won't be printed and have their quote list updated
                #   HENCE, skip_quote & non-hi_liq cases will indeed be printed
                #    when they are compared against non-skip_quote & hi_liq cases
                skip_quote = price_usd == '-1.0' or liquid < USD_LIQ_REQ
                hi_liq = liquid > float(price_usd) or True # or True (disabled)

                # NOTE: hi_liq still lets the low liq pairs get stored
                #   but low liq pairs not printed & have no quote list updates
                if hi_liq and not skip_quote:
                    quote = lst_quotes[-1]
                    # if this BT symbol is not stored already
                    #   and the price is diffrent than whats stored
                    #   and price is not set to -1
                    if symb != quote[1] and float(quote[-1]) != float(price_usd) and float(quote[-1]) != -1:

                        # check for native price diff and quoteTokens match
                        diff_nat = diff_perc_nat = log_diff_nat = -1
                        if addr_quote == quote[2]:
                            diff_nat = float(price_nat) - float(quote[-2])
                            diff_perc_nat = abs(1 - (float(quote[-2]) / float(price_nat))) * 100
                            log_diff_nat = f'{diff_nat:,.4f} {quote_tok_symb} _ {diff_perc_nat:,.2f}% diff'
                        
                        # check for usd price diff than what we've logged so far
                        diff_usd = float(price_usd) - float(quote[-1])
                        diff_perc = abs(1 - (float(quote[-1]) / float(price_usd))) * 100
                        usd_diff_ok = diff_usd >= USD_DIFF or diff_usd <= -USD_DIFF
                        
                        # exclude arb from same dex/ver combo
                        dex_vers_ok = dex_id != lst_symbs[3] and labels[0] != lst_symbs[4][0]

                        # exclude tokens: [wstETH, graviAURA]
                        lst_addr_ignore = ['0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0', '0xBA485b556399123261a5F9c95d413B4f93107407']
                            # dexscreener misquotes / liquidity issues
                        base_addr_ok = base_tok_addr not in lst_addr_ignore
                        quote_addr_ok = quote_tok_addr not in lst_addr_ignore and quote[2] not in lst_addr_ignore
                        
                        # exclude dex 'balancer'
                        #dex_ok = not (dex_id == 'balancer' or lst_symbs[3] == 'balancer')
                        
                        # check for usd price diff based on max liquidity
                        diff_usd_low_liq = diff_perc_low_liq = log_diff_liq = low_liq = -1
                        if liquid < float(price_usd):
                            low_liq = liquid if liquid < quote[3] else quote[3]
                            low_liq_usd = liquid - quote[3] if liquid > quote[3] else quote[3] - liquid
                            diff_usd_low_liq = low_liq_usd * (diff_perc / 100)
                            diff_perc_low_liq = diff_perc
                            log_diff_liq = f'${diff_usd_low_liq:,.2f} _ {diff_perc_low_liq:,.2f}% diff'
                        
                        if dex_vers_ok and base_addr_ok and quote_addr_ok and usd_diff_ok:
                            ARB_OPP_CNT += 1
                            print(f'\n[r{NET_CALL_CNT}] _ T | {tok_symb}: {tok_addr} returned {len(data["pairs"])} pairs _ start: [{RUN_TIME_START}] _ now: [{get_time_now()}]')
                            print(f'FOUND arb-opp #{ARB_OPP_CNT} ... PRICE-DIFF = ${diff_usd:,.2f} _ {diff_perc:,.2f}%')
                            print(f'  base_tok | {lst_symbs[1]}: {addr} | {lst_symbs[2:5]}')
                            print(f'  quote_tok | {quote[1]}: {quote[2]} _ price: ${float(quote[-1]):,.2f} ({float(quote[-2])} {quote[1]})')
                            print(f'  pair_addr: {quote[0]}')
                            print(f'  LIQUIDITY: ${quote[3]:,.2f}')
                            print('\n  cross-dex ...')
                            print(f'   base_tok | {base_tok_symb}: {base_tok_addr} | {_chain_id}, {dex_id}, {labels}')
                            print(f'   quote_tok | {quote_tok_symb}: {quote_tok_addr} _ price: ${float(price_usd):,.2f} ({float(price_nat)} {quote_tok_symb})')
                            print(f'   pair_addr: {pair_addr}')
                            print(f'   LIQUIDITY: ${liquid:,.2f}')
                            print(f'\n  PRICE-DIFF-NAT = {log_diff_nat}')
                            print(f'  PRICE-DIFF-USD = {log_diff_liq} from lowest liquidity price _ ${low_liq:,.2f}')
                            print(f'\n  PRICE-DIFF-USD = ${diff_usd:,.2f} _ {diff_perc:,.2f}% diff from market prices _ {lst_symbs[3]} <-> {dex_id}\n')
                            

                    DICT_ALL_SYMBS[addr][-1].append([pair_addr, quote_tok_symb, quote_tok_addr, liquid, price_nat, price_usd])
                    #[print(k, DICT_ALL_SYMBS[k]) for k in DICT_ALL_SYMBS.keys()]

            if v['quoteToken']['address'] and v['quoteToken']['address'] not in DICT_ALL_SYMBS:
                addr = v['quoteToken']['address']
                symb = v['quoteToken']['symbol']
                DICT_ALL_SYMBS[addr] = [0, symb, v['chainId'], v['dexId'], labels, [['', '', '', -1, '-1', '-1']]]
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
    sel_chain = input('select chain to search...\n 0 = ethereum mainnet\n 1 = pulsechain\n 2 = both\n > ')
    assert 0 <= int(sel_chain) <= 2, 'invalid selection, aborting...'
    if sel_chain == '0':
        LST_CHAIN_PARAMS.append(['ethereum','WETH',addr_weth_eth])
    elif sel_chain == '1':
        LST_CHAIN_PARAMS.append(['pulsechain','WPLS',addr_wpls_pc])
    else:
        LST_CHAIN_PARAMS.append(['ethereum','WETH',addr_weth_eth])
        LST_CHAIN_PARAMS.append(['pulsechain','WPLS',addr_wpls_pc])

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
        #[print(k, d0[k][0:5]) for k in d0.keys()]
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
