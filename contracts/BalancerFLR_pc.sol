// house_102523 _ ref: https://docs.balancer.fi/reference/contracts/flash-loans.html#example-code
// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.22;

import "@balancer-labs/v2-interfaces/contracts/vault/IVault.sol";
import "@balancer-labs/v2-interfaces/contracts/vault/IFlashLoanRecipient.sol";
interface IUniswapV2 {
    function swapExactTokensForTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
    function swapTokensForExactTokens(
        uint amountOut,
        uint amountInMax,
        address[] calldata path,
        address to,
        uint deadline
    ) external returns (uint[] memory amounts);
    function getAmountsOut(uint amountIn, address[] calldata path) external view returns (uint[] memory amounts);
}

contract BalancerFLR_pc is IFlashLoanRecipient {
    // ref: https://docs.balancer.fi/reference/contracts/flash-loans.html#example-code
    IVault private constant vault = IVault(0xBA12222222228d8Ba445958a75a0704d566BF2C8);

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
        require(msg.sender == _owner, "loan to owner only ;)");
        emit logMFL(address(this), msg.sender, "logMFL 1");
        vault.flashLoan(this, tokens, amounts, userData);
        emit logMFL(address(this), msg.sender, "logMFL -1");
    }
    
    // note_110523: only uniswap v2 protocol support for _pc
    function receiveFlashLoan(
        IERC20[] memory tokens,
        uint256[] memory amounts,
        uint256[] memory feeAmounts,
        bytes memory userData
    ) external override {
        emit logRFL(address(this), msg.sender, "logRFL 0");
        require(msg.sender == address(vault), "loan from vault only :p");
        
        emit logRFL(address(this), msg.sender, "logRFL 1");
        // (1) get loan in WETH (0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2)
        //  max loan = 114983659 WETH from pc->balancer-vault
        (address[] memory routers, address[][] memory paths) = abi.decode(userData, (address[], address[][]));
        require(routers.length == paths.length, 'err: router / path mismatch :/');
        require(tokens[0].balanceOf(address(this)) >= amounts[0], "err: loan transfer failed :?");

        // (2) arb setup -> (3) arb swap -> (4) arb tear-down _ (weth->wpls->...->wpls->weth)
        //  (2) [weth, wpls] _ plsx_rtr_v2 _ amounts[0]
        //  (3) [wpls, rob] _ 9inch_rtr _ amntOut
        //  (3) [rob, wpls] _ plsx_rtr_v2 _ amntOut
        //  (4) [wpls, weth] _ plsx_rtr_v2 _ amntOut
        uint256 amntOut = amounts[0];
        for (uint256 i = 0; i < routers.length; i++) {
            amntOut = swap_v2_wrap(paths[i], routers[i], amntOut);
        }
        
        // (5) payback WETH (0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2)
        //  note: no 'token.approve(,)' needed since this contract is transfering its own tokens
        uint256 amountOwed = amounts[0] + feeAmounts[0]; // note_110523: no fee on pc->balancer
        require(tokens[0].balanceOf(address(this)) >= amountOwed, "err: arb failed payback QQ");
        IERC20(tokens[0]).transfer(address(vault), amountOwed);
    }
    
    // uniwswap v2 protocol based: get quote and execute swap
    function swap_v2_wrap(address[] memory path, address router, uint256 amntIn) private returns (uint256) {
        //address[] memory path = [weth, wpls];
        uint256[] memory amountsOut = IUniswapV2(router).getAmountsOut(amntIn, path); // quote swap
        uint256 amntOut = swap_v2(router, path, amntIn, amountsOut[amountsOut.length -1]); // execute swap
                
        // verifiy new balance of token received
        uint256 new_bal = IERC20(path[path.length -1]).balanceOf(address(this));
        require(new_bal >= amntOut, "err: balance low :{");
        
        return amntOut;
    }
    
    // v2: solidlycom, kyberswap, pancakeswap, sushiswap, uniswap v2, pulsex v1|v2, 9inch
    function swap_v2(address router, address[] memory path, uint256 amntIn, uint256 amntOutMin) private returns (uint256) {
        emit logRFL(address(this), msg.sender, "logRFL 6a");
        IUniswapV2 swapRouter = IUniswapV2(router);
        
        emit logRFL(address(this), msg.sender, "logRFL 6b");
        IERC20(address(path[0])).approve(address(swapRouter), amntIn);
        uint deadline = block.timestamp + 300;
        
        emit logRFL(address(this), msg.sender, "logRFL 6c");
        uint[] memory amntOut = swapRouter.swapExactTokensForTokens(
                        amntIn,
                        amntOutMin,
                        path, //address[] calldata path,
                        address(this),
                        deadline
                    );

        emit logRFL(address(this), msg.sender, "logRFL 6d");
        return uint256(amntOut[amntOut.length - 1]); // idx 0=path[0].amntOut, 1=path[1].amntOut, etc.
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

