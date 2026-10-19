"""
Bài về nhà 1 - So sánh chuỗi base fee: TrustKeys L1 vs Sepolia Testnet
"""

import sys
from web3 import Web3

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

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

def fetch_network_fee(name, rpc_url, is_poa=False, count=10):
    print(f"\n[*] Đang kết nối mạng {name} ({rpc_url}) ...")
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 10}))
        if not w3.is_connected():
            print(f"[-] Không thể kết nối tới {name}")
            return None
        if is_poa and poa_middleware:
            w3.middleware_onion.inject(poa_middleware, layer=0)

        chain_id = w3.eth.chain_id
        latest_block = w3.eth.block_number
        fh = w3.eth.fee_history(count, "latest", [50])
        
        base_fees = fh["baseFeePerGas"][:-1]
        gas_ratios = fh["gasUsedRatio"]
        avg_base_fee = sum(base_fees) / len(base_fees) if base_fees else 0
        avg_ratio = sum(gas_ratios) / len(gas_ratios) if gas_ratios else 0
        
        return {
            "name": name,
            "chain_id": chain_id,
            "latest_block": latest_block,
            "base_fees": base_fees,
            "gas_ratios": gas_ratios,
            "avg_base_fee": avg_base_fee,
            "avg_ratio": avg_ratio
        }
    except Exception as e:
        print(f"[-] Lỗi khi truy vấn {name}: {e}")
        return None

def main():
    print("=" * 80)
    print("      SO SÁNH LỊCH SỬ BASE FEE VÀ GAS DÙNG: TRUSTKEYS L1 VS SEPOLIA")
    print("=" * 80)
    
    trustkeys_info = fetch_network_fee(
        "TrustKeys L1 Testnet", 
        "https://l1testnet.trustkeys.network", 
        is_poa=True, 
        count=10
    )
    
    sepolia_info = fetch_network_fee(
        "Sepolia Testnet", 
        "https://ethereum-sepolia-rpc.publicnode.com", 
        is_poa=False, 
        count=10
    )
    
    print("\n" + "=" * 80)
    print(f"{'Mạng':<22} | {'Chain ID':<10} | {'Block mới nhất':<16} | {'Avg Base Fee':<20} | {'Avg Gas Ratio'}")
    print("-" * 80)
    
    for info in [trustkeys_info, sepolia_info]:
        if info:
            base_fee_str = f"{info['avg_base_fee']:.1f} wei ({Web3.from_wei(info['avg_base_fee'], 'gwei'):.4f} gwei)"
            ratio_str = f"{info['avg_ratio'] * 100:.2f}%"
            print(f"{info['name']:<22} | {info['chain_id']:<10} | {info['latest_block']:<16} | {base_fee_str:<20} | {ratio_str}")

    print("=" * 80)
    print("\n[PHÂN TÍCH SO SÁNH (Cho bài tập về nhà)]:")
    print("1. Sự khác biệt về Base Fee:")
    print("   - TrustKeys L1: Base fee cực thấp (chỉ ~8 wei, xấp xỉ 0 gwei).")
    print("   - Sepolia: Base fee dao động quanh ~1 gwei (1,000,000,000 wei), cao hơn TrustKeys hàng trăm triệu lần.")
    print("2. Nguyên nhân theo cơ chế EIP-1559:")
    print("   - TrustKeys L1: Lưu lượng giao dịch rất thấp, block gas used ~0-5% (nhỏ hơn nhiều so với mục tiêu target 50%). Do đó base fee liên tục bị giảm tối đa 12.5% mỗi block và chạm mức sàn.")
    print("   - Sepolia: Là testnet công khai chính thức của Ethereum toàn cầu, liên tục có dev test dApp, bot swap/mint NFT, gas used thường xuyên biến động quanh 50%, đẩy base fee duy trì ở mức cao và thay đổi liên tục.")
    print("=" * 80)

if __name__ == "__main__":
    main()
