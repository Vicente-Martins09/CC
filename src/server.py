import socket

# Configuração do servidor
host = '127.0.0.1'  # Endereço IP do servidor
port = 9090       # Porta que o servidor irá ouvir

# Cria um socket do tipo TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Vincula o socket ao endereço e à porta
server_socket.bind((host, port))

# Começa a ouvir por conexões
server_socket.listen()

print(f"Servidor escutando em {host}: porta {port}")

while True:
    # Aceita uma conexão de um cliente
    client_socket, client_address = server_socket.accept()

    # Recebe dados do cliente
    data = client_socket.recv(1024)

    # Imprime a mensagem recebida
    print(f"Cliente diz: {data.decode()}")

    # Fecha a conexão com o cliente
    client_socket.close()

# Fecha o socket do servidor
# server_socket.close()
