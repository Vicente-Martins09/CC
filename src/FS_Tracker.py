import socket
import threading

# criar um diiconário para relembrar em que node está cada ficheiro
ficheiroDoNodo = {}
node_threads = {}

# Configuração do servidor
host = '127.0.0.2'  # Endereço IP do servidor
port = 9090       # Porta que o servidor irá ouvir

# Cria um socket do tipo TCP
tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Vincula o socket ao endereço e à porta
tracker_socket.bind((host, port))

# Começa a ouvir por conexões
tracker_socket.listen()

x = 0

print(f"Servidor escutando em {host}: porta {port}")

def print_listaFiles():
    print("Ficheiros em cada Node: \n")
    for nomeFicheiro, node in ficheiroDoNodo.items():
        print(f"{nomeFicheiro} pertence aos nodes com IP {node}")

def guarda_Localizacao(data, nodeIP):
        
    nomeFicheiros = data.split(' | ')
        
    for ficheiro in nomeFicheiros:
        if ficheiro in ficheiroDoNodo:
                ficheiroDoNodo[ficheiro].append(nodeIP)
        else:
            ficheiroDoNodo[ficheiro] = [nodeIP]
            
    print_listaFiles()
            
def remover_info_node(nodeIP):
    for ficheiro, nodes in ficheiroDoNodo.items():
        for node in nodes:   
            if nodeIP == node:
                nodes.remove(node)
        
    print(f"Informação do {nodeIP} removida")
    print_listaFiles()
    
def procurar_file(nomeFile):
    for ficheiro, nodes in ficheiroDoNodo.items():
        if ficheiro == nomeFile:
            if len(nodes) > 0:
                print_listaFiles()
                return nodes
            else:
                print_listaFiles()
                return None

def handle_node(node_socket):
    # nodeIP = node_socket.getpeername()[0]
    nodeIP = x
    while True:    
        message = node_socket.recv(1024).decode()
        
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
                guarda_Localizacao(data, nodeIP)
            else:
                print("Ocorreu um erro a enviar os ficheiros.")
                
        elif key == "get":
            if len(format) == 2:
                nomeFile = format[1]
                localizacao = procurar_file(nomeFile)
                
                if localizacao is not None:
                    response = f"IP's onde se encontram o ficheiro são {localizacao}"
                else:
                    response = "File not found"

                node_socket.send(response.encode())
            else:
                print("Ocorreu um erro a pedir o file")
                
        
while True:
    # Aceita uma conexão de um cliente
    node_socket, node_address = tracker_socket.accept()

    x = x+1
    
    node_thread = threading.Thread(target = handle_node, args = (node_socket,))
    node_thread.start()
    
    nodeIP = x
    # nodeIP = node_socket.getpeername()[0]
    node_threads[nodeIP] = node_thread
    
# Fecha o socket do servidor
tracker_socket.close()
    

# lsof -i :9090 // caso não seja possivel ligar o servidor mata quem estiver a usar a porta