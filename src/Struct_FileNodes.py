ficheiroDoNodo = {}
memoriaLogin = []

# Método que imprime a estrutura que armazena os ficheiros e os Nodes 
def print_listaFiles():
    print("\n#######################\n\nFicheiros em cada Node: \n")
    for nomeFicheiro, node_info in ficheiroDoNodo.items():
        print(f"{nomeFicheiro}\n\tBlocos = {node_info[0]}\n\tNodes com ficheiro: {node_info[1]}")
        if len(node_info[2]) > 0:
            for node, blocos in node_info[2]:
                numBlocos = sum(blocos)
                print(f"\n\tNodes com alguns blocos:\n\t\tNode de ip {node[0]} têm {numBlocos} blocos e uma pontuação de transferência de {node[1]}")

# Método que recebe a informação enviada pelo Node após a sua conexão e guarda numa struct em que a chave principal é o nome do ficheiro e liga a este um tuple de 3 elementos 
# o primeiro é o número total de blocos que o ficheiro têm 
# o segundo é uma lista de ips dos Nodes que contêm o ficheiro completo 
# o terceiro é uma lista vazia que irá conter um tuple com o ip de um node que não tenha o ficheiro completo e um array que diz que blocos é que o Node têm do ficheiro
# será atribuído um peso a cada node através do método procura_peso
def guarda_Localizacao(data, nodeIP):  
    peso = procura_peso(nodeIP)
    infoFicheiros = data.split(' | ')
    for infoFicheiro in infoFicheiros:
        ficheiro, numBlocks = infoFicheiro.split("-")
        if ficheiro in ficheiroDoNodo:
                ficheiroDoNodo[ficheiro][1].append((nodeIP, peso))
        else:
            ficheiroDoNodo[ficheiro] = [numBlocks, [(nodeIP, peso)], []]
    # print("guarda")        
    print_listaFiles()

# Método utilizado para atualizar o valor do peso cada vez que a função update_file_info é chamada
def atualiza_pesos(ipAtualizar, peso):
    for ficheiro, node_info in ficheiroDoNodo.items():
        node_info[1] = [(ip, peso) if ip == ipAtualizar else (ip, pesoAtual) for ip, pesoAtual in node_info[1]]
        node_info[2] = [((ip, peso), array) if ip == ipAtualizar else ((ip, pesoAtual), array) for (ip, pesoAtual), array in node_info[2]]

# Método que à medida que um Node transfere um ficheiro atualiza a estrutura que armazena os Nodes que contêm informações relativamente a cada ficheiro. 
# No caso do Node ter acabado de transferir um ficheiro remove o Node da lista de tuples e coloca o seu ip na lista de Nodes com o file completo .
# No caso de ainda não ter o ficheiro todo cria um tuple com o ip do Node que está a transferir e um array que diz que blocos é que o Node contêm, indíce do array é igual ao nº do bloco - 1
# caso já contenha o ip atualiza o array de blocos
def update_info_file(nomeFile, nodeIP, numBlocos, ipAtualizar, peso):
    tamanho = len(numBlocos)
    if(tamanho == 0):
        for ficheiro, node_info in ficheiroDoNodo.items():
            if ficheiro == nomeFile:
                ficheiroDoNodo[ficheiro][1].append((nodeIP, node_info[2][0][0][1]))  # node_info[2][0][0][1]) é o peso que o ip já têm
                nodes_sem_file_compl = ficheiroDoNodo[ficheiro][2]
                ficheiroDoNodo[ficheiro][2] = [node for node in nodes_sem_file_compl if node[0][0] != nodeIP]
                print_listaFiles()
                break
    
    elif(tamanho != 0):
        atualiza_pesos(ipAtualizar, peso)
        for ficheiro, node_info in ficheiroDoNodo.items():    # node_info ---> node_info[0] = blocos totais; node_info[1] = lista de ips com file completo; node_info[2] = lista de tuples de nodes que nao tem o ficheiro completo
            if ficheiro == nomeFile:
                if nodeIP in [node[0][0] for node in node_info[2]]:  # cria uma lista com os nodes que ainda não têm o ficheiro completo
                    for node, blocos in node_info[2]:
                        if nodeIP == node[0]:
                            for i in numBlocos:
                                blocos[i - 1] = 1
                            #print(blocos)
                            print_listaFiles()
                            break
                else:
                    blocos = [0] * int(node_info[0])
                    for i in numBlocos:
                        blocos[i - 1] = 1
                    #print(blocos)
                    ficheiroDoNodo[ficheiro][2].append(((nodeIP, 0), blocos)) 
                    print_listaFiles()
                    break
        
# Método que remove um Node da memória do Tracker quando o Node se desconecta    
def remover_info_node(nodeIP):
    removido = 0
    for ficheiro, node_info in ficheiroDoNodo.items():
        node_info[1] = [(node1, _) for node1, _ in node_info[1] if nodeIP != node1]
        node_info[2] = [((node2, _), blocos) for (node2, _), blocos in node_info[2] if nodeIP != node2]
        
    print(f"Informação do {nodeIP} removida")
    # print("remover")
    print_listaFiles()
    
# Método que verifica se o file que estamos a tentar transferir existe e se sim devolve a informação que a ele está vinculada
def procurar_file(nomeFile):
    for ficheiro, node_info in ficheiroDoNodo.items():
        if ficheiro == nomeFile:
            # print("procura")
            if len(node_info[1]) > 0 or len(node_info[2]) > 0:
                print_listaFiles()
                return node_info
            else:
                print_listaFiles()
                return None
            
# Método que recebe a informação dos Nodes relativa a cada ficheiro e transforma num array com a lista dos ips dos Nodes que contêm os blocos na posição do array nº bloco - 1
def blocos_por_node(fileCompl, fileIncpl, numBlocos):   # [('127.0.0.1', 0)]  [(('127.0.0.1', 0), [1, 1, 1, 0])]] 4
    blocosIps = []
    array_node = []
    i = 0
    
    while i < numBlocos:
        for ip in fileCompl:
            array_node.append(ip)
            
        
        for tpl in fileIncpl:
            if tpl[1][i] == 1:
                array_node.append(tpl[0])
        
        blocosIps.append(array_node)
        array_node = []
        i += 1
 
    return blocosIps

# Método que irá recordar o peso de um node que se desconectou para se no futuro ele se voltar a conectar ao server
# no caso de ter um peso menor ou igual a 0 este não será guardado e quando se voltar a conectar leva reset para 0
def relembrar_nota(ip):
    ipEncontrado = False
    for ficheiro, node_info in ficheiroDoNodo.items():
        if ipEncontrado: break
        for nodeIp, value in node_info[1]:
            if ipEncontrado:
                break
            elif ip == nodeIp and value > 0:
                memoriaLogin.append((ip, value))
                ipEncontrado = True
                break
        for (nodeIp, value), array in node_info[2]:
            if ipEncontrado:
                break
            elif ip == nodeIp and value > 0:
                memoriaLogin.append((ip, value))
                ipEncontrado = True
                break
    print(memoriaLogin)

# Método utilizado para procurar se um ip que se conectou ao tracker têm um peso guardado
def procura_peso(nodeIP):
    for ip, peso in memoriaLogin:
       if ip == nodeIP:
            memoriaLogin.remove((ip,peso))
            if peso < 0: peso = 0
            return peso
    return 0