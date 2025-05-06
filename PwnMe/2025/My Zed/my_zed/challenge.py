from openzedlib import openzed
import os
import zlib

FLAG = b'PWNME{..............}'


file = openzed.Openzed(b'zed', os.urandom(16), 'flag.txt', len(FLAG))

file.encrypt(FLAG)

file.generate_container()

with open(f"{file.filename}.ozed", "wb") as f:
	f.write(file.secure_container)
	

