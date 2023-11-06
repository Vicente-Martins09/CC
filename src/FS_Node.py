import socket
import sys
import os

if len(sys.argv) != 4:
    print("Uso: python cliente.py <IP do host> <Número da Porta> <Pasta com os ficheiros>")
    sys.exit(1)

print("Escreva 'comandos' em caso de dúvida")

# Configuração do cliente
host = sys.argv[1]  # Endereço IP do servidor
port = int(sys.argv[2])  # Porta que o servidor está ouvindo


# Cria um socket do tipo TCP
node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta-se ao servidor
node_socket.connect((host, port))

# Cria uma lista com o nome dos ficheiros dentro de uma pasta
# Recolhe a porta UDP de um node
# Cria a mensagem que é enviada assim que o node conecta ao tracker
nomesFicheiros = os.listdir(sys.argv[3])
message = f"files . {' | '.join(nomesFicheiros)}" # meter o n de ficheiros aqui?

# Envia a mensagem para o servidor
node_socket.send(message.encode())

# Deixar o Node ativo enquanto não for desligado

while True:
    
    user_input = input("Selecione um comando: ")
    comando = user_input.strip().lower().split(' ')
    
    if comando[0] == "quit":
        node_socket.send("quit . ".encode())
        print("Desligada a conexão ao servidor")
        break
    
    elif comando[0] == "comandos":
        print("\tquit: Desligar a ligação ao servidor.")
        print("\get 'file_name': Digite o nome do file que pretende transferir no lugar de file_name.")
        print("\tcomandos: Lista os comandos existentes.")
        
    elif comando[0] == "get":
        nomeFicheiro = comando[1]  # Obtém o nome do arquivo
        message = f"get . {nomeFicheiro}"
        node_socket.send(message.encode())
        resposta = node_socket.recv(1024).decode('utf-8')
        print(resposta)

# Fecha a conexão com o servidor
node_socket.close()
