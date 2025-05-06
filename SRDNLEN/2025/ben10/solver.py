import base64, zlib

a = "eyJ1c2VybmFtZSI6Im5lbW8ifQ.Z4xQjw.Op6YOO3BsgCzWNdUUdZ7scScisU"
print(zlib.decompress(base64.urlsafe_b64decode(a)))