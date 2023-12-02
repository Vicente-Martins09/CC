import threading
import select
import socket
import time
import sys
import ast
import os

from Metodo_Transf import *

MTU = 1200
ID_SIZE = 4
CHECK_SUM = 2
TamanhoBloco = MTU - (ID_SIZE + CHECK_SUM)
udpAtivo = True

# Método que desliga a socket udp de um node que foi desconectado 
def set_udp_false():
    global udpAtivo
    udpAtivo = False

if len(sys.argv) != 4:
    print("Uso: python cliente.py <IP do host> <Número da Porta> <Pasta com os ficheiros>")
    sys.exit(1)

# Configuração do cliente
host = sys.argv[1]  # Endereço IP do servidor
port = int(sys.argv[2])  # Porta que o servidor está ouvindo

# Métodos que prepara a lista dos ficheiros e os blocos que um node têm e vai colocar na mensagem de conexão ao tracker
def calcula_num_blocos(caminho_ficheiro):
    tamanhoFicheiro = os.path.getsize(caminho_ficheiro)
    numBlocos = tamanhoFicheiro // TamanhoBloco
    
    if tamanhoFicheiro % TamanhoBloco != 0:
        numBlocos += 1

    return numBlocos

def calcula_blocos_por_ficheiro(caminho_pasta):
    ficheiros_comBlocos = []
    
    for filename in os.listdir(caminho_pasta):
        caminho_ficheiro = os.path.join(caminho_pasta, filename)
        blocosTotais = calcula_num_blocos(caminho_ficheiro)
        ficheiros_comBlocos.append((filename, blocosTotais))
        
    return ficheiros_comBlocos
        
# Cria uma lista com o nome dos ficheiros e o número de blocos ocupados dentro de uma pasta
caminho_pasta = sys.argv[3] 
ficheiros_comBlocos = calcula_blocos_por_ficheiro(caminho_pasta)   
 
# Fim dos métodos de construção da lista de blocos e ficheiros

# Método que estabelece a comunicação de um Node com o Tracker    
def tracker_protocol():
    # Cria um socket do tipo TCP
    socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Conecta-se ao servidor
    socketTCP.connect((host, port))
    
    # Cria a mensagem que é enviada assim que o node conecta ao tracker
    mensagemFiles = f"files/" + ' | '.join([f"{file}-{blocks}" for file, blocks in ficheiros_comBlocos]) + '\n'
    socketTCP.send(mensagemFiles.encode())
    
    print("Escreva 'comandos' em caso de dúvida")
    
    while True:
        
        user_input = input("Selecione um comando: ")
        comando = user_input.strip().lower().split(' ')
        
        if comando[0] == "quit":
            socketTCP.send("quit/\n".encode())
            print("Desligada a conexão ao servidor")
            set_udp_false()
            break
        
        elif comando[0] == "get":
            nomeFicheiro = comando[1]  # Obtém o nome do arquivo
            mensagemGet = f"get/{nomeFicheiro}\n"
            socketTCP.send(mensagemGet.encode())
            fileInfo_str = socketTCP.recv(1024).decode() # (nºblocos, ips)
            if fileInfo_str == "None":
                print("O ficheiro que está a tentar transferir não existe")
            else:
                fileInfo = ast.literal_eval(fileInfo_str)
                transf_file(fileInfo, caminho_pasta,  nomeFicheiro, socketTCP, port)
                mensagemUpdate = f"updfin/{nomeFicheiro}\n"
                print("enviei fim")
                socketTCP.send(mensagemUpdate.encode())
       
        elif comando[0] == "comandos":
            print("\tquit: Desligar a ligação ao servidor.")
            print("\tget 'file_name': Digite o nome do file que pretende transferir no lugar de file_name.")
            print("\tcomandos: Lista os comandos existentes.")
        
    socketTCP.close()
    
# Método que mantém a porta udp de um node aberta à espera de pedidos de transferência 
def transfer_protocol():
    socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketUDP.bind(('0.0.0.0', 9090)) 
    
    while udpAtivo:
        ready, _, _ = select.select([socketUDP], [], [], 1.0)
        
        if ready:
            data, addr = socketUDP.recvfrom(1024)
            infoFile = data.decode()
            #print(infoFile)
            #print(addr)
            if infoFile == "Ping":
                reply = "Pong"
                socketUDP.sendto(reply.encode(), addr)
                #print("enviei", reply)
            else:
                fileName, numBloco = infoFile.split("|")
                #print(numBloco)
                env_File(caminho_pasta, fileName, int(numBloco), socketUDP, addr)
            ready = False
   
udp_thread = threading.Thread(target = transfer_protocol)
udp_thread.start()
tracker_thread = threading.Thread(target = tracker_protocol)
tracker_thread.start()

udp_thread.join()
tracker_thread.join()