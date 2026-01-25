import json
import os
import shutil
import urllib.request
import subprocess

def get_country_name():
    try:
        url = "http://ip-api.com/json?lang=zh-CN"
        response = urllib.request.urlopen(url).read().decode('utf-8')
        data = json.loads(response)
        if data.get('status') == 'success':
            return data.get('country', '未知')
        return "未知"
    except Exception as e:
        print(f"Error fetching IP info: {e}")
        return "未知"

def update_manifest(country_name):
    manifest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extension", "manifest.json")
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Set name strictly to country name
    new_name = country_name
    data['name'] = new_name
    
    print(f"Updating Extension Name to: {new_name}")
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def package_extension():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    
    if os.path.exists('release/OneClick_Client.zip'):
        os.remove('release/OneClick_Client.zip')
        
    print("Packaging extension...")
    shutil.make_archive('release/OneClick_Client', 'zip', 'extension')
    
    # Copy to downloads with a clear name if downloads dir exists
    dest_path = "/gemini/downloads/OneClick_Client_With_Country.zip"
    if os.path.exists("/gemini/downloads"):
        shutil.copy('release/OneClick_Client.zip', dest_path)
        print(f"Packaged to: {dest_path}")
    else:
        print(f"Packaged to: {os.path.join(base_dir, 'release/OneClick_Client.zip')}")

def main():
    print(">>> Fetching Server Location...")
    country = get_country_name()
    print(f"Detected Country: {country}")
    
    update_manifest(country)
    package_extension()

if __name__ == "__main__":
    main()
