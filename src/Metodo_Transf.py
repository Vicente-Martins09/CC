import threading
import socket
import copy
import time
import ast
import os

from Metodo_SelecNodes import *

MTU = 1200
ID_SIZE = 4
CHECK_SUM = 2
TamanhoBloco = MTU - (ID_SIZE + CHECK_SUM)
tentativasMAX = 3

file_size = 0
blocos_em_falta = []

# Método utilizado para guardar a informação relativa aos blocos recebidos num dicionário
def guarda_bloco_recebido(fileName, numBlocoRec, conteudoFile, blocos_recebidos):
    if fileName in blocos_recebidos:
        blocos_recebidos[fileName].append((numBlocoRec, conteudoFile))
    else:
        blocos_recebidos[fileName] = [(numBlocoRec, conteudoFile)]
    #print(blocos_recebidos)

# Método que pede e recebe os blocos aos nodes
# Começa por determinar o tempo de espera que irá ser utilizado a cada pedido
# é enviando um ping ao node a que vai transferir o bloco e aguarda a resposta pong após receber a resposta calcula o intervalo de tempo
# De seguida pede o bloco ao node e aguarda o tempo de espera se não receber o bloco até o tempo de espera passar volta a pedir o bloco ao mesmo node
# Cada vez que é recida uma resposta é aumentado o peso do node com que esytá a falar por 1
# No caso de ter de voltar a pedir é decrementado em -2 o peso do mesmo node sendo assim definido a prioridade de cada node
# Cada vez que o node que está a transferir recebe um bloco ele envia um update ao tracker a dizer o bloco que recebeu
# e o peso que têm de atualizar ao node a quem transferiu o bloco
def pedir_file(filename, hostname, peso, port, blocos, blocos_recebidos, socketTCP):
    global file_size
    global blocos_em_falta

    print(hostname)
    ip = socket.gethostbyname(hostname)
    blocoUpd = []
    timeout = 10

    for i in blocos:
        #time.sleep(3)
        ping = 1
        socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socketUDP.settimeout(timeout)
        ti = time.time()
        request = "Ping"
        print("sented request", ip)
        socketUDP.sendto(request.encode(), (ip, port))
        while ping <= 2:
            try:
                data, addr = socketUDP.recvfrom(1024)
            except socket.timeout:
                print("Timeout - retrying - ping...", ip)
                socketUDP.sendto(request.encode(), (ip, port))
                peso -= 2
                ping += 1
                continue
            
            if data:
                peso += 1 
                break
        
        tf = time.time()
        td = (tf - ti) * 1000
        timeout = td
        if ping > 1: timeout = (timeout / 1000) * 1.5
        
        print(timeout, "tempo espera", ip)

        pedido = 1
        pedeBloco = f"{filename}|{i}"
        #print(ip, pedeBloco)
        socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socketUDP.settimeout(timeout)
        socketUDP.sendto(pedeBloco.encode(), (ip, port))

        data = None
        while pedido <= tentativasMAX:
            try:
                data, addr = socketUDP.recvfrom(MTU)
            except socket.timeout:
                print("Timeout - retrying...", ip)
                socketUDP.settimeout(timeout)
                socketUDP.sendto(pedeBloco.encode(), (ip, port))
                peso -= 2
                pedido += 1
                continue

            if data:
                if len(data) >= 2:
                    checksumRecebido = int.from_bytes(data[:2], 'big')
                    dataVerificar = data[2:]

                    checksum_dataRecebida = calcula_checksum(dataVerificar)

                    if checksumRecebido == checksum_dataRecebida:
                        peso += 1 
                        print("recebi bloco", i)
                        break
                    else: 
                        peso -= 1

        if data:   
            numBlocoRec = int.from_bytes(dataVerificar[:4], byteorder='big')
            conteudoFile = dataVerificar[4:]
            guarda_bloco_recebido(filename, numBlocoRec, conteudoFile, blocos_recebidos)
            file_size += len(conteudoFile)

            blocoUpd.append(i)

            mensagemUpdateBlocos = f"updblc/{filename}/{blocoUpd}/{peso}/{hostname}\n" 
            socketTCP.send(mensagemUpdateBlocos.encode())
            #print("enviei bloc", mensagemUpdateBlocos)
            blocoUpd = []
        else:
            print("Não recebi o bloco", i)
            blocos_em_falta.append(i)
        
        socketUDP.close()

# Método utilizado para escrever o ficheiro após terem sido transferidos todos os blocos de todos os nodes
def escreve_file(file, fileName, blocos_recebidos): 
    for data in blocos_recebidos[fileName]:
        posInic = TamanhoBloco * (data[0]-1)
        file.seek(posInic)
        file.write(data[1])

    blocos_recebidos.pop(fileName, None)
    #print(blocos_recebidos)

# Método que o Node usa para transferir um ficheiro
# No caso de só um node ter um ficheiro é pedido diretamente a esse node todos os blocos do ficheiro
# No caso de vários nodes terem vários blocos do ficheiro e terem todos a mesma prioridade é repartido o número de blocos a pedir igualmente pelos nodes existentes
# No caso de haver uma diferença na prioridade dos nodes (haver um node com mais peso que os outros nodes) quanto mais peso um node têm mais blocos lhe serão pedidos
def transf_file(fileInfo, caminho_pasta, fileName, blocos_recebidos, socketTCP, port):
    global file_size
    global blocos_em_falta
    lockFile = threading.Lock()

    listaNodes = fileInfo[1]
    listaNodes = ordena_por_nodes(listaNodes)
    listaIpsAux = copy.deepcopy(listaNodes)
    print(listaNodes)

    numBlocos = int(fileInfo[0])
    ipsIndv = int(fileInfo[2])
    
    if ipsIndv == 1:
        blocos, err = escolhe_nodes(listaNodes, ipsIndv, numBlocos)
        listaFinal = lista_pedir_blocos(blocos)
        #print(listaFinal, "if ipsIndv == 1")
        pedir_file(fileName, listaFinal[0][0][0], int(listaFinal[0][0][1]), port, listaFinal[0][1], blocos_recebidos, socketTCP)

    elif verifica_existe_prioridade(listaNodes, ipsIndv) == 0 and ipsIndv > 1:  
        MaxBlocos = numBlocos // ipsIndv
        if numBlocos % ipsIndv != 0 :
            MaxBlocos += 1
        blocos, err = escolhe_nodes(listaNodes, ipsIndv, MaxBlocos)
        listaFinal = lista_pedir_blocos(blocos)
        #print(listaFinal, "elif == 0")

        threads = []

        for ip, blocos in listaFinal:
            thread = threading.Thread(target=pedir_file, args=(fileName, ip[0], ip[1], port, blocos, blocos_recebidos, socketTCP))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()    
        
    elif verifica_existe_prioridade(listaNodes, ipsIndv) != 0 and ipsIndv > 1:
        MaxBlocos = 5
        blocos, blocos_por_pedir = escolhe_nodes(listaNodes, ipsIndv, MaxBlocos)
        listaFinal = lista_pedir_blocos(blocos)
        #print(listaFinal, "elif != 0")
        
        threads = []

        iteracoes = 1
        while (numBlocos - ipsIndv * MaxBlocos) >= 0 or listaFinal != []:
            for ip, blocos in listaFinal:
                thread = threading.Thread(target=pedir_file, args=(fileName, ip[0], ip[1], port, blocos, blocos_recebidos, socketTCP))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            if blocos_por_pedir == []:
                break

            listaFinal, blocos_por_pedir = escolhe_nodes(blocos_por_pedir, ipsIndv, MaxBlocos)
            listaFinal = lista_pedir_blocos(listaFinal)
            iteracoes += 1
    
    faltamBlocos = verifica_lista(blocos_em_falta)

    while faltamBlocos:
        print("A pedir novamente os blocos:", blocos_em_falta)
        listaBlocosEmFalta = filtraLista(listaIpsAux,blocos_em_falta)
        blocos, err = escolhe_nodes(listaBlocosEmFalta, ipsIndv, 5)
        listaFinal = lista_pedir_blocos(blocos)

        blocos_em_falta = []

        threads = []
        for ip, blocos in listaFinal:
            thread = threading.Thread(target=pedir_file, args=(fileName, ip[0], ip[1], port, blocos, blocos_recebidos, socketTCP))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        faltamBlocos = verifica_lista(blocos_em_falta)

    file = open(os.path.join(caminho_pasta, fileName), "wb")
    file.seek(file_size)
    file.write(b"\0")

    escreve_file(file, fileName, blocos_recebidos)

    file.close()
    file_size = 0

# Método utilizado para verificar o checksum aos dados que vão ser enviados e aos que foram recebidos
def calcula_checksum(data):
    checksum = 0
    for byte in data:
        checksum ^= byte
    return checksum   

# Método que o Node usa para enviar um ficheiro caso tenho o ficheiro completo na sua pasta
def env_FileCmpl(caminho_pasta, fileName, numBloco, socketUDP, addr):  
    print("enviei do completo bloco", numBloco)   
    caminhoFile = os.path.join(caminho_pasta, fileName)
      
    with open(caminhoFile, "rb") as file:
        posInic = TamanhoBloco * (numBloco-1)
        if posInic < file.seek(0, os.SEEK_END):
            file.seek(posInic)

        data = file.read(TamanhoBloco)
        if not data:
            print("Erro a ler a data")  
            
        numBloco_bytes = numBloco.to_bytes(4, 'big')

        dataEnviar = numBloco_bytes + data

    checksum = calcula_checksum(dataEnviar) 
    checksum_bytes = checksum.to_bytes(2, 'big')  
    dataComChecksum = checksum_bytes + dataEnviar

    socketUDP.sendto(dataComChecksum, addr)

# Método que o Node usa para enviar um ficheiro caso ainda esteja a trasnferir blocos 
def env_FileIncl(blocos_recebidos, fileName, numBloco, socketUDP, addr):
    print("enviei do incompleto bloco", numBloco)
    dataEnviar = b''
    for numero, data in blocos_recebidos[fileName]:
        if numero == numBloco:
            print("está aqui o bloco")
            numBloco_bytes = numBloco.to_bytes(4, 'big')
            dataEnviar = numBloco_bytes + data
            break

    checksum = calcula_checksum(dataEnviar) 
    checksum_bytes = checksum.to_bytes(2, 'big')  
    dataComChecksum = checksum_bytes + dataEnviar

    socketUDP.sendto(dataComChecksum, addr)