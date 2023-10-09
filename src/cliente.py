import socket
import sys

if len(sys.argv) != 3:
    print("Uso: python cliente.py <IP do host> <Número da Porta>")
    sys.exit(1)


# Configuração do cliente
host = sys.argv[1]  # Endereço IP do servidor
port = int(sys.argv[2])  # Porta que o servidor está ouvindo
message = "Hello, World!"

# Cria um socket do tipo TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta-se ao servidor
client_socket.connect((host, port))

# Envia a mensagem para o servidor
client_socket.send(message.encode())

# Fecha a conexão com o servidor
client_socket.close()
