"""
Lab 5.3 - Gửi giao dịch type-2 và phân rã phí
TrustKeys L1 testnet RPC: https://l1testnet.trustkeys.network
Chain ID: 11968
"""

import sys
from web3 import Web3

# Đảm bảo hiển thị tiếng Việt trên console Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# PoA middleware
poa_middleware = None
try:
    from web3.middleware import ExtraDataToPOAMiddleware
    poa_middleware = ExtraDataToPOAMiddleware
except ImportError:
    try:
        from web3.middleware import geth_poa_middleware
        poa_middleware = geth_poa_middleware
    except ImportError:
        pass

def decompose_tx_fee(tx_hash_hex: str):
    rpc_url = "https://l1testnet.trustkeys.network"
    print("=" * 75)
    print(f"[*] Kết nối RPC: {rpc_url}")
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print("[-] Không thể kết nối tới RPC!")
        sys.exit(1)

    if poa_middleware:
        w3.middleware_onion.inject(poa_middleware, layer=0)

    tx_hash_hex = tx_hash_hex.strip()
    if not tx_hash_hex.startswith("0x"):
        tx_hash_hex = "0x" + tx_hash_hex

    print(f"[*] Đang truy vấn giao dịch: {tx_hash_hex} ...")
    try:
        rcpt = w3.eth.get_transaction_receipt(tx_hash_hex)
        tx = w3.eth.get_transaction(tx_hash_hex)
        blk = w3.eth.get_block(rcpt["blockNumber"])
    except Exception as e:
        print(f"[-] Lỗi khi truy vấn thông tin giao dịch: {e}")
        print("Vui lòng kiểm tra lại xem tx hash đã được xác nhận (mined) trên mạng chưa!")
        return

    # Lấy các trường dữ liệu
    tx_type = tx.get("type", 0)
    tx_from = tx.get("from")
    tx_to = tx.get("to")
    value_wei = tx.get("value", 0)
    block_number = rcpt.get("blockNumber")
    gas_used = rcpt.get("gasUsed")
    base_fee = blk.get("baseFeePerGas", 0)
    eff_price = rcpt.get("effectiveGasPrice")
    max_fee = tx.get("maxFeePerGas", None)
    max_priority = tx.get("maxPriorityFeePerGas", None)

    # Tính toán phân rã phí
    paid = gas_used * eff_price
    burned = gas_used * base_fee
    tip = gas_used * (eff_price - base_fee)
    is_valid = (paid == burned + tip)

    print("\n" + "=" * 75)
    print("           BẢNG PHÂN RÃ PHÍ GIAO DỊCH TYPE-2 (EIP-1559)")
    print("=" * 75)
    print(f"Tx Hash               : {tx_hash_hex}")
    print(f"Block Number          : {block_number}")
    print(f"Transaction Type      : {tx_type} ({'Type-2 (EIP-1559)' if tx_type == 2 or tx_type == '0x2' else 'Legacy / Type-1'})")
    print(f"From                  : {tx_from}")
    print(f"To                    : {tx_to}")
    print(f"Value                 : {value_wei} wei ({Web3.from_wei(value_wei, 'ether')} coin)")
    print("-" * 75)
    print(f"Gas Used              : {gas_used:,} gas")
    print(f"Base Fee per Gas      : {base_fee} wei")
    print(f"Effective Gas Price   : {eff_price} wei ({Web3.from_wei(eff_price, 'gwei')} gwei)")
    if max_fee is not None:
        print(f"Max Fee per Gas       : {max_fee} wei ({Web3.from_wei(max_fee, 'gwei')} gwei)")
    if max_priority is not None:
        print(f"Max Priority Fee      : {max_priority} wei ({Web3.from_wei(max_priority, 'gwei')} gwei)")
    print("-" * 75)
    print("CÔNG THỨC PHÂN RÃ: paid = burned + tip")
    print(f"  • Paid   (Tổng phí trả) : {paid:,} wei ({Web3.from_wei(paid, 'ether')} coin)")
    print(f"  • Burned (Phí bị đốt)   : {burned:,} wei ({Web3.from_wei(burned, 'ether')} coin)")
    print(f"  • Tip    (Thưởng miner) : {tip:,} wei ({Web3.from_wei(tip, 'ether')} coin)")
    print("-" * 75)
    print(f"Kiểm tra: {paid:,} = {burned:,} + {tip:,} ? => {is_valid}")
    if is_valid:
        print("[CHECK / DEMO = OK] ĐẲNG THỨC HOÀN TOÀN CHÍNH XÁC!")
        print("-> Phí gas đã được phân rã thành công thành 2 phần: burned (đốt bỏ) và tip (thưởng validator).")
    else:
        print("[!] Đẳng thức không khớp!")
    print("=" * 75)

def main():
    if len(sys.argv) > 1:
        tx_hash = sys.argv[1]
    else:
        print("Nhập tx hash từ MetaMask của bạn (hoặc nhấn Enter để dùng tx mẫu trên mạng TrustKeys):")
        tx_hash = input("Tx Hash: ").strip()
        if not tx_hash:
            # Giao dịch mẫu có thật trên mạng
            tx_hash = "0xcee77f2985042d26fbc71421a1dfd1faa8a43e2649b22fe55a5b2537ed47ee1e"
            print(f"[*] Sử dụng tx hash mẫu: {tx_hash}")

    decompose_tx_fee(tx_hash)

if __name__ == "__main__":
    main()
