from classe_grafo import ler_arquivo, imprimir_grafo, Grafo
import algoritmos_grafos
# ler o arquivo do grafo e implementar a estrutura
grafo, vertice_roubo, portos, num_policiais, pos_policiais = ler_arquivo('grafo.txt')

# visualização da estrutura
imprimir_grafo(grafo)

# lógica do jogo
#enquanto jogo não acabou:
#    1. Ladrão verifica se está em um porto → escapou
#    2. Ladrão verifica se todos os vizinhos estão bloqueados → preso
#    3. Ladrão se move um vértice
#    4. Cada policial calcula Dijkstra até o ladrão
#    5. Cada policial se move dois vértices nesse caminho
#    6. Verificar se algum policial chegou ao mesmo vértice do ladrão → preso
#    7. Registrar tudo no relatório
#    8. Imprimir a situação da estrutura


# relatório final do jogo

