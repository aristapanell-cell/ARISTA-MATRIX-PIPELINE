import os
import hashlib
import requests
import time
import json
from datetime import datetime

BOT_TOKEN = "7620426804:AAFK-ftNMhNBY9fN7eO-M38CJApH899-kTo"
CHANNEL_ID = -1002325683219

class ConfigCombiner:
    def __init__(self):
        self.categories = [
            'vmess', 'vless', 'trojan', 'ss',
            'hysteria2', 'hysteria', 'tuic', 
            'wireguard', 'other'
        ]
        
        self.protocol_names_fa = {
            'vmess': 'VMess',
            'vless': 'VLess',
            'trojan': 'Trojan',
            'ss': 'Shadowsocks',
            'hysteria2': 'Hysteria2',
            'hysteria': 'Hysteria',
            'tuic': 'TUIC',
            'wireguard': 'WireGuard',
            'other': 'سایر پروتکل‌ها'
        }
    
    def send_to_telegram(self, file_path, caption):
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
            with open(file_path, 'rb') as file:
                files = {'document': file}
                data = {
                    'chat_id': CHANNEL_ID,
                    'caption': caption,
                    'parse_mode': 'HTML'
                }
                response = requests.post(url, files=files, data=data, timeout=30)
                if response.status_code == 200:
                    print(f"  ✅ ارسال شد: {os.path.basename(file_path)}")
                else:
                    print(f"  ❌ خطا در ارسال {os.path.basename(file_path)}: {response.text}")
                time.sleep(2)
        except Exception as e:
            print(f"  ❌ خطا در ارسال به تلگرام: {e}")
    
    def create_persian_caption(self, category, count, source_type):
        protocol_name = self.protocol_names_fa.get(category, category.upper())
        source_persian = "تلگرام" if source_type == "telegram" else "گیت‌هاب"
        
        caption = f"""
🔰 <b>کانفیگ‌های {protocol_name}</b>

📊 تعداد: {count} عدد
📡 منبع: {source_persian}
👈 قابل استفاده در کلاینت‌های <b>V2rayNG</b> • <b>Hiddify</b> • <b>NekoBox</b> • <b>Nnpsternet</b>

➖➖➖➖➖➖➖➖
<blockquote>@aristapanel</blockquote>
➖➖➖➖➖➖➖➖

#arista #{category} #V2rayNG #Hiddify #NekoBox #Nnpsternet
"""
        return caption
    
    def read_configs(self, filepath):
        if not os.path.exists(filepath):
            return []
        
        configs = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    configs.append(line)
        
        return configs
    
    def deduplicate(self, configs):
        unique_configs = []
        seen_hashes = set()
        
        for config in configs:
            config_hash = hashlib.md5(config.encode()).hexdigest()
            if config_hash not in seen_hashes:
                seen_hashes.add(config_hash)
                unique_configs.append(config)
        
        return unique_configs
    
    def post_telegram_files(self):
        os.makedirs('configs/telegram', exist_ok=True)
        
        print("\n" + "=" * 60)
        print("📤 ارسال فایل‌های تلگرام به کانال")
        print("=" * 60)
        
        for category in self.categories:
            telegram_configs = self.read_configs(f'configs/telegram/{category}.txt')
            
            if telegram_configs:
                unique_configs = self.deduplicate(telegram_configs)
                filename = f"configs/telegram/{category}.txt"
                caption = self.create_persian_caption(category, len(unique_configs), "telegram")
                self.send_to_telegram(filename, caption)
                time.sleep(1)
    
    def post_github_files(self):
        print("\n" + "=" * 60)
        print("📤 ارسال فایل‌های گیت‌هاب به کانال")
        print("=" * 60)
        
        for category in self.categories:
            github_configs = self.read_configs(f'configs/github/{category}.txt')
            
            if github_configs:
                unique_configs = self.deduplicate(github_configs)
                filename = f"configs/github/{category}.txt"
                caption = self.create_persian_caption(category, len(unique_configs), "github")
                self.send_to_telegram(filename, caption)
                time.sleep(1)
    
    def create_combined_files(self):
        os.makedirs('configs/combined', exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        all_combined = []
        
        for category in self.categories:
            telegram_configs = self.read_configs(f'configs/telegram/{category}.txt')
            github_configs = self.read_configs(f'configs/github/{category}.txt')
            combined_configs = telegram_configs + github_configs
            unique_configs = self.deduplicate(combined_configs)
            
            if unique_configs:
                filename = f"configs/combined/{category}.txt"
                content = f"# Combined {category.upper()} Configurations\n"
                content += f"# Updated: {timestamp}\n"
                content += f"# Count: {len(unique_configs)}\n"
                content += f"# Sources: Telegram ({len(telegram_configs)}) + GitHub ({len(github_configs)})\n\n"
                content += "\n".join(unique_configs)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                all_combined.extend(unique_configs)
        
        if all_combined:
            filename = "configs/combined/all.txt"
            content = f"# All Combined Configurations\n"
            content += f"# Updated: {timestamp}\n"
            content += f"# Total Count: {len(all_combined)}\n"
            content += "# Sources: Telegram + GitHub\n\n"
            content += "\n".join(all_combined)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def combine_and_post(self):
        print("\n" + "=" * 60)
        print("🔄 شروع فرآیند ترکیب و ارسال کانفیگ‌ها")
        print("=" * 60)
        
        self.create_combined_files()
        self.post_telegram_files()
        self.post_github_files()
        
        total_telegram = len(self.read_configs('configs/telegram/all.txt'))
        total_github = len(self.read_configs('configs/github/all.txt'))
        total_combined = len(self.read_configs('configs/combined/all.txt'))
        
        print("\n" + "=" * 60)
        print("✅ گزارش نهایی")
        print("=" * 60)
        print(f"📊 کانفیگ‌های تلگرام: {total_telegram}")
        print(f"📊 کانفیگ‌های گیت‌هاب: {total_github}")
        print(f"📊 کانفیگ‌های ترکیبی یکتا: {total_combined}")
        print("=" * 60)

def main():
    combiner = ConfigCombiner()
    combiner.combine_and_post()

if __name__ == "__main__":
    main()
