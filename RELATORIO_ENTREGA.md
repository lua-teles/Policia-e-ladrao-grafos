# Checklist Final de Entrega

Este documento consolida os itens de entrega esperados pelo trabalho em quatro eixos:

- Corretude (40%)
- Eficiência (20%)
- Qualidade de código (20%)
- Análise dos resultados (20%)

Também inclui um roteiro curto para validação final antes de submissão.

## 1. Corretude (40%)

### 1.1 Modelagem e ordem dos eventos

A simulação implementa a ordem de eventos rodada a rodada conforme comportamento racional do problema:

1. Cerco antes do movimento do ladrão.
2. Escolha do melhor porto via Bellman-Ford no grafo original.
3. Movimento do ladrão para o próximo vértice no menor caminho.
4. Verificação de fuga ao alcançar porto.
5. Cerco após movimento.
6. Cálculo compartilhado no grafo reverso para perseguição policial.
7. Dois sub-passos de movimento das equipes, com captura verificada após cada sub-passo.

Essa ordem é importante porque trocar a precedência entre polícia e ladrão altera o desfecho. Por exemplo, no cenário de cerco inicial, o ladrão é preso na rodada 1 antes de tentar fugir.

### 1.2 Condições de captura e fuga cobertas

- Preso por cerco total em todas as saídas do vértice atual.
- Preso por alcance direto de equipe (captura por encontro no mesmo vértice).
- Preso sem rota viável a porto na rodada.
- Preso por estrutura quando não existe porto alcançável a partir do castelo.
- Fuga ao alcançar porto após movimento.
- Rejeição de entrada inválida quando castelo e porto coincidem.

### 1.3 Validações de entrada

- Detecção de ciclo negativo alcançável por Bellman-Ford.
- Verificação de vértices fora do intervalo.
- Checagem de consistência de k/portos e q/equipes.
- Validação de que nenhum porto coincide com o castelo.
- Tratamento de arquivo incompleto.

## 2. Eficiência (20%)

### 2.1 Caminhos mínimos

Foi usada a estratégia de Bellman-Ford com parada antecipada para suportar pesos negativos e reduzir iterações quando há convergência.

### 2.2 Grafo reverso compartilhado

A perseguição policial usa uma execução compartilhada de Bellman-Ford no grafo reverso por rodada, evitando executar Bellman-Ford por equipe.

Comparação de custo por rodada:

- Abordagem ingênua: O(Q * |V| * |E|)
- Abordagem adotada: O(|V| * |E|)

Ganho assintótico linear em Q.

### 2.3 Min-Cut

O mínimo teórico de equipes foi modelado com vertex split e Edmonds-Karp em rede de capacidades.

- Vértices bloqueáveis: capacidade 1 no arco interno v_in -> v_out.
- Castelo: capacidade infinita para não ser removido.
- Demais vértices, incluindo portos: capacidade 1 para poderem compor o corte.
- Arestas do grafo original: capacidade infinita entre u_out -> v_in.

## 3. Qualidade de Código (20%)

### 3.1 Organização modular

- [projeto/main.py](projeto/main.py)
- [projeto/grafo.py](projeto/grafo.py)
- [projeto/algoritmos.py](projeto/algoritmos.py)
- [projeto/simulacao.py](projeto/simulacao.py)
- [projeto/relatorio.py](projeto/relatorio.py)

Separação clara de responsabilidades e baixo acoplamento entre módulos.

### 3.2 Legibilidade e manutenção

- Funções pequenas e com nomes semânticos.
- Constantes explícitas (INF, CAP_INF).
- Tratamento de exceções na leitura de entrada.
- Relatório textual padronizado para depuração e comparação de cenários.

### 3.3 Robustez adicional implementada

- Geração de relatório mesmo quando não há porto alcançável.
- Segunda tentativa automática com reposicionamento no corte mínimo quando a estratégia inicial falha.

## 4. Análise dos Resultados (20%)

## 4.1 Cenários executados

Comandos reproduzíveis:

- python main.py casos_teste/01_insuficiente.txt casos_teste/01_saida.txt
- python main.py casos_teste/02_exato_k.txt casos_teste/02_saida.txt
- python main.py casos_teste/03_acima_k.txt casos_teste/03_saida.txt
- python main.py casos_teste/04_escapou.txt casos_teste/04_saida_resultado.txt
- python main.py casos_teste/06_sem_porto_alcancavel.txt casos_teste/06_saida.txt
- python main.py casos_teste/07_ciclo_negativo.txt casos_teste/07_saida.txt

### 4.2 Síntese observada

- 01_insuficiente: PRESO_ALCANCE na rodada 1, apesar de equipes < k mínimo.
- 02_exato_k: PRESO_CERCO na rodada 1 com equipes = k mínimo.
- 03_acima_k: PRESO_CERCO na rodada 1 com equipes > k mínimo.
- 04_escapou: tentativa inicial falha, mas o replanejamento no corte mínimo prende o ladrão na rodada 1.
- 06_sem_porto_alcancavel: PRESO_SEM_PORTO_ALCANCAVEL na rodada 0.
- 05_castelo_e_porto: entrada inválida rejeitada pelo parser.
- 07_ciclo_negativo: entrada inválida detectada e execução interrompida.

### 4.3 Discussão Min-Cut versus simulação

O Min-Cut fornece limite teórico de bloqueio global, mas a simulação é dinâmica e depende de posicionamento inicial e ordem temporal.

Evidência prática:

- No cenário 01, mesmo com equipes abaixo do mínimo teórico, houve captura por alcance em dinâmica local favorável.
- No cenário 04, o reposicionamento automático no corte mínimo compensou a ausência de equipes iniciais.
- Nos cenários 02 e 03, o cerco inicial já determinou captura imediata.

Conclusão: Min-Cut é referência estrutural, enquanto a simulação captura comportamento tático rodada a rodada.

## 5. Checklist de Submissão

- [ ] Código executa com Python 3.10+.
- [ ] Estrutura de arquivos segue o enunciado.
- [ ] Sem bibliotecas externas de grafos.
- [ ] Bellman-Ford, BFS e Edmonds-Karp implementados manualmente.
- [ ] Relatório de saída é gerado para cenários válidos e para caso sem porto alcançável.
- [ ] Cenários de teste incluem insuficientes, exato k, acima de k e fuga.
- [ ] Caso de ciclo negativo demonstrado como inválido.
- [ ] Discussão de corretude, eficiência e trade-offs incluída na entrega.

## 6. Referências rápidas

- Documento principal de execução: [projeto/README.md](projeto/README.md)
- Relatório gerado no caso padrão: [projeto/saida.txt](projeto/saida.txt)
- Pasta de cenários: [projeto/casos_teste](projeto/casos_teste)
