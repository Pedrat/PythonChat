import socket, datetime, os,sys

PORT = 4040 #Porta que ira ser usada sempre
messages=[] #Usado para logs de system
Mayday="/exit"
listaasneira=[]
listaasneiraaux=[]
svmsg=""

for x in open("listaAsneira.txt",'r'):
    listaasneira.append(x)


def criasocket(address): #Função para criar a socket de sv
    sv = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #Cria a socket em IPv4 e TCP/IP
    sv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Se exisir uma socket aberta, ele reusa-a
    sv.setblocking(0) #Não bloqueia caso receba uma empty data
    sv.bind(address) #Faz bind ad socket
    sv.listen(27) #Começa a ouvir a socket por conexões.
    print("OUVINDO: ",address)
    return sv

class SALAS: #Class para todas as salas.
    def __init__(self,name):
        self.user=[] #Uma Lista com todos os users la dentro
        self.name = name #Nomes de salas
    def ENTRADA(self, utilizador): #Função para mandar uma msg de Saudações
        msg = b"Bem vindo,"+utilizador.name.encode()+b"  a sala:\n"+self.name.encode() #Saudações da room
        self.BROADCAST(utilizador,msg)
    def remove_user(self,utilizador): #Função para um utilizador sair da salas
        self.user.remove(utilizador) #Remove o user da sala
        msg = utilizador.name.encode() + b' saiu da sala\n'
        self.BROADCAST(utilizador,msg)
    def BROADCAST(self,utilizador,msg): #Função para broadcast de tudo
        for x in (msg.decode()).split():
            for y in listaasneira:
                if x in y:
                    msg=msg.replace(x.encode(),(b"*"*len(x)))
        msg = ((("[{} ".format(datetime.datetime.now().strftime("%H:%M:%S")).encode()))+utilizador.name.encode() + b']: ' + msg) #Formato standard de msg
        messages.append(msg.decode()) #Faz append para system logs
        for users in self.user: #Faz o broadcast em si.
            users.socket.sendall(msg)

class USER:
    def __init__(self,socket,name="Guest"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name

    def fileno(self): #Enumera as sockets
        return self.socket.fileno()


class LOBBY: #Class para o lobby
    def __init__(self):
        self.room={} #Nome da room
        self.pessoasemsala = {}
    def saudacao(self,novouser):
        novouser.socket.sendall(b'User:')

    def listasalas(self, user): #Lista todos as salas dsiponiveis
        if len(self.room) == 0:
            msg = "Nenhuma sala existe neste momento.\n"
            user.socket.sendall(msg.encode())
        else:
            msg = "Salas:\n"
            for sala in self.room:

                msg+= sala + ": "+str(len(self.room[sala].user))+ " Online\n"
            user.socket.sendall(msg.encode())
    def swearupdate(self):
        file=open("listaAsneira.txt",'a')
        while 1:
            aux=input("Qual asneira?")
            if aux=="exit":
                file.close()
                del listaasneira[:]
                for x in open("listaAsneira.txt",'r'):
                    listaasneira.append(x)
                break
            else:
                file.write(aux+'\n')
                listaasneira.append(aux)

    def save_log(self):
        valida=0
        date = datetime.datetime.now().strftime("%d-%m-%Y")
        nome = "Chatroom"+date+".txt" #Da o nome ao ficheiro de logs
        for x in os.popen("ls"): #Checks se existe o ficheiro com mm nome
            if nome in x:
                valida=1
        if valida == 1:
            #print("FICHEIRO EXISTE")
            file=open(nome,'a') #Adiciona ao ficheiro se ele existir
            for x in messages:
                file.write(x)
            file.close()
            del messages[:] #Da clear do buffer das msg para não repetir as msg
        else: #everyday(s
            #print("Ficheiro não existe")
            file=open(nome,'w') #Cria o ficheiro se não existir
            for x in messages:
                file.write(x)
            file.close()
            del messages[:]

    def svinput(self,svmsg):
        #self.msghandler("SERVER",svmsg)
        if "/save" in svmsg:
            self.save_log()
        elif "/update" in svmsg:
            self.swearupdate()


    def msghandler(self,user,msg):
        print(("[{} ".format(datetime.datetime.now().strftime("%H:%M:%S")))+user.name + "] says: " + msg) #O que o user diz no sv
        comandos=b'Comandos:\n/list Para listar as salas disponiveis\n/join room_name para criar,juntar-se, ou mudar de sala\n/help Para mostrar comandos\n/exit Para desconectar-se\n/save Para salvar os logs\n'
        if "name: " in msg: #Faz check se o user é novo ou não, se for, guarda o nome
            name = msg.split()[1]
            user.name = name
            auxmsg = ("[{}]Nova conexão de: {}".format(datetime.datetime.now().strftime("%H:%M:%S"),user.name))+'\n'
            messages.append(auxmsg)
            print("Nova conexão de: ", user.name)
            user.socket.sendall(comandos)
        elif "/join" in msg:
            same_room = False
            if len(msg.split())>=2:
                room_name = msg.split()[1] #Guarda o nome da sala criada
                if user.name in self.pessoasemsala: # User a fazer a troca
                    if self.pessoasemsala[user.name] == room_name: # Faz check se o user esta na sala que esta a tentar criar/juntar
                        user.socket.sendall(b'Ja se encontra na sala: ' + room_name.encode())
                        same_room = True
                    else: # switch
                        old_room = self.pessoasemsala[user.name] #Guarda a room em que o user estava
                        self.room[old_room].remove_user(user) #E remove o user da sala antiga
                if not same_room: #Se o user não estiver na sala
                    if not room_name in self.room: # Criação de new room
                        new_room = SALAS(room_name)
                        self.room[room_name] = new_room #Faz a nova room
                    self.room[room_name].user.append(user) #Junta o user a nova room
                    self.room[room_name].ENTRADA(user)
                    self.pessoasemsala[user.name] = room_name #User esta nessa room
            else:
                user.socket.sendall(comandos)
        elif "/list" in msg or "/list" in svmsg:
            self.listasalas(user)

        elif "/help" in msg or "/help" in svmsg  :
            user.socket.sendall(comandos)
        elif "/exit" in msg:
            user.socket.sendall(b'/exit')
            self.remove_user(user)

        elif "/save" in msg or "/save" in svmsg:
            self.save_log()
        elif "/update" in msg or "/update" in svmsg:
            self.swearupdate()

        else:
            # Faz check se o user esta em uma sala
            if user.name in self.pessoasemsala:
                self.room[self.pessoasemsala[user.name]].BROADCAST(user, msg.encode())
            else:
                msg ='Junta-te a uma sala primeiro. \n/list Para veres quais estao disponiveis\n/join para criares ou juntares'
                user.socket.sendall(msg.encode())


    def remove_user(self, user): #Função para remover user
        if user.name in self.pessoasemsala:
            self.room[self.pessoasemsala[user.name]].remove_user(user)
            del self.pessoasemsala[user.name]
        print("User: " + user.name + "  disconectou-se\n")
