import asyncio, random
import base64, json
from typing import Any, Dict, List, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

arkl: Dict[str, Any] = {
    'pl': [],
    'cbid': None, # no idea wtf this is
    'rs': None  
}


def prepPayload(payload: List[Dict[str, Any]]) -> None:
    if len(payload) < 5 or not payload[4].get('value'):
        return

    container = payload[4]

    container['value'].append({'key': 'vsadsa', 'value': random.randint(0,20)})
    container['value'].append({'key': 'basfas', 'value': 4294705152})
    container['value'].append({'key': 'lfasdgs', 'value': arkl.get('cbid')})

    try:
        item25 = container['value'][25]
        item26 = container['value'][26]
        item1 = container['value'][1]
        item18 = container['value'][18]
    except IndexError:
        return

    if item25 and item1 and item18:
        v1 = item1.get('value')
        v18 = item18.get('value')
        if isinstance(v1, str) and isinstance(v18, str) and len(v1) > 12 and len(v18) > 12:
            container['value'][25] = {
                'key': item25['key'],
                'value': v1[:3] + v18[:3]
            }
        else:
            container['value'][25] = {
                'key': item25['key'],
                'value': 'abcdef'
            }

    if item26 and item26.get('value') is not None:
        try:
            multiplied = item26['value'] * 3
        except TypeError:
            multiplied = None
        container['value'][26] = {
            'key': item26['key'],
            'value': multiplied
        }


async def encrpyt(
    payload: Any, rsa_public_pem: str
) -> Optional[str]:
    if payload is None or not rsa_public_pem:
        return None

    payload_bytes = str(payload).encode('utf-8')

    aesgcm = AESGCM.generate_key(bit_length=256)
    aes = AESGCM(aesgcm)

    iv = AESGCM.generate_key(bit_length=128)[:12]

    ciphertext = aes.encrypt(iv, payload_bytes, None)
    
    tag = ciphertext[-16:]
    ct = ciphertext[:-16]

    public_key = serialization.load_pem_public_key(
        rsa_public_pem.encode('utf-8'),
        backend=default_backend()
    )

    encrypted_key = public_key.encrypt(
        aesgcm,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    b64_iv = base64.b64encode(iv).decode('utf-8')
    b64_tag = base64.b64encode(tag).decode('utf-8')
    b64_key = base64.b64encode(encrypted_key).decode('utf-8')
    b64_ct = base64.b64encode(ct).decode('utf-8')

    return b64_iv + b64_tag + b64_key + b64_ct


async def main():
    payload = arkl.get('pl')
    prepPayload(payload)
    public_key_pem = arkl.get('publicKeyPem')

    encrypted_result = await encrpyt(payload, public_key_pem)

    arkl['rs'] = encrypted_result


if __name__ == '__main__':
    arkl['pl'] = json.loads(open("ass.json", "r").read())
    arkl['publicKeyPem'] = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzjl0t5bLoeEA1f3uTVUEf
EfOoSH3hCfFEu6dFvrxeZML84tv2d5r3x5KEhc7eJfFUGHyA/W5cAS8gGKzIrA433
mWP5m4gZUwMIL8wSuusqNMcohIVObwWn8imhS+Bt0yH8q0q/Zz1WyACxbkrGhQqzl
lqc0gHbZkjNfQC2h5Si4jIYJXBF5X6asM07WJmeZynXTCdrJJUnzDZNERmbpkmsvk
poBrLnZ2XMY1bR9o+X4PFIBDpF+LdYXPuvAby/iIVfFzlVh/pX1n9ZIdSgFplM5+2
TL+rlmPiC26ekxIsUBv/yHInwPMr6xpe0XolOvPu8D3xzpIIVX9BAJvyU/H/QIDAQAB
-----END PUBLIC KEY-----'''
    asyncio.run(main())


    print(arkl['rs'])