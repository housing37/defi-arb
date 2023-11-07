__fname = 'track_liq'
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
print('', cStrDivider, f'START _ {__filename}', cStrDivider, sep='\n')
print(f'GO {__filename} -> starting IMPORTs and globals decleration')

#------------------------------------------------------------#
#   IMPORTS                                                  #
#------------------------------------------------------------#
import sys, os, time
from datetime import datetime
import requests, json
import db_controller as dbc
#from web3 import Web3
#import inspect # this_funcname = inspect.stack()[0].function
#parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(parent_dir) # import from parent dir of this file

#------------------------------------------------------------#
#   GLOBALS
#------------------------------------------------------------#
SEC_WAIT = 60*10 # 10 minutes

#------------------------------------------------------------#
#   FUNCTNION SUPPORT                                        #
#------------------------------------------------------------#
def parse_pairs_lst(data, tok_addr, plog=True):

    lst_pair_toks = []
    pair_skip_chain_cnt = 0
    for k,v in enumerate(data['pairs']):
        # ignore pairs not from 'pulsechain'|'pulsex'
        if v['chainId'] != 'pulsechain' or v['dexId'] != 'pulsex':
            pair_skip_chain_cnt += 1
            if plog: print(f' ... found chainId: "{v["chainId"]}" != "pulsechain" OR dexId: "{v["dexId"]}" != "pulsex" ... skip/continue _ {pair_skip_chain_cnt}')
            continue


#        pair_type = 'QT' if str(base_tok_addr) == str(tok_addr) else 'BT' # paried WITH QT|BT ?
#        liquid = -1 if 'liquidity' not in v else v['liquidity']['usd']
#        price_usd = -1 if 'priceUsd' not in v else v['priceUsd']
#        lst_pair_toks.append({
#                'chain_id':v['chainId'],
#                'dex_id':v['dexId'],
#                'dex_id_v':v['labels'][0],
#                'p_addr':v['pairAddress'],
#                'p_type':pair_type,
#                'p_liq':liquid,
#                'price_usd':price_usd,
#                'p_bt_name':v['baseToken']['address'],
#                'p_bt_symb':v['baseToken']['symbol'],
#                'p_bt_addr':v['baseToken']['name'],
#                'p_qt_name':v['quoteToken']['address'],
#                'p_qt_symb':v['quoteToken']['symbol'],
#                'p_qt_addr':v['quoteToken']['name']})
                
        pair_addr = v['pairAddress']
        liquid = -1 if 'liquidity' not in v else v['liquidity']['usd']
        chain_id = v['chainId']
        dex_id = v['dexId']
        labels = v['labels']
        price_usd = -1 if 'priceUsd' not in v else v['priceUsd']
        base_tok_addr = v['baseToken']['address']
        base_tok_symb = v['baseToken']['symbol']
        base_tok_name = v['baseToken']['name']
        quote_tok_addr = v['quoteToken']['address']
        quote_tok_symb = v['quoteToken']['symbol']
        quote_tok_name = v['quoteToken']['name']

        ## filter out duplicates ##
        # if the paired token is BT & not yet in lst_pair_toks
        #   add BT to lst_pair_toks
        if str(base_tok_addr) != str(tok_addr) and str(base_tok_addr) not in lst_pair_toks:
            # NOTE: dict order must match db stored proc param order
            lst_pair_toks.append({
                    'chain_id':chain_id,
                    'dex_id':dex_id,
                    'dex_id_v':labels[0],
                    'tok_name':quote_tok_name,
                    'tok_symb':quote_tok_symb,
                    'tok_addr':quote_tok_addr,
                    'tok_price_usd':price_usd,
                    'liq_usd':liquid,
                    'p_tok_type':'BT',
                    'p_addr':pair_addr,
                    'p_tok_name':base_tok_name,
                    'p_tok_symb':base_tok_symb,
                    'p_tok_addr':base_tok_addr})
            
        # if the paired token is QT & not yet in lst_pair_toks
        #   add QT to lst_pair_toks
        if str(quote_tok_addr) != str(tok_addr) and str(quote_tok_addr) not in lst_pair_toks:
            # NOTE: dict order must match db stored proc param order
            lst_pair_toks.append({
                    'chain_id':chain_id,
                    'dex_id':dex_id,
                    'dex_id_v':labels[0],
                    'tok_name':base_tok_name,
                    'tok_symb':base_tok_symb,
                    'tok_addr':base_tok_addr,
                    'tok_price_usd':price_usd,
                    'liq_usd':liquid,
                    'p_tok_type':'QT',
                    'p_addr':pair_addr,
                    'p_tok_name':quote_tok_name,
                    'p_tok_symb':quote_tok_symb,
                    'p_tok_addr':quote_tok_addr})

    return list(lst_pair_toks)
    
def get_pairs_lst(url='nil_url'):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Request failed with status code {response.status_code}\n returning empty list")
            return []
    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        print(f"Request error: {e};\n returning -1")
        return -1
        
def db_add_log(proc_name, keyVals, go_print=False):
    #if kPin in keyVals: del keyVals[kPin]
    db_return = dbc.exe_stored_proc(-1, proc_name, keyVals)
    bErr = 'status' not in db_return[0] or db_return[0]['status'] != 'success'
    if bErr and go_print:
        print(f'\n\n*** DB ERROR ***', " _ bErr from '{proc_name}'", f"info:\n {db_return}", '*** DB ERROR ***\n', sep='\n')
    return db_return, bErr, db_return[0]['info']

def get_lps(t_addr='nil_', t_name='nil_', t_symb='nil_', d_print=True):
    print('', cStrDivider, f'Getting/Parsing pairs for T | {t_symb}: {t_addr} _ {get_time_now()}', cStrDivider, sep='\n')
    data = get_pairs_lst(f"https://api.dexscreener.io/latest/dex/tokens/{t_addr}")
    lst_t_pair_toks = parse_pairs_lst(data, t_addr, d_print)
        # NOTE: ignores pairs not from 'pulsechain'|'pulsex'
        
    if d_print: print('', cStrDivider, f'Print pairs for T | {t_symb}: {t_addr} _ {get_time_now()}', cStrDivider, sep='\n')
    if d_print: [print(d) for d in lst_t_pair_toks]
    return list(lst_t_pair_toks)

def log_pair_lst(lst_t_pair_toks):
    # update db
    for d in lst_t_pair_toks:
        # NOTE_0: dict order must match db stored proc param order
        # NOTE_1: db performs sanity check to prevent dup pair_addr logs (due to multiple LP to BT/QT combos)
        lst_db_return, failed, info = db_add_log('tok_pair_ADD_LOG', d, go_print=False)
        if failed:
            print(f'** LOG to db FAILED ** ... liq: ${d["liq_usd"]} _ pair_addr: {d["p_addr"]} _ [{get_time_now()}]')
            print(f'  db_info = {info}\n')
        else:
            print(f'LOGGED successfully to db... liq: ${d["liq_usd"]} _ pair_addr: {d["p_addr"]} _ [{get_time_now()}]')
            print(f' T | {d["tok_symb"]} _ {d["tok_addr"]} _ price: ${d["tok_price_usd"]}')
            print(f' {d["p_tok_type"]} | {d["p_tok_symb"]} _ {d["p_tok_addr"]}\n')
    
    return list(lst_t_pair_toks)

#------------------------------------------------------------#
#   DEFAULT SUPPORT                                          #
#------------------------------------------------------------#
READ_ME = f'''
    *EXAMPLE EXECUTION*
        $ python3 {__filename} -<nil> <nil>
        $ python3 {__filename}
        
    *NOTE* INPUT PARAMS...
        nil
'''
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
    dict_tokens = {
            'wpls':'0xA1077a294dDE1B09bB078844df40758a5D0f9a27',
            'bear':'0xd6c31bA0754C4383A41c0e9DF042C62b5e918f6d',
            'a1a':'0x697fc467720B2a8e1b2F7F665d0e3f28793E65e8',
#            'ying':'0x271197EFe41073681577CdbBFD6Ee1DA259BAa3c',
#            'write':'0x26D5906c4Cdf8C9F09CBd94049f99deaa874fB0b', # ޖޮޔިސްދޭވޯހީ (write) $M price token
            'r':'0x557F7e30aA6D909Cfe8a229A4CB178ab186EC622',
            'bear9':'0x1f737F7994811fE994Fe72957C374e5cD5D5418A',
#            'wenti':'0xA537d6F4c1c8F8C41f1004cc34C00e7Db40179Cc', # '问题 (问题) _ wenti'
#            'atropa':'0xCc78A0acDF847A2C1714D2A925bB4477df5d48a6', # 313 Atropa (AtropaContract) _ 'ATROPA'
            'tsfi':'0x4243568Fa2bbad327ee36e06c16824cAd8B37819',
            'caw':'0xf3b9569F82B18aEf890De263B84189bd33EBe452',

            'wenti':'0xA537d6F4c1c8F8C41f1004cc34C00e7Db40179Cc', # '问题 (问题) _ wenti'
            'Yu':'0x52a4682880E990ebed5309764C7BD29c4aE22deB', # 2,000,000 유 (YuContract) _ (ì = EC9CA0)
            'Di':'0x347BC40503E0CE23fE0F5587F232Cd2D07D4Eb89', # 1 Di (DiContract) _ (ç¬¬ä½ = E7ACACE4BD9C)
            '清导':'0xE63191967735C52f5de78CE2471759a9963Ce118', # 清导
            'write':'0x26D5906c4Cdf8C9F09CBd94049f99deaa874fB0b', # ޖޮޔިސްދޭވޯހީ (write) $M price token

            'bond':'0x25d53961a27791B9D8b2d74FB3e937c8EAEadc38',
            'Legal':'0x0b1307dc5D90a0B60Be18D2634843343eBc098AF', # 1 LEGAL (LegalContract) _ 'LEGAL'
            'Ojeon':'0xFa4d9C6E012d946853386113ACbF166deC5465Bb', # 500 ã (OjeonContract) _ (ã = E3889D)
            'Ying':'0x271197EFe41073681577CdbBFD6Ee1DA259BAa3c', # 900 Ying (YingContract) _ (ç±¯ = E7B1AF)
            'LOL':'0xA63F8061A67ecdbf147Cd1B60f91Cf95464E868D', # 999 LOL (LOLContract) _ (Þ = DE8D)
            'Atropa':'0xCc78A0acDF847A2C1714D2A925bB4477df5d48a6', # 313 Atropa (AtropaContract) _ 'ATROPA'
            'Treas':'0x463413c579D29c26D59a65312657DFCe30D545A1', # 100,000 Treasury (TreasuryBillContract) _ 'TREASURY BILL'
            'BUL8':'0x2959221675bdF0e59D0cC3dE834a998FA5fFb9F4' # 131.1 Bullion (Bullion8Contract) _ (â§ = E291A7)
        }
    #========================================================#
    cnt = 0
    for k,v in dict_tokens.items():
        lst_t_pair_toks = get_lps(t_addr=v, t_symb=k, d_print=False)
        log_pair_lst(lst_t_pair_toks)
        cnt+=1
    return cnt

if __name__ == "__main__":
    ## start ##
    run_time_start = get_time_now()
    print(f'\n\nRUN_TIME_START: {run_time_start}\n'+READ_ME)
    lst_argv_OG, argv_cnt = read_cli_args()
    
    ## exe ##
    tot_req_cnt = tot_iter_cnt = 0
    while True:
        net_req_cnt = go_main()
        tot_req_cnt += net_req_cnt
        tot_iter_cnt += 1
        print(f'\nRequest Cycle #{tot_iter_cnt}: {net_req_cnt} requests ({tot_req_cnt} total since start)')
        wait_sleep(SEC_WAIT, b_print=True, bp_one_line=True)
        #wait_sleep(5, b_print=True, bp_one_line=True)
    
    ## end ##
    print(f'\n\nRUN_TIME_START: {run_time_start}\nRUN_TIME_END:   {get_time_now()}\n')

print('', cStrDivider, f'# END _ {__filename}', cStrDivider, sep='\n')
