import hashlib, helper_gpu
from Crypto.Util.number import long_to_bytes


formal = hashlib.sha256(b'1234').hexdigest()

gpu = helper_gpu.HelperGPU('1234')
gpu.convert_string_to_binary()
gpu.add_padding()
gpu.break_message_into_chunks()

print(formal)
print(gpu.digest())