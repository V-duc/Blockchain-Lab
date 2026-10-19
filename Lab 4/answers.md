# Lab 04 Answers: Real Bitcoin Blocks, PoW, fees and Merkle root

## Q1

The target of block `840000` starts with about 19 leading zero hexadecimal digits. Its target is approximately `2^224`, so a valid header represents roughly that scale of possible work. The expected number of trials is approximately `2^256 / target`, or around `2^32` hashes for this difficulty target.

## Q2

SHA-256 has a one-way, unpredictable output. Changing the nonce does not provide a shortcut for predicting a valid digest, so miners must try candidates one by one. Verification only needs to run double SHA-256 once and compare the result with the target. That is the difference between searching for a valid Proof of Work and checking one.

## Q3

Block `840000` was mined on the day of the fourth Bitcoin halving. The Runes protocol also launched that day, which caused unusually high demand for block space. Users competed by offering higher fees, creating a mempool auction. Bitcoin fees therefore depend mainly on demand for limited block space and the fee rates offered by transactions, rather than on a fixed fee schedule.

## Q4

The difference is the transaction fees paid by the transactions in the block:

```text
4,075,061,499 - 312,500,000 = 3,762,561,499 sat
```

The coinbase transaction collects both the block subsidy and the fees from the included transactions.

## Q5

The computed Merkle root matches the root in the block header. This means the supplied transaction list produces the same transaction commitment as the actual block. Since double SHA-256 is collision-resistant and has the avalanche property, changing, removing or reordering a transaction would produce a different root and fail the comparison.

## Verification notes

* The code reuses the bottom-up Merkle algorithm from Lab 3.
* Bitcoin-specific changes are double SHA-256 and reversing txid bytes before hashing and after computing the root.
* `bitcoin_explorer_starter.py` checks the 80-byte header, block ID, target comparison, transaction count, fee calculation, vsize, coinbase fee total and Merkle root.

## Bonus

Run:

```bash
python3 bitcoin_explorer_starter.py --bonus
```

The script finds the latest block before the current UTC midnight, recomputes its Merkle root and compares it with the root in that block's header. At the time of verification (`2026-10-10T16:06:12Z`), the selected previous-day block was height `970694`, with `4,740` transactions. Its Merkle-root check passed. The live mempool snapshot contained `78,470` transactions, `40,211,752` vbytes and `6,439,636 sat` in total fees. The recommended rate was `1 sat/vB` for the fastest, half-hour, hour, economy and minimum targets. These values change over time and are printed by the script instead of being hard-coded.
