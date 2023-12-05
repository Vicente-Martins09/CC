import threading
import socket

from Struct_FileNodes import *

# criar um diconário para relembrar em que node está cada ficheiro
node_threads = {}

# Configuração do servidor
# host = '127.0.0.1'
host = '10.4.4.1'  # Endereço IP do servidor
port = 9090       # Porta que o servidor irá ouvir

# Cria um socket do tipo TCP
socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Vincula o socket ao endereço e à porta
socketTCP.bind((host, port))

# Começa a ouvir por conexões
socketTCP.listen()

x = 0

print(f"Servidor escutando em {host}: porta {port}")

# Método que interage diretamente com o Node
def handle_node(node_socket):
    trackerAtivo = True
    nodeIP = node_socket.getpeername()[0]
    hostname, _, _ = socket.gethostbyaddr(nodeIP)
    buffer = b''
    while trackerAtivo:    
        data = node_socket.recv(1024)
        if not data:
            print("Cona 2 bazou")
            relembrar_nota(hostname)
            remover_info_node(hostname)
            node_socket.close()
            break
        print(data)
        buffer += data
        messages = buffer.split(b'\n') 
        buffer = messages.pop()
        #print(messages, "messages")

        for message in messages:
            #print(message)
            message_str = message.decode()
            #print(message_str)
            format = message_str.split("/")
            key = format[0]
            print(key, "chave")
        
            if key == "quit":
                print("Node desconectado")
                relembrar_nota(hostname)
                remover_info_node(hostname)
                # remover_info_node('10.0.0.2')
                node_socket.close()
                trackerAtivo = False
                break
                
            elif key == "files":
                if len(format) == 2:
                    data = format[1]
                    if data:
                        guarda_Localizacao(data, hostname)
                        # guarda_Localizacao("file3.txt-2", "10.0.0.5")
                        # update_info_file("file3.txt", "10.0.0.2", [2])
                else:
                    print("Ocorreu um erro a enviar os ficheiros.")
                    
            elif key == "get":
                if len(format) == 2:
                    nomeFile = format[1]
                    localizacao = procurar_file(nomeFile)
                    print(localizacao, "localizacao")
                    
                    if localizacao is not None:
                        numBlocos = int(localizacao[0])
                        ipsIndv = len(localizacao[1]) + len(localizacao[2])  # numero máximo de blocos que se pode transferir
                        ips = blocos_por_node(localizacao[1], localizacao[2], numBlocos)
                        node_info = (numBlocos, ips, ipsIndv)
                        response = f"{node_info}"
                    else:
                        response = "None"

                    node_socket.send(response.encode())
                else:
                    print("Ocorreu um erro a pedir o file")
                    
            elif key == "updblc":
                if len(format) == 5:
                    nomeFile = format[1]
                    num = format[2]
                    peso = int(format[3])
                    hostnamePeso = format[4] 
                    print(peso, hostnamePeso)
                    numBlocos = [int(x) for x in num.strip("[]").split(",")]
                    update_info_file(nomeFile, hostname, numBlocos, hostnamePeso, peso)
                    
            elif key == "updfin":
                if len(format) == 2:
                    nomeFile = format[1]
                    update_info_file(nomeFile, hostname, [], 0, 0)
                
while True:
    # Aceita uma conexão de um cliente
    node_socket, node_address = socketTCP.accept()

    x = x+1
    
    node_thread = threading.Thread(target = handle_node, args = (node_socket,))
    node_thread.start()
    
    # nodeIP = x
    node_threads[x] = node_thread
    
# Fecha o socket do servidor
socketTCP.close()

# lsof -i :9090 // caso não seja possivel ligar o servidor mata quem estiver a usar a porta