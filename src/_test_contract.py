## house_102823:
from web3 import Web3, HTTPProvider
import env
eth_main = f'https://mainnet.infura.io/v3/{env.ETH_MAIN_RPC_KEY}'
NET_URL = eth_main
W3 = Web3(HTTPProvider(NET_URL))


# The contract address
CONTR_ARB_ADDR = '0x59012124c297757639E4AB9b9E875eC80a5c51DA'
print(f'reading contract abi file: {CONTR_ARB_ADDR}...')
with open("../contracts/BalancerFLR.json", "r") as file: CONTR_ARB_ABI = file.read()

# The hexadecimal data you provided
hex_data = '0xc9a69562000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000e00000000000000000000000000000000000000000000000000000000000000001000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000106e0368a386780000000000000000000000000000000000000000000000000000000000000000180000000000000000000000000e592427a0aece92de3edee1f18e0157c05861564000000000000000000000000e592427a0aece92de3edee1f18e0157c0586156400000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000000000000012000000000000000000000000000000000000000000000000106e0368a386780000000000000000000000000000000000000000000000000000ddf4ae7657b00000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000009be89d2a4cd102d8fecc6bf9da793be995c2254100000000000000000000000000000000000000000000000000000000000000020000000000000000000000009be89d2a4cd102d8fecc6bf9da793be995c225410000000000000000000000002260fac5e5542a773aa44fbcfedf7c193bc2c599'

# Decode the data
#decoded_data = W3.eth.contract(address=CONTR_ARB_ADDR, abi=CONTR_ARB_ABI).decode_function_input(hex_data)
CONTR_ARB = W3.eth.contract(address=CONTR_ARB_ADDR, abi=CONTR_ARB_ABI)
decoded_data = CONTR_ARB.decode_function_input(hex_data)
print(decoded_data)
print()
import pprint

## Your dictionary
#data_dict = {'tokens': ['0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'], 'amounts': [18942200000000000000], 'userData': b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe5\x92Bz\n\xec\xe9-\xe3\xed\xee\x1f\x18\xe0\x15|\x05\x86\x15d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe5\x92Bz\n\xec\xe9-\\xe3\xed\xee\x1f\x18\xe0\x15|\x05\x86\x15d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x06\xe06\x8a8g\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\xdfJ\xe7e{\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0*\aa9\b2#\fe\8d\n\0e\\O\'\ea\d9\08\ul\c2\00\00\00\00\00\00\00\00\00\00\00\00\00\9b\e8\9d*L\d1\02\d8\fe\cc\k\f9\ay;\e9\95\c2\A\00\00\00\00\00\00\00\00`\fa\c5\e5\T\*w\:\a4\O\bc\fe\df\|\19\;\c2\c5\99'}

# Pretty print the dictionary
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(decoded_data)

from ethereum.abi import decode_abi
from ethereum.utils import normalize_address

# Define the data you want to decode and the types of the values.
encoded_data = decoded_data[1]['userData']  # Replace with the actual encoded data
data_types = ['address', 'address', 'address[]', 'address[]', 'uint256', 'uint256']

# Decode the data
decoded_data = decode_abi(data_types, encoded_data)

# The decoded_data will be a tuple containing the decoded values
router_0, router_1, addr_path_0, addr_path_1, amntIn_0, amntOutMin_1 = decoded_data
#print(decoded_data, sep='\n')

# Now you can access the individual decoded values
print(f"router_0: {router_0}")
print(f"router_1: {router_1}")
print(f"addr_path_0: {addr_path_0}")
print(f"addr_path_1: {addr_path_1}")
print(f"amntIn_0: {amntIn_0}")
print(f"amntOutMin_1: {amntOutMin_1}")

# Define the ABI for the function you are decoding
# Replace this with the actual ABI of the function
#abi = [
#    {
#        "type": "function",
#        "name": "makeFlashLoan",
#        "inputs": [
#            {"type": "address[]"},
#            {"type": "uint256[]"},
#            {"type": "bytes"},
#        ],
#    }
#]

#
#import binascii
#
## Define the ABI for the function you are decoding
## Replace this with the actual ABI of the function
##abi = [
##    {
##        "name": "makeFlashLoan",
##        "inputs": [
##            {"name": "addresses", "type": "address[]"},
##            {"name": "values", "type": "uint256[]"},
##            {"name": "bytesData", "type": "bytes"},
##        ],
##    }
##]
#
## Extract the function selector (first 4 bytes)
#function_selector = decoded_data[1]['userData'][:4]
#
## Find the matching ABI entry based on the function selector
#matching_abi = next(entry for entry in CONTR_ARB_ABI if entry['name'] == "makeFlashLoan")
#
## The remaining data is the encoded parameters
#encoded_params = data_tuple[1]['userData'][4:]
#
## Decode the parameters using the ABI
#decoded_params = []
#for input_param in matching_abi['inputs']:
#    param_type = input_param['type']
#    param_name = input_param['name']
#    param_size = len(param_type) // 4  # Convert type to bytes
#
#    # Extract and decode each parameter
#    param_data = encoded_params[:param_size]
#    if param_type == 'address':
#        decoded_param = normalize_address(binascii.hexlify(param_data).decode('utf-8'))
#    elif param_type == 'uint256':
#        decoded_param = int(binascii.hexlify(param_data).decode('utf-8'), 16)
#    elif param_type == 'bytes':
#        decoded_param = param_data
#    else:
#        decoded_param = None  # Handle other types as needed
#
#    decoded_params.append({param_name: decoded_param})
#
#    # Remove the processed parameter from the encoded data
#    encoded_params = encoded_params[param_size:]
#
## Print the decoded parameters
#print(decoded_params)

#####

# Define the function signature
function_signature = "makeFlashLoan(address[],uint256[],bytes)"

# Decode the userData using the ABI and function signature
#decoded_params = decode_abi(CONTR_ARB_ABI, function_signature, decoded_data[1]['userData'])
#decoded_params = decode_abi(CONTR_ARB_ABI, decoded_data[1]['userData'])
decoded_params = decode_abi(function_signature, decoded_data[1]['userData'])

# Print the decoded parameters
print(decoded_params)


#####3
# Decode the binary userData to a string using UTF-8 encoding
decoded_user_data = decoded_data[1]['userData'].decode('utf-8')

# Print the decoded user data
print(decoded_user_data)



import ast, pprint
pprint(decoded_data)
data_dict = ast.literal_eval(decoded_data)

# Print the decoded data
print(decoded_data)
print()
print(data_dict)

### house_102823: test 'transferTokens' from deployed BalancerFLR.sol ##
#from web3 import Web3, HTTPProvider
#import env
#
#print('getting keys and intializing web3...')
#SENDER_ADDRESS = env.sender_address_1 # default
#SENDER_SECRET = env.sender_secret_1 # default
#
#addr_arb_contr = '0xFD2AaD9Ef84C001a3622188493A8AFd9436892c8'
#with open("../contracts/BalancerFLR.json", "r") as file: abi_arb_contr = file.read()
#addr_pdai = "0x6B175474E89094C44Da98b954EedeAC495271d0F" # pDAI token
#abi_pdai = [
#    {
#        "constant": True,
#        "inputs": [{"name": "_owner", "type": "address"}],
#        "name": "balanceOf",
#        "outputs": [{"name": "balance", "type": "uint256"}],
#        "type": "function"
#    },
#    {
#        "constant": True,
#        "inputs": [],  # No inputs required
#        "name": "symbol",
#        "outputs": [{"name": "", "type": "string"}],
#        "type": "function"
#    }
#]
#W3 = Web3(HTTPProvider(f'https://rpc.pulsechain.com'))
#pdai_contr = W3.eth.contract(address=addr_pdai, abi=abi_pdai)
#arb_contr = W3.eth.contract(address=addr_arb_contr, abi=abi_arb_contr)
#
## check pdai balance
#pdai_bal = pdai_contr.functions.balanceOf(addr_arb_contr).call()
#print(f'pdai balance: {pdai_bal}\n for contr: {addr_arb_contr}')
#
## transfer pdai out (102823: doesn't seem to work)
##print('attempting "transferTokens"...')
##arb_contr.functions.transferTokens(addr_pdai, SENDER_ADDRESS, 1)
#
## check pdai balance again
#pdai_bal = pdai_contr.functions.balanceOf(addr_arb_contr).call()
#print(f'pdai balance: {pdai_bal}\n for contr: {addr_arb_contr}')
#
## check PLS balance
#wei_bal = W3.eth.getBalance(addr_arb_contr)
#eth_bal = W3.fromWei(wei_bal, 'ether')
#print(f'PLS balance: {eth_bal}\n for contr: {addr_arb_contr}')
