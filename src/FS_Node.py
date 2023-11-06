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
socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta-se ao servidor
socketTCP.connect((host, port))


caminho_pasta = sys.argv[3]

ficheiros_blocos = []

for filename in os.listdir(caminho_pasta):
    caminho_ficheiro = os.path.join(caminho_pasta, filename)
    stat_info = os.stat(caminho_ficheiro)
    n_blocos = stat_info.st_blocks
    ficheiros_blocos.append((filename, n_blocos))

# print(ficheiros_blocos)
# print(' | '.join([f"{file}-{blocks}" for file, blocks in ficheiros_blocos]))

# Cria uma lista com o nome dos ficheiros e o número de blocos ocupados dentro de uma pasta
# Cria a mensagem que é enviada assim que o node conecta ao tracker
mensagemFiles = "files . " + ' | '.join([f"{file}-{blocks}" for file, blocks in ficheiros_blocos])


# Envia a mensagem para o servidor
socketTCP.send(mensagemFiles.encode())

# Deixar o Node ativo enquanto não for desligado

def transf_file(nodeIP, fileName):
    
    socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketUDP.bind((nodeIP, port))
    
    socketUDP.send(fileName.encode())

while True:
    
    user_input = input("Selecione um comando: ")
    comando = user_input.strip().lower().split(' ')
    
    if comando[0] == "quit":
        socketTCP.send("quit . ".encode())
        print("Desligada a conexão ao servidor")
        break
    
    elif comando[0] == "get":
        nomeFicheiro = comando[1]  # Obtém o nome do arquivo
        mensagemGet = f"get . {nomeFicheiro}"
        socketTCP.send(mensagemGet.encode())
        resposta = socketTCP.recv(1024).decode()
        print(resposta)
    
    elif comando[0] == "comandos":
        print("\tquit: Desligar a ligação ao servidor.")
        print("\get 'file_name': Digite o nome do file que pretende transferir no lugar de file_name.")
        print("\tcomandos: Lista os comandos existentes.")
        

# Fecha a conexão com o servidor
socketTCP.close()
