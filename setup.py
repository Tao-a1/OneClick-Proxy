import os
import random
import string
import shutil
import sys
import subprocess
import time

def get_input(prompt, default=None):
    if default:
        user_input = input(f"{prompt} [{default}]: ")
        return user_input.strip() if user_input.strip() else default
    else:
        while True:
            user_input = input(f"{prompt}: ")
            if user_input.strip():
                return user_input.strip()

def generate_id(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def run_shell(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, result.stdout.decode()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode()

def run_certbot(domain, email):
    print(f"\n>>> Running Certbot for {domain}...")
    print("    (This requires Port 80 to be open and free)")
    
    # Check if port 80 is busy
    # Simple check using lsof or netstat is hard across distros, so we just try certbot
    
    cmd = f"certbot certonly --standalone --non-interactive --agree-tos --no-eff-email -m {email} -d {domain}"
    success, output = run_shell(cmd)
    
    if success:
        print(">>> Certificate generated successfully!")
        return True
    else:
        print(">>> Error generating certificate:")
        print(output)
        print("Possible reasons:")
        print("1. Domain does not point to this server's IP.")
        print("2. Port 80 is blocked by firewall or used by another app (Nginx/Apache).")
        return False

def main():
    print("==========================================")
    print("   OneClick Secure Proxy - Setup v2.0     ")
    print("==========================================")
    
    # 1. Gather Info
    domain = get_input("Enter your Domain Name (e.g., vpn.mysite.com)")
    port = get_input("Enter Proxy Port", "8083")
    
    # 2. SSL Setup
    key_path = ""
    cert_path = ""
    
    print("\n[SSL Configuration]")
    auto_ssl = get_input("Do you want to automatically generate a free SSL certificate now? (y/n)", "y")
    
    if auto_ssl.lower() == 'y':
        email = get_input("Enter your email for Certbot registration")
        
        # Verify Certbot is installed
        chk, _ = run_shell("which certbot")
        if not chk:
            print("Error: 'certbot' is not found. Please run 'server/install_env.sh' first.")
            return

        if run_certbot(domain, email):
            key_path = f"/etc/letsencrypt/live/{domain}/privkey.pem"
            cert_path = f"/etc/letsencrypt/live/{domain}/fullchain.pem"
        else:
            print("\nAuto-SSL failed. Switching to manual mode.")
            auto_ssl = 'n'
            
    if auto_ssl.lower() != 'y':
        key_path = get_input("Path to Private Key (privkey.pem)", f"/etc/letsencrypt/live/{domain}/privkey.pem")
        cert_path = get_input("Path to Certificate (fullchain.pem)", f"/etc/letsencrypt/live/{domain}/fullchain.pem")
        
    # Check if certs exist (Warning only)
    if not os.path.exists(key_path):
        print(f"Warning: Key file not found at {key_path}")
    if not os.path.exists(cert_path):
        print(f"Warning: Cert file not found at {cert_path}")
        
    # Generate Credentials
    username = "User_" + generate_id(6)
    password = "Pwd_" + generate_id(16)
    print(f"\nGenerated Credentials:\n  Username: {username}\n  Password: {password}")
    
    # 3. Process Server Config
    print("\nConfiguring Server...")
    with open('server/proxy.js.template', 'r') as f:
        server_tpl = f.read()
    
    server_content = server_tpl.replace('{PORT}', port)\
                               .replace('{USERNAME}', username)\
                               .replace('{PASSWORD}', password)\
                               .replace('{KEY_PATH}', key_path)\
                               .replace('{CERT_PATH}', cert_path)
                               
    with open('server/proxy.js', 'w') as f:
        f.write(server_content)
        
    # 4. Process Extension Config
    print("Configuring Extension...")
    with open('extension/background.js.template', 'r') as f:
        ext_tpl = f.read()
        
    ext_content = ext_tpl.replace('{DOMAIN}', domain)\
                         .replace('{PORT}', port)\
                         .replace('{USERNAME}', username)\
                         .replace('{PASSWORD}', password)
                         
    with open('extension/background.js', 'w') as f:
        f.write(ext_content)
        
    # 5. Package Extension
    print("Packaging Extension...")
    if not os.path.exists('release'):
        os.makedirs('release')
        
    shutil.make_archive('release/OneClick_Client', 'zip', 'extension')
    print("Extension packaged: release/OneClick_Client.zip")
    
    # 6. Start Server
    print("\nSetup Complete!")
    print("To start the server, run:")
    print("  cd server")
    print("  ./start.sh")
    print("\nDownload 'release/OneClick_Client.zip' to your client machine and load it into Chrome.")

if __name__ == "__main__":
    main()
