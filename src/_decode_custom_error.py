import re
import binascii

hex_message = "0x4e487b710000000000000000000000000000000000000000000000000000000000000011"
print(f'\nencoded input: {hex_message}')
# Remove the "0x" prefix
hex_message = hex_message[2:]

# Convert the hex message to bytes
message_bytes = bytes.fromhex(hex_message)

# Find the position of the string in the message
string_pattern = re.compile(b'\x00[^\x00]*\x00')
match = string_pattern.search(message_bytes)

if match:
    string_start = match.start()
    string_end = match.end()

    # Decode the string data as UTF-8 (note_110623: attempt failed)
    string_data = message_bytes[string_start:string_end]
    err_msg_string_data = string_data[1:-1].decode('utf-8')
    
    # Decode the entire message as UTF-8 (note_110623: attempt failed)
    err_msg_message_bytes = message_bytes[1:-1].decode('utf-8')

    # Decode just the function name (note_110623: attempt failed)
    func_name_data = message_bytes[:string_start]
    func_name = func_name_data.decode('utf-8')
    
    # The amount is stored as a byte array, convert it to an integer
    amount_data = message_bytes[string_end:]
    amount_owed = int.from_bytes(amount_data, byteorder='big')

    print(f' string_start: {string_start}\n string_end: {string_end}')
    print("Error Message (message_bytes):", err_msg_message_bytes)
    print("Error Message (string_data):", err_msg_string_data)
    print("Function Name:", func_name)
    print("Amount Owed:", amount_owed)
    print()
else:
    print("Error: Dynamic data not found in the message")
    print()

