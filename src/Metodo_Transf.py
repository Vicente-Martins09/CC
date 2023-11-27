import threading
import socket
import time
import ast
import os

MTU = 1200
ID_SIZE = 4
# CHECK_SUM = 4
# TamanhoBloco = MTU - (ID_SIZE + CHECK_SUM)
TamanhoBloco = MTU - ID_SIZE

socketTCP_lock = threading.Lock()

def send_update(message, socketTCP):
    with socketTCP_lock:
        socketTCP.send(message.encode())

# Método que o Node usa para transferir um ficheiro
def transf_file(fileInfo, caminho_pasta, fileName, socketTCP, port):
    nodeIPs = fileInfo[1]
    numBlocos = int(fileInfo[0])
    tentativasMAX = 3
    print(nodeIPs)
    print(numBlocos)
    
    file = open(os.path.join(caminho_pasta, fileName), "wb")
    file_expectedsize = numBlocos * TamanhoBloco + 1
    file.seek(file_expectedsize + 1)
    file.write(b"\0")
    file_size = 0
    
    socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    blocos = []
    aux = 1
    i = 1
    pedido = 1
    while numBlocos >= i:
        pedeBloco = f"{fileName}|{i}"
        print(pedeBloco)
        socketUDP.sendto(pedeBloco.encode(), (nodeIPs[0][0], port))  # ip do um node na lista de nodes  têm de ser feito uma espera de 3 ms e se nao receber o bloco volta a pedir(3 vezes máximo se não der pede a outro node)

        socketUDP.settimeout(2.0)
        data = None
        while pedido <= tentativasMAX:
            try:
                data, addr = socketUDP.recvfrom(MTU)
            except socket.timeout:
                print("Timeout - retrying...")
                pedido += 1
                continue
            
            if data:
                # print(data.decode())
                break
            
        if data:    
            num_Bloco = int.from_bytes(data[:4], byteorder='big')
            conteudoFile = data[4:]
            file_size += len(conteudoFile)
            
            posInic = TamanhoBloco * (num_Bloco-1)
            file.seek(posInic)
            file.write(conteudoFile)
            blocos.append(i)
            
            mensagemUpdateBlocos = f"updblc . {fileName} . {blocos}\n"  # o i passa a ser um array com os blocos que ja foram escritos, atualiza o código
            send_update(mensagemUpdateBlocos, socketTCP)
            print("enviei bloc", blocos)
            blocos = []
        i += 1
    
    file.seek(0)
    file.truncate(file_size)
    file.close()
    socketUDP.close()

# Método que o Node usa para enviar um ficheiro
def env_File(caminho_pasta, fileName, numBloco, socketUDP, addr):     
    caminhoFile = os.path.join(caminho_pasta, fileName)
      
    with open(caminhoFile, "rb") as file:
        posInic = TamanhoBloco * (numBloco-1)
        file.seek(posInic)

        data = file.read(TamanhoBloco)
        if not data:
            print("Erro a ler a data")  
            
        numBloco_bytes = numBloco.to_bytes(4, 'big')

        dataEnviar = numBloco_bytes + data
        # checksum = len(dataEnviar)
         
    # print(dataEnviar)

    socketUDP.sendto(dataEnviar, addr)
