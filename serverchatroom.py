import select,socket,sys, threading,time,os
from headerchatroom import LOBBY, SALAS, USER
import headerchatroom
os.system("clear")
BUFFER=8192

host = sys.argv[1] #Recebe Host
listen_sock = headerchatroom.criasocket((host,headerchatroom.PORT)) #Cria a socket
lobby = LOBBY()
online=[]
online.append(listen_sock)  #Quem esta conectado


def server():
    while True:
        #print(threading.active_count())
        read_users, write_users,error_sockets = select.select(online, [], [])
        #Organiza tudo em listas(User,Mensagens,Erros)
        for user in read_users:

            if user is listen_sock: #Nova conexão, user é um socket
                new_socket, add = user.accept()
                new_user = USER(new_socket)
                online.append(new_user)
                lobby.saudacao(new_user)

            else: # Nova mensagem
                msg = user.socket.recv(BUFFER)
                if msg:
                    msg = msg.decode()
                    lobby.msghandler(user, msg)
                else: #User disconecta
                    user.socket.close()
                    online.remove(user)

        for sock in error_sockets: # Fecha error sockets
            sock.close()
            online.remove(sock)

def svinput():
    while True:
        ola=sys.stdin.readline()
        lobby.svinput(ola,online)

var2 = threading.Thread(target=svinput)#, #args=(sys.stdin.readline()))
var2.daemon=True
var2.start()

var = threading.Thread(target=server)
var.daemon=True
var.start()
while 1:
    s=0
