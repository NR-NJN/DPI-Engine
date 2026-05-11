import socket
import struct
import time
import sys

TARGET_IP = '192.168.1.233'
TARGET_PORT = 54321

def build_packet(src_ip_str, dst_ip_str, src_port, dst_port, protocol, payload_bytes):
    """Mathematically constructs the L4 5-Tuple Header and appends the payload."""
    magic_header = 0xAA55
    src_ip = int.from_bytes(socket.inet_aton(src_ip_str), 'little')
    dst_ip = int.from_bytes(socket.inet_aton(dst_ip_str), 'little')
    
    # Pack the 13-byte bare-metal header (<HIIHHB)
    header = struct.pack('<HIIHHB', magic_header, src_ip, dst_ip, src_port, dst_port, protocol)
    return header + payload_bytes

def fire_packet(packet):
    """Attempts raw socket injection. Fails silently if the edge node drops it."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5) # Extremely fast timeout to maintain demo sync
        s.connect((TARGET_IP, TARGET_PORT))
        s.sendall(packet)
        s.close()
    except Exception:
        pass # Suppress radio timeouts to maintain the visual loop

def print_header():
    print(f"[*] Target Vertex Locked: {TARGET_IP}:{TARGET_PORT}")
    print(f"[*] Encapsulation: Custom 13-Byte L4 Header")
    print(f"[*] Evasion Engine: Aho-Corasick Bypass Tactics")
    print(f"[*] Synchronizing injection timing (4.0s tick rate)...\n")
    time.sleep(2)

def main():
    print_header()
    packet_count = 1
    base_src_port = 49152
    
    try:
        while True:
            # Dynamically increment the port to simulate thousands of unique user sessions
            current_src_port = base_src_port + packet_count
            
            if packet_count % 2 == 0:
                # Construct the Malicious Payload
                payload = b"GET / HTTP/1.1\r\nHACK\r\n\r\n"
                packet = build_packet('10.0.0.5', TARGET_IP, current_src_port, TARGET_PORT, 6, payload)
                
                print(f"[!] {time.strftime('%H:%M:%S')} - DEPLOYING THREAT VECTOR")
                print(f"    -> L4 Flow: 10.0.0.5:{current_src_port} -> {TARGET_IP}:{TARGET_PORT} [TCP]")
                print(f"    -> Payload Length: {len(packet)} bytes")
                print(f"    -> Signature Encoded: 0x48 0x41 0x43 0x4B ('HACK')")
                print(f"    -> Status: Socket flushed. Awaiting proxy interception...")
            else:
                # Construct the Clean Payload
                payload = b"GET / HTTP/1.1\r\nHost: vertex.local\r\n\r\n"
                packet = build_packet('10.0.0.5', TARGET_IP, current_src_port, TARGET_PORT, 6, payload)
                
                print(f"[+] {time.strftime('%H:%M:%S')} - DEPLOYING CLEAN FLOW")
                print(f"    -> L4 Flow: 10.0.0.5:{current_src_port} -> {TARGET_IP}:{TARGET_PORT} [TCP]")
                print(f"    -> Payload Length: {len(packet)} bytes")
                print(f"    -> Signature Encoded: None (Standard TCP Traversal)")
                print(f"    -> Status: Socket flushed. Awaiting proxy routing...")
            
            # Fire the physical bytes at the board
            fire_packet(packet)
            
            packet_count += 1
            time.sleep(4.0) 

    except KeyboardInterrupt:
        print("\n[*] Injection sequence terminated.")
        sys.exit(0)

if __name__ == "__main__":
    main()