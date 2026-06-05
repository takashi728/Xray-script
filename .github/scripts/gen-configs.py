#!/usr/bin/env python3
"""Generate Xray server + client configs for E2E REALITY test.

Reads env vars: UUID, PRIVATE_KEY, PUBLIC_KEY, SHORT_ID
Writes to:      /tmp/xray-e2e/server/config.json
                /tmp/xray-e2e/client/config.json
"""
import json, os

uuid   = os.environ['UUID']
priv   = os.environ['PRIVATE_KEY']
pub    = os.environ['PUBLIC_KEY']
short  = os.environ['SHORT_ID']

server = {
    'log': {'loglevel': 'debug'},
    'inbounds': [{
        'port': 8443,
        'protocol': 'vless',
        'settings': {
            'clients': [{
                'id': uuid,
                'flow': 'xtls-rprx-vision',
                'email': 't@t.com'
            }],
            'decryption': 'none'
        },
        'streamSettings': {
            'network': 'tcp',
            'security': 'reality',
            'realitySettings': {
                'show': False,
                'dest': 'www.fandom.com:443',
                'xver': 0,
                'serverNames': ['www.fandom.com', 'fandom.com'],
                'privateKey': priv,
                'shortIds': [short]
            }
        }
    }],
    'outbounds': [{'protocol': 'freedom', 'tag': 'direct'}]
}

client = {
    'log': {'loglevel': 'debug'},
    'inbounds': [{
        'port': 1080,
        'listen': '0.0.0.0',
        'protocol': 'socks',
        'settings': {'auth': 'noauth', 'udp': True}
    }],
    'outbounds': [{
        'protocol': 'vless',
        'settings': {
            'vnext': [{
                'address': 'xray-server',
                'port': 8443,
                'users': [{
                    'id': uuid,
                    'flow': 'xtls-rprx-vision',
                    'encryption': 'none'
                }]
            }]
        },
        'streamSettings': {
            'network': 'tcp',
            'security': 'reality',
            'realitySettings': {
                'fingerprint': 'chrome',
                'serverName': 'www.fandom.com',
                'publicKey': pub,
                'shortId': short,
                'spiderX': '/'
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

print('Configs written to /tmp/xray-e2e/')
