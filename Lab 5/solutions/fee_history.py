"""
Lab 5.2 - Đọc chuỗi bằng web3.py
TrustKeys L1 testnet RPC: https://l1testnet.trustkeys.network
Chain ID: 11968
"""

import sys
import io

# Đảm bảo hiển thị tiếng Việt mượt mà trên console Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from web3 import Web3

# Hỗ trợ PoA middleware cho chuỗi clique/PoA
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

def main():
    rpc_url = "https://l1testnet.trustkeys.network"
    print("=" * 75)
    print(f"[*] Đang kết nối tới RPC: {rpc_url} ...")
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    if not w3.is_connected():
        print("[-] Lỗi: Không thể kết nối tới RPC! Vui lòng kiểm tra kết nối mạng.")
        sys.exit(1)

    print(f"[+] Kết nối thành công! Chain ID: {w3.eth.chain_id}")

    # Inject middleware xử lý ExtraData dài 97 bytes của PoA (clique)
    if poa_middleware:
        try:
            w3.middleware_onion.inject(poa_middleware, layer=0)
            print("[+] Đã nạp PoA Middleware thành công.")
        except Exception as e:
            print(f"[!] Ghi chú middleware: {e}")

    # 1. Gọi eth_getBlockByNumber (lấy block mới nhất)
    print("\n" + "=" * 75)
    print("--- 1. THÔNG TIN BLOCK MỚI NHẤT (eth_getBlockByNumber) ---")
    latest_block = w3.eth.get_block("latest")
    block_num = latest_block["number"]
    base_fee = latest_block.get("baseFeePerGas", None)
    gas_used = latest_block.get("gasUsed", 0)
    gas_limit = latest_block.get("gasLimit", 1)

    print(f"Block Number     : {block_num}")
    print(f"Timestamp        : {latest_block.get('timestamp')}")
    print(f"Gas Used / Limit : {gas_used:,} / {gas_limit:,} ({gas_used / gas_limit * 100:.2f}%)")
    if base_fee is not None:
        print(f"baseFeePerGas    : {base_fee} wei ({Web3.from_wei(base_fee, 'gwei')} gwei)")
    else:
        print("baseFeePerGas    : None (EIP-1559 chưa kích hoạt ở block này)")

    # 2. Gọi eth_getBalance (lấy số dư một địa chỉ)
    print("\n" + "=" * 75)
    print("--- 2. KIỂM TRA SỐ DƯ (eth_getBalance) ---")
    test_addr = latest_block.get("miner", "0x0000000000000000000000000000000000000000")
    if len(sys.argv) > 1 and sys.argv[1].startswith("0x"):
        test_addr = sys.argv[1]
    try:
        bal_wei = w3.eth.get_balance(test_addr)
        print(f"Địa chỉ kiểm tra : {test_addr}")
        print(f"Số dư            : {bal_wei} wei ({Web3.from_wei(bal_wei, 'ether')} coin)")
    except Exception as e:
        print(f"Lỗi truy vấn số dư: {e}")

    # 3. Gọi eth_feeHistory (20 blocks gần nhất, percentiles [10, 50, 90])
    print("\n" + "=" * 75)
    print("--- 3. LỊCH SỬ PHÍ 20 BLOCKS GẦN NHẤT (eth_feeHistory) ---")
    block_count = 20
    try:
        fh = w3.eth.fee_history(block_count, "latest", [10, 50, 90])
        oldest_block = fh["oldestBlock"]
        base_fees = fh["baseFeePerGas"]  # Dài N + 1 = 21
        gas_ratios = fh["gasUsedRatio"]  # Dài N = 20
        rewards = fh.get("reward", [])   # N hàng x 3 percentiles

        print(f"{'Block #':<10} | {'Base Fee (wei)':<16} | {'Gas Used Ratio':<18} | {'Priority Fee (p10, p50, p90) in wei'}")
        print("-" * 80)
        
        total_ratio = 0.0
        for i in range(len(gas_ratios)):
            blk_id = oldest_block + i
            b_fee = base_fees[i]
            ratio = gas_ratios[i]
            total_ratio += ratio
            p_rewards = rewards[i] if i < len(rewards) else []
            rew_str = ", ".join([str(r) for r in p_rewards]) if p_rewards else "0, 0, 0"
            print(f"{blk_id:<10} | {b_fee:<16} | {ratio:<8.4f} ({ratio*100:5.2f}%) | [{rew_str}]")

        # Phần tử thứ N+1 của baseFeePerGas
        next_base_fee = base_fees[-1]
        print("-" * 80)
        print(f"[*] Base fee dự kiến cho block tiếp theo (#{oldest_block + len(gas_ratios)}): {next_base_fee} wei")

        # 4. Đánh giá chuỗi bận/rảnh
        avg_ratio = total_ratio / len(gas_ratios) if gas_ratios else 0
        print("\n" + "=" * 75)
        print("--- 4. KẾT LUẬN TÌNH TRẠNG MẠNG (CHECK = OK) ---")
        print(f"Tỷ lệ sử dụng gas trung bình: {avg_ratio * 100:.2f}% (Target EIP-1559 là 50.00%)")
        if avg_ratio < 0.5:
            print("[CHECK = OK] Chuỗi đang RẢNH (Gas used << 50% target).")
            print("-> Cơ chế EIP-1559: Khi gas used < 50% target, base fee tự động giảm tối đa 12.5% mỗi block.")
            print("-> Vì lượng giao dịch ít, base fee liên tục giảm về mức sàn (vài wei) và giữ nguyên ở đáy.")
        else:
            print("[CHECK = OK] Chuỗi đang BẬN (Gas used > 50% target). Base fee đang có xu hướng tăng.")
    except Exception as e:
        print(f"Lỗi khi gọi eth_feeHistory: {e}")
    print("=" * 75)

if __name__ == "__main__":
    main()
