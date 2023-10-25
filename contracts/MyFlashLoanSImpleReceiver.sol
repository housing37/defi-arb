// house_102523 _ ref: https://www.youtube.com/watch?v=PtMs8FZJhkU
// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.7.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
//    IERC20(_tokenIn).approve(address(uniswapRouter), _amountIn);

// house_102523: should be 'deployable' (references to your 'node & modules' folder)
import {FlashLoanSimpleReceiverBase} from '@aave/core-v3/contracts/interfaces/FlashLoanSimpleReceiverBase.sol';
import {IPoolAddressesProvider} from '@aave/core-v3/contracts/interfaces/IPoolAddressesProvider.sol';
import {IPool} from '@aave/core-v3/contracts/interfaces/IPool.sol';

// house_102523: should need for remix execution (i guess?)
//  "these references to my node & modules folder won't work in remix"
//import {FlashLoanSimpleReceiverBase} from 'https://github.com/aave/aave-v3-core/blob/master/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol';
//import {IPoolAddressesProvider} from 'https://github.com/aave/aave-v3-core/blob/master/contracts/interfaces/IPoolAddressesProvider.sol';
//import {IPool} from 'https://github.com/aave/aave-v3-core/blob/master/contracts/interfaces/IPool.sol';

// house_102523: use interface manually (not tested)
///**
// * @title IFlashLoanSimpleReceiver
// * @author Aave
// * @notice Defines the basic interface of a flashloan-receiver contract.
// * @dev Implement this interface to develop a flashloan-compatible flashLoanReceiver contract
// */
//interface IFlashLoanSimpleReceiver {
//  /**
//   * @notice Executes an operation after receiving the flash-borrowed asset
//   * @dev Ensure that the contract can return the debt + premium, e.g., has
//   *      enough funds to repay and has approved the Pool to pull the total amount
//   * @param asset The address of the flash-borrowed asset
//   * @param amount The amount of the flash-borrowed asset
//   * @param premium The fee of the flash-borrowed asset
//   * @param initiator The address of the flashloan initiator
//   * @param params The byte-encoded params passed when initiating the flashloan
//   * @return True if the execution of the operation succeeds, false otherwise
//   */
//  function executeOperation(
//    address asset,
//    uint256 amount,
//    uint256 premium,
//    address initiator,
//    bytes calldata params
//  ) external returns (bool);
  
contract FlashLoanSimpleReceiverBase is FlashLoanSimpleReceiverBase {
    address payable owner;
    
    constructor(address _addressProvider) FlashLoanSimpleReceiverBase(IPoolAddressesProvider(_addressProvider))
    {
        owner = payable(msg.sender)
    }
    
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external override returns (bool) {
        uint256 amountOwed = amount + premium;
        IERC20(asset).approve(address(POOL), amountOwed);
        
        return true;
    }
    
    function requestFlashLoan(address _token, uint256 _amount) public {
        address receiverAddress = address(this);
        address asset = _token;
        uint256 amount = _amount;
        byte memory params = "";
        uint16 referralCode = 0;
        POOL.flashLoanSimple(
                receiverAddress,
                asset,
                amount,
                params,
                referralCode
        );
    }
    
    function getBalance(address _tokenAddress) external view returns (uint256) {
        return IERC20(_tokenAddress).balanceOf(address(this));
    }
    
    function withdraw(address _tokenAddress) external onlyOwner {
        IERC20 token = IERC(_tokenAddress);
        token.transfer(msg.sender, token.balanceOf(address(this)));
    }
    
    modifier ownlyOwner() {
        require(msg.sender == owner, "Only owner allowed for this function");
    }
    
    // just in case we ant this contract to receive ether for any reason
    receive() external payable {}
}
