import os
import shutil
import subprocess
import time
import json
import urllib.request
import sys

def run_shell(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, result.stdout.decode()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode()

def get_input(prompt):
    return input(prompt).strip()

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
    print(">>> Starting OneClick Proxy Deployment (Domain Mode)")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    # 0. Get Domain
    if len(sys.argv) > 1:
        domain = sys.argv[1]
    else:
        domain = get_input("Enter your Domain Name (e.g., vpn.mysite.com): ")
    
    if not domain:
        print("Error: Domain is required.")
        return

    print(f"Deploying for Domain: {domain}")

    # 1. Stop existing server
    print("Stopping existing server...")
    if os.path.exists("server/proxy.pid"):
        try:
            with open("server/proxy.pid", "r") as f:
                pid = f.read().strip()
            run_shell(f"kill {pid}")
            print(f"Stopped PID {pid}")
        except:
            pass
        os.remove("server/proxy.pid")
    
    # 2. Prepare Certs
    print("Checking SSL Certificates...")
    # Assume Let's Encrypt standard path
    src_cert_dir = f"/etc/letsencrypt/live/{domain}"
    dst_cert_dir = os.path.join(base_dir, "server", "certs")
    
    if not os.path.exists(src_cert_dir):
        print(f"Error: Certificate not found at {src_cert_dir}")
        print("Please ensure you have generated a certificate using Certbot first.")
        print(f"Command: certbot certonly --standalone -d {domain}")
        return

    if not os.path.exists(dst_cert_dir):
        os.makedirs(dst_cert_dir)
        
    shutil.copy(os.path.join(src_cert_dir, "privkey.pem"), os.path.join(dst_cert_dir, "privkey.pem"))
    shutil.copy(os.path.join(src_cert_dir, "fullchain.pem"), os.path.join(dst_cert_dir, "fullchain.pem"))
    
    key_path = os.path.join(dst_cert_dir, "privkey.pem")
    cert_path = os.path.join(dst_cert_dir, "fullchain.pem")

    # 3. Credentials
    # Check for existing to preserve, else generate new
    username = "User_" + str(int(time.time()))[-6:]
    password = "Pwd_" + str(int(time.time()))
    
    if os.path.exists("DEPLOY_INFO.txt"):
        with open("DEPLOY_INFO.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                if "Username:" in line:
                    username = line.split(":")[1].strip()
                if "Password:" in line:
                    password = line.split(":")[1].strip()
    
    print(f"Using Credentials: {username} / {password}")

    # 4. Configure Server (proxy.js)
    print("Configuring Server...")
    port = "8083"
    with open('server/proxy.js.template', 'r') as f:
        server_tpl = f.read()
    
    server_content = server_tpl.replace('{PORT}', port)\
                               .replace('{USERNAME}', username)\
                               .replace('{PASSWORD}', password)\
                               .replace('{KEY_PATH}', key_path)\
                               .replace('{CERT_PATH}', cert_path)
                               
    with open('server/proxy.js', 'w') as f:
        f.write(server_content)
        
    # 5. Configure Extension (background.js)
    print("Configuring Extension...")
    with open('extension/background.js.template', 'r') as f:
        ext_tpl = f.read()
    
    ext_content = ext_tpl.replace('{DOMAIN}', domain)\
                         .replace('{PORT}', port)\
                         .replace('{USERNAME}', username)\
                         .replace('{PASSWORD}', password)
                         
    with open('extension/background.js', 'w') as f:
        f.write(ext_content)

    # 6. Add Country Tag
    print("Detecting Server Location...")
    country = get_country_name()
    if country:
        print(f"Location detected: {country}")
        update_manifest_with_country(country)
    else:
        print("Location detection failed or skipped.")
        
    # 7. Package Extension
    print("Packaging Extension...")
    if os.path.exists('release/OneClick_Client.zip'):
        os.remove('release/OneClick_Client.zip')
        
    if not os.path.exists('release'):
        os.makedirs('release')

    shutil.make_archive('release/OneClick_Client', 'zip', 'extension')
    
    # 8. Start Server
    print("Starting Server...")
    os.chmod('server/start.sh', 0o755)
    run_shell("cd server && ./start.sh")
    
    # 9. Update Info
    with open('DEPLOY_INFO.txt', 'w') as f:
        f.write(f"Domain: {domain}\n")
        f.write(f"Port: {port}\n")
        f.write(f"Username: {username}\n")
        f.write(f"Password: {password}\n")
        
    print("\n=== Domain Deployment Successful ===")
    print(f"Extension packaged: {os.path.join(base_dir, 'release/OneClick_Client.zip')}")

if __name__ == "__main__":
    main()
