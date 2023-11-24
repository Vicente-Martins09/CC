import socket
import threading

from Struct_FileNodes import *

# criar um diconário para relembrar em que node está cada ficheiro
node_threads = {}

# Configuração do servidor
host = '127.0.0.1'
# host = '10.4.4.1'  # Endereço IP do servidor
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
    nodeIP = node_socket.getpeername()[0]
    while True:    
        message = node_socket.recv(1024).decode()
        print(message)
        format = message.split(" . ")
        key = format[0]
        
        if key == "quit":
            print("Node desconectado")
            remover_info_node(nodeIP)
            node_socket.close()
            break
            
        elif key == "files":
            if len(format) == 2:
                data = format[1]
                if data:
                    guarda_Localizacao(data, nodeIP)
            else:
                print("Ocorreu um erro a enviar os ficheiros.")
                
        elif key == "get":
            if len(format) == 2:
                nomeFile = format[1]
                localizacao = procurar_file(nomeFile)
                
                if localizacao is not None:
                    response = f"{localizacao}"
                else:
                    response = "File not found"

                node_socket.send(response.encode())
            else:
                print("Ocorreu um erro a pedir o file")
                
        elif key == "updblc":
            if len(format) == 3:
                nomeFile = format[1]
                num = format[2]
                numBlocos = [int(x) for x in num.strip("[]").split(",")]
                update_info_file(nomeFile, nodeIP, numBlocos)
                
        elif key == "updfin":
            if len(format) == 2:
                nomeFile = format[1]
                update_info_file(nomeFile, nodeIP, [])
                
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