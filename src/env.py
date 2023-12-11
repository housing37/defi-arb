__fname = 'env'
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
print('', cStrDivider, f'GO _ {__filename} -> starting IMPORTs & declaring globals', cStrDivider, sep='\n')
#============================================================================#
## log paths (should use same 'log' folder as access & error logs from nginx config)
#GLOBAL_PATH_DEV_LOGS = "../logs/dev.log"
#GLOBAL_PATH_ISE_LOGS = "../logs/ise.log"

#============================================================================#
## .env support
#============================================================================#
import os
from read_env import read_env

try:
    #ref: https://github.com/sloria/read_env
    #ref: https://github.com/sloria/read_env/blob/master/read_env.py
    read_env() # recursively traverses up dir tree looking for '.env' file
except:
    print("#==========================#")
    print(" ERROR: no .env files found ")
    print("#==========================#")

##
# db support (use for remote & local server)
#   use w/ .env
#       DB_DATABASE=mydbname
#       DB_USERNAME=root
#       DB_PASSWORD=password
##
dbHost = os.environ['DB_HOST']
dbName = os.environ['DB_DATABASE']
dbUser = os.environ['DB_USERNAME']
dbPw = os.environ['DB_PASSWORD']

# s3 support (use for remote server)
ACCESS_KEY = os.environ['ACCESS_KEY']
SECRET_KEY = os.environ['SECRET_KEY']

# infura support
#ETH_MAIN_RPC_KEY = os.environ['ETH_MAIN_INFURA_KEY_0']
ETH_MAIN_RPC_KEY = os.environ['ETH_MAIN_INFURA_KEY_1']

# etherscan support
ETHERSCAN_API_KEY = os.environ['ETHERSCAN_API_KEY']

# wallet support
sender_address_0 = os.environ['PUBLIC_KEY_3']
sender_secret_0 = os.environ['PRIVATE_KEY_3']
sender_address_1 = os.environ['PUBLIC_KEY_4']
sender_secret_1 = os.environ['PRIVATE_KEY_4']
sender_address_2 = os.environ['PUBLIC_KEY_5']
sender_secret_2 = os.environ['PRIVATE_KEY_5']
sender_address_3 = os.environ['PUBLIC_KEY_6']
sender_secret_3 = os.environ['PRIVATE_KEY_6']

#============================================================================#
## Misc smtp email requirements (house_121032: simple_email.py -> gastracker.py)
#============================================================================#
SES_SERVER = os.environ['SES_SERVER']
SES_PORT = os.environ['SES_PORT']
SES_LOGIN = os.environ['SES_LOGIN']
SES_PASSWORD = os.environ['SES_PASSWORD']
SENDER_EMAIL = os.environ['SENDER_EMAIL']
LST_RECEIVERS = [os.environ['RECEIVERS_0'], os.environ['RECEIVERS_1']]

corp_admin_email = 'nil'
corp_recept_email = 'nil'
admin_email = 'nil'

#============================================================================#
## web3 constants
#============================================================================#
local_test = 'http://localhost:8545'
eth_main = f'https://mainnet.infura.io/v3/{ETH_MAIN_RPC_KEY}'
eth_test = f'https://goerli.infura.io/v3/'
pc_main = f'https://rpc.pulsechain.com'
eth_main_cid=1
pc_main_cid=369

#============================================================================#
## mysql return keys
#============================================================================#

