# Lab 04 Answers — Real Bitcoin Blocks: PoW, Fees & Merkle Root

## Q1

The target of block `840000` starts with approximately 19 leading zero hexadecimal digits. Its target is approximately `2^224`, so a valid header represents roughly `2^224` possible-work scale. The expected number of trials is approximately `2^256 / target`, around `2^32` hashes for this difficulty target.

## Q2

SHA-256 has a one-way, unpredictable output: changing the nonce does not provide a shortcut for predicting a valid digest. Therefore miners must try candidates by brute force, while verification only recomputes the double SHA-256 once and compares the result with the target. This is the one-way asymmetry of Proof of Work.

## Q3

Block `840000` was mined on the fourth Bitcoin halving day, when the Runes protocol launched and created intense demand for block space. Users competed by bidding unusually high fees, creating a mempool auction. This shows that Bitcoin fees are market-based: they depend mainly on demand for limited block space and the fee rates offered by transactions, not on a fixed fee schedule.

## Q4

The difference is transaction fees paid by the transactions in the block:

```text
4,075,061,499 − 312,500,000 = 3,762,561,499 sat
```

The coinbase transaction collects both the block subsidy and the fees from all included transactions.

## Q5

The computed Merkle root matches the root committed in the block header, proving that the supplied transaction list folds to exactly the transaction commitment recorded by the block. Because double SHA-256 is collision-resistant and has the avalanche property, changing, removing, or reordering a transaction would produce a different Merkle root and fail the comparison.

## Verification notes

- The code reuses the Lab 3 bottom-up Merkle algorithm.
- Bitcoin-specific changes are double SHA-256 and reversing txid bytes before hashing / after computing the root.
- `bitcoin_explorer_starter.py` checks the 80-byte header, block ID, target comparison, transaction count, fee calculation, vsize, coinbase fee total, and Merkle root.

## Bonus

Run:

```bash
python3 bitcoin_explorer_starter.py --bonus
```

The script finds the latest block before today's UTC midnight, recomputes its Merkle root, and checks it against that block's header. At the time of verification (`2026-10-10T16:06:12Z`), the selected previous-day block was height `970694`, with `4,740` transactions; its Merkle-root check passed. The live mempool snapshot contained `78,470` transactions, `40,211,752` vbytes, and `6,439,636 sat` total fees. Recommended rates were `1 sat/vB` for fastest, half-hour, hour, economy, and minimum targets. These values are time-sensitive and are printed by the script rather than hard-coded.
