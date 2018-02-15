import select, socket, sys, pdb
from pychat_util import Hall, Room, Player
import pychat_util

READ_BUFFER = 4096

host = sys.argv[1] if len(sys.argv) >= 2 else '' #Se não ser introduzido nada ele faz default para o localhost
listen_sock = pychat_util.create_socket((host, pychat_util.PORT)) #Cria a socketServer
hall = Hall()
connection_list = []
connection_list.append(listen_sock) #Quem esta connectado

while True:
    # Player.fileno() ####Debuggin
    read_players, write_players, error_sockets = select.select(connection_list, [], []) #Organiza tudo em listas(User,Mensagens,Erros)
    for player in read_players:
        if player is listen_sock: #Nova conexão, user é um socket
            new_socket, add = player.accept()
            new_player = Player(new_socket)
            connection_list.append(new_player)
            hall.welcome_new(new_player)

        else: # Nova mensagem
            msg = player.socket.recv(READ_BUFFER)
            if msg:
                msg = msg.decode()    #.lower()
                hall.handle_msg(player, msg)
            else: #User disconecta
                player.socket.close()
                connection_list.remove(player)

    for sock in error_sockets: # Fecha error sockets
        sock.close()
        connection_list.remove(sock)
