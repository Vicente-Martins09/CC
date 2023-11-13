import threading
import socket
import sys
import os

MTU = 1200
ID_SIZE = 4
TamanhoBloco = MTU - ID_SIZE
ipNode = socket.gethostbyname(socket.gethostname())

exit_event = threading.Event()

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
    nodeIP = fileInfo[1]
    numBlocos = fileInfo[0]
    
    socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # socketUDP.connect((nodeIP, port))
    socketUDP.connect('127.0.1.1', port)
    
    socketUDP.send(fileName.encode())
    
    ficheiroRecebido = b''
    while True:
        data, addr = socketUDP.recvfrom(MTU)
        
        if not data:
            break
        
        num_Bloco = int.from_bytes(data[:4], byteorder= 'big')
        blocosRec += num_Bloco
        conteudoFile = data[4:]
        
        ficheiroRecebido += conteudoFile
        
        if len(ficheiroRecebido) >= numBlocos * TamanhoBloco:
            break
    
    socketUDP.close()
    
    caminho_newFile = os.path.join(caminho_pasta, fileName)
    
    with open(caminho_newFile, "wb") as file:
        file.write(ficheiroRecebido)
        
def tracker_protocol(udp_thread):
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
            exit_event.set()
            break
        
        elif comando[0] == "get":
            nomeFicheiro = comando[1]  # Obtém o nome do arquivo
            mensagemGet = f"get . {nomeFicheiro}"
            socketTCP.send(mensagemGet.encode())
            fileInfo = socketTCP.recv(1024).decode()
            transf_file(fileInfo, nomeFicheiro)
            print(fileInfo)
        
        elif comando[0] == "comandos":
            print("\tquit: Desligar a ligação ao servidor.")
            print("\tget 'file_name': Digite o nome do file que pretende transferir no lugar de file_name.")
            print("\tcomandos: Lista os comandos existentes.")
        
    socketTCP.close()

def env_File(fileName, socketUDP, addr):
    
    for file in ficheiros_comBlocos:
        if fileName == file[0]:
            num_blocks = file[1]
         
    caminhoFile = os.path.join(caminho_pasta, fileName)
       
    with open(caminhoFile, "rb") as file:
        while True:
            data = file.read(TamanhoBloco)

            if not data:
                break  

            block_number_bytes = num_blocks.to_bytes(4, 'big')

            data_to_send = block_number_bytes + data

            socketUDP.send(data_to_send, (addr,))

            num_blocks -= 1 
            
            if num_blocks == 0:
                break

    socketUDP.send(b"")
    socketUDP.close()
     
def transfer_protocol():
    socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketUDP.bind(('127.0.1.1', 9090)) 
    
    while not exit_event.is_set():
        data, addr = socketUDP.recvfrom(1024)
        fileName = data.decode()
        
        env_File(fileName, socketUDP, addr)
        
   
udp_thread = threading.Thread(target = transfer_protocol)
udp_thread.start()
tracker_thread = threading.Thread(target = tracker_protocol, args= (udp_thread,))
tracker_thread.start()

udp_thread.join()
tracker_thread.join()