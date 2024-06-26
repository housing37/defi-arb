// SPDX-License-Identifier: agpl-3.0
// pragma solidity 0.6.12;
pragma solidity ^0.8.24; 

// import {IFlashLoanReceiver, ILendingPoolAddressesProvider, ILendingPool, IERC20  } from "Interfaces.sol";
// import { SafeERC20, SafeMath } from "Libraries.sol";

// local _ $ git clone https://github.com/aave/code-examples-protocol.git
import "./Interfaces.sol"; 
import "./Libraries.sol"; 

abstract contract FlashLoanReceiverBase is IFlashLoanReceiver {
  using SafeERC20 for IERC20;
  using SafeMath for uint256;

  ILendingPoolAddressesProvider public immutable ADDRESSES_PROVIDER;
  ILendingPool public immutable LENDING_POOL;

  constructor(ILendingPoolAddressesProvider provider) {
    ADDRESSES_PROVIDER = provider;
    LENDING_POOL = ILendingPool(provider.getLendingPool());
  }
}