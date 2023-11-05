# house_110523
'''
	decodes function hex value function signature acquired from blockchain explore raw trace
        requires contract address and ABI file (may need to decompile to get ABI)
'''
__fname = '_decode_func_sign' # 102423: direct copy of 'atropa-kb-priv/_src/map_route/map_route.py'
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
print('', cStrDivider, f'GO _ {__filename} -> starting IMPORTs & declaring globals', cStrDivider, sep='\n')

from web3 import Web3, HTTPProvider
import env

print('\nsetting globals...')
abi_file = "../contracts/Balancer_0xce88.json"
CONTR_ARB_ADDR = '0xce88686553686da562ce7cea497ce749da109f9f'

print('initializing web3...')
RPC_URL = env.pc_main
W3 = Web3(HTTPProvider(RPC_URL))
CONTR_ARB_ADDR = W3.to_checksum_address(CONTR_ARB_ADDR)

print(f'reading abi file for contract: {CONTR_ARB_ADDR} ...')
with open(abi_file, "r") as file: CONTR_ARB_ABI = file.read()

# input hexadecimal data (ex: '0xd877845c' == 'getFlashLoanFeePercentage')
print('\n enter hex value function signature obtained from block explorer... (ex: "0xd877845c")')
hex_data = input(' > ')

try:
    print('\ndecoding data...')
    decoded_data = W3.eth.contract(address=CONTR_ARB_ADDR, abi=CONTR_ARB_ABI).decode_function_input(hex_data)
    print(f' decoded function_signature: "{decoded_data[0].fn_name}"\n\n')
except Exception as e:
    print(f' ERROR: {e} ("{hex_data}")\n')

