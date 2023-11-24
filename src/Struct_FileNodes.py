ficheiroDoNodo = {}

# Método que imprime a estrutura que armazena os ficheiros e os Nodes 
def print_listaFiles():
    print("\n#######################\n\nFicheiros em cada Node: \n")
    for nomeFicheiro, node_info in ficheiroDoNodo.items():
        print(f"{nomeFicheiro}\n\tBlocos = {node_info[0]}\n\tNodes com ficheiro: {node_info[1]}")
        if len(node_info[2]) > 0:
            for node, blocos in node_info[2]:
                numBlocos = sum(blocos)
                print(f"\n\tNodes com alguns blocos:\n\t\tNode de ip {node} têm {numBlocos} blocos")

# Método que recebe a informação enviada pelo Node após a sua conexão e guarda numa struct em que a chave principal é o nome do ficheiro e liga a este um tuple de 3 elementos 
# o primeiro é o número total de blocos que o ficheiro têm 
# o segundo é uma lista de ips dos Nodes que contêm o ficheiro completo 
# o terceiro é uma lista vazia que irá conter um tuple com o ip de um node que não tenha o ficheiro completo e um array que diz que blocos é que o Node têm do ficheiro
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
 
# Método que à medida que um Node transfere um ficheiro atualiza a estrutura que armazena os Nodes que contêm informações relativamente a cada ficheiro. 
# No caso do Node ter acabado de transferir um ficheiro remove o Node da lista de tuples e coloca o seu ip na lista de Nodes com o file completo .
# No caso de ainda não ter o ficheiro todo cria um tuple com o ip do Node que está a transferir e um array que diz que blocos é que o Node contêm, indíce do array é igual ao nº do bloco - 1
# caso já contenha o ip atualiza o array de blocos
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
        
# Método que remove um Node da memória do Tracker quando o Node se desconecta    
def remover_info_node(nodeIP):
    removido = 0
    for ficheiro, node_info in ficheiroDoNodo.items():
        for node1 in node_info[1]: 
            if nodeIP == node1:
                node_info[1].remove(node1)
                removido = 1
                break
        if removido == 0:
            for node2, _ in node_info[2]:
                if nodeIP == node2:
                    node_info[2].remove((node2, _))
                    break
        removido = 0
        
    print(f"Informação do {nodeIP} removida")
    # print("remover")
    print_listaFiles()
    
# Método que verifica se o file que estamos a tentar transferir existe e se sim devolve a informação que a ele está vinculada
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