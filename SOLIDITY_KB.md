# defi-arb

## SOLIDITY_KB

### checking for existing mappings
    address gameCode = generateAddressHash(msg.sender, gameName);
    require(bytes(games[gameCode].gameName).length == 0, "err: game name already exists :/");
    
    games[gameCode] is used to access the gameCode key in the mapping. If the key doesn't exist, the result will be a default value for the type of the mapping's value (in this case, an uninitialized Game struct with all fields set to their default values).

    This code is a valid way to check if a specific gameCode already exists in the mapping without creating a new mapping entry.

### using 'memory' isntead of 'storage'
    In the Solidity code I provided, I used `Game memory` instead of `Game storage` in the `createGame` function because, in this context, it's more efficient and appropriate to use `Game memory`.

    When you use `Game memory`, you are creating a temporary copy of the `Game` struct in memory, which is suitable for temporary operations like initializing a new `Game` instance within a function. This is more efficient because you don't need to persist the `Game` struct on the blockchain or in storage; it's only relevant within the scope of the function. Storing data in memory consumes less gas compared to storage.

    Using `Game storage` would be appropriate when you want to persist the `Game` struct on the blockchain, and you need to modify it in a way that the changes should be stored permanently. For example, if you want to update the properties of an existing game or maintain a list of games over time, then you would use `Game storage`.

    In the `createGame` function, we are creating a new `Game` instance and storing it in the `games` array. However, we are not modifying an existing game's properties, so using `Game memory` for creating and initializing the new game instance is more efficient and appropriate. Storing data in memory when you don't need to use storage can help reduce gas costs in your Solidity contract.
    
### UINT storage sizes (chatGPT)
    uint8: 8 bits (0 to 255)
    uint16: 16 bits (0 to 65,535)
    uint32: 32 bits (0 to 4,294,967,295)
    uint64: 64 bits
    uint128: 128 bits
    uint256: 256 bits (the most common choice for very large values)
    note: uint defauls to uint256
    
### reasons gas consumption when modifying the state of a smart contract (chatGPT)
    1. **Storage Changes**: Modifying the state of a smart contract, such as clearing an array or deleting key-value pairs in a mapping, involves changes to the contract's storage. Each storage change consumes gas.
    2. **Iteration**: In the case of a mapping, if you need to clear all key-value pairs, you would typically iterate through the keys and delete each key-value pair. Each iteration consumes gas, and the gas cost increases with the number of key-value pairs.
    3. **Gas Cost for Deletion**: The `delete` keyword in Solidity is used to set values to their default state. Deleting a key-value pair in a mapping consumes gas, as the operation involves clearing storage slots.
    4. **Execution Overhead**: Gas is also used to cover the overhead associated with executing a transaction on the Ethereum network.

    Keep in mind that the gas cost can vary based on the specific circumstances, such as the size of the array or mapping and the overall complexity of the contract. Therefore, it's essential to consider the gas cost when designing and interacting with smart contracts, particularly when dealing with large data structures.

### IERC-20 widely recognized
    ref: https://github.com/balancer/balancer-v2-monorepo/blob/master/pkg/interfaces/contracts/solidity-utils/openzeppelin/IERC20.sol
    FUNCTION signatures and their corresponding keccak256 (SHA-3) hash values for the functions defined in the ERC-20 interface:
     1. `totalSupply()`: `0x18160ddd` - Returns the total supply of tokens.
     2. `balanceOf(address)`: `0x70a08231` - Returns the token balance owned by the specified `account`.
     3. `transfer(address, uint256)`: `0xa9059cbb` - Moves tokens from the caller's account to the `recipient` and returns a boolean indicating success.
     4. `allowance(address, address)`: `0xdd62ed3e` - Returns the remaining number of tokens that `spender` is allowed to spend on behalf of `owner`.
     5. `approve(address, uint256)`: `0x095ea7b3` - Sets the allowance of `spender` over the caller's tokens and returns a boolean indicating success.
     6. `transferFrom(address, address, uint256)`: `0x23b872dd` - Moves tokens from `sender` to `recipient` using the allowance mechanism and returns a boolean indicating success.

    ref: https://github.com/balancer/balancer-v2-monorepo/blob/master/pkg/interfaces/contracts/solidity-utils/openzeppelin/IERC20.sol
    EVENTS
     1. `Transfer(address indexed from, address indexed to, uint256 value)` - Emitted when `value` tokens are moved from one account (`from`) to another (`to`).
     2. `Approval(address indexed owner, address indexed spender, uint256 value)` - Emitted when the allowance of a `spender` for an `owner` is set by a call to `approve`. `value` is the new allowance.
     
    ref: chatGPT
    ADDITIONAL FUNCTIONS included for clarity and completeness, even though they are not part of the standard ERC-20 interface
        functions provide versatility and customization to the token contract, accommodating specific project requirements while adhering to the core ERC-20 standard for token functionality.
     1. `increaseAllowance(address spender, uint256 addedValue)`: `0xd73dd623` - Allows the owner to increase the allowance for a spender, providing more flexibility in managing allowances.
     2. `decreaseAllowance(address spender, uint256 subtractedValue)`: `0x6af65710` - Allows the owner to decrease the allowance for a spender, offering finer control over allowances.
     3. `mint(address account, uint256 amount)`: `0x40c10f19` - Enables the contract owner to mint new tokens and assign them to a specific account, which is a common feature in many token contracts to increase the token supply.
     4. `_transfer(address sender, address recipient, uint256 amount)`: An internal function used for the actual transfer of tokens within the contract, essential for implementing the ERC-20 functions.
     5. `_approve(address owner, address spender, uint256 amount)`: Another internal function for setting the allowance between the owner and spender, playing a crucial role in the contract's functionality.

### indexing event parameters (chatGPT)
    In Solidity, when defining event parameters, you have the option to mark some of them as "indexed." Indexed parameters are a way to optimize event filtering and search functionality in Ethereum clients like web3.py.

    Here's what "indexed" means and how it affects event parameters:

    1. **Indexing for Efficiency**: When an event parameter is marked as "indexed," it means that Ethereum clients, such as Ethereum nodes and libraries like web3.py, create an index for that parameter's value. This index allows for efficient filtering and searching through events.

    2. **Filtering Events**: Indexed parameters are particularly useful when you want to filter and search for specific events efficiently. By marking a parameter as indexed, you can filter events based on the indexed parameter's value, which is significantly faster than filtering by non-indexed parameters.

    3. **Limitations**: There are some limitations regarding indexed parameters:
       - You can mark up to three parameters as indexed in a single event.
       - Indexed parameters must be of data types `address` or `uint256`.
       - Marking a parameter as indexed consumes more gas compared to non-indexed parameters.

    4. **Web3.py Example**: When working with web3.py, you can use indexed parameters to filter events. For example, if you have an event with an indexed address parameter, you can efficiently filter events by the address value in your Python code, like this:

       ```python
       from web3 import Web3

       # Replace with your contract instance
       contract = web3.eth.contract(address=contract_address, abi=contract_abi)

       # Filter events by indexed parameter (address)
       event_filter = contract.events.MyEvent.createFilter(
           argument_filters={'sender': sender_address}
       )

       events = event_filter.get_all_entries()
       ```

    By using indexed parameters, you can quickly retrieve only the events that match the specified criteria, improving the efficiency of event handling and data retrieval in Ethereum applications.

### Common solidity functions mapped to hex values (that you see in the block explorer)
    Examples of common Ethereum function names along with their corresponding function selectors represented as hexadecimal values:
    1. `transfer(address,uint256)`: `0xa9059cbb` - Used in ERC-20 token contracts for transferring tokens from one address to another.
    2. `approve(address,uint256)`: `0x095ea7b3` - Another ERC-20 function used for approving a spender to transfer tokens from the caller's address.
    3. `transferFrom(address,address,uint256)`: `0x23b872dd` - Used in ERC-20 contracts to allow a third party (spender) to transfer tokens on behalf of the token holder.
    4. `balanceOf(address)`: `0x70a08231` - Retrieves the token balance of a specific address in ERC-20 contracts.
    5. `totalSupply()`: `0x18160ddd` - ERC-20 function that returns the total supply of tokens.
    6. `allowance(address,address)`: `0xdd62ed3e` - Used to check the amount of tokens that an owner has approved for a spender to transfer.
    7. `name()`: `0x06fdde03` - Commonly used in ERC-20 and ERC-721 token contracts to get the name of the token.
    8. `symbol()`: `0x95d89b41` - Retrieves the symbol or ticker of a token (e.g., "ETH" for Ether).
    9. `decimals()`: `0x313ce567` - Returns the number of decimals for token representation (e.g., 18 for Ether).
    10. `transferOwnership(address)`: `0xf2fde38b` - Used in various smart contracts to transfer ownership from one address to another.
    11. `owner()`: `0x8da5cb5b` - Retrieves the current owner of a contract with ownership functionality.
    12. `balance()`: `0x70a08231` - Retrieves the balance of Ether in an address.
    13. `kill()`: `0x3ccfd60b` - A common function used in older contract examples for self-destructing a contract.
    14. `get()`: Custom function names used to retrieve data from a contract.
    15. `set(uint256)`: Custom function names used to set data in a contract.
    16. `mint(address,uint256)`: Custom function used to create new tokens in various token standards.
    17. `burn(uint256)`: Custom function used to destroy or "burn" tokens in token contracts.
    18. `getBalance(address)`: Custom function used to check the balance of a specific address in various contracts.
    19. `transferEther(address,uint256)`: Custom function used to send Ether from one address to another in smart contracts.
    20. `execute(address,uint256,bytes)`: Custom function used for executing arbitrary transactions within a contract.
    21. `setAdmin(address)`: Custom function used to set the admin of a contract.
    22. `getAdmin()`: Custom function used to retrieve the admin of a contract.
    23. `buyTokens(uint256)`: Custom function used in ICO contracts to purchase tokens.
    24. `sellTokens(uint256)`: Custom function used in ICO contracts to sell tokens and receive Ether.
    25. `pause()`: Custom function used to pause the functionality of a contract.
    26. `unpause()`: Custom function used to unpause a paused contract.
    27. `transferFromSenderTo(address,uint256)`: Custom function used to transfer tokens from the sender to a specified address.
    28. `withdraw()`: Custom function used to withdraw funds from a contract.
    29. `addMember(address)`: Custom function used to add a member to a membership-based contract.
    30. `removeMember(address)`: Custom function used to remove a member from a membership-based contract.
    31. `setPrice(uint256)`: Custom function used to set the price of a product or service in a contract.
    32. `getPrice()`: Custom function used to retrieve the price of a product or service in a contract.
    33. `getOwner()`: Custom function used to retrieve the owner of a contract.
    34. `setBeneficiary(address)`: Custom function used to set the beneficiary of a contract.
    35. `getBeneficiary()`: Custom function used to retrieve the beneficiary of a contract.
    36. `setRate(uint256)`: Custom function used to set a conversion rate in a contract (e.g., for token swaps).
    37. `getRate()`: Custom function used to retrieve a conversion rate in a contract.
    38. `addFriend(address)`: Custom function used to add a friend in a social contract.
    39. `sendMessage(string,address)`: Custom function used to send messages in a messaging contract.
    40. `deleteAccount()`: Custom function used to delete an account in various contracts.
    41. `setAllowed(address,bool)`: Custom function used to set allowances in access control contracts.
    42. `isAllowed(address)`: Custom function used to check allowances in access control contracts.
    43. `initialize()`: Custom function used for contract initialization.
    44. `setParameters(uint256,uint256)`: Custom function used to set parameters in a contract.
    45. `getParameters()`: Custom function used to retrieve parameters from a contract.
    46. `addAsset(address)`: Custom function used to add an asset to a contract.
    47. `removeAsset(address)`: Custom function used to remove an asset from a contract.
    48. `addProposal(string,uint256)`: Custom function used to add a proposal in governance contracts.
    49. `vote(uint256,bool)`: Custom function used for voting on proposals in governance contracts.
    50. `getProposal(uint256)`: Custom function used to retrieve a proposal in governance contracts.
    51. `setWhitelist(address,bool)`: Custom function used to manage whitelists in contracts.
    52. `addToBlacklist(address)`: Custom function used to add an address to a blacklist.
    53. `removeFromBlacklist(address)`: Custom function used to remove an address from a blacklist.
    54. `getBlacklistStatus(address)`: Custom function used to check if an address is in a blacklist.
    55. `setLimit(uint256)`: Custom function used to set limits or caps in contracts.
    56. `getLimit()`: Custom function used to retrieve limits or caps from contracts.
    57. `setThreshold(uint256)`: Custom function used to set thresholds in multi-signature wallets.
    58. `getThreshold()`: Custom function used to retrieve thresholds from multi-signature wallets.
    59. `setApprovalStatus(bool)`: Custom function used to set approval status in contracts.
    60. `getApprovalStatus()`: Custom function used to retrieve approval status from contracts.
    61. `createOrder(uint256)`: Custom function used to create orders in decentralized exchanges.
    62. `cancelOrder(uint256)`: Custom function used to cancel orders in decentralized exchanges.
    63. `fillOrder(uint256)`: Custom function used to fill orders in decentralized exchanges.
    64. `claimTokens(address,uint256)`: Custom function used

### FUNCTION MODIFIERS & DECORATORS
    In Solidity, there are various function modifiers and decorators that can change the behavior of a function. Here's a list of some common ones:

    1. Visibility Modifiers:
       - `public`: The function can be called from anywhere.
       - `internal`: The function can only be called from within the current contract or derived contracts.
       - `external`: The function can be called from outside the contract and other contracts.
       - `private`: The function can only be called from within the current contract.
    2. State Mutability:
       - `view` or `constant`: The function does not modify the state and only reads data.
       - `pure`: The function does not modify the state and does not read data.
       - (Default): If none of the above are specified, the function is considered "non-payable" and can modify the state.
    3. `payable`: Allows a function to receive Ether as part of the function call;
    3b.`payable(address)`: an Ethereum address that can receive and send Ether.
    4. `returns`: Specifies the return data types of a function.
    5. `modifier`: User-defined functions that can be used to modify the behavior of other functions. You can define custom logic to be executed before or after the main function.
    6. `revert`: Used to revert a transaction if certain conditions are not met. For example, you can use `require` and `assert` statements to revert transactions.
    7. Events: Events are used to log information about transactions and changes in the contract's state.
    8. `constant` and `immutable` variables: These can be used to store constant data and their values cannot be changed after deployment.
    9. `assembly`: Allows low-level inline assembly code to be included in the contract.
    10. Function Overloading: Solidity supports function overloading, which means you can have multiple functions with the same name but different parameter lists.
    11. The `override` keyword is used to explicitly indicate in a derived contract that a function is intended to override a function from a base contract.
        When you use the override keyword, you're essentially telling the compiler that you intend to replace a function in the base contract with a new implementation in the derived contract.
    
These modifiers and decorators allow you to control how functions behave, who can call them, and what changes they can make to the contract state. You can use a combination of these modifiers and decorators to design the behavior of your smart contracts according to your requirements.

