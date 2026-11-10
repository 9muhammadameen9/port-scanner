import socket
import re
from common_ports import ports_and_services

def get_open_ports(target, port_range, verbose=False):
    open_ports = []
    
    # --- 1. Resolve Target (IP or Hostname) ---
    is_ip = False
    ip = None
    hostname = None
    
    # Check if the target is a valid IP address
    try:
        ip = socket.gethostbyname(target)
        # If the target was already an IP, gethostbyname returns it.
        # We try to get the hostname to see if it's a URL.
        try:
            hostname = socket.gethostbyaddr(target)[0]
        except socket.herror:
            # No hostname found, it's just an IP.
            is_ip = True
    except socket.gaierror:
        # If gethostbyname fails, it's an invalid hostname or IP.
        # We check if it looks like an IP to give the right error.
        if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", target):
            return "Error: Invalid IP address"
        else:
            return "Error: Invalid hostname"

    # --- 2. Scan Ports ---
    for port in range(port_range[0], port_range[1] + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)  # Don't hang forever on closed ports
        result = s.connect_ex((ip, port))
        if result == 0:
            open_ports.append(port)
        s.close()

    # --- 3. Return Result (Verbose or List) ---
    if not verbose:
        return open_ports
    else:
        # Build the verbose string
        # If the hostname is the same as the IP, we don't show the parentheses
        if hostname and hostname != ip and not is_ip:
            output = f"Open ports for {hostname} ({ip})\nPORT     SERVICE"
        else:
            output = f"Open ports for {target}\nPORT     SERVICE"

        for port in open_ports:
            service = ports_and_services.get(port, "unknown")
            # Formatting: Port left-justified in 9 spaces, then service
            output += f"\n{str(port).ljust(9)}{service}"
        
        return output