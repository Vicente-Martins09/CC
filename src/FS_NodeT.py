import threading
import select
import socket
import sys
import ast
import os

MTU = 1200
ID_SIZE = 4
TamanhoBloco = MTU - ID_SIZE
ipNode = socket.gethostbyname(socket.gethostname())

udpAtivo = True

def set_udp_false():
    global udpAtivo
    udpAtivo = False

print(ipNode)

if len(sys.argv) != 4:
    print("Uso: python cliente.py <IP do host> <Número da Porta> <Pasta com os ficheiros>")
    sys.exit(1)

# Configuração do cliente
host = sys.argv[1]  # Endereço IP do servidor
port = int(sys.argv[2])  # Porta que o servidor está ouvindo

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
        n_Blocos = calcula_num_blocos(caminho_ficheiro)
        ficheiros_comBlocos.append((filename, n_Blocos))
        
    return ficheiros_comBlocos
        
# Cria uma lista com o nome dos ficheiros e o número de blocos ocupados dentro de uma pasta
caminho_pasta = sys.argv[3] 
ficheiros_comBlocos = calcula_blocos_por_ficheiro(caminho_pasta)

# print(ficheiros_comBlocos)

def transf_file(fileInfo, fileName):
    nodeIPs = fileInfo[1]
    numBlocos = int(fileInfo[0])
    # print("teste", numBlocos)
    print(nodeIPs)
    
    file = open(os.path.join(caminho_pasta, fileName), "wb")
    file_size = numBlocos * TamanhoBloco
    file.seek(file_size-1)
    file.write(b"\0")
    print(file_size)
    
    socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # socketUDP.bind((ipNode, 9090))
    
    i = 1
    while numBlocos >= i:
        pedeBloco = f"{fileName}|{i}|{ipNode}"
        print(pedeBloco)
        socketUDP.sendto(pedeBloco.encode(), (nodeIPs[0], port))  # ip do um node na lista de nodes
        # socketUDP.sendto(pedeBloco.encode(), ('127.0.1.1', port))
    
    
        data, addr = socketUDP.recvfrom(MTU)
        print(data.decode())
        if not data:
            print("Erro a receber")
            break
        
        num_Bloco = int.from_bytes(data[:4], byteorder='big')
        conteudoFile = data[4:]
        
        posInic = TamanhoBloco * (num_Bloco-1)
        file.seek(posInic)
        file.write(conteudoFile)
        
        
        i += 1
    
    if i >= numBlocos: file.close()
    socketUDP.close()
    
        
def tracker_protocol():
    # Cria um socket do tipo TCP
    socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Conecta-se ao servidor
    socketTCP.connect((host, port))
    
    # Cria a mensagem que é enviada assim que o node conecta ao tracker
    mensagemFiles = f"files . {ipNode} . " + ' | '.join([f"{file}-{blocks}" for file, blocks in ficheiros_comBlocos])
    socketTCP.send(mensagemFiles.encode())
    
    print("Escreva 'comandos' em caso de dúvida")
    
    while True:
        
        user_input = input("Selecione um comando: ")
        comando = user_input.strip().lower().split(' ')
        
        if comando[0] == "quit":
            socketTCP.send("quit . ".encode())
            print("Desligada a conexão ao servidor")
            set_udp_false()
            break
        
        elif comando[0] == "get":
            nomeFicheiro = comando[1]  # Obtém o nome do arquivo
            mensagemGet = f"get . {nomeFicheiro}"
            socketTCP.send(mensagemGet.encode())
            fileInfo = socketTCP.recv(1024).decode() # (nºblocos, ips)
            fileInfo = ast.literal_eval(fileInfo)
            transf_file(fileInfo, nomeFicheiro)
        
        elif comando[0] == "comandos":
            print("\tquit: Desligar a ligação ao servidor.")
            print("\tget 'file_name': Digite o nome do file que pretende transferir no lugar de file_name.")
            print("\tcomandos: Lista os comandos existentes.")
        
    socketTCP.close()

def env_File(fileName, numBloco, socketUDP, addr):     
    caminhoFile = os.path.join(caminho_pasta, fileName)
      
    with open(caminhoFile, "rb") as file:
        posInic = TamanhoBloco * (numBloco-1)
        file.seek(posInic)

        data = file.read(TamanhoBloco)
        if not data:
            print("Erro a ler a data")  
            
        numBloco_bytes = numBloco.to_bytes(4, 'big')

        dataEnviar = numBloco_bytes + data
         
    print(dataEnviar)

    socketUDP.sendto(dataEnviar, addr)

     
def transfer_protocol():
    print(ipNode)
    socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # socketUDP.bind(('127.0.1.1', 9090))
    socketUDP.bind((ipNode, 9090)) 
    
    while udpAtivo:
        ready, _, _ = select.select([socketUDP], [], [], 1.0)
        
        if ready:
            data, addr = socketUDP.recvfrom(1024)
            infoFile = data.decode()
        
            print(addr)
            
            fileName, numBloco, ipRetorno = infoFile.split("|")
            env_File(fileName, int(numBloco), socketUDP, addr)
            ready = False
        
tracker_thread = threading.Thread(target = tracker_protocol)
tracker_thread.start()