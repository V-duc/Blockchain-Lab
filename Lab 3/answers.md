# Lab 03 Answers

## Lab 3.1: Hash properties and toy Proof of Work

**Q1:** Each extra leading zero multiplies the expected work by about 16 times.
Each hexadecimal character of a SHA-256 digest has 16 possible values. Requiring one more leading zero reduces the valid search space by a factor of 16. On average, finding a nonce for k leading zeros takes about 16^k tries.

**Q2:** Verification takes only one hash call. This is the main difference between finding and checking a Proof of Work nonce. Finding one may require millions of attempts, but checking it needs only one hash computation.

## Lab 3.2: Merkle tree

**Q3:** For n = 1,000,000 transactions, a Merkle proof contains
ceil(log2(1,000,000)) = 20 hash values. Each value is the sibling hash for one level of the tree.

**Q4:** SPV (Simplified Payment Verification) wallets use this mechanism. A lightweight Bitcoin client does not download complete blocks. It stores block headers, including the Merkle root, and requests a Merkle proof from a full node when it needs to check a transaction. The wallet recomputes the path from the transaction to the root and compares the result with the root in the trusted header. This verifies that the transaction is included without storing the entire block.

Other examples include airdrop eligibility proofs. A project publishes a Merkle root on chain, and each user submits their leaf and proof to claim tokens. Proof of reserves works similarly: an exchange publishes a Merkle root of customer balances so users can check that their balance was included without seeing other customers' balances.

## Lab 3.3: Sign, verify and recover with eth account

**Task 1: Same message, run twice. Is the signature identical?**

[x] Yes (verified: sig_identical = True)
[ ] No

RFC 6979 explains this result. It generates the ECDSA nonce k deterministically from the private key and message hash using HMAC, rather than choosing a random k for every signature. Signing the same message with the same key therefore produces the same signature (r, s, v). It also avoids the private-key risk caused by accidentally reusing a random nonce.

**Task 2: Tampered message**

```
address:    0xa440e67b75f7FbeE0be33ff3E21F7fAC0de2C2e3
r:          0xd5050de14858c236e342487ea390081629a88caeb3a32a0ce74d147a95f5449d
s:          0x314b8fc3af407541681a301c17f99b6ac13c176b183fdcf7bbe7a868e0aca46d
v:          28
recovered:  0xa440e67b75f7FbeE0be33ff3E21F7fAC0de2C2e3
match:      True
tampered:   0xF9B354029c8133D1BdBfE7e59Fb24aafF0b80E2C
```

The signature depends on both the private key and the exact message bytes. `encode_defunct` hashes the message before signing. Changing even one character changes the message hash because of the avalanche effect from Lab 3.1. Recovering the signer address with the original signature and the tampered message therefore gives a different address from `acct.address`. The mismatch shows that the message was changed after signing. This is the integrity part of a digital signature, in addition to proving who signed it.

**Task 3 (Bonus): MetaMask personal_sign**

[ ] Done, recovered address matched the MetaMask account
[ ] Not attempted
