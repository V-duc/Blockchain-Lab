#!/usr/bin/env python3
"""Lab 04: inspect Bitcoin block 840000 (PoW, fees, Merkle root)."""
import argparse, hashlib, json, math
from datetime import datetime, timezone
from pathlib import Path
import requests

BASE = "https://blockstream.info/api"
MEMPOOL_BASE = "https://mempool.space/api"
PINNED_HEIGHT = 840_000
DATA = Path(__file__).with_name("data")


def api(path, offline=False):
    DATA.mkdir(exist_ok=True)
    name = path.strip("/").replace("/", "_") + ".json"
    file = DATA / name
    if offline:
        return json.loads(file.read_text())
    r = requests.get(BASE + "/" + path.strip("/"), timeout=30)
    r.raise_for_status()
    text = r.text
    try: value = r.json()
    except ValueError: value = text
    file.write_text(json.dumps(value))
    return value


def mempool_api(path):
    r = requests.get(MEMPOOL_BASE + "/" + path.strip("/"), timeout=30)
    r.raise_for_status()
    return r.json()


def dsha256(b):
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()


def target_from_bits(bits):
    exponent = bits >> 24
    mantissa = bits & 0x007fffff
    return mantissa * 256 ** (exponent - 3)


def header_bytes(block):
    return (
        int(block["version"]).to_bytes(4, "little", signed=True)
        + bytes.fromhex(block["previousblockhash"])[::-1]
        + bytes.fromhex(block["merkle_root"])[::-1]
        + int(block["timestamp"]).to_bytes(4, "little")
        + int(block["bits"]).to_bytes(4, "little")
        + int(block["nonce"]).to_bytes(4, "little")
    )


def merkle_root(txids):
    level = [bytes.fromhex(txid)[::-1] for txid in txids]
    if not level: raise ValueError("empty transaction list")
    while len(level) > 1:
        if len(level) % 2: level.append(level[-1])
        level = [dsha256(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
    return level[0][::-1].hex()


def verify_block(height, offline=False):
    block = api(f"block-height/{height}", offline)
    block = api(f"block/{block}", offline)
    txids = api(f"block/{block['id']}/txids", offline)
    print("Block height:", height)

    raw = header_bytes(block)
    block_hash = dsha256(raw)[::-1].hex()
    target = target_from_bits(block["bits"])
    work_hash = int.from_bytes(bytes.fromhex(block_hash), "big")
    print("CHECK PoW header length:", "OK" if len(raw) == 80 else "FAIL")
    print("CHECK PoW block id:", "OK" if block_hash == block["id"] else "FAIL")
    print("CHECK PoW target:", "OK" if work_hash < target else "FAIL")
    print("CHECK transaction count:", "OK" if len(txids) == block["tx_count"] else "FAIL", len(txids))

    first = api(f"tx/{txids[1]}", offline)
    input_sat = sum(i["prevout"]["value"] for i in first["vin"] if i.get("prevout"))
    output_sat = sum(o["value"] for o in first["vout"])
    fee = input_sat - output_sat
    vsize = math.ceil(first["weight"] / 4)
    print("CHECK fee:", "OK" if fee == first["fee"] else "FAIL", fee)
    print("CHECK vsize:", "OK" if 4 * (vsize - 1) < first["weight"] <= 4 * vsize else "FAIL", vsize)

    coinbase = api(f"tx/{txids[0]}", offline)
    coinbase_total = sum(o["value"] for o in coinbase["vout"])
    subsidy = 5_000_000_000 >> (height // 210_000)
    print("CHECK coinbase fee:", "OK" if coinbase_total - subsidy >= 0 else "FAIL", coinbase_total - subsidy)
    root = merkle_root(txids)
    print("CHECK Merkle root:", "OK" if root == block["merkle_root"] else "FAIL", root)
    print(json.dumps({"block": block["id"], "tx_count": len(txids), "fee_sat": fee,
                      "vsize": vsize, "fee_rate_sat_vb": fee / vsize,
                      "coinbase_total_sat": coinbase_total,
                      "coinbase_fees_sat": coinbase_total - subsidy,
                      "merkle_root": root}, indent=2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--offline", action="store_true")
    p.add_argument("--bonus", action="store_true", help="verify yesterday's UTC tip and query live fees")
    args = p.parse_args()
    verify_block(PINNED_HEIGHT, args.offline)
    if args.bonus:
        if args.offline:
            snapshot = json.loads((DATA / "bonus.json").read_text())
        else:
            midnight = int(datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
            height = int(api("blocks/tip/height"))
            # Walk backwards: block timestamps are not strictly monotonic.
            while True:
                batch = api(f"blocks/{height}")
                candidate = next((b for b in batch if b["timestamp"] < midnight), None)
                if candidate:
                    break
                height = batch[-1]["height"] - 1
            snapshot = {"observed_utc": datetime.now(timezone.utc).isoformat(),
                        "yesterday_height": candidate["height"],
                        "mempool": mempool_api("mempool"),
                        "fees": mempool_api("v1/fees/recommended")}
            (DATA / "bonus.json").write_text(json.dumps(snapshot))
        yesterday_height = snapshot["yesterday_height"]
        print("BONUS yesterday height:", yesterday_height)
        verify_block(yesterday_height, args.offline)
        mempool = snapshot["mempool"]
        fees = snapshot["fees"]
        print("Observed UTC:", snapshot["observed_utc"])
        print(json.dumps({"mempool": {"count": mempool["count"], "vsize": mempool["vsize"],
                                       "total_fee_sat": mempool["total_fee"]},
                          "recommended_fee_sat_vb": fees}, indent=2))


if __name__ == "__main__": main()
