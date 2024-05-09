// SPDX-License-Identifier: agpl-3.0
// pragma solidity 0.6.12;
pragma solidity ^0.8.24;        

// import { FlashLoanReceiverBase } from "FlashLoanReceiverBase.sol";
// import { ILendingPool, ILendingPoolAddressesProvider, IERC20 } from "Interfaces.sol";
// import { SafeMath } from "Libraries.sol";

// local _ $ git clone https://github.com/aave/code-examples-protocol.git
import "./FlashLoanReceiverBase.sol"; 
import "./Interfaces.sol"; 
import "./Libraries.sol"; 

/** 
    !!!
    Never keep funds permanently on your FlashLoanReceiverBase contract as they could be 
    exposed to a 'griefing' attack, where the stored funds are used by an attacker.
    !!!
 */
contract MyV2FlashLoan is FlashLoanReceiverBase {
    using SafeMath for uint256;

    // aave lending pool PHIAT (pulsechain)
    ILendingPoolAddressesProvider private constant lendPoolV1_phiat = ILendingPoolAddressesProvider(0x59BC239cAb00CADd9b14f299835ae39E8B4B569c);
        // aave v2 ref: https://sourcehat.com/audits/PhiatProtocol/
    // aave lending pools
    ILendingPoolAddressesProvider private constant lendPoolV1 = ILendingPoolAddressesProvider(0x398eC7346DcD622eDc5ae82352F02bE94C62d119);
    ILendingPoolAddressesProvider private constant lendPoolV2 = ILendingPoolAddressesProvider(0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9);
    ILendingPoolAddressesProvider private constant lendPoolV3 = ILendingPoolAddressesProvider(0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2);
        // aave v1 ref: https://docs.aave.com/developers/v/1.0/deployed-contracts/deployed-contract-instances
        // aave v2 ref: https://docs.aave.com/developers/v/2.0/deployed-contracts/deployed-contracts
        // aave v3 ref: https://docs.aave.com/developers/deployed-contracts/v3-mainnet/ethereum-mainnet
     
    constructor(ILendingPoolAddressesProvider _addressProvider) FlashLoanReceiverBase(_addressProvider) {}

    /**
        This function is called after your contract has received the flash loaned amount
     */
    function executeOperation(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata premiums,
        address initiator,
        bytes calldata params
    )
        external
        override
        returns (bool)
    {

        //
        // This contract now has the funds requested.
        // Your logic goes here.
        //

        // At the end of your logic above, this contract owes
        // the flashloaned amounts + premiums.
        // Therefore ensure your contract has enough to repay
        // these amounts.

        // Approve the LendingPool contract allowance to *pull* the owed amount
        for (uint i = 0; i < assets.length; i++) {
            uint amountOwing = amounts[i].add(premiums[i]);
            IERC20(assets[i]).approve(address(LENDING_POOL), amountOwing);
        }

        return true;
    }

    function myFlashLoanCall() public {
        address receiverAddress = address(this);

        address[] memory assets = new address[](7);
        assets[0] = address(0xB597cd8D3217ea6477232F9217fa70837ff667Af); // Kovan AAVE
        assets[1] = address(0x2d12186Fbb9f9a8C28B3FfdD4c42920f8539D738); // Kovan BAT
        assets[2] = address(0xFf795577d9AC8bD7D90Ee22b6C1703490b6512FD); // Kovan DAI
        assets[3] = address(0x075A36BA8846C6B6F53644fDd3bf17E5151789DC); // Kovan UNI
        assets[4] = address(0xb7c325266ec274fEb1354021D27FA3E3379D840d); // Kovan YFI
        assets[5] = address(0xAD5ce863aE3E4E9394Ab43d4ba0D80f419F61789); // Kovan LINK
        assets[6] = address(0x7FDb81B0b8a010dd4FFc57C3fecbf145BA8Bd947); // Kovan SNX

        uint256[] memory amounts = new uint256[](7);
        amounts[0] = 1 ether;
        amounts[1] = 1 ether;
        amounts[2] = 1 ether;
        amounts[3] = 1 ether;
        amounts[4] = 1 ether;
        amounts[5] = 1 ether;
        amounts[6] = 1 ether;

        // 0 = no debt, 1 = stable, 2 = variable
        uint256[] memory modes = new uint256[](7);
        modes[0] = 0;
        modes[1] = 0;
        modes[2] = 0;
        modes[3] = 0;
        modes[4] = 0;
        modes[5] = 0;
        modes[6] = 0;

        address onBehalfOf = address(this);
        bytes memory params = "";
        uint16 referralCode = 0;

        LENDING_POOL.flashLoan(
            receiverAddress,
            assets,
            amounts,
            modes,
            onBehalfOf,
            params,
            referralCode
        );
    }
}
