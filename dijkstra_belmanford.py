import heapq

def djkstra(grafo, origem):
    INF = float('inf')
    dist = {v: INF for v in grafo.adj}
    pred = {v: None for v in grafo.adj}
    dist[origem] = 0
    
    #Fila de Prioridade: (custo_acumulado, vertice)
    heap = [(0, origem)]
    while heap:
        custo_atual, u = heapq.heappop(heap)
        
        # Se o custo atual for maior que a distância registrada, ignore
        if custo_atual > dist[u]:
            continue
        
        for v, peso in grafo.vizinhos(u):
            custo_novo = dist[u] + peso
            
            if custo_novo < dist[v]:
                dist[v] = custo_novo
                pred[v] = u
                heapq.heappush(heap, (custo_novo, v))
                
    return dist, pred

def bellman_ford(grafo, origem):
    INF = float('inf')
    dist = {v: INF for v in grafo.adj}
    pred = {v: None for v in grafo.adj}
    dist[origem] = 0
    
    n = grafo.num_vertices
    
    #Relaxamento das arestas (v-1) vezes
    for _ in range(n - 1):
        atualizado = False
        for u in grafo.adj:
            if dist[u] == INF:
                continue # Se o vértice u não é alcançável, pule
            for v, peso in grafo.vizinhos(u):
                if dist[u] + peso < dist[v]:
                    dist[v] = dist[u] + peso
                    pred[v] = u
                    atualizado = True
        if not atualizado:
            break # Se não houve atualização, podemos parar
        
    # Verificação de ciclo negativo
    detectado_ciclo_negativo = False
    for u in grafo.adj:
        if dist[u] == INF:
            continue # Se o vértice u não é alcançável, pule
        for v, peso in grafo.vizinhos(u):
            if dist[u] + peso < dist[v]:
                detectado_ciclo_negativo = True
                break
    return dist, pred, detectado_ciclo_negativo

def tem_pesos_negativos(grafo):
    """Verifica se o grafo possui arestas com pesos negativos"""
    for u in grafo.adj:
        for _, peso in grafo.vizinhos(u):
            if peso < 0:
                return True
    return False

def caminho_minimo_auto(grafo, origem):
    if tem_pesos_negativos(grafo):
        dist, pred, _ = bellman_ford(grafo, origem)
        return dist, pred, 'bellman-ford'
    else:
        dist, pred = djkstra(grafo, origem)
        return dist, pred, 'djkstra'

def caminho_minimo(pred, origem, destino):
    caminho = []
    atual = destino
    
    while atual is not None:
        caminho.append(atual)
        atual = pred[atual]
    caminho.reverse()
    
    # Verifica se o caminho começa na origem
    if caminho and caminho[0] == origem:
        return caminho
    return []  # Retorna caminho vazio se não for possível alcançar o destino

def obter_caminho_lista(pred, destino):
    caminho = []
    atual = destino
    
    while atual is not None:
        caminho.append(atual)
        atual = pred.get(atual)
    caminho.reverse()
    
    return caminho


def escolher_movimento_ladrao(grafo, pos_atual, portos, pos_policiais):
    
    vizinhos = grafo.vizinhos(pos_atual)
    
    if not vizinhos:
        return None  # Sem movimentos possíveis
    
    # Filtra os vizinhos para evitar os policiais
    vizinhos_livres = [(v,peso) for v, peso in vizinhos if v not in pos_policiais]
    
    if not vizinhos_livres:
        return None  # Sem movimentos possíveis sem intersectar com policiais
    
    melhor_vizinho = None
    melhor_custo = float('inf')
    
    for v, peso in vizinhos_livres:
        
        #calcula caminhos a partir do vizinho
        dist, pred, _ = caminho_minimo_auto(grafo, v)
        
        for porto in portos:
            custo_total = peso + dist[porto]  # Custo do movimento atual + custo do caminho até o porto
            if custo_total < melhor_custo:
                melhor_custo = custo_total
                melhor_vizinho = v
    return melhor_vizinho if melhor_vizinho is not None else vizinhos_livres[0][0]  # Retorna o melhor vizinho ou o primeiro disponível