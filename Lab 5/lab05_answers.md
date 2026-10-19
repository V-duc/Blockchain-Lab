# Lab 05: Ethereum accounts, gas and the EVM

## Lab 5.2: Observed TrustKeys L1 output

* RPC: `https://l1testnet.trustkeys.network`
* Chain ID: `11968`
* Observed latest block: `717631`
* Latest `baseFeePerGas`: `8 wei`
* Average `gasUsedRatio` over the 20-block window: `0.90%`
* Projected next base fee: `8 wei`
* Verdict: `CHECK = OK`; the chain is quiet.

These values were read from `solutions/fee_history.py`. Block numbers and fee values may change when the script is run again.

## Q1

`chainId` is included in the signed transaction data under EIP-155. A signature created for one chain is therefore not valid for replay on another chain with a different `chainId`. This protects against cross-chain replay attacks.[2]

## Q2

The target gas usage is 15 million, half of the 30-million gas limit. The observed average `gasUsedRatio` is only 0.90%, so the blocks are well below the target. Under EIP-1559, the base fee therefore moves down. Since it is already only 8 wei, integer rounding makes the decrease zero, so the base fee stays at the network floor until demand rises.[3]

## Q3

For a request covering `N` blocks, `gasUsedRatio` contains one value for each block. `baseFeePerGas` contains those same `N` values plus the base fee calculated for the next block. A wallet can use the final value as a short-term estimate and set `maxFeePerGas` to that estimate plus the chosen `maxPriorityFeePerGas`, with an optional safety margin.[3]

## Lab 5.3: Type-2 transaction fee decomposition

This section must use the real type-2 transfer sent on **TrustKeys L1**. The Sepolia transaction below is a contract interaction for Lab 5.4, not the required 0.001-coin TrustKeys transfer.

Fill in the following after the TrustKeys transaction is mined:

```text
Transaction hash: <your TrustKeys transaction hash>
Transaction type: 2
Block number: <block number>
Gas used: <gas used>
Base fee: <base fee in wei>
Effective gas price: <effective gas price in wei>
Paid: gasUsed * effectiveGasPrice
Burned: gasUsed * baseFeePerGas
Tip: gasUsed * (effectiveGasPrice - baseFeePerGas)
Check: paid == burned + tip -> True
```

## Q4

Usually, no. The effective gas price is

```text
effectiveGasPrice = baseFee + min(maxPriorityFee, maxFee - baseFee)
```

If the original `maxFeePerGas` is at least `baseFee + maxPriorityFeePerGas`, increasing only `maxFeePerGas` does not change the effective price. It only increases the maximum amount the sender is willing to pay. The effective price changes when the previous max fee was the limiting value.

For the supplied transaction, `baseFee = 18 wei`, `maxPriorityFeePerGas = 1,000,000 wei` and `effectiveGasPrice = 1,000,018 wei`, which equals `18 + 1,000,000`.[1]

## Q5

A simple ETH transfer with empty calldata and no access list costs 21,000 gas. This is the base transaction-processing cost. Contract execution and non-zero calldata require additional gas.[3]

A failed transaction still consumes gas because the EVM has already used computational resources. The state changes are reverted, but the gas used is charged. Only unused gas can be returned, subject to the applicable refund rules.

## Lab 5.4: Sepolia contract interaction

Transaction link: [Open the supplied transaction on Sepolia Etherscan](https://sepolia.etherscan.io/tx/0x51a3c957852d9533049694d0b48e7a6656169e8de729c86673d7fa119e7a0614)

Observed transaction details:

* Network: Sepolia
* Chain ID: `11155111`
* Status: successful
* Transaction type: `2 (EIP-1559)`
* Contract: `0x5543ca71ed8c88daf217488b1808994e080d925b`
* Function: `approve(address to, uint256 tokenId)`
* Function selector / MethodID: `0x095ea7b3`
* `to`: `0x18eb5daceb55e69de7154ae5e9067bc1c6f2f42b`
* `tokenId`: `115792089237316195423570985008687907853269984665640564039457584007913129639935` (`2^256 - 1`)

The transaction emitted an `Approval` event:

```text
Approval(address owner, address approved, uint256 tokenId)
owner:    0x7272C069A1745Ca754Ff5d95F763757deCf03B4d
approved: 0x18EB5daCEb55E69de7154AE5E9067Bc1C6F2f42b
tokenId: 2^256 - 1
```

### Required screenshots

![Decoded Input Data](lab54_input-data.png)

![Logs](lab54_logs.png)

## Q6

The EVM dispatcher reads the first four bytes of calldata, called the function selector. For example, `0xa9059cbb` is the selector for `transfer(address,uint256)`. The dispatcher uses it to route execution to the matching function. Etherscan needs the contract ABI to decode the remaining bytes because the ABI defines the function signature, parameter types and encoding rules.

The supplied transaction uses `approve(address,uint256)`, so its actual selector is `0x095ea7b3`. The worksheet's `0xa9059cbb` value is the generic ERC-20 `transfer(address,uint256)` example.

## Sources

[1] [Supplied Sepolia transaction](https://sepolia.etherscan.io/tx/0x51a3c957852d9533049694d0b48e7a6656169e8de729c86673d7fa119e7a0614) for transaction fields, input data and logs.

[2] [EIP-155: Simple replay attack protection](https://eips.ethereum.org/EIPS/eip-155)

[3] [EIP-1559: Fee market change for ETH 1.0 chain](https://eips.ethereum.org/EIPS/eip-1559)
