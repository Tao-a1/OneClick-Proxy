import os
import random
import string
import shutil
import sys
import subprocess
import time

# Hardcoded values
DOMAIN = "us.lytide.asia"
PORT = "8083"
EMAIL = "admin@lytide.asia"
AUTO_SSL = True

def generate_id(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def run_shell(command):
    try:
        print(f"Executing: {command}")
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, result.stdout.decode()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode()

def run_certbot(domain, email):
    print(f"\n>>> Running Certbot for {domain}...")
    
    cmd = f"certbot certonly --standalone --non-interactive --agree-tos --no-eff-email -m {email} -d {domain}"
    success, output = run_shell(cmd)
    
    if success:
        print(">>> Certificate generated successfully!")
        return True
    else:
        print(">>> Error generating certificate:")
        print(output)
        return False

def main():
    print("==========================================")
    print("   OneClick Secure Proxy - Auto Deploy    ")
    print("==========================================")
    
    # Change working directory to script location to ensure relative paths work
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # 2. SSL Setup
    key_path = ""
    cert_path = ""
    
    if AUTO_SSL:
        if run_certbot(DOMAIN, EMAIL):
            key_path = f"/etc/letsencrypt/live/{DOMAIN}/privkey.pem"
            cert_path = f"/etc/letsencrypt/live/{DOMAIN}/fullchain.pem"
        else:
            print("\nAuto-SSL failed. Exiting.")
            sys.exit(1)
            
    # Check if certs exist
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
    
    server_content = (server_tpl.replace('{PORT}', PORT)
                                .replace('{USERNAME}', username)
                                .replace('{PASSWORD}', password)
                                .replace('{KEY_PATH}', key_path)
                                .replace('{CERT_PATH}', cert_path))
                               
    with open('server/proxy.js', 'w') as f:
        f.write(server_content)
        
    # 4. Process Extension Config
    print("Configuring Extension...")
    with open('extension/background.js.template', 'r') as f:
        ext_tpl = f.read()
        
    ext_content = (ext_tpl.replace('{DOMAIN}', DOMAIN)
                          .replace('{PORT}', PORT)
                          .replace('{USERNAME}', username)
                          .replace('{PASSWORD}', password))
                         
    with open('extension/background.js', 'w') as f:
        f.write(ext_content)
        
    # 5. Package Extension
    print("Packaging Extension...")
    if not os.path.exists('release'):
        os.makedirs('release')
        
    shutil.make_archive('release/OneClick_Client', 'zip', 'extension')
    print("Extension packaged: release/OneClick_Client.zip")
    
    # 6. Start Server (We will do this separately via shell to ensure it runs in background properly)
    print("\nSetup Complete!")

if __name__ == "__main__":
    main()
