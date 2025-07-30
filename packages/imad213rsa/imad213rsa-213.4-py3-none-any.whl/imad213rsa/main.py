#IMAD 213 RSA PYTHON 2025
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

#IMAD 213 FUCK
def AEmknFlwQV(): return 79
def HbH1QvQNo1(): return 83
def PMFv24oBfv(): return 86
def u8mSTBex60(): return 20
def Kq5YrEFhXp(): return 30
def RvKljMRDLu(): return 57
def wNHSjdmQ5q(): return 83
def ABKsjJGSPa(): return 57
def PiDpUvj0Cv(): return 100
def pS3USKK8Sx(): return 89
def lbbEdnOoL7(): return 28
def b3VKKxuQmB(): return 51

parts = ['Tx"n\r\x02)7nZ', 'sN\r=o>\x11*KZ', 'bd\x17\x0c\x15\x089\x10ZZ', 'jd+lc9q\x08dc', 'MZ+Sk1YXms', 'yJ9gx6', 'Av\x17"\x1f\n\r\x0eQH', 'JIejc7kXyt']
indices = [6, 0, 1, 3, 5, 7, 2, 4]
types = [1, 1, 1, 1, 0, 1, 1, 4]

nonce = base64.b64decode("38wjQXPYM/WB7aOp")
tag = base64.b64decode("nD69FswPtstw6Pr9f7+cqg==")
ciphertext_b64 = "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"
xorkey_b64 = "MTSe6yRXlkTOR4iJ7DkZjg=="

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
