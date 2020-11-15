from pwn import *

port = 12345

p = remote("127.0.0.1", port)

p.send("GET / HTTP/1.0\r\nContent-length: 200")

p.interactive()