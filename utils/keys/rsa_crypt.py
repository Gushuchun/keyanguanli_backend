import base64
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto import Random

def read_private_key() -> bytes:
    with open('utils/keys/private_key.pem', 'rb') as key_file:
        private_key = key_file.read()
        return private_key

def read_public_key() -> bytes:
    with open('utils/keys/private_key.pem', 'rb') as key_file:
        private_key = key_file.read()
        return private_key

def decryption(text_encrypted_base64: str):
    # 字符串指定编码（转为bytes）
    text_encrypted_base64 = text_encrypted_base64.encode('utf-8')
    # base64解码
    text_encrypted = base64.b64decode(text_encrypted_base64)
    # 构建私钥对象
    cipher_private = PKCS1_v1_5.new(RSA.importKey(read_private_key()))
    # 解密（bytes）
    text_decrypted = cipher_private.decrypt(text_encrypted, Random.new().read)
    # 解码为字符串
    text_decrypted = text_decrypted.decode()
    return text_decrypted