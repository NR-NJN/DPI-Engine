import socket
import struct
import time
TARGET_IP = '192.168.1.233'
TARGET_PORT = 54321

# 1. Define the simulated L3/L4 Flow (The 5-Tuple)
# We convert standard IP strings into 32-bit integers
# 1. Define the simulated L3/L4 Flow
src_ip = int.from_bytes(socket.inet_aton('10.0.0.5'), 'little')
dst_ip = int.from_bytes(socket.inet_aton(TARGET_IP), 'little')
src_port = 49152
dst_port = TARGET_PORT
protocol = 6 

# NEW: Magic bytes to identify the start of the tuple
magic_header = 0xAA55 

# 2. Pack the header (added 'H' for the magic bytes)
header = struct.pack('<HIIHHB', magic_header, src_ip, dst_ip, src_port, dst_port, protocol)

# 3. Append the actual Application Layer payload
payload = b"Hello ThreatProxy, this is a clean flow."
packet = header + payload

print(f"[*] Firing encapsulated 5-tuple at {TARGET_IP}:{TARGET_PORT}...")

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(15.0)
    s.connect((TARGET_IP, TARGET_PORT))
    s.sendall(packet)
    print(f"[+] 5-Tuple successfully injected ({len(packet)} bytes).")
    
    # CRITICAL FIX: Keep the TCP socket open for 2 seconds 
    # so the slow radio hardware has time to push the data over SPI.
    time.sleep(2) 
    
    s.close()   
except Exception as e:
    print(f"[!] Injection failed: {e}")