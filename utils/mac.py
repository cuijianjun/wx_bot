import uuid

def get_mac_address():
    mac = uuid.getnode()
    mac_address = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
    return mac_address

if __name__ == "__main__":
    print("MAC Address:", get_mac_address())
import psutil

def get_mac_address_psutil():
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                return addr.address
    return None

if __name__ == "__main__":
    print("MAC Address:", get_mac_address_psutil())