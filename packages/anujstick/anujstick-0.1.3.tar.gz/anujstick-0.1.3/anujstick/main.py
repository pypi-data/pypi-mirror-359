import argparse
from anujstick.core import network_attacks, web_exploits, brute_force

def main():
    parser = argparse.ArgumentParser(description=" AnujStrike - Offensive Strike Toolkit ")
    parser.add_argument('--attack', choices=['arp_spoof', 'syn_flood', 'sql_injection', 'brute_force'], required=True, help="Choose attack module")
    parser.add_argument('--target', help="Target IP or URL")
    parser.add_argument('--interface', help="Network Interface (for network attacks)")
    parser.add_argument('--threads', type=int, default=10, help="Number of threads (optional)")

    args = parser.parse_args()

    if args.attack == 'arp_spoof':
        network_attacks.arp_spoof(args.target, args.interface)
    elif args.attack == 'syn_flood':
        network_attacks.syn_flood(args.target)
    elif args.attack == 'sql_injection':
        web_exploits.sql_injection_test(args.target)
    elif args.attack == 'brute_force':
        brute_force.start_brute_force(args.target)

if __name__ == "__main__":
    main()
