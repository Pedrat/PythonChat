import select, socket, sys,os
from pychat_util import Room, Hall, Player
import pychat_util

READ_BUFFER = 4096
messages=[]
if len(sys.argv) < 2:
    print("Usage: Python3 client.py [hostname]", file = sys.stderr) #Msg de Erro Customizada
    sys.exit(1)
else: #Cria a socket de conexão ao sv
    server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_connection.connect((sys.argv[1], pychat_util.PORT))

def prompt(): #Input do User
    print('>', end=' ', flush = True) # FLush é boa pratica

print("Connected to server\nWelcome! Take a seat\n...We don't appear to have seats...\nHope you enjoy! :)")
msg_prefix = '' #Para o sv nao confundir com o prompt inicial de nome

socket_list = [sys.stdin, server_connection] #Lista de sockets

while True:
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], []) #Organiza tudo em listas(User,Mensagens,Erros)
    for s in read_sockets:
        if s is server_connection: # Se existe uma msg a vir, recebe
            #os.system("clear")
            msg = s.recv(READ_BUFFER)
            #messages.append(msg.decode())
            #for x in messages:
                #print(x)
            if not msg: #Se não, significa que o server esta em baixo.
                print("Server down!")
                sys.exit(2)
            else:
                if msg == pychat_util.QUIT_STRING.encode(): #Se a msg for igual a <quit>
                    sys.stdout.write('Bye\n')
                    sys.exit(2)
                else: #Manda msg
                    sys.stdout.write(msg.decode())
                    if 'Please tell us your name' in msg.decode(): #Se a string inicial ainda la estiver
                        msg_prefix = 'name: ' # identifier for name
                    else:
                        msg_prefix = ''
                    prompt()

        else:
            msg = msg_prefix + sys.stdin.readline()
            server_connection.sendall(msg.encode())
