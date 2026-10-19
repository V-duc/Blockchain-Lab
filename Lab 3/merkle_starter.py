#!/usr/bin/env python3
"""Lab 3.2 — Merkle tree (starter)."""
import hashlib


def H(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


# TODO 1 — dựng cây Merkle từ dưới lên, trả về hash gốc (root).
# Đây là bước cốt lõi: từ danh sách lá, ghép cặp và băm liên tiếp
# lên tới khi chỉ còn 1 node duy nhất (root), đại diện cho toàn bộ
# tập giao dịch chỉ bằng một hash 32 byte.
def merkle_root(leaves: list[bytes]) -> bytes:
    if not leaves:
        return H(b"")
    level = leaves[:]
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])  # tầng lẻ: nhân đôi node cuối
        level = [H(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
    return level[0]


# TODO 2 — trả về đường dẫn chứng minh (proof) cho lá tại vị trí `index`.
# Proof là danh sách các hash "anh em" (sibling) trên đường từ lá lên root,
# kèm vị trí (trái/phải), để bên xác minh có thể tự tính lại root mà
# không cần biết toàn bộ cây.
def merkle_proof(leaves: list[bytes], index: int) -> list[tuple[bytes, bool]]:
    proof = []
    level = leaves[:]
    idx = index
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        if idx % 2 == 0:
            sibling = level[idx + 1]
            sibling_is_left = False
        else:
            sibling = level[idx - 1]
            sibling_is_left = True
        proof.append((sibling, sibling_is_left))
        level = [H(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
        idx //= 2
    return proof


# TODO 3 — xác minh một lá thuộc cây bằng proof, không cần toàn bộ cây.
# Tính ngược từ leaf_hash lên root theo proof, rồi so sánh với root đã biết.
def verify_proof(leaf_hash: bytes, proof: list[tuple[bytes, bool]], root: bytes) -> bool:
    h = leaf_hash
    for sibling, sibling_is_left in proof:
        if sibling_is_left:
            h = H(sibling + h)
        else:
            h = H(h + sibling)
    return h == root


if __name__ == "__main__":
    txs = [f"tx{i}: A->B {i} coin".encode() for i in range(8)]
    leaves = [H(t) for t in txs]
    root = merkle_root(leaves)

    print("root:", root.hex())

    ok = all(verify_proof(leaves[i], merkle_proof(leaves, i), root) for i in range(8))
    print("CHECK 1 (all 8 proofs valid):", "OK" if ok else "FAIL")

    print("CHECK 2 (proof length == 3):", "OK" if len(merkle_proof(leaves, 4)) == 3 else "FAIL")

    fake = H(b"tx4: A->B 999999 coin")
    print("CHECK 3 (tampered leaf fails):",
          "OK" if not verify_proof(fake, merkle_proof(leaves, 4), root) else "FAIL")

    l7 = leaves[:7]
    r7 = merkle_root(l7)
    print("CHECK 4 (odd count works):",
          "OK" if all(verify_proof(l7[i], merkle_proof(l7, i), r7) for i in range(7)) else "FAIL")
