# Lab 03 Answers

## Lab 3.1: Hash properties & toy Proof of Work

**Q1:** Each extra leading zero multiplies the expected work by about 16x.
Each hex character of a SHA-256 digest has 16 possible values, so requiring
one more leading zero hex digit shrinks the valid search space by a factor
of 16. On average, finding a nonce for k leading zeros takes about 16^k tries.

**Q2:** Verifying takes just 1 hash call. This shows the core asymmetry of
Proof of Work: finding a valid nonce can take millions of tries, but checking
it only needs a single hash computation. This asymmetry is what makes the
consensus mechanism practical.

## Lab 3.2: Merkle tree

**Q3:** For n = 1,000,000 transactions, a Merkle proof contains
ceil(log2(1,000,000)) = 20 hash values, one sibling hash per level of the tree.

**Q4:** SPV (Simplified Payment Verification) wallets use exactly this
mechanism. A lightweight Bitcoin client does not download full blocks. It
only stores block headers, which include the Merkle root, and to confirm a
specific transaction is in a block, it requests a Merkle proof from a full
node. It recomputes the path up to the root and compares it against the
root already stored in the header it trusts. This lets the light client
verify inclusion without downloading or storing the entire block.

Other valid examples: airdrop eligibility proofs, where a project publishes
only a Merkle root on chain and each user submits their own leaf plus proof
to claim tokens; and proof of reserves, where an exchange publishes a
Merkle root of all customer balances so users can verify their balance was
included without seeing anyone else's.

## Lab 3.3: Sign, verify and recover with eth account

**Task 1: Same message, run twice. Is the signature identical?**

[x] Yes (verified: sig_identical = True)
[ ] No

Which RFC explains this? RFC 6979 defines deterministic generation of the
ECDSA nonce k from the private key and message hash using HMAC, instead of
using a random k each time. This is why signing the same message with the
same key twice produces the same signature (r, s, v). It also removes the
risk of nonce reuse leaking the private key, which is a real vulnerability
when k is random and gets reused.

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

Why does this prove integrity? The signature is a function of both the
private key and the exact message bytes, since encode_defunct hashes the
message before signing. Changing even a single character changes the
message hash completely, due to the avalanche effect from Lab 3.1. So
recovering a signer address from the original signature against the
tampered message hash yields a different address than acct.address. Since
the recovered address no longer matches, anyone verifying the signature
can immediately tell the message was altered after it was signed. This is
what gives a digital signature its integrity guarantee, in addition to
authenticity.

**Task 3 (Bonus): MetaMask personal_sign**

[ ] Done, recovered address matched the MetaMask account
[ ] Not attempted
