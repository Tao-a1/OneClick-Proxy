import os
import random
import string
import shutil
import subprocess
import socket
import json
import urllib.request

def generate_id(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def run_shell(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, result.stdout.decode()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode()

def get_public_ip():
    try:
        # Try to get public IP via external service
        return urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
    except:
        # Fallback to local hostname resolution (might be private IP)
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "127.0.0.1"

def get_country_name():
    try:
        url = "http://ip-api.com/json?lang=zh-CN"
        response = urllib.request.urlopen(url, timeout=5).read().decode('utf-8')
        data = json.loads(response)
        if data.get('status') == 'success':
            return data.get('country', '')
        return ""
    except Exception as e:
        print(f"Warning: Could not fetch country info: {e}")
        return ""

def update_manifest_with_country(country_name):
    if not country_name:
        return

    manifest_path = "extension/manifest.json"
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Set extension name strictly to country name
        new_name = country_name
        data['name'] = new_name
        
        print(f"Updated Extension Name to: {new_name}")
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Failed to update manifest: {e}")

def main():
    print(">>> Starting Auto Deployment (Self-Signed Mode)...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    # Config
    port = "8083"
    username = "User_" + generate_id(6)
    password = "Pwd_" + generate_id(16)
    
    # Get IP for extension config
    server_ip = get_public_ip()
    print(f"Detected Server IP: {server_ip}")

    # SSL Certs (Self-Signed)
    cert_dir = os.path.join(base_dir, "server", "certs")
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
        
    key_path = os.path.join(cert_dir, "privkey.pem")
    cert_path = os.path.join(cert_dir, "fullchain.pem")
    
    print("Generating Self-Signed Certificate...")
    # OpenSSL command to generate self-signed cert
    openssl_cmd = (
        f'openssl req -x509 -newkey rsa:4096 -keyout "{key_path}" -out "{cert_path}" '
        f'-days 365 -nodes -subj "/CN={server_ip}"'
    )
    
    success, output = run_shell(openssl_cmd)
    if not success:
        print(f"Error generating SSL cert: {output}")
        return

    # 1. Configure Server (proxy.js)
    print("Configuring Server...")
    with open('server/proxy.js.template', 'r') as f:
        server_tpl = f.read()
    
    server_content = server_tpl.replace('{PORT}', port)\
                               .replace('{USERNAME}', username)\
                               .replace('{PASSWORD}', password)\
                               .replace('{KEY_PATH}', key_path)\
                               .replace('{CERT_PATH}', cert_path)
                               
    with open('server/proxy.js', 'w') as f:
        f.write(server_content)
        
    # 2. Configure Extension (background.js)
    print("Configuring Extension...")
    with open('extension/background.js.template', 'r') as f:
        ext_tpl = f.read()
        
    ext_content = ext_tpl.replace('{DOMAIN}', server_ip)\
                         .replace('{PORT}', port)\
                         .replace('{USERNAME}', username)\
                         .replace('{PASSWORD}', password)
                         
    with open('extension/background.js', 'w') as f:
        f.write(ext_content)

    # 3. Add Country Tag
    print("Detecting Server Location...")
    country = get_country_name()
    if country:
        print(f"Location detected: {country}")
        update_manifest_with_country(country)
    else:
        print("Location detection failed or skipped.")
        
    # 4. Package Extension
    print("Packaging Extension...")
    if not os.path.exists('release'):
        os.makedirs('release')
        
    shutil.make_archive('release/OneClick_Client', 'zip', 'extension')
    
    # 5. Save Info

    with open('DEPLOY_INFO.txt', 'w') as f:
        f.write(f"Server IP: {server_ip}\n")
        f.write(f"Port: {port}\n")
        f.write(f"Username: {username}\n")
        f.write(f"Password: {password}\n")
        f.write(f"Cert Path: {cert_path}\n")
        
    print("\n=== Deployment Successful ===")
    print(f"Credentials saved to {os.path.join(base_dir, 'DEPLOY_INFO.txt')}")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Extension ZIP: {os.path.join(base_dir, 'release/OneClick_Client.zip')}")
    print("\nStarting Server now...")
    
    # Start server in background using nohup
    # We use start.sh logic but directly
    
    # Ensure start.sh is executable
    os.chmod('server/start.sh', 0o755)

if __name__ == "__main__":
    main()
