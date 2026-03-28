class Grafo:
    def __init__(self, num_vertices):
        # Inicializa o grafo com um número específico de vértices
        # Cria uma lista de adjacências para armazenar as conexões entre os vértices
        self.num_vertices = num_vertices
        self.adjacency_list = {i: [] for i in range(num_vertices)}
        
    def adicionar_aresta(self, u, v, peso):
        # Adiciona uma aresta ao grafo com um peso específico
        self.adjacency_list[u].append((v, peso))
    
    def vizinhos(self, u):
        # Retorna os vizinhos (e os pesos das arestas) de um vértice específico
        return self.adjacency_list[u]
    
    def __repr__(self):
        resultado = "Grafo (lista de adjacências):\n"
        for u, vizinhos in self.adjacency_list.items():
            resultado += f"  {u}: {vizinhos}\n"
        return resultado
    
def ler_arquivo(caminho):
    # Lê um arquivo de texto e constrói um grafo a partir dos dados contidos nele
    try:
        with open(caminho, 'r') as f:
            linhas = [line.strip() for line in f if line.strip()]
            
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo '{caminho}' não encontrado.")
    
    if not linhas:
        return None
    
    idx = 0
    # n= vertices, m= arestas
    n, m = map(int, linhas[idx].split())
    idx += 1
    
    grafo = Grafo(n)
    #Lendo as m arestas
    for _ in range(m):
        u, v, peso = linhas[idx].split()
        grafo.adicionar_aresta(int(u), int(v), float(peso))
        idx += 1
    
    #vertice do roubo
    vertice_roubo = int(linhas[idx])
    idx += 1
    
    #Portos
    linhas_portos = linhas[idx].replace("portos:", "").strip()
    portos = [int(p) for p in linhas_portos.split()]
    idx += 1
    
    #Policiais
    linhas_policiais = linhas[idx].replace("policiais:", "").strip()
    partes = linhas_policiais.split()
    num_policiais = int(partes[0])
    pos_policiais = [int(p) for p in partes[1:]]
    
    return grafo, vertice_roubo, portos, num_policiais, pos_policiais

def imprimir_grafo(grafo, vertice_roubo, portos, pos_policiais):
    #Imprime a estrutura do grafo
    print(grafo)
            
          