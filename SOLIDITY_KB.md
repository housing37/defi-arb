# defi-arb

## SOLIDITY_KB

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

3. `payable`: Allows a function to receive Ether as part of the function call.

4. `returns`: Specifies the return data types of a function.

5. `modifier`: User-defined functions that can be used to modify the behavior of other functions. You can define custom logic to be executed before or after the main function.

6. `revert`: Used to revert a transaction if certain conditions are not met. For example, you can use `require` and `assert` statements to revert transactions.

7. Events: Events are used to log information about transactions and changes in the contract's state.

8. `constant` and `immutable` variables: These can be used to store constant data and their values cannot be changed after deployment.

9. `assembly`: Allows low-level inline assembly code to be included in the contract.

10. Function Overloading: Solidity supports function overloading, which means you can have multiple functions with the same name but different parameter lists.

These modifiers and decorators allow you to control how functions behave, who can call them, and what changes they can make to the contract state. You can use a combination of these modifiers and decorators to design the behavior of your smart contracts according to your requirements.

