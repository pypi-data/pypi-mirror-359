import os
import re
import sys
import pyotp

import argparse
import shlex

from pathlib import Path

def parse_ssh_config():
    def search(pattern, text):
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        return None
    
    cfg = Path("~/.ssh/config").expanduser().read_text()
    hosts = {}
    matches = list(re.finditer(r"Host\s+(.*)", cfg))
    for i, match in enumerate(matches):
        host = match.group(1)
        host_info = cfg[match.end() + 1:matches[i+1].start() - 1 if i+1 < len(matches) else None]
        password = search(r"#Password\s+(.*)", host_info)
        totp = search(r"#TOTP\s+(.*)", host_info)

        hosts[host] = {
            "password": password,
            "totp": totp
        }
    
    return hosts

def main():
    ssh_cfg = parse_ssh_config()
    if len(sys.argv) == 1:
        SSH_ORIG_ARGS = shlex.split(os.environ["SSH_ORIG_ARGS"])
        parser = argparse.ArgumentParser()
        parser.add_argument('host', nargs='?')
        host = parser.parse_known_args(SSH_ORIG_ARGS)[0].host
        
        if host in ssh_cfg:
            if "password" in ssh_cfg[host]:
                print(ssh_cfg[host]["password"])
            if "totp" in ssh_cfg[host]:
                print(pyotp.TOTP(ssh_cfg[host]["totp"]).now())
                
        return 0
    else:
        host = sys.argv[1]
        if host in ssh_cfg:
            print("force", end="")
        else:
            print("never", end="")

if __name__ == "__main__":
    main()