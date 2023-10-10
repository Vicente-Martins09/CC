import socket
import sys
import os

if len(sys.argv) != 4:
    print("Uso: python cliente.py <IP do host> <Número da Porta> <Pasta com os ficheiros>")
    sys.exit(1)


# Configuração do cliente
host = sys.argv[1]  # Endereço IP do servidor
port = int(sys.argv[2])  # Porta que o servidor está ouvindo

# Recolhe uma lista de ficheiros dentro de uma pasta

nomesFicheiros = os.listdir(sys.argv[3])
message = ' | '.join(nomesFicheiros)

# Cria um socket do tipo TCP
node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta-se ao servidor
node_socket.connect((host, port))

# Envia a mensagem para o servidor
node_socket.send(message.encode())

# Deixar o Node ativo enquanto não for desligado

while True:
    
    user_input = input("Selecione um comando: ")
    
    if user_input.strip().lower() == "quit":
        print("Desligada a conexão ao servidor")
        break
    
    if user_input.strip().lower() == "comandos":
        print("\tquit: Desligar a ligação ao servidor.")
        print("\tcomandos: Lista os ccomandos existentes.")
    
    data = node_socket.recv(1024).decode('utf-8')
        


# Fecha a conexão com o servidor
node_socket.close()
