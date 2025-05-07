import socket
import struct

from hashlib import sha384, sha256
from cryptography.hazmat.primitives.asymmetric import x25519


from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF, HKDFExpand
from cryptography.hazmat.primitives.asymmetric import padding, ec
from cryptography.x509 import load_der_x509_certificate

from Crypto.Util.number import bytes_to_long, long_to_bytes

# TLS record content type
HANDSHAKE = 22
TLS_VERSION = b'\x03\x03'  # TLS 1.2

def build_supported_versions() -> bytes:
    return (
        b'\x00\x2b' +         # Extension type: supported_versions
        b'\x00\x03' +         # Length
        b'\x02' +             # List length
        b'\x03\x04'           # TLS 1.3
    )

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
        b'\x04\x03',
        b'\x05\x03',
        b'\x06\x03',
        b'\x08\x07',
        b'\x08\x08',
        b'\x08\x09',
        b'\x08\x0a',
        b'\x08\x0b',
        b'\x08\x04',
        b'\x08\x05',
        b'\x08\x06',
        b'\x04\x01',
        b'\x05\x01',
        b'\x06\x01',
        b'\x03\x03',
        b'\x03\x01',
        b'\x03\x02',
        b'\x04\x02',
        b'\x05\x02',
        b'\x06\x02',
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

def build_extensions(client_key: x25519.X25519PrivateKey):
    all_ext = (
        build_supported_versions() +
        build_signature_algorithms() +
        build_supported_groups() +
        build_key_share(client_key=client_key) +
        build_padding(200)
    )
    return struct.pack('!H', len(all_ext)) + all_ext

def build_cipher_suites() -> bytes:
    # TLS 1.3 cipher suites
    return (struct.pack('!H', 2) + b'\x13\x02')

def build_client_hello(
    client_random: bytes,
    session_id: bytes,
    client_key: x25519.X25519PrivateKey
) -> bytes:
    session_id_len = len(session_id).to_bytes(1, 'big')
    cipher_suites = build_cipher_suites()
    compression_methods = b"\x01\x00"
    extensions = build_extensions(client_key)

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


def recv_server_hello(sock: socket.socket) -> tuple[bytes, bytes, list[bytes]]:
    server_hello_header = sock.recv(5)
    server_hello_length = int.from_bytes(server_hello_header[3:5], 'big')
    server_hello = server_hello_header + sock.recv(server_hello_length)

    change_cipher_spec_header = sock.recv(5)
    change_cipher_spec_length = int.from_bytes(change_cipher_spec_header[3:5], 'big')
    change_cipher_spec = change_cipher_spec_header + sock.recv(change_cipher_spec_length)

    application_data = []
    for _ in range(4):
        tmp_header = sock.recv(5)
        tmp_length = int.from_bytes(tmp_header[3:5], 'big')
        tmp_data = sock.recv(tmp_length)
        application_data.append(tmp_header + tmp_data)

    return server_hello, change_cipher_spec, application_data


def extract_server_hello_info(server_hello: bytes):
    assert server_hello[5] == 2
    server_hello_body = server_hello[6:]
    length = int.from_bytes(server_hello_body[0:3], 'big')
    version = server_hello_body[3:5]
    server_random = server_hello_body[5:5+32]
    sess_id_len = server_hello_body[37]
    sess_id = server_hello_body[38:38+sess_id_len]
    cipher_suite = server_hello_body[38+sess_id_len:38+sess_id_len+2]
    comp_method = server_hello_body[38+sess_id_len+2]
    server_hello_extension_len = int.from_bytes(server_hello_body[38+sess_id_len+3:38+sess_id_len+5], 'big')
    server_hello_extension = server_hello_body[38+sess_id_len+5:]

    cnt = 0
    while True:
        extension_header = server_hello_extension[cnt:cnt+4]
        cnt += 4
        extension_length = int.from_bytes(extension_header[2:], 'big')
        extension_body = server_hello_extension[cnt:cnt+extension_length]
        cnt += extension_length

        # Key share
        if extension_header[:2] == b"\x00\x33":
            key_share_group = extension_body[:2]
            key_share_key_length = int.from_bytes(extension_body[2:4], 'big')
            key = extension_body[4:4+key_share_key_length]

        if cnt >= server_hello_extension_len:
            break

    return server_random, key


def HKDF_Expand_Label(
    key, label, context, length, backend=default_backend(), algorithm=hashes.SHA384()
):
    tmp_label = b"tls13 " + label.encode()
    hkdf_label = (
        struct.pack(">h", length)
        + struct.pack("b", len(tmp_label))
        + tmp_label
        + struct.pack("b", len(context))
        + context
    )
    return HKDFExpand(
        algorithm=algorithm, length=length, info=hkdf_label, backend=backend
    ).derive(key)


def decrypt_tls_record(server_key: bytes, server_iv: bytes, record: bytes, seq_num: int):
    aesgcm = AESGCM(server_key)

    content_type = record[0]
    assert content_type == 23  # Application Data
    length = int.from_bytes(record[3:5], 'big')

    ciphertext = record[5:]
    ct = ciphertext[:-16]  # 실제 암호화된 payload
    tag = ciphertext[-16:] # GCM 인증 태그

    # Nonce = IV XOR seq_num (8-byte big-endian, left-padded to 12 bytes)

    seq_bytes = b"\x00" * 4 + seq_num.to_bytes(8, "big")
    nonce = bytes(a ^ b for a, b in zip(server_iv, seq_bytes))

    # TLS 1.3 uses the full header as AAD
    aad = record[:5]

    # GCM tag is last 16 bytes
    decrypted = aesgcm.decrypt(nonce, ct+tag, aad)
    return decrypted

def mgf1(seed: bytes, mask_len: int, hash_func=sha256):
    h_len = hash_func().digest_size
    mask = b""
    for i in range((mask_len + h_len - 1) // h_len):
        c = i.to_bytes(4, byteorder='big')
        mask += hash_func(seed + c).digest()
    return mask[:mask_len]


def pss_verify(m_hash: bytes, em: bytes, em_bits=2048, hash_func=sha256, salt_len=32):
    h_len = hash_func().digest_size
    em_len = (em_bits + 7) // 8

    if len(em) != em_len:
        print(len(em), em_len)
        return False

    masked_db = em[:em_len - h_len - 1]
    h = em[em_len - h_len - 1 : em_len - 1]

    # Leading bits must be zero if em_bits is not a multiple of 8
    if em_bits % 8 != 0:
        if masked_db[0] >> (8 - em_bits % 8) != 0:
            print(masked_db[0] >> (8 - em_bits % 8))
            return False

    # Unmask the DB
    db_mask = mgf1(h, em_len - h_len - 1, hash_func)
    db = bytes(a ^ b for a, b in zip(masked_db, db_mask))

    if em_bits % 8 != 0:
        db = bytes([db[0] & (0xFF >> (8 - em_bits % 8))]) + db[1:]

    # Split DB: PS || 0x01 || salt
    ps_end = db.find(b'\x01')
    if ps_end == -1 or any(x != 0x00 for x in db[:ps_end]):
        return False

    salt = db[ps_end + 1:]
    if len(salt) != salt_len:
        return False

    # Recompute hash
    prefix = b'\x00' * 8
    m_prime = prefix + m_hash + salt
    h_prime = hash_func(m_prime).digest()

    return h == h_prime

def main(trigger: int | None):
    host = "141.223.175.203"
    # host = "44.210.92.118"
    port = 1337
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    if trigger is not None:
        sock.send(bytes([trigger]), socket.MSG_OOB)
    
    client_random = b"\x00" * 32
    session_id = b"\x00"
    client_x25519_key = x25519.X25519PrivateKey.generate()
    client_hello = build_client_hello(client_random, session_id, client_x25519_key)
    sock.sendall(client_hello)

    server_hello, _, application_data = recv_server_hello(sock)
    server_random, server_x25519_pubkey_bytes = extract_server_hello_info(server_hello)
    #print("server_random", server_random.hex())
    #print("server_pubkey", server_x25519_pubkey_bytes.hex())

    server_x25519_pubkey = x25519.X25519PublicKey.from_public_bytes(server_x25519_pubkey_bytes)
    shared_secret = client_x25519_key.exchange(server_x25519_pubkey)

    client_hello_handshake = client_hello[5:]
    server_hello_handshake = server_hello[5:]
    
    transcript = sha384()
    transcript.update(client_hello_handshake)
    transcript.update(server_hello_handshake)
    thash = transcript.digest()

    backend = default_backend()
    early_secret = HKDF(
        algorithm=hashes.SHA384(),
        length=48,
        info=b"\x00",
        salt=b"\x00",
        backend=backend
    )._extract(b"\x00"*48)

    empty_hash = sha384(b"").digest()
    derived_secret = HKDF_Expand_Label(
        key=early_secret,
        algorithm=hashes.SHA384(),
        length=48,
        label="derived",
        context=empty_hash,
        backend=backend
    )
    handshake_secret = HKDF(
        algorithm=hashes.SHA384(),
        salt=derived_secret,
        info=None,
        backend=backend,
        length=48
    )._extract(shared_secret)

    server_hs_traffic_secret = HKDF_Expand_Label(
        context=thash,
        length=48,
        algorithm=hashes.SHA384(),
        label="s hs traffic",
        backend=backend,
        key=handshake_secret
    )

    server_hs_key = HKDF_Expand_Label(
        algorithm=hashes.SHA384(),
        length=32,
        context=b"",
        label="key",
        backend=backend,
        key=server_hs_traffic_secret
    )
    server_hs_iv = HKDF_Expand_Label(
        algorithm=hashes.SHA384(),
        length=12,
        context=b"",
        label="iv",
        backend=backend,
        key=server_hs_traffic_secret
    )

    result = []
    for i, record in enumerate(application_data):
        decrypted = decrypt_tls_record(server_hs_key, server_hs_iv, record, i)
        result.append(decrypted)
        #print(decrypted.hex())
        #print("-"*10)

    sock.close()

    # ---

    extensions = result[0]

    certification = result[1].rstrip(b'\x00')
    _, length = certification[0], certification[1:4]
    current = 4
    current += 4
    length = bytes_to_long(certification[current : current + 3])
    current += 3

    cert = load_der_x509_certificate(certification[current : current + length])
    public_key = cert.public_key()


    certVerify = result[2]
    _, length = certVerify[0], bytes_to_long(certVerify[1:4])
    current = 4
    assert certVerify[current : current + 2] == b'\x08\x04'
    current += 2
    length = bytes_to_long(certVerify[current : current + 2])
    current += 2
    
    signature = certVerify[current : current + length]

    hasher = hashes.SHA256()
    signed_data = b' ' * 64 +  \
                  b'TLS 1.3, server CertificateVerify' +  \
                  b'\x00' +  \
                  sha384(
                      client_hello[5:] + \
                      server_hello[5:] + \
                      extensions[:-1] + \
                      certification[:-1]
                  ).digest()
    
    #print(client_hello[:10])
    #print(server_hello[:10])
    #print(extensions)
    #print(certification[:10], certification[-10:])

    n = public_key.public_numbers().n
    e = public_key.public_numbers().e
    
    try:
        #calc_sig = pow(bytes_to_long(signature), e, n).to_bytes((n.bit_length() + 7) // 8, byteorder='big')
        #h = sha256(signed_data).digest()
        #print(pss_verify(h, calc_sig))

        public_key.verify(
            signature,
            signed_data,
            padding.PSS(
                mgf=padding.MGF1(hasher),
                salt_length=hasher.digest_size # 32
            ),
            hasher
        )

        print('SUCCESS')

        from Crypto.PublicKey import RSA
        from Crypto.Signature import pss
        from Crypto.Hash import SHA256

        public_key = RSA.construct((n, e))
        hash = SHA256.new(signed_data)
        pss.new(public_key).verify(hash, signature)
        return True
    except:
        return False
    

if __name__ == "__main__":
    for _ in range(1):
        flag = main(trigger=0)
        print('success' if flag else 'fail')