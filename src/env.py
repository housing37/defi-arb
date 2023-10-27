__fname = 'env'
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
print('', cStrDivider, f'START _ {__filename}', cStrDivider, sep='\n')
print(f'GO {__filename} -> starting IMPORTs and globals decleration')
#============================================================================#
## log paths (should use same 'log' folder as access & error logs from nginx config)
#GLOBAL_PATH_DEV_LOGS = "../logs/dev.log"
#GLOBAL_PATH_ISE_LOGS = "../logs/ise.log"

#============================================================================#
## Misc smtp email requirements (eg_121019: inactive)
SES_SERVER = 'nil'
SES_PORT = 'nil'
SES_FROMADDR = 'nil'
SES_LOGIN = 'nil'
SES_PASSWORD = 'nil'

corp_admin_email = 'nil'
corp_recept_email = 'nil'
admin_email = 'nil'

#============================================================================#
#============================================================================#
## .env support
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
ETH_MAIN_RPC_KEY = os.environ['ETH_MAIN_INFURA_KEY']

# wallet support
sender_address_0 = os.environ['PUBLIC_KEY_4']
sender_secret_0 = os.environ['PRIVATE_KEY_4']

#============================================================================#
## s3 & receipt constants
#============================================================================#

#============================================================================#
## mysql return keys
#============================================================================#

