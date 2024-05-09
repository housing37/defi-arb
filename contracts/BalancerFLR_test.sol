// house_102523 _ ref: https://docs.balancer.fi/reference/contracts/flash-loans.html#example-code
// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.22;

import "@balancer-labs/v2-interfaces/contracts/vault/IVault.sol";
import "@balancer-labs/v2-interfaces/contracts/vault/IFlashLoanRecipient.sol";

contract BalancerFLR_test is IFlashLoanRecipient {
    // ref: https://docs.balancer.fi/reference/contracts/flash-loans.html#example-code
    IVault private constant vault = IVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);
    // pWETH: 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 -> 203658647860394116213752201 / 10**18 == 203658647.86039412 ~= $12,228.2445082
    // pUSDC: 0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48 -> 23937491402753 / 10**6 == 23937491.402753 ~= $74,767.781978741
    // pWBTC: 0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599 -> 5994742939 / 10**8 == 59.94742939 ~= $13,208.5705829
    // pUSDT: 0xdAC17F958D2ee523a2206206994597C13D831ec7 -> 13296690613518 / 10**6 == 13296690.613518 ~= $39,213.741269448

    // pDOLA: 0x865377367054516e17014CcdED1e7d814EDC9ce4 -> 30614508079920854526255527 / 10**18 ~= $236.198849851
    // pAAVE: 0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9 -> 2114928347848533872595 / 10**18 ~= $280.453860038

    // ERROR: LIQUIDITY < BALANCE
    // pBAL: 0xba100000625a3754423978a60c9317c58a424e3D ->  3946496821522180948639451 / 10**18 == 3946496.821522181 ~= $41,153.679623988
    // prETH: 0xae78736cd615f374d3085123a210448e74fc6393 -> 27843230642023975590639 / 10**18 ~= $8,067.713537987

    address private constant balancerRouter = address(0x37);
    address public _owner;

    event logX(address indexed contr, address sender, string message);
    event logRFL(address indexed contr, address sender, string message);
    event logMFL(address indexed contr, address sender, string message);

    modifier onlyOwner() {
        require(msg.sender == _owner, "Only owner");
        _;
    }
    
    constructor() {
        emit logX(address(this), msg.sender, "logX 0");
        _owner = msg.sender;
    }

    function makeFlashLoan(
        IERC20[] memory tokens,
        uint256[] memory amounts,
        bytes memory userData
    ) external {
        emit logMFL(address(this), msg.sender, "logMFL 0");
        require(msg.sender == _owner, "loan to owner only");
        emit logMFL(address(this), msg.sender, "logMFL 1");
        vault.flashLoan(this, tokens, amounts, userData);
        emit logMFL(address(this), msg.sender, "logMFL -1");
    }

    function receiveFlashLoan(
        IERC20[] memory tokens,
        uint256[] memory amounts,
        uint256[] memory feeAmounts,
        bytes memory userData
    ) external override {
        emit logRFL(address(this), msg.sender, "logRFL 0");
        require(msg.sender == address(vault), "loan from vault only");
        
        emit logRFL(address(this), msg.sender, "logRFL 1");
        // (address router_0, address router_1, address[] memory path_0, address[] memory path_1, uint256 amntIn_0, uint256 amntOutMin_1) = abi.decode(userData, (address, address, address[], address[], uint256, uint256));
        
        emit logRFL(address(this), msg.sender, "logRFL 2");
        uint256 bal = tokens[0].balanceOf(address(this));
        
        emit logRFL(address(this), msg.sender, "logRFL 3");
        // approve for payback when execution finished
        //  init testing: return immediately (payback right away; req funds in this contract)
        //uint256 amountOwed = amounts[0] + feeAmounts[0];
        // IERC20(asset).approve(address(vault), amountOwed);
        //tokens[0].approve(address(vault), amountOwed);
        
        // payback loan
        uint256 amountOwed = amounts[0] + feeAmounts[0];
        //tokens[0].approve(address(vault), amountOwed);
        IERC20(tokens[0]).transfer(address(vault), amountOwed);
        
        // Approve the LendingPool contract allowance to *pull* the owed amount
        // i.e. AAVE V2's way of repaying the flash loan
        //for (uint i = 0; i < tokens.length; i++) {
        //    uint amountOwing = amounts[i].add(feeAmounts[i]);
        //    IERC20(tokens[i]).transfer(address(vault), amountOwing);
        //}
    }

    function withdraw(uint256 amount) external onlyOwner {
        require(address(this).balance >= amount, "Insufficient native token balance");
        
        // cast owner address to a 'payable' address so it can receive ETH
        payable(_owner).transfer(amount);
    }
    
    receive() external payable {}
    
    // Function to transfer ERC20 tokens to a target address
    function transferTokens(address token, address to, uint256 amount) external onlyOwner {
        // Create an instance of the ERC20 token
        IERC20 tok = IERC20(token);

        // Check the contract's balance of the token
        uint256 contractBalance = tok.balanceOf(address(this));
        require(contractBalance >= amount, "Insufficient balance in the contract");

        // Transfer tokens to the target address
        tok.transfer(to, amount);
    }
}
