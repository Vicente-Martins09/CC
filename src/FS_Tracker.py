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
        print(f"{nomeFicheiro} pertence ao node {node}")

def guarda_Localizacao(data):
        
    nomeFicheiros = data.split(' | ')
        
    nodeIP = node_socket.getpeername()[0]
        
    for ficheiro in nomeFicheiros:
        if ficheiro in ficheiroDoNodo:
            # Vincula o mesmo ficheiro a diferentes nodes
            # ficheiroDoNodo[ficheiro].append(nodeIP)
            ficheiroDoNodo[ficheiro].append(x)
        else:
            # ficheiroDoNodo[ficheiro] = [nodeIP]
            ficheiroDoNodo[ficheiro] = [x]
            
    print_listaFiles()
            
def remover_info_node(nodeIP):
    for ficheiro, node in ficheiroDoNodo.items():
        if nodeIP in node:
            node.remove(x)
    
    print(f"Informação do {nodeIP} removida")
    print_listaFiles()
    
def handle_node(node_socket):
    while True:    
        data = node_socket.recv(1024).decode()
        
        if data == "delete":
            print("Node desconectado")
            # nodeIP = node_socket.getpeername()[0]
            remover_info_node(node_ip)
            node_socket.close()
            break
        else:
            guarda_Localizacao(data)
        
while True:
    # Aceita uma conexão de um cliente
    node_socket, node_address = tracker_socket.accept()

    x = x+1
    
    node_thread = threading.Thread(target = handle_node, args = (node_socket,))
    node_thread.start()
    
    
    node_ip = x
    # node_ip = node_socket.getpeername()[0]
    node_threads[node_ip] = node_thread
    
# Fecha o socket do servidor
tracker_socket.close()
    

# lsof -i :9090 // caso não seja possivel ligar o servidor mata quem estiver a usar a porta
