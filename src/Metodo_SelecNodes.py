import copy

# Método que compara os nodes todos que têm blocos do ficheiro pretendido 
# e verifica se têm todos a mesma pontuação ou se existe algum node com prioridade
def verifica_existe_prioridade(listaIps, ipsIndv):  # listaIps = [[('ip1', 4), ('ip2', 7), ('ip3', -3)], [('ip2', 7)]] res = 1  listaIps = [[('ip1', 0), ('ip2', 0), ('ip3', 0)], [('ip2', 0)]] res = 0
    ipsVerificados = []
    aux = 0
    aux2 = listaIps[0][0][1]

    for array in listaIps:
         for tpl in array:
            if aux > ipsIndv: 
               return 0 

            if ipsVerificados.count(tpl) == 0:
               aux += 1
               if tpl[1] != aux2:
                  return 1
               else:
                  ipsVerificados.append(tpl)

    return 0

# Método que recebendo a lista dos blocos ordenada pela ordem dos blocos reorganiza a lista
# de forma a que os primeiros blocos a ser pedidos são os que se encontram em menor número de nodes
def ordena_por_nodes(listaIps):
   tam = len(listaIps)
   blocos_nodes = []
   aux = 1

   while (len(blocos_nodes) != tam):
      i = 0
      for array in listaIps:
         if len(array) == aux:
            blocos_nodes.append((array, i))
         i += 1
      aux += 1
   
   return blocos_nodes

# Algoritmo de round robin por pesos que escolhe dentro de uma lista de nodes o que têm o maior peso para ser pedido o bloco
def weighted_round_robin(listaIps):  # listaIps = [('ip1', 4), ('ip2', 7), ('ip3', -3)] res = ('ip2', 7)
   listaIps.sort(key=lambda x: x[1], reverse=True)
   melhorIp = listaIps[0]

   return melhorIp

# Função que utilizando o algoritmo de round robin decide a que node vai ser pedido cada bloco 
# sendo que recebe um N que é o número máximo de blocos que cada node pode enviar sem ficar sobre carregado 
# No caso de haverem blocos por pedir guarda numa lista que voltará a ser processada futuramente
def escolhe_nodes(listaIps, ipsIndv, N):
   ipsEscolhidos = []
   aux = []
   blocos_por_pedir = []
   listaIpsAux = copy.deepcopy(listaIps)

   try:
      for tuple in listaIpsAux:
         ip = weighted_round_robin(tuple[0])
         if aux.count(ip) >= N and ipsIndv > 1:
            aux2 = tuple[0]
            aux2.remove(ip)
            ip2 = weighted_round_robin(aux2)
            if aux.count(ip2) >= N:
               while aux.count(ip2) >= N:
                  aux2.remove(ip2)
                  ip2 = weighted_round_robin(aux2)
                  aux.append(ip2)
                  ipsEscolhidos.append((ip2, tuple[1]))
            else:
               aux.append(ip2)
               ipsEscolhidos.append((ip2, tuple[1]))
         else:
            aux.append(ip)
            ipsEscolhidos.append((ip, tuple[1]))
   except Exception as e: # lista de blocos que ainda não foram pedidos
      blocos_por_pedir = [tpl for tpl in listaIps if not any(tpl[1] == bloco[1] for bloco in ipsEscolhidos)]
      return ipsEscolhidos, blocos_por_pedir

   return ipsEscolhidos, []

# Método que recebe a lista final organizada pelos blocos e o node a que vão ser pedidos cada bloco
# e coloca tudo numa lista que irá conter cada node ligado a uma lista dos blocos que lhe serão pedidos
# Passa [(ip1, 1), (ip2, 3), (ip1, 4), (ip2, 2), (ip1, 5)] para [(ip1, [1,4,5]), (ip2, [3,2])]
def lista_pedir_blocos(listaIps):
   aux = {}

   for ip, bloco in listaIps:
      aux.setdefault(ip, []).append(bloco+1)
   ipBlocos = [(ip, blocos) for ip, blocos in aux.items()]

   return ipBlocos