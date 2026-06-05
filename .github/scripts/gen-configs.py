#!/usr/bin/env python3
"""Generate Xray server + client REALITY configs for E2E test.

Generates x25519 keypair using cryptography library (no xray binary needed).
Reads UUID and SHORT_ID from env if set, otherwise generates fresh ones.
Writes to /tmp/xray-e2e/server/config.json and /tmp/xray-e2e/client/config.json.
"""
import json, os, base64
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization

# --- Generate or read keys ---
key = x25519.X25519PrivateKey.generate()
PRIVATE_KEY = base64.urlsafe_b64encode(
    key.private_bytes(serialization.Encoding.Raw,
                      serialization.PrivateFormat.Raw,
                      serialization.NoEncryption())
).rstrip(b'=').decode()

PUBLIC_KEY = base64.urlsafe_b64encode(
    key.public_key().public_bytes(serialization.Encoding.Raw,
                                  serialization.PublicFormat.Raw)
).rstrip(b'=').decode()

UUID = os.environ.get('UUID') or open('/proc/sys/kernel/random/uuid').read().strip()
SHORT_ID = os.environ.get('SHORT_ID') or os.urandom(8).hex()

# --- Strip whitespace (env might contain newlines) ---
PRIVATE_KEY = PRIVATE_KEY.strip()
PUBLIC_KEY = PUBLIC_KEY.strip()
UUID = UUID.strip()
SHORT_ID = SHORT_ID.strip()

# --- Server (VPS) config ---
server = {
    'log': {'loglevel': 'debug'},
    'inbounds': [{
        'port': 8443, 'protocol': 'vless',
        'settings': {
            'clients': [{'id': UUID, 'flow': 'xtls-rprx-vision', 'email': 't@t.com'}],
            'decryption': 'none'
        },
        'streamSettings': {
            'network': 'tcp', 'security': 'reality',
            'realitySettings': {
                'show': False, 'dest': 'www.fandom.com:443', 'xver': 0,
                'serverNames': ['www.fandom.com', 'fandom.com'],
                'privateKey': PRIVATE_KEY, 'shortIds': [SHORT_ID]
            }
        }
    }],
    'outbounds': [{'protocol': 'freedom', 'tag': 'direct'}]
}

# --- Client (Linux) config ---
client = {
    'log': {'loglevel': 'debug'},
    'inbounds': [{
        'port': 1080, 'listen': '0.0.0.0',
        'protocol': 'socks',
        'settings': {'auth': 'noauth', 'udp': True}
    }],
    'outbounds': [{
        'protocol': 'vless',
        'settings': {
            'vnext': [{
                'address': 'xray-server', 'port': 8443,
                'users': [{'id': UUID, 'flow': 'xtls-rprx-vision', 'encryption': 'none'}]
            }]
        },
        'streamSettings': {
            'network': 'tcp', 'security': 'reality',
            'realitySettings': {
                'fingerprint': 'chrome', 'serverName': 'www.fandom.com',
                'publicKey': PUBLIC_KEY, 'shortId': SHORT_ID, 'spiderX': '/'
            }
        }
    }]
}

os.makedirs('/tmp/xray-e2e/server', exist_ok=True)
os.makedirs('/tmp/xray-e2e/client', exist_ok=True)

with open('/tmp/xray-e2e/server/config.json', 'w') as f:
    json.dump(server, f, indent=2)

with open('/tmp/xray-e2e/client/config.json', 'w') as f:
    json.dump(client, f, indent=2)

print(f'Configs written (privateKey={PRIVATE_KEY[:8]}... publicKey={PUBLIC_KEY[:8]}... uuid={UUID[:8]}...)')
