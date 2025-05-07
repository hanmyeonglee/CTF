import socket
import struct

import hmac, os, hashlib
from hashlib import sha384, sha256
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF, HKDFExpand

from Crypto.Util.number import long_to_bytes, bytes_to_long

# TLS record content type
HANDSHAKE = 22
TLS_VERSION = b'\x03\x03'  # TLS 1.2

def build_supported_groups() -> bytes:
    groups = [
        b'\x00\x1d',  # x25519
    ]
    group_list = b''.join(groups)
    return (
        b'\x00\x0a' +                           # Extension type: supported_groups
        struct.pack('!H', len(group_list) + 2) +  # Extension length
        struct.pack('!H', len(group_list)) +      # List length
        group_list
    )

def build_signature_algorithms() -> bytes:
    sigalgs = [
        b'\x04\x01' # rsa_pkcs1_sha256
    ]
    sigalg_list = b''.join(sigalgs)
    return (
        b'\x00\x0d' +
        struct.pack('!H', len(sigalg_list) + 2) +
        struct.pack('!H', len(sigalg_list)) +
        sigalg_list
    )

def build_key_share(client_key: x25519.X25519PrivateKey) -> bytes:
    # Group: x25519 = 0x001D
    group = b'\x00\x1d'
    # key_exchange = os.urandom(32)  # Random 32-byte x25519 public key (fake for demo)
    key_exchange = client_key.public_key().public_bytes_raw()

    return (
        b'\x00\x33' +                          # Extension type: key_share
        struct.pack('!H', 4 + 2 + len(key_exchange)) +  # Extension length
        struct.pack('!H', 2 + 2 + len(key_exchange)) +  # Client Key Share Length
        group +
        struct.pack('!H', len(key_exchange)) +
        key_exchange
    )

def build_padding(pad_len):
    return (
        b'\x00\x15' +  # Extension type: padding
        struct.pack('!H', pad_len) +
        b'\x00' * pad_len
    )

def build_extensions():
    all_ext = (
        build_signature_algorithms() +
        build_supported_groups() +
        b"\x00\x0b\x00\x02\x01\x00" + 
        build_padding(200)
    )
    return struct.pack('!H', len(all_ext)) + all_ext

def build_cipher_suites() -> bytes:
    # TLS 1.3 cipher suites
    return (struct.pack('!H', 2) + b'\xc0\x30')

def build_client_hello(
    client_random: bytes,
    session_id: bytes,
) -> bytes:
    session_id_len = len(session_id).to_bytes(1, 'big')
    cipher_suites = build_cipher_suites()
    compression_methods = b"\x01\x00"
    extensions = build_extensions()

    hello_body = (
        TLS_VERSION +
        client_random +
        session_id_len +
        session_id +
        cipher_suites +
        compression_methods + 
        extensions
    )

    handshake_msg = b'\x01' + struct.pack('!I', len(hello_body))[1:] + hello_body
    record = (
        bytes([HANDSHAKE]) +
        TLS_VERSION +
        struct.pack('!H', len(handshake_msg)) +
        handshake_msg
    )
    return record


def recv_server_hello(sock: socket.socket) -> tuple[bytes, bytes, bytes, bytes]:
    server_hello_header = sock.recv(5)
    server_hello_length = int.from_bytes(server_hello_header[3:5], 'big')
    server_hello = sock.recv(server_hello_length)

    certificate_header = sock.recv(5)
    certificate_length = int.from_bytes(certificate_header[3:5], 'big')
    certificate = sock.recv(certificate_length)

    server_key_exchange_header = sock.recv(5)
    server_key_exchange_length = int.from_bytes(server_key_exchange_header[3:5], 'big')
    server_key_exchange = sock.recv(server_key_exchange_length)

    server_hello_done = sock.recv(5)

    return server_hello_header+server_hello, certificate_header+certificate, server_key_exchange_header + server_key_exchange, server_hello_done



def get_server_random(server_hello: bytes) -> bytes:
    server_random = server_hello[11:43]
    return server_random


def parse_server_key_exchange(server_key_exchange: bytes) -> tuple[bytes, bytes, bytes]:
    curve_info = server_key_exchange[9:12]
    server_pubkey = server_key_exchange[12:13+32]
    signature = server_key_exchange[45+4:]
    #print(server_key_exchange[45:45+4].hex())
    return curve_info, server_pubkey, signature



def parse_certificate(cert_data: bytes):
    cert_len = int.from_bytes(cert_data[12:15], 'big')
    cert_bytes = cert_data[15:15+cert_len]

    cert = x509.load_der_x509_certificate(cert_bytes, backend=default_backend())
    print(f"[+] Subject: {cert.subject}")
    print(f"[+] Issuer: {cert.issuer}")
    
    return cert

# SHA-256을 위한 ASN.1 DER Prefix (PKCS#1 v1.5에서 사용)
SHA256_DER_PREFIX = bytes.fromhex(
    "3031300d060960864801650304020105000420"
)

def emsa_pkcs1_v1_5_encode(hash_bytes: bytes, em_len: int) -> bytes:
    """
    EMSA-PKCS1-v1_5 encoding.
    hash_bytes: 해시 결과 (SHA256 등)
    em_len: modulus 길이 (바이트)
    """
    t = SHA256_DER_PREFIX + hash_bytes
    if em_len < len(t) + 11:
        raise ValueError("Encoding error: intended encoded message length too short")

    ps = b'\xff' * (em_len - len(t) - 3)
    return b'\x00\x01' + ps + b'\x00' + t

def rsa_verify(message: bytes, signature: int, n: int, e: int) -> bool:
    """
    RSA-PKCS1-v1_5 + SHA256 signature 검증
    message: 원본 메시지 (bytes)
    signature: 서명 (정수형)
    n, e: 공개키 (modulus, exponent)
    """
    # 서명 복호화 (modular exponentiation)
    k = (n.bit_length() + 7) // 8  # modulus 크기 (bytes)

    hashed = hashlib.sha256(message).digest()
    expected_em = emsa_pkcs1_v1_5_encode(hashed, k)

    em = pow(signature, e, n).to_bytes(k, byteorder='big')
    return em == expected_em

    for diff in range(-7, 8):
        # 메시지 해시
        sig_p = (signature * pow(bytes_to_long(expected_em), diff, n)) % n
        m_prime = pow(sig_p, e, n)
        em = m_prime.to_bytes(k, byteorder='big')

        if em == expected_em:
            print(f'[Success] : {diff = }, {em.hex() = }')
            return diff
        
        #print(f'[Failed] : {diff = }, {em.hex() = }, {expected_em.hex() = }')

    raise Exception("fucking TLS")


def main(trigger: int | None = None):
    host = "141.223.175.203"
    # host = "44.210.92.118"
    port = 12345
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    if trigger is not None:
        sock.send(bytes([trigger]), socket.MSG_OOB)
    
    client_random = os.urandom(32)
    session_id = b""
    client_x25519_key = x25519.X25519PrivateKey.generate()
    client_hello = build_client_hello(client_random, session_id)
    sock.sendall(client_hello)

    server_hello, certificate, server_key_exchange, _ = recv_server_hello(sock)

    server_random = get_server_random(server_hello)
    cert = parse_certificate(certificate)
    curve_info, server_pubkey, signature = parse_server_key_exchange(server_key_exchange)

    cert_pubkey = cert.public_key()
    sock.close()

    print((client_random + server_random + curve_info + server_pubkey).hex())
    print(signature.hex())
    
    return rsa_verify(
        client_random + server_random + curve_info + server_pubkey,
        bytes_to_long(signature),
        cert_pubkey.public_numbers().n,
        cert_pubkey.public_numbers().e,
    )
    

if __name__ == "__main__":
    windows = [0] * 15
    for _ in range(1):
        x = main(0)
        print(x)

    print(windows)
