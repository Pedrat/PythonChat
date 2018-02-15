import socket, pdb,datetime,os

MAX_CLIENTS = 30 #Nº Maximo de Clientes
PORT = 22222 # Default Port
QUIT_STRING = '/$exit'
messages=[]

def create_socket(address): #Função para criar a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Cria a socket em si
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Se existir uma socket ja aberta, re-usa o address
    s.setblocking(0) #Não bloqueia caso exista uma empty data
    s.bind(address) #Faz bind
    s.listen(MAX_CLIENTS) # Começa a ouvir
    print("Now listening at ", address)
    return s

class Hall: #Class para o lobby
    def __init__(self):
        self.rooms = {} # {room_name: Room}
        self.room_player_map = {} # {playerName: roomName}

    def welcome_new(self, new_player): #Função de um user novo
        new_player.socket.sendall(b'Welcome to pychat.\nPlease tell us your name:\n')

    def list_rooms(self, player): # Lista os rooms
        if len(self.rooms) == 0:
            msg = 'Oops, no active rooms currently. Create your own!\n' \
                + 'Use [/join> room_name] to create a room.\n'
            player.socket.sendall(msg.encode())
        else:
            msg = 'Listing current rooms...\n'
            for room in self.rooms:
                msg += room + ": " + str(len(self.rooms[room].players)) + " player(s)\n"
            player.socket.sendall(msg.encode())

    def save_log(self): #Guarda os logs dos servers
        valida = 0
        dateee= datetime.datetime.now().strftime("%D")
        dateee=dateee.split("/")
        nome = "Chatroom"+dateee[1]+dateee[0]+dateee[2]+".txt" #Da o nome ao ficheiro a ser criado diariamente
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
        else:
            #print("Ficheiro não existe")
            file=open(nome,'w') #Cria o ficheiro se não existir
            for x in messages:
                file.write(x)
            file.close()
            del messages[:]

    def handle_msg(self, player, msg):
        #Comandos
        instructions = b'Instructions:\n/list to list all rooms\n/join room_name to join/create/switch to a room\n/help to show commands\n/exit to quit\n/save to save logs\n'
        print(("[{} ".format(datetime.datetime.now().strftime("%H:%M:%S")))+player.name + "] says: " + msg) #O que o user diz como log em sv
        if "name:" in msg: #Faz check se o user é novo ou não, se for, guarda o nome
            name = msg.split()[1]
            player.name = name
            #dating=datetime.datetime.now().strftime("%H:%M:%S")
            auxmsg = ("[{}]New connection from: {}".format(datetime.datetime.now().strftime("%H:%M:%S"),player.name))+'\n'
            #print("AUXMSG",auxmsg)
            messages.append(auxmsg)
            print("New connection from: ", player.name)
            player.socket.sendall(instructions)

        elif "/join" in msg:
            same_room = False
            if len(msg.split()) >= 2: # Faz check se o commando foi correctamente introduzido
                room_name = msg.split()[1] #Guarda         #for users in self.user:
            #user.socket.sendall(msg.encode())so o nome que o user quiz dar a sala
                if player.name in self.room_player_map: # Player a fazer a troca
                    if self.room_player_map[player.name] == room_name: # Faz check se o user esta na sala que esta a tentar criar/juntar
                        player.socket.sendall(b'You are already in room: ' + room_name.encode())
                        same_room = True
                    else: # switch
                        old_room = self.room_player_map[player.name] #Guarda a room em que o user estava
                        self.rooms[old_room].remove_player(player) #E remove o user da sala antiga
                if not same_room: #Se o user não estiver na sala
                    if not room_name in self.rooms: # Criação de new room
                        new_room = Room(room_name)
                        self.rooms[room_name] = new_room #Faz a nova room
                    self.rooms[room_name].players.append(player) #Junta o user a nova room
                    self.rooms[room_name].welcome_new(player)
                    self.room_player_map[player.name] = room_name #User esta nessa room
            else:
                player.socket.sendall(instructions)

        elif "/list" in msg:
            self.list_rooms(player)

        elif "/help" in msg:
            player.socket.sendall(instructions)

        elif "/exit" in msg:
            player.socket.sendall(QUIT_STRING.encode())
            self.remove_player(player)

        elif "/save" in msg:
            self.save_log()


        else:
            # Faz check se o user esta em uma sala
            if player.name in self.room_player_map:
                self.rooms[self.room_player_map[player.name]].broadcast(player, msg.encode())
            else:
                msg = 'You are currently not in any room! \n' \
                    + 'Use [/list] to see available rooms! \n' \
                    + 'Use [/join room_name] to join a room! \n'
                player.socket.sendall(msg.encode())

    def remove_player(self, player): #Função para remover players
        if player.name in self.room_player_map:
            self.rooms[self.room_player_map[player.name]].remove_player(player)
            del self.room_player_map[player.name]
        print("User: " + player.name + "  has disconnected\n")


class Room: #Class para as Salas
    def __init__(self, name):
        self.players = [] #Uma lista de sockets
        self.name = name

    def welcome_new(self, from_player):
        msg = self.name + " welcomes: " + from_player.name + '\n' #Rom da bem vindas ao novo player
        for player in self.players:
            player.socket.sendall(msg.encode())

    def broadcast(self, from_player, msg):
        #messages = []
        msg = (("[{} ".format(datetime.datetime.now().strftime("%H:%M:%S")).encode()))+from_player.name.encode() + b"]: " + msg
        messages.append(msg.decode())
        for player in self.players:
            player.socket.sendall(msg)

    def remove_player(self, player): #Função de um user sair da sala
        self.players.remove(player)
        leave_msg = player.name.encode() + b" has left the room\n"
        self.broadcast(player, leave_msg)

class Player:
    def __init__(self, socket, name = "new"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name

    def fileno(self): #Enumera as sockets
        return self.socket.fileno()
