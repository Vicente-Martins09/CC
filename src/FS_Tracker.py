import socket

# criar um diiconário para relembrar em que node está cada ficheiro
ficheiroDoNodo = {}

# Configuração do servidor
host = '127.0.0.1'  # Endereço IP do servidor
port = 9090       # Porta que o servidor irá ouvir

# Cria um socket do tipo TCP
tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Vincula o socket ao endereço e à porta
tracker_socket.bind((host, port))

# Começa a ouvir por conexões
tracker_socket.listen()

print(f"Servidor escutando em {host}: porta {port}")

def guarda_Localizacao(node_socket):
    data = node_socket.recv(1024).decode()
    
    nomeFicheiros = data.split(' | ')
    
    nodeIP = node_socket.getpeername()[0]
    
    for ficheiro in nomeFicheiros:
        ficheiroDoNodo[ficheiro] = nodeIP
        
    print("Ficcheiros em cada Node: \n")
    for nomeFicheiro, node in ficheiroDoNodo.items():
        print(f"{nomeFicheiro} pertence ao node {node}")
    
while True:
    # Aceita uma conexão de um cliente
    node_socket, node_address = tracker_socket.accept()

    # Recebe dados do cliente
    guarda_Localizacao(node_socket)

    # Fecha a conexão com o cliente
    node_socket.close()
    
# Fecha o socket do servidor
tracker_socket.close()
    

# lsof -i :9090 // caso não seja possivel ligar o servidor mata quem estiver a usar a porta
