import subprocess

print('reading source file...')
with open("../contracts/BalancerFLR.sol", "r") as file:
    CONTR_SOURCE = file.read()
    
#source_code = """
#// Your Solidity code here
#"""
source_code = CONTR_SOURCE

#command = [
#    'solc',
#    '--bin',
#    '--abi',
#    '--optimize',
#    '-o', 'output_directory',  # Specify the output directory
#    '-e', 'utf-8',            # Specify the output encoding
#    '--overwrite',             # Overwrite existing files
#    '--',                      # To separate options from source code
#    '-'                         # Read source code from stdin
#]

#command = [
#   'solc',
#   '--bin-runtime',  # Specify that you want the bytecode
#   '--abi',          # Specify that you want the ABI
#   '--optimize',
#   '--overwrite',
#   '--',              # To separate options from source code
#   '-'               # Read source code from stdin
#]

#command = [
#   'solc',
#   '--bin',    # Specify that you want the bytecode
#   '--abi',    # Specify that you want the ABI
#   '--optimize',
#   '--overwrite',
#   '--',        # To separate options from source code
#   '-'         # Read source code from stdin
#]

command = [
    'solc',
#    '--combined-json', 'bin,abi',  # Specify the desired output formats
    '--optimize',
    '--',                          # To separate options from source code
    '-'                            # Read source code from stdin
]

print('compiling source code...')
process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
stdout, stderr = process.communicate(input=source_code)

#if process.returncode != 0:
#    print("Compilation failed:", stderr)
#else:
#    print("Compilation succeeded:", stdout)
    
if process.returncode != 0:
   print("Compilation failed:", stderr)
else:
   print("Compilation succeeded:")
   print("Bytecode (bin-runtime):", stdout)
