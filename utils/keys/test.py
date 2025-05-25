import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

private_key_pem = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC0R32yX97oWpaq
sffnUGwMFl2eQyxOi6dGi/mF0TmclkELKXGm2x5Dd6k/0btkJIH/pYMbIEgZnd1S
7aScg/5/g4HzRTGIfiFSRbwxmdEibmbaHGfU7uD3VA8ryXozQgtZzYXtuBkc9Vy5
S2BkGRThXdthBF58hqwu013C8Diw7HByPxSPHwcY9IootVQzoX/REzIxpOF8OnHB
c1bbeHLu1GM9F+xXxw1inkvjPKe69SX7ruzrtsLz2350+DT6XN/PZfXbTmeLf8/2
M5cE/4Z24D2wtLWSS3vy4q6613a7Z34KuecqygmgReks2QkcF5gjAfjjhebvjkQY
LWXubDHlAgMBAAECggEAJTq2TIXb5KQAhVOnXE+RYJWl068PkVDpxHnXl7jzatDk
scdnPwv1Hf2yKAnJ5w5bAk5N2uY5vYCKWjvVSLVBc1fXGEPrzMIvY2wfRyb6t1+R
Qe2ny6NhNfJYB7Td1YQIEA2PYN4p4X8SHPnh+Ant8/SL/2cFlDXDjQ/9RuqQ6ogw
Z/X9QZgXiHWQTX4TbJBYh0Fe1NgGRAW/HU7by8K6jZZ6SdOBKrJIKd/XlM8TpN59
eoelH1dLiPIBfqtIxYm5x4eL4ikOBBG5eKQ9kFJY8+1r8nnUdYCoCs1G7ultcMTW
0IHiwsYy5suSE5Fb80kjHsVmvTC041UE9ac5OhXzqQKBgQDmIGJ1eUtZktrLfFXV
Dsp8MHsSAAGFnyPWyCJj1Al7lX0p08grpxbm9izYk8AulwOP+wXfqLa27Lah37gW
kAh25nQ3iUEzmJ96vsmS7xwHd90Ef3ldMWc+z1QUJx4lzFc9vk7pxLIPnfo7z0wP
T6kIm8X5kNiSbHcPwW/FmS3v1wKBgQDIjGDattiwH6wY4SO+pkNNevRkoCAQxNaw
Ge0+pArcQZn1ugIa/PcQ+H37kG3S/T2LFosFViJ00HMWTMCQfz2cX6ttaANwdN4I
rZo/A9hZieG+40Ree1oXBA6XBHPQiGxzzGLBsIa2icIbxYUdubkUUMlEKd5IEKeZ
OG9WidfkowKBgCmv9CYTsvKnB7uU6neOFmAo6CJ6ncv26CcgWhp7brxUeDf7hWdi
/WMZdUZGfany8VJDxuydQ3wfpXXtcQulS+M+HA9zbbxLCZjStvFHH2y66e7GqNWY
/XsDU9fSvkNaoPMuZl0ypI7vr0TmaIDdjWFh1ps/AfyEaY0RHY5OEWRBAoGAGejg
/oDO//onjtNPfesXGOSAvJtfaSs1HW1MFGK3MHudO3z7lqcF+IBSLnUbaz3ifJy9
+0OEkhj4NXJXEpQNzq0hhbIBd77xjKd5HRkPE4pXywSrqZVAL2cLx4EAwXlOoatP
OvzmeqDTnijnqM581d4WEqNiH2dfb9E1uTV32gcCgYEAiuU2lJXMJFv5gvChzgZ+
urCR/pw+fUzK5RqTQlGdcOb2HLslEs9qaeUIWilNBxrUFNbqZpDy+6YrDwYs6azz
u0Hi4TkWjxKWbjDst+tk0Hl4lrp3iiaLLPlvNXZyy6FA1d42jU6ZYjg/2eesAkFE
FnFxCdbyEmU9XnQWvRPg8/U=
-----END PRIVATE KEY-----"""

public_key_pem = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtEd9sl/e6FqWqrH351Bs
DBZdnkMsTounRov5hdE5nJZBCylxptseQ3epP9G7ZCSB/6WDGyBIGZ3dUu2knIP+
f4OB80UxiH4hUkW8MZnRIm5m2hxn1O7g91QPK8l6M0ILWc2F7bgZHPVcuUtgZBkU
4V3bYQRefIasLtNdwvA4sOxwcj8Ujx8HGPSKKLVUM6F/0RMyMaThfDpxwXNW23hy
7tRjPRfsV8cNYp5L4zynuvUl+67s67bC89t+dPg0+lzfz2X1205ni3/P9jOXBP+G
duA9sLS1kkt78uKuutd2u2d+CrnnKsoJoEXpLNkJHBeYIwH444Xm745EGC1l7mwx
5QIDAQAB
-----END PUBLIC KEY-----"""


def test_rsa():
    # 加载密钥
    with open('private_key.pem', 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode(),
        backend=default_backend()
    )

    # 原始消息
    message = b"1234561231"

    try:
        # 加密
        ciphertext = public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        cc = b'qoGrvt6UDPng/gTA1qmj4EwKw3Tcghc9RZsGHf1FtUm8qGk+7DaZ1ICIjlkDoE9dDiIwYmmW4mCSuMXIQzBXh6ebtdjGSRs1XJgLFMSqEpIA6kvLxEUOaU0p8PSLBOM5o+O8Ik+nDo8zCpS2nMYylF4QHAyGFdIpzZDCxiZx3t7V0gOrdG0dEf+WjoVca8OuD5AOV+bYzoT1dO7YIPK+iSez8iCKKx69FzSriv33/ODYumTr1+sX2K/Og24ks+jkxdhu8oqwVogHTWl0bpPsNZK+1ZDbWXueUplDpzvVo8Y7nchDrjE4G5d/PsQQ6vHHRkvTpxDY6EcbE+CPVLJ1kw=='
        encrypted_password = base64.b64decode(cc)

        # 解密
        plaintext = private_key.decrypt(
            encrypted_password,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )


        # 验证结果
        assert plaintext == message
        print("加解密验证成功！")
        print(f"原始消息: {message.decode()}")
        print(f"加密结果: {ciphertext.hex()}")
        print(f"加密结果长度: {len(ciphertext)}")
        print(f"cc长度: {len(cc)}")
        print(f"解密结果: {plaintext.decode()}")

    except Exception as e:
        print(f"加解密失败: {str(e)}")


if __name__ == "__main__":
    test_rsa()