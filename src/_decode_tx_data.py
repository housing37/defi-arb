## house_102823:
# The hexadecimal data you provided
hex_data = '0xc9a69562000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000e00000000000000000000000000000000000000000000000000000000000000001000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc200000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000010655a83f1e2a00000000000000000000000000000000000000000000000000000000000000000180000000000000000000000000e592427a0aece92de3edee1f18e0157c05861564000000000000000000000000e592427a0aece92de3edee1f18e0157c0586156400000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000001200000000000000000000000000000000000000000000000010655a83f1e2a00000000000000000000000000000000000000000000000000000ddf4ae7657b00000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000009be89d2a4cd102d8fecc6bf9da793be995c2254100000000000000000000000000000000000000000000000000000000000000020000000000000000000000009be89d2a4cd102d8fecc6bf9da793be995c225410000000000000000000000002260fac5e5542a773aa44fbcfedf7c193bc2c599'

from web3 import Web3, HTTPProvider
import env
import pprint
from ethereum.abi import decode_abi
from ethereum.utils import normalize_address

eth_main = f'https://mainnet.infura.io/v3/{env.ETH_MAIN_RPC_KEY}'
RPC_URL = eth_main
W3 = Web3(HTTPProvider(RPC_URL))


# The contract address
CONTR_ARB_ADDR = '0x59012124c297757639E4AB9b9E875eC80a5c51DA'
print(f'reading contract abi file: {CONTR_ARB_ADDR}...')
with open("../contracts/BalancerFLR.json", "r") as file: CONTR_ARB_ABI = file.read()

# Decode the data
#decoded_data = W3.eth.contract(address=CONTR_ARB_ADDR, abi=CONTR_ARB_ABI).decode_function_input(hex_data)
CONTR_ARB = W3.eth.contract(address=CONTR_ARB_ADDR, abi=CONTR_ARB_ABI)
decoded_data = CONTR_ARB.decode_function_input(hex_data)
print(decoded_data)
print()

# Pretty print the dictionary
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(decoded_data)

# Define the data you want to decode and the types of the values.
encoded_data = decoded_data[1]['userData']  # Replace with the actual encoded data
data_types = ['address', 'address', 'address[]', 'address[]', 'uint256', 'uint256']

# Decode the data
decoded_data = decode_abi(data_types, encoded_data)

# The decoded_data will be a tuple containing the decoded values
router_0, router_1, addr_path_0, addr_path_1, amntIn_0, amntOutMin_1 = decoded_data

# Now you can access the individual decoded values
print(f"router_0: {router_0}")
print(f"router_1: {router_1}")
print(f"addr_path_0: {addr_path_0}")
print(f"addr_path_1: {addr_path_1}")
print(f"amntIn_0: {amntIn_0}")
print(f"amntOutMin_1: {amntOutMin_1}")

