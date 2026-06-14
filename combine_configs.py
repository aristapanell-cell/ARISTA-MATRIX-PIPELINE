import os
import hashlib
import requests
import time
import json
import base64
import uuid
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs

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
        
        self.setup_webhook()
    
    def setup_webhook(self):
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
            requests.get(url)
            time.sleep(1)
            
            webhook_url = "https://your-domain.com/webhook"  
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
            data = {'url': webhook_url}
            requests.post(url, data=data)
        except:
            pass
    
    def send_message(self, chat_id, text, reply_markup=None):
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            if reply_markup:
                data['reply_markup'] = json.dumps(reply_markup)
            
            response = requests.post(url, data=data, timeout=30)
            return response.json()
        except Exception as e:
            print(f"خطا در ارسال پیام: {e}")
            return None
    
    def answer_callback(self, callback_id, text):
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
            data = {
                'callback_query_id': callback_id,
                'text': text,
                'show_alert': False
            }
            requests.post(url, data=data, timeout=30)
        except:
            pass
    
    def edit_message(self, chat_id, message_id, text, reply_markup=None):
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
            data = {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            if reply_markup:
                data['reply_markup'] = json.dumps(reply_markup)
            
            requests.post(url, data=data, timeout=30)
        except:
            pass
    
    def handle_webhook(self, update):
        try:
            if 'callback_query' in update:
                self.handle_callback(update['callback_query'])
            elif 'message' in update:
                self.handle_message(update['message'])
        except Exception as e:
            print(f"خطا در پردازش webhook: {e}")
    
    def handle_message(self, message):
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        if text == '/start':
            self.show_os_selection(chat_id)
        elif text == '/clients':
            self.show_os_selection(chat_id)
    
    def show_os_selection(self, chat_id):
        text = "🔹 <b>لطفاً سیستم عامل خود را انتخاب کنید:</b>\n\nبرای دریافت لینک دانلود کلاینت‌های مناسب، روی گزینه مورد نظر کلیک کنید."
        
        keyboard = []
        row = []
        os_list = [
            {'id': 'windows', 'name': 'ویندوز', 'emoji': '🪟'},
            {'id': 'android', 'name': 'اندروید', 'emoji': '📱'},
            {'id': 'ios', 'name': 'iOS', 'emoji': '📱'},
            {'id': 'linux', 'name': 'لینوکس', 'emoji': '🐧'},
            {'id': 'macos', 'name': 'مک', 'emoji': '🍎'},
            {'id': 'router', 'name': 'روتر', 'emoji': '📡'}
        ]
        for i, os_item in enumerate(os_list):
            row.append({
                'text': f"{os_item['emoji']} {os_item['name']}",
                'callback_data': f"os_{os_item['id']}"
            })
            if (i + 1) % 2 == 0 or i == len(os_list) - 1:
                keyboard.append(row)
                row = []
        
        reply_markup = {'inline_keyboard': keyboard}
        self.send_message(chat_id, text, reply_markup)
    
    def show_clients(self, chat_id, message_id, os_id):
        os_list = [
            {'id': 'windows', 'name': 'ویندوز', 'emoji': '🪟'},
            {'id': 'android', 'name': 'اندروید', 'emoji': '📱'},
            {'id': 'ios', 'name': 'iOS', 'emoji': '📱'},
            {'id': 'linux', 'name': 'لینوکس', 'emoji': '🐧'},
            {'id': 'macos', 'name': 'مک', 'emoji': '🍎'},
            {'id': 'router', 'name': 'روتر', 'emoji': '📡'}
        ]
        os_name = next((item['name'] for item in os_list if item['id'] == os_id), os_id)
        os_emoji = next((item['emoji'] for item in os_list if item['id'] == os_id), '📱')
        
        text = f"{os_emoji} <b>{os_name}</b>\n\n🔹 <b>کلاینت‌های موجود:</b>\n\nدر حال حاضر لینکی موجود نیست.\n"
        
        keyboard = []
        keyboard.append([{
            'text': '🔙 بازگشت به انتخاب سیستم عامل',
            'callback_data': 'back_to_os'
        }])
        
        reply_markup = {'inline_keyboard': keyboard}
        
        if message_id:
            self.edit_message(chat_id, message_id, text, reply_markup)
        else:
            self.send_message(chat_id, text, reply_markup)
    
    def handle_callback(self, callback_query):
        callback_id = callback_query['id']
        chat_id = callback_query['message']['chat']['id']
        message_id = callback_query['message']['message_id']
        data = callback_query['data']
        
        if data.startswith('os_'):
            os_id = data.replace('os_', '')
            self.answer_callback(callback_id, f"در حال نمایش کلاینت‌های {os_id}")
            self.show_clients(chat_id, message_id, os_id)
        
        elif data == 'back_to_os':
            self.answer_callback(callback_id, "بازگشت به منوی اصلی")
            self.show_os_selection(chat_id)
            try:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
                data = {'chat_id': chat_id, 'message_id': message_id}
                requests.post(url, data=data)
            except:
                pass
    
    def is_ip(self, hostname):
        ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        return bool(ip_pattern.match(hostname))
    
    def get_original_tag(self, url_str):
        try:
            if '#' in url_str:
                tag = url_str.split('#')[-1].strip()
                if tag and tag != 'ARISTA':
                    return tag
        except:
            pass
        return None
    
    def decode_vmess_config(self, vmess_url):
        try:
            base64_part = vmess_url[8:]
            if len(base64_part) % 4 != 0:
                base64_part += '=' * (4 - len(base64_part) % 4)
            decoded = base64.b64decode(base64_part).decode('utf-8')
            return json.loads(decoded)
        except:
            return None
    
    def decode_ss_config(self, ss_url):
        try:
            result = {'name': None, 'server': None, 'port': None, 'method': None, 'password': None}
            
            if '#' in ss_url:
                result['name'] = ss_url.split('#')[-1].strip()
                ss_url = ss_url.split('#')[0]
            
            ss_without_proto = ss_url[5:]
            
            if '@' in ss_without_proto:
                parts = ss_without_proto.split('@')
                if len(parts) == 2:
                    encoded_part, server_part = parts
                    decoded = base64.b64decode(encoded_part + '=' * (4 - len(encoded_part) % 4)).decode('utf-8')
                    if ':' in decoded:
                        result['method'], result['password'] = decoded.split(':', 1)
                    
                    if ':' in server_part:
                        result['server'], port_str = server_part.split(':', 1)
                        result['port'] = int(port_str)
            else:
                encoded_part = ss_without_proto
                decoded = base64.b64decode(encoded_part + '=' * (4 - len(encoded_part) % 4)).decode('utf-8')
                if '@' in decoded:
                    auth_part, server_part = decoded.split('@', 1)
                    if ':' in auth_part:
                        result['method'], result['password'] = auth_part.split(':', 1)
                    if ':' in server_part:
                        result['server'], port_str = server_part.split(':', 1)
                        result['port'] = int(port_str)
            
            return result if result['server'] and result['port'] and result['method'] and result['password'] else None
        except:
            return None
    
    def vless_to_clash_meta(self, url_str, index):
        try:
            url = url_str.split('#')[0] if '#' in url_str else url_str
            url = url.replace('vless://', 'http://')
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            params = {k: v[0] for k, v in params.items()}
            
            original_name = self.get_original_tag(url_str) or "VLESS"
            config_name = f"{original_name} #{index + 1}"
            
            network_type = params.get('type', 'tcp')
            tls_enabled = params.get('security') in ['tls', 'reality']
            
            final_server = parsed.hostname
            final_sni = params.get('sni') or params.get('host') or parsed.hostname
            
            if self.is_ip(final_server) and (not final_sni or self.is_ip(final_sni)):
                final_sni = params.get('host') or parsed.hostname or 'cloudflare.com'
            
            config = {
                "name": config_name,
                "type": "vless",
                "server": final_server,
                "port": parsed.port or 443,
                "uuid": parsed.username or "",
                "network": network_type,
                "tls": tls_enabled,
                "udp": params.get('udp') != 'false',
                "skip-cert-verify": False,
                "tcp-fast-open": True,
                "servername": final_sni,
                "flow": params.get('flow', ''),
                "client-fingerprint": params.get('fp', 'chrome'),
                "packet-encoding": "xudp"
            }
            
            if params.get('fragment'):
                config["fragment"] = {
                    "enabled": True,
                    "packets": params.get('fragment', '2-4'),
                    "length": params.get('fragment_length', '80-150'),
                    "interval": params.get('fragment_interval', '20-40'),
                    "sleep": int(params.get('fragment_sleep', '20'))
                }
            
            if params.get('alpn'):
                config["alpn"] = [v.strip() for v in params['alpn'].split(',')]
            elif tls_enabled:
                config["alpn"] = ["h2", "http/1.1"]
            
            if network_type == "ws":
                config["ws-opts"] = {
                    "path": params.get('path', '/'),
                    "headers": {
                        "Host": final_sni
                    },
                    "max-early-data": int(params.get('maxEarlyData', '2048')),
                    "early-data-header-name": params.get('earlyDataHeaderName', 'Sec-WebSocket-Protocol')
                }
            
            if network_type == "grpc":
                config["grpc-opts"] = {
                    "grpc-service-name": params.get('serviceName', 'GunService')
                }
            
            if network_type == "http":
                config["http-opts"] = {
                    "method": params.get('method', 'GET'),
                    "path": [params.get('path', '/')],
                    "headers": {
                        "Host": [final_sni]
                    }
                }
            
            if params.get('security') == 'reality':
                config["reality-opts"] = {
                    "public-key": params.get('pbk', ''),
                    "short-id": params.get('sid', '').lower() if params.get('sid') and re.match(r'^[0-9a-fA-F]{2,16}$', params.get('sid')) else ''
                }
            
            return config
        except Exception as e:
            return None
    
    def ss_to_clash_meta(self, ss_url, index):
        decoded = self.decode_ss_config(ss_url)
        if not decoded:
            return None
        
        original_name = decoded.get('name') or "Shadowsocks"
        config_name = f"{original_name} #{index + 1}"
        
        allowed_ciphers = [
            "aes-128-gcm", "aes-256-gcm", "chacha20-ietf-poly1305",
            "aes-128-cfb", "aes-256-cfb", "chacha20", "chacha20-ietf"
        ]
        
        cipher = decoded['method'] if decoded['method'] in allowed_ciphers else None
        if not cipher:
            return None
        
        return {
            "name": config_name,
            "type": "ss",
            "server": decoded['server'],
            "port": decoded['port'],
            "cipher": cipher,
            "password": decoded['password'],
            "udp": True,
            "tcp-fast-open": True
        }
    
    def hysteria2_to_clash_meta(self, url_str, index):
        try:
            url_str_normalized = url_str.replace('hy2://', 'hysteria2://')
            url_str_normalized = url_str_normalized.split('#')[0] if '#' in url_str_normalized else url_str_normalized
            
            url = url_str_normalized.replace('hysteria2://', 'http://')
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            params = {k: v[0] for k, v in params.items()}
            
            original_name = self.get_original_tag(url_str) or "Hysteria2"
            config_name = f"{original_name} #{index + 1}"
            
            final_server = parsed.hostname
            sni_value = params.get('sni') or params.get('host') or parsed.hostname
            
            config = {
                "name": config_name,
                "type": "hysteria2",
                "server": final_server,
                "port": parsed.port or 443,
                "password": parsed.username or "",
                "sni": sni_value,
                "skip-cert-verify": False,
                "fast-open": True,
                "client-fingerprint": params.get('fingerprint', 'chrome')
            }
            
            if params.get('alpn'):
                config["alpn"] = [v.strip() for v in params['alpn'].split(',')]
            
            if params.get('obfs') and params.get('obfs-password'):
                config["obfs"] = params['obfs']
                config["obfs-password"] = params['obfs-password']
            
            if params.get('up') or params.get('down'):
                config["up"] = params.get('up', '100 Mbps')
                config["down"] = params.get('down', '100 Mbps')
            
            if params.get('ports'):
                config["ports"] = params['ports']
            
            return config
        except Exception as e:
            return None
    
    def vmess_to_clash_meta(self, vmess_url, index):
        try:
            vmess_config = self.decode_vmess_config(vmess_url)
            if not vmess_config:
                return None
            
            def sanitize(s):
                s = str(s) if s is not None else ""
                s = re.sub(r'[\u0000-\u001F\u007F-\u009F]', '', s)
                s = re.sub(r'[^\x20-\x7E\u0600-\u06FF]', '', s)
                s = re.sub(r'\s+', ' ', s)
                return s.strip()
            
            original_name = sanitize(vmess_config.get('ps', 'VMess'))
            config_name = f"{original_name} #{index + 1}"
            
            final_server = vmess_config.get('add', '')
            host_value = vmess_config.get('host', '')
            sni_value = vmess_config.get('sni') or vmess_config.get('host') or vmess_config.get('add', '')
            network_type = vmess_config.get('net', 'tcp')
            tls_enabled = vmess_config.get('tls') == 'tls'
            
            config = {
                "name": config_name,
                "type": "vmess",
                "server": final_server,
                "port": int(vmess_config.get('port', 443)),
                "uuid": vmess_config.get('id', ''),
                "alterId": int(vmess_config.get('aid', 0)),
                "cipher": vmess_config.get('scy', 'auto'),
                "network": network_type,
                "tls": tls_enabled,
                "udp": True,
                "skip-cert-verify": False,
                "tcp-fast-open": True,
                "servername": sni_value,
                "client-fingerprint": vmess_config.get('fp', 'chrome')
            }
            
            if vmess_config.get('alpn'):
                config["alpn"] = [v.strip() for v in vmess_config['alpn'].split(',')]
            
            if network_type == "ws":
                config["ws-opts"] = {
                    "path": vmess_config.get('path', '/'),
                    "headers": {
                        "Host": host_value or sni_value or final_server
                    }
                }
            
            if network_type == "h2":
                config["h2-opts"] = {
                    "host": [host_value or sni_value or final_server],
                    "path": vmess_config.get('path', '/')
                }
            
            if network_type == "grpc":
                config["grpc-opts"] = {
                    "grpc-service-name": vmess_config.get('path', 'GunService')
                }
            
            return config
        except Exception as e:
            return None
    
    def trojan_to_clash_meta(self, trojan_url, index):
        try:
            url_str = trojan_url.split('#')[0] if '#' in trojan_url else trojan_url
            url_str = url_str.replace('trojan://', 'http://')
            parsed = urlparse(url_str)
            params = parse_qs(parsed.query)
            params = {k: v[0] for k, v in params.items()}
            
            original_name = self.get_original_tag(trojan_url) or "Trojan"
            config_name = f"{original_name} #{index + 1}"
            
            final_server = parsed.hostname
            sni_value = params.get('sni') or params.get('host') or parsed.hostname
            network_type = params.get('type', 'tcp')
            
            config = {
                "name": config_name,
                "type": "trojan",
                "server": final_server,
                "port": parsed.port or 443,
                "password": parsed.username or "",
                "network": network_type,
                "udp": True,
                "skip-cert-verify": False,
                "tcp-fast-open": True,
                "servername": sni_value,
                "client-fingerprint": params.get('fp', 'chrome')
            }
            
            if params.get('alpn'):
                config["alpn"] = [v.strip() for v in params['alpn'].split(',')]
            
            if network_type == "grpc":
                config["grpc-opts"] = {
                    "grpc-service-name": params.get('serviceName', 'GunService')
                }
            
            if network_type == "ws":
                config["ws-opts"] = {
                    "path": params.get('path', '/'),
                    "headers": {
                        "Host": sni_value
                    }
                }
            
            return config
        except Exception as e:
            return None
    
    def generate_clashmeta_protocol_files(self, protocol_configs, protocol_name):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if not protocol_configs:
            return None
        
        settings = {
            'ipver': 'ipv4',
            'dns': '8.8.8.8,1.1.1.1',
            'direct': '8.8.8.8'
        }
        
        proxies = []
        for index, config in enumerate(protocol_configs):
            try:
                if protocol_name == 'vless' and config.startswith('vless://'):
                    if '@' in config and config.split('@')[0].count(':') >= 1:
                        proxy = self.vless_to_clash_meta(config, index)
                        if proxy:
                            proxies.append(proxy)
                elif protocol_name == 'ss' and config.startswith('ss://'):
                    proxy = self.ss_to_clash_meta(config, index)
                    if proxy:
                        proxies.append(proxy)
                elif protocol_name in ['hysteria2', 'hy2'] and (config.startswith('hysteria2://') or config.startswith('hy2://')):
                    proxy = self.hysteria2_to_clash_meta(config, index)
                    if proxy:
                        proxies.append(proxy)
                elif protocol_name == 'vmess' and config.startswith('vmess://'):
                    proxy = self.vmess_to_clash_meta(config, index)
                    if proxy:
                        proxies.append(proxy)
                elif protocol_name == 'trojan' and config.startswith('trojan://'):
                    proxy = self.trojan_to_clash_meta(config, index)
                    if proxy:
                        proxies.append(proxy)
            except Exception as e:
                continue
        
        if not proxies:
            return None
        
        proxy_names = [p["name"] for p in proxies]
        use_ipv6 = settings.get('ipver') == 'ipv6'
        
        clash_config = {
            "mixed-port": 7890,
            "ipv6": use_ipv6,
            "allow-lan": True,
            "mode": "rule",
            "log-level": "warning",
            "unified-delay": False,
            "tcp-concurrent": True,
            "geo-auto-update": True,
            "geo-update-interval": 168,
            "external-controller": "127.0.0.1:9090",
            "external-controller-cors": {
                "allow-origins": ["*"],
                "allow-private-network": True
            },
            "external-ui": "ui",
            "external-ui-url": "https://github.com/MetaCubeX/metacubexd/archive/refs/heads/gh-pages.zip",
            "profile": {
                "store-selected": True,
                "store-fake-ip": True
            },
            "dns": {
                "enable": True,
                "respect-rules": True,
                "use-system-hosts": False,
                "listen": "0.0.0.0:1053",
                "ipv6": use_ipv6,
                "nameserver": settings.get('dns', '').split(',') if settings.get('dns') and settings.get('dns') != 'none' else ["https://8.8.8.8/dns-query#DIRECT", "https://1.1.1.1/dns-query#DIRECT"],
                "proxy-server-nameserver": settings.get('direct', '').split(',') if settings.get('direct') and settings.get('direct') != 'none' else ["8.8.8.8#DIRECT"],
                "direct-nameserver": settings.get('direct', '').split(',') if settings.get('direct') and settings.get('direct') != 'none' else ["8.8.8.8#DIRECT"],
                "direct-nameserver-follow-policy": True,
                "enhanced-mode": "fake-ip",
                "fake-ip-range": "198.18.0.1/16",
                "fake-ip-filter": [
                    "*.lan", "*.local", "*.localhost", "*.ir",
                    "*.test", "*.localdomain", "*.home", "*.internal"
                ]
            },
            "tun": {
                "enable": True,
                "stack": "mixed" if use_ipv6 else "gvisor",
                "auto-route": True,
                "strict-route": True,
                "auto-detect-interface": True,
                "dns-hijack": ["any:53", "tcp://any:53"],
                "mtu": 9000
            },
            "sniffer": {
                "enable": True,
                "force-dns-mapping": True,
                "parse-pure-ip": True,
                "override-destination": True,
                "sniff": {
                    "HTTP": {
                        "ports": [80, 8080, 8880, 2052, 2082, 2086, 2095]
                    },
                    "TLS": {
                        "ports": [443, 8443, 2053, 2083, 2087, 2096]
                    }
                }
            },
            "proxies": proxies,
            "proxy-groups": [
                {
                    "name": "Proxy Select",
                    "type": "select",
                    "proxies": ["Auto Select"] + proxy_names + ["DIRECT"]
                },
                {
                    "name": "Auto Select",
                    "type": "url-test",
                    "proxies": proxy_names,
                    "url": "http://www.gstatic.com/generate_204",
                    "interval": 300,
                    "tolerance": 150,
                    "lazy": True
                }
            ],
            "rules": [
                "DOMAIN-SUFFIX,net2025.afsharidempire.uk,DIRECT",
                "DOMAIN,cp.cloudflare.com,Auto Select",
                "DOMAIN-SUFFIX,cdn.ir,DIRECT",
                "DOMAIN-SUFFIX,aparat.com,DIRECT",
                "DOMAIN-SUFFIX,digikala.com,DIRECT",
                "DOMAIN-SUFFIX,divar.ir,DIRECT",
                "DOMAIN-SUFFIX,snapp.ir,DIRECT",
                "DOMAIN-SUFFIX,torob.com,DIRECT",
                "DOMAIN-SUFFIX,bamilo.com,DIRECT",
                "DOMAIN-SUFFIX,alibaba.ir,DIRECT",
                "DOMAIN-SUFFIX,ban.ir,DIRECT",
                "DOMAIN-KEYWORD,telegram,Auto Select",
                "DOMAIN-SUFFIX,t.me,Auto Select",
                "DOMAIN-SUFFIX,telegram.org,Auto Select",
                "DOMAIN-SUFFIX,google.com,Auto Select",
                "DOMAIN-SUFFIX,youtube.com,Auto Select",
                "DOMAIN-SUFFIX,github.com,Auto Select",
                "DOMAIN-SUFFIX,instagram.com,Auto Select",
                "DOMAIN-SUFFIX,twitter.com,Auto Select",
                "DOMAIN-SUFFIX,whatsapp.com,Auto Select",
                "GEOIP,IR,DIRECT",
                "MATCH,Proxy Select"
            ],
            "ntp": {
                "enable": True,
                "server": "time.cloudflare.com",
                "port": 123,
                "interval": 30
            }
        }
        
        return clash_config
    
    def generate_clashmeta_files(self):
        os.makedirs('configs/clashmeta', exist_ok=True)
        os.makedirs('configs/clashmeta/telegram', exist_ok=True)
        os.makedirs('configs/clashmeta/github', exist_ok=True)
        
        supported_protocols = ['vmess', 'vless', 'trojan', 'ss', 'hysteria2']
        
        for protocol in supported_protocols:
            telegram_configs = self.read_configs(f'configs/telegram/{protocol}.txt')
            github_configs = self.read_configs(f'configs/github/{protocol}.txt')
            
            if telegram_configs:
                clash_config = self.generate_clashmeta_protocol_files(telegram_configs, protocol)
                if clash_config:
                    filename = f"configs/clashmeta/telegram/{protocol}.yaml"
                    with open(filename, 'w', encoding='utf-8') as f:
                        import yaml
                        yaml.dump(clash_config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
                    proxy_count = len(clash_config.get('proxies', []))
                    print(f"  ✅ فایل ClashMeta برای پروتکل {protocol} از تلگرام با {proxy_count} پروکسی ایجاد شد")
            
            if github_configs:
                clash_config = self.generate_clashmeta_protocol_files(github_configs, protocol)
                if clash_config:
                    filename = f"configs/clashmeta/github/{protocol}.yaml"
                    with open(filename, 'w', encoding='utf-8') as f:
                        import yaml
                        yaml.dump(clash_config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
                    proxy_count = len(clash_config.get('proxies', []))
                    print(f"  ✅ فایل ClashMeta برای پروتکل {protocol} از گیت‌هاب با {proxy_count} پروکسی ایجاد شد")
    
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
    
    def create_persian_caption(self, category, count, source, timestamp, source_type):
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
    
    def create_clashmeta_caption(self, protocol, count, timestamp, source_type):
        protocol_name = self.protocol_names_fa.get(protocol, protocol.upper())
        source_persian = "تلگرام" if source_type == "telegram" else "گیت‌هاب"
        
        caption = f"""
🔰 <b>کانفیگ‌های {protocol_name}</b>

📊 تعداد: {count} عدد
📡 منبع: {source_persian}
👈 قابل استفاده در کلاینت <b>ClashMeta</b>

➖➖➖➖➖➖➖➖
<blockquote>@aristapanel</blockquote>
➖➖➖➖➖➖➖➖

#arista #{protocol} #ClashMeta
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
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        display_timestamp = datetime.now().strftime('%Y/%m/%d - %H:%M UTC')
        
        posted_files = []
        
        print("\n" + "=" * 60)
        print("📤 ارسال فایل‌های تلگرام به کانال")
        print("=" * 60)
        
        for category in self.categories:
            telegram_configs = self.read_configs(f'configs/telegram/{category}.txt')
            
            if telegram_configs:
                unique_configs = self.deduplicate(telegram_configs)
                
                filename = f"configs/telegram/{category}.txt"
                
                caption = self.create_persian_caption(
                    category, 
                    len(unique_configs), 
                    "کانال‌های تلگرام",
                    display_timestamp,
                    "telegram"
                )
                
                self.send_to_telegram(filename, caption)
                posted_files.append(filename)
                time.sleep(1)
    
    def post_github_files(self):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        display_timestamp = datetime.now().strftime('%Y/%m/%d - %H:%M UTC')
        
        posted_files = []
        
        print("\n" + "=" * 60)
        print("📤 ارسال فایل‌های گیت‌هاب به کانال")
        print("=" * 60)
        
        for category in self.categories:
            github_configs = self.read_configs(f'configs/github/{category}.txt')
            
            if github_configs:
                unique_configs = self.deduplicate(github_configs)
                
                filename = f"configs/github/{category}.txt"
                
                caption = self.create_persian_caption(
                    category, 
                    len(unique_configs), 
                    "مخازن گیت‌هاب",
                    display_timestamp,
                    "github"
                )
                
                self.send_to_telegram(filename, caption)
                posted_files.append(filename)
                time.sleep(1)
    
    def post_clashmeta_files(self):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        display_timestamp = datetime.now().strftime('%Y/%m/%d - %H:%M UTC')
        
        print("\n" + "=" * 60)
        print("📤 ارسال فایل‌های ClashMeta به کانال")
        print("=" * 60)
        
        supported_protocols = ['vmess', 'vless', 'trojan', 'ss', 'hysteria2']
        
        for protocol in supported_protocols:
            telegram_file = f'configs/clashmeta/telegram/{protocol}.yaml'
            if os.path.exists(telegram_file):
                configs = self.read_configs(f'configs/telegram/{protocol}.txt')
                proxy_count = len([c for c in configs if c.startswith(('vmess://', 'vless://', 'trojan://', 'ss://', 'hysteria2://', 'hy2://'))])
                caption = self.create_clashmeta_caption(protocol, proxy_count, display_timestamp, "telegram")
                self.send_to_telegram(telegram_file, caption)
            
            github_file = f'configs/clashmeta/github/{protocol}.yaml'
            if os.path.exists(github_file):
                configs = self.read_configs(f'configs/github/{protocol}.txt')
                proxy_count = len([c for c in configs if c.startswith(('vmess://', 'vless://', 'trojan://', 'ss://', 'hysteria2://', 'hy2://'))])
                caption = self.create_clashmeta_caption(protocol, proxy_count, display_timestamp, "github")
                self.send_to_telegram(github_file, caption)
    
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
        
        self.generate_clashmeta_files()
        
        self.post_telegram_files()
        
        self.post_github_files()
        
        self.post_clashmeta_files()
        
        all_telegram = self.read_configs('configs/telegram/all.txt')
        all_github = self.read_configs('configs/github/all.txt')
        all_combined = self.read_configs('configs/combined/all.txt')
        
        total_telegram = len(all_telegram)
        total_github = len(all_github)
        total_combined = len(all_combined)
        
        print("\n" + "=" * 60)
        print("✅ گزارش نهایی")
        print("=" * 60)
        print(f"📊 کانفیگ‌های تلگرام: {total_telegram}")
        print(f"📊 کانفیگ‌های گیت‌هاب: {total_github}")
        print(f"📊 کانفیگ‌های ترکیبی یکتا: {total_combined}")
        print("\n📁 فایل‌های ایجاد شده در پوشه configs/:")
        
        protocol_emojis = {
            'vmess': '🚀', 'vless': '⚡', 'trojan': '🛡️',
            'ss': '📡', 'hysteria2': '🌪️', 'hysteria': '🌀',
            'tuic': '🔌', 'wireguard': '🔒', 'other': '📦'
        }
        
        for category in self.categories:
            if os.path.exists(f'configs/combined/{category}.txt'):
                with open(f'configs/combined/{category}.txt', 'r', encoding='utf-8') as f:
                    lines = [line for line in f if line.strip() and not line.startswith('#')]
                print(f"  {protocol_emojis.get(category, '📄')} combined/{category}.txt: {len(lines)} کانفیگ")
        
        supported_protocols = ['vmess', 'vless', 'trojan', 'ss', 'hysteria2']
        for protocol in supported_protocols:
            if os.path.exists(f'configs/clashmeta/telegram/{protocol}.yaml'):
                print(f"  🔥 clashmeta/telegram/{protocol}.yaml: فایل ClashMeta از تلگرام")
            if os.path.exists(f'configs/clashmeta/github/{protocol}.yaml'):
                print(f"  🔥 clashmeta/github/{protocol}.yaml: فایل ClashMeta از گیت‌هاب")
        
        print(f"  📦 combined/all.txt: {total_combined} کانفیگ")
        print("=" * 60)

def main():
    combiner = ConfigCombiner()
    combiner.combine_and_post()

if __name__ == "__main__":
    main()
