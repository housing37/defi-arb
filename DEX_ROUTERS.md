# dex routers
    list of dex routers to interface with for arb

## Balancer dex 
    PC -> balancer max loan amnts (found in sol logs `balanceOf(address)`: `0x70a08231`)
        max amnt: 114,983,659.41104437 WETH (greater fails w/ "Fail with revert message: 'BAL#528'")
        ADDR_WETH: 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2
        vault: 0xba12222222228d8ba445958a75a0704d566bf2c8
        ProtocolFeesCollector: 0xce88686553686DA562CE7Cea497CE749DA109f9F
            - note: this addr is called by vault addr during loan process
            - note_2: this addr was created by 0xBA12222222228d8Ba445958a75a0704d566BF2C8
            
        max amnt: 1 USDC (fails on loan for just 1 USDC)    
        ADDR_USDC = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
        vault: 0xba12222222228d8ba445958a75a0704d566bf2c8
        ProtocolFeesCollector: 0xce88686553686DA562CE7Cea497CE749DA109f9F
            - note: fails on call to '0xd877845c' == 'getFlashLoanFeePercentage'
                 (on PC -> for USDC, but indeed succeeds for WETH)

## PulseChain dex routers
    DEX: 9inch (found through pc blockexplorer) _ 110423: uniswapV2 protocol YES confirmed
     addr: 0xeB45a3c4aedd0F47F345fB4c8A1802BB5740d725 // i think
     ref: https://www.9inch.io/
     ref: https://9inch.gitbook.io/9inch-gitbook/features/contracts
     ref: https://scan.pulsechain.com/address/0xeB45a3c4aedd0F47F345fB4c8A1802BB5740d725   
        
    DEX: pulseX
        addr: 0x98bf93ebf5c380C0e6Ae8e192A7e2AE08edAcc02 // pulsex router_v1 
        addr: 0x165C3410fC91EF562C50559f7d2289fEbed552d9 // pulsex router_v2
    
    DEX: pulse-rate (found in arb_seercher logs, no research yet)

## Ethereum mainnet dex routers
    DEX: balancer (found in .py logs)
     ref: https://docs.balancer.fi/reference/contracts/deployment-addresses/mainnet.html
     note: don't see 'router' address anywhere
     note: found discord and asked for support

    DEX: defiswap (found in .py logs)
     ref: https://docs.defiswap.io/developer/smart-contracts
     note: can only find BSC: 
        ref: https://bscscan.com/address/0xeb33cbbe6f1e699574f10606ed9a495a196476df#writeContract
     note: found discord and asked for support (https://discord.com/invite/UjTUyN6qhx)

    DEX: 9inch (found etherscan.io blockexplorer) _ 110423: uniswapV2 protocol MAYBE confirmed
     addr: 0x13f4EA83D0bd40E75C8222255bc855a974568Dd4 // i think
     ref: https://www.9inch.io/
     ref: https://9inch.gitbook.io/9inch-gitbook/features/contracts
     ref: https://etherscan.io/token/0xFD8b9Ba4845fB38c779317eC134b298C064937a2
     
    DEX: uniswap v3 (found in .py logs)
     addr: 0xE592427A0AEce92De3Edee1F18E0157C05861564 // SwapRouter
     ref: https://docs.uniswap.org/contracts/v3/reference/deployments
     ref: https://github.com/Uniswap/v3-periphery/blob/v1.0.0/contracts/SwapRouter.sol
     
    DEX: uniswap v2 (found in .py logs)
     adddr: 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D // 'UniswapV2Router02'
     ref: https://docs.uniswap.org/contracts/v2/reference/smart-contracts/router-02

    DEX: solidlycom (found in .py logs)
     addr: 0x77784f96C936042A3ADB1dD29C91a55EB2A4219f // Router ('v2 contracts')
     ref: https://docs.solidly.com/resources/contract-addresses)
     ref: https://etherscan.io/address/0x77784f96C936042A3ADB1dD29C91a55EB2A4219f#writeProxyContract

    DEX: kyberswap (found in .py logs)
     addr: 0x1c87257F5e8609940Bc751a07BB085Bb7f8cDBE6 // DMMRouter ('Dynamic Fee')
     addr: 0x5649B4DD00780e99Bab7Abb4A3d581Ea1aEB23D0 // KSRouter ('Static Fee')
     addr: 0x5F1dddbf348aC2fbe22a163e30F99F9ECE3DD50a // found in logs (etherscan.io say kyberswap)
     ref: https://docs.kyberswap.com/liquidity-solutions/kyberswap-classic/contracts/classic-contract-addresses
     ref: https://etherscan.io/address/0x1c87257F5e8609940Bc751a07BB085Bb7f8cDBE6#writeContract
     ref: https://etherscan.io/address/0x5649B4DD00780e99Bab7Abb4A3d581Ea1aEB23D0#code
     note: found discord and asked for support: forward me to ask Q -> https://support.kyberswap.com/hc/en-us/requests/new

    DEX: pancakeswap (found in .py logs)
     addr: 0x13f4EA83D0bd40E75C8222255bc855a974568Dd4 // ethereum: v3
     addr: 0x10ED43C718714eb63d5aA57B78B54704E256024E // ethereum: v2
     ref: https://etherscan.io/address/0x13f4EA83D0bd40E75C8222255bc855a974568Dd4#writeContract
     ref: https://etherscan.io/address/0x10ed43c718714eb63d5aa57b78b54704e256024e
     note: verified on discord

    DEX: sushiswap (found in .py logs)
     addr: 0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F // ethereum: V2Router02 'specifically for v2 pools'
     ref: https://docs.sushi.com/docs/Developers/Deployment%20Addresses
     ref: https://etherscan.io/address/0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F#writeContract
     note: verified on discord
     note: found V2Router02, and asked support for v3 in discord
     note: other addresses found (not confirmed as 'routers'
        addr: 0x02a480a258361c9bc3eaacbd6473364c67adcd3a // sushiswap AxelarAdapter has swap function _ ref: https://github.com/sushiswap
        addr: 0x580ED43F3BBa06555785C81c2957efCCa71f7483 // sushiswap StargateAdapter has swap function _ ref: https://github.com/sushiswap
        addr: 0x804b526e5bF4349819fe2Db65349d0825870F8Ee // sushiswap SushiXSwapV2 has swap function _ ref: https://github.com/sushiswap
        addr: 0xc5578194D457dcce3f272538D1ad52c68d1CE849 // sushiswap i dunno
        addr: 0x827179dD56d07A7eeA32e3873493835da2866976 // sushiswap 'RouteProcessor3'
        addr: 0x011E52E4E40CF9498c79273329E8827b21E2e581 // sushiswap 'SushiXSwap'

    DEX: misc found in arb_searcher.py logs (no research yet)
        addr: 0xcBAE5C3f8259181EB7E2309BC4c72fDF02dD56D8
        addr: 0x03407772F5EBFB9B10Df007A2DD6FFf4EdE47B53
        addr: 0x564C4529E12FB5a48AD609820D37D15800c1f539
        addr: 0x696708Db871B77355d6C2bE7290B27CF0Bb9B24b
    
    DEX: safemoonswap (found in .py logs; no research yet)
    
    DEX: fraxswap (found in .py logs; no research yet)   

    DEX: radioshack (found in .py logs; no research yet)
    
    DEX: shibaswap (found in .py logs)
     note: found https://docs.shibatoken.com/shibaswap and https://shibaswap.com/#/
        not sure which one is right
     note: found discord and opened support request
     note: found pdf on one of the sites above with 'MULTISIGADDRESSES' (i dunno)
        ref: https://github.com/shytoshikusama/woofwoofpaper/raw/main/SHIBA_INU_WOOF_WOOF.pdf

    DEX: verse (found in .py logs)
        ref: https://docs.swapverse.exchange/ & https://twitter.com/Swapverse_)
     note: can't find discord or list of contract addresses
     addr: https://etherscan.io/token/0xeacadc656c9394fb09af25aebc0897fdffe484a1#code
        found through .py log pairs (102923)
