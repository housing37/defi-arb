__fname = 'arb_searcher' # 102423: direct copy of 'atropa-kb-priv/_src/map_route/map_route.py'
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
#from web3 import Web3
#import inspect # this_funcname = inspect.stack()[0].function
#parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(parent_dir) # import from parent dir of this file

#------------------------------------------------------------#
#   GLOBALS
#------------------------------------------------------------#

#------------------------------------------------------------#
#   FUNCTION SUPPORT                                         #
#------------------------------------------------------------#
def get_pairs_lst(tok_addr, tok_symb, plog=True):
    try:
        url = f"https://api.dexscreener.io/latest/dex/tokens/{tok_addr}"
        response = requests.get(url)
        lst_pair_toks = []
        pair_skip_chain_cnt = 0
        if response.status_code == 200:
            data = response.json()
            for k,v in enumerate(data['pairs']):
                # ignore pairs not from 'pulsechain'|'pulsex'
                if v['chainId'] != 'pulsechain' or v['dexId'] != 'pulsex':
                    pair_skip_chain_cnt += 1
                    if plog: print(f' ... found chainId: "{v["chainId"]}" != "pulsechain" OR dexId: "{v["dexId"]}" != "pulsex" ... skip/continue _ {pair_skip_chain_cnt}')
                    continue
                    
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

                if str(base_tok_addr) != str(tok_addr) and str(base_tok_addr) not in lst_pair_toks:
                    lst_pair_toks.append({'tok_addr':base_tok_addr, 'pair_addr':pair_addr, 'liq':liquid, 'pr_BT':price_usd, 'tok_symb':base_tok_symb, 'tok_name':base_tok_name, dex_id:labels[0]})
                if str(quote_tok_addr) != str(tok_addr) and str(quote_tok_addr) not in lst_pair_toks:
                    lst_pair_toks.append({'tok_addr':quote_tok_addr, 'pair_addr':pair_addr, 'liq':liquid, 'pr_QT':price_usd, 'tok_symb':quote_tok_symb, 'tok_name':quote_tok_name, dex_id:labels[0]})

            return list(lst_pair_toks)
        else:
            print(f"Request failed with status code {response.status_code}\n returning empty list")
            return []
    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        print(f"Request error: {e};\n returning -1")
        return -1

def get_lps(t_addr='nil_', t_symb='nil_', t_name='nil_', d_print=True):
    print('', cStrDivider, f'Getting pairs for T | {t_symb}: {t_addr} _ {get_time_now()}', cStrDivider, sep='\n')
    lst_t_pair_toks = get_pairs_lst(t_addr, t_symb, d_print)
    
    if d_print: print('', cStrDivider, f'Print pairs for T | {t_symb}: {t_addr} _ {get_time_now()}', cStrDivider, sep='\n')
    if d_print: [print(d) for d in lst_t_pair_toks]
    
    # TODO: send_to_db(lst_t_pair_toks)
    
    return list(lst_t_pair_toks)

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
    addr_bond = '0x25d53961a27791B9D8b2d74FB3e937c8EAEadc38'
    addr_wpls = '0xA1077a294dDE1B09bB078844df40758a5D0f9a27'
    addr_bear = '0xd6c31bA0754C4383A41c0e9DF042C62b5e918f6d'
    addr_a1a = '0x697fc467720B2a8e1b2F7F665d0e3f28793E65e8'
    
    addr_legal = '0x0b1307dc5D90a0B60Be18D2634843343eBc098AF' # 1 LEGAL (LegalContract) _ 'LEGAL'
    addr_ojeon = '0xFa4d9C6E012d946853386113ACbF166deC5465Bb' # 500 ã (OjeonContract) _ (ã = E3889D)
    addr_ying = '0x271197EFe41073681577CdbBFD6Ee1DA259BAa3c'
    addr_lol = '0xA63F8061A67ecdbf147Cd1B60f91Cf95464E868D' # 999 LOL (LOLContract) _ (Þ = DE8D)
    addr_treas = '0x463413c579D29c26D59a65312657DFCe30D545A1' # 100,000 Treasury (TreasuryBillContract) _ 'TREASURY BILL'
    addr_bul8 = '0x2959221675bdF0e59D0cC3dE834a998FA5fFb9F4' # (1311 * 9**18) / 10**18 Bullion (Bullion8Contract) _ (â§ = E291A7)
    
    addr_write = '0x26D5906c4Cdf8C9F09CBd94049f99deaa874fB0b' # ޖޮޔިސްދޭވޯހީ (write) $M price token
    addr_r = '0x557F7e30aA6D909Cfe8a229A4CB178ab186EC622'
    addr_bear9 = '0x1f737F7994811fE994Fe72957C374e5cD5D5418A'
    
    addr_wenti = '0xA537d6F4c1c8F8C41f1004cc34C00e7Db40179Cc' # '问题 (问题) _ wenti'
    
    addr_atrop = '0xCc78A0acDF847A2C1714D2A925bB4477df5d48a6' # 313 Atropa (AtropaContract) _ 'ATROPA'
    addr_tsfi = '0x4243568Fa2bbad327ee36e06c16824cAd8B37819'
    addr_caw = '0xf3b9569F82B18aEf890De263B84189bd33EBe452'
    addr_pdai = '0x6B175474E89094C44Da98b954EedeAC495271d0F'
    #========================================================#

    get_lps(t_addr=addr_pdai,
            t_symb='pDAI',
            d_print=True)
    
    #addr_wenti = '0xA537d6F4c1c8F8C41f1004cc34C00e7Db40179Cc' # '问题 (问题) _ wenti'
    addr_bond = '0x25d53961a27791B9D8b2d74FB3e937c8EAEadc38'
    st0_addr = '0x52a4682880E990ebed5309764C7BD29c4aE22deB' # 2,000,000 유 (YuContract) _ (ì = EC9CA0)
    st1_addr = '0x347BC40503E0CE23fE0F5587F232Cd2D07D4Eb89' # 1 Di (DiContract) _ (ç¬¬ä½ = E7ACACE4BD9C)
    liq_tok_0 = '0xE63191967735C52f5de78CE2471759a9963Ce118' # 清导
    liq_tok_1 = '0x26D5906c4Cdf8C9F09CBd94049f99deaa874fB0b' # ޖޮޔިސްދޭވޯހީ (write)
    w_sec = 0
    time.sleep(w_sec)
    find_comm_toks_lvl_1(pt_addr=addr_bond,
                            pt_symb='BOND',
                            st_addr=st0_addr,
                            st_symb='LEGAL',
                            d_print=True)


if __name__ == "__main__":
    ## start ##
    run_time_start = get_time_now()
    print(f'\n\nRUN_TIME_START: {run_time_start}\n'+READ_ME)
    lst_argv_OG, argv_cnt = read_cli_args()
    
    ## exe ##
    go_main()
    
    ## end ##
    print(f'\n\nRUN_TIME_START: {run_time_start}\nRUN_TIME_END:   {get_time_now()}\n')

print('', cStrDivider, f'# END _ {__filename}', cStrDivider, sep='\n')
