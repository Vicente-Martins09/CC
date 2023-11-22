import socket
import threading

# criar um diiconário para relembrar em que node está cada ficheiro
ficheiroDoNodo = {}
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

def print_listaFiles():
    print("\n#######################\n\nFicheiros em cada Node: \n")
    for nomeFicheiro, node_info in ficheiroDoNodo.items():
        print(f"{nomeFicheiro}\n\tBlocos = {node_info[0]}\n\tNodes com ficheiro: {node_info[1]}")
        if len(node_info[2]) > 0:
            for node, blocos in node_info[2]:
                numBlocos = sum(blocos)
                print(f"\n\tNodes com alguns blocos:\n\t\tNode de ip {node} têm {numBlocos} blocos")

def guarda_Localizacao(data, nodeIP):
        
    infoFicheiros = data.split(' | ')
        
    for infoFicheiro in infoFicheiros:
        ficheiro, numBlocks = infoFicheiro.split("-")
        if ficheiro in ficheiroDoNodo:
                ficheiroDoNodo[ficheiro][1].append(nodeIP)
        else:
            ficheiroDoNodo[ficheiro] = [numBlocks, [nodeIP], []]
    # print("guarda")        
    print_listaFiles()
 
def update_info_file(nomeFile, nodeIP, numBlocos):
    tamanho = len(numBlocos)
    if(tamanho == 0):
        for ficheiro, node_info in ficheiroDoNodo.items():
            if ficheiro == nomeFile:
                ficheiroDoNodo[ficheiro][1].append(nodeIP) 
                nodes_sem_file_compl = ficheiroDoNodo[ficheiro][2]
                ficheiroDoNodo[ficheiro][2] = [node for node in nodes_sem_file_compl if node[0] != nodeIP]
                print_listaFiles()
                break
    
    elif(tamanho != 0):
        for ficheiro, node_info in ficheiroDoNodo.items():    # node_info ---> node_info[0] = blocos totais; node_info[1] = lista de ips com file completo; node_info[2] = lista de tuples de nodes que nao tem o ficheiro completo
            if ficheiro == nomeFile:
                if nodeIP in [node[0] for node in node_info[2]]:  # cria uma lista com os nodes que ainda não têm o ficheiro completo
                    for node, blocos in node_info[2]:
                        if nodeIP == node:
                            for i in numBlocos:
                                blocos[i - 1] = 1
                            print(blocos)
                            print_listaFiles()
                            break
                else:
                    blocos = [0] * int(node_info[0])
                    for i in numBlocos:
                        blocos[i - 1] = 1
                    print(blocos)
                    ficheiroDoNodo[ficheiro][2].append((nodeIP, blocos)) 
                    print_listaFiles()
                    break
    
    
                    
        
            
def remover_info_node(nodeIP):
    for ficheiro, node_info in ficheiroDoNodo.items():
        for node in node_info[1]: 
            if nodeIP == node:
                node_info[1].remove(node)
        
    print(f"Informação do {nodeIP} removida")
    # print("remover")
    print_listaFiles()
    
def procurar_file(nomeFile):
    for ficheiro, node_info in ficheiroDoNodo.items():
        if ficheiro == nomeFile:
            # print("procura")
            if len(node_info[1]) > 0:
                print_listaFiles()
                return node_info
            else:
                print_listaFiles()
                return None

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