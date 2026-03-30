# Sistema de Captura do Ladrao

Implementacao em Python 3.10+ da simulação de perseguição em grafo direcionado e ponderado.

## Estrutura

- `main.py`: orquestra leitura, validações, min-cut, simulação, replanejamento e relatório;
- `grafo.py`: estrutura do grafo e parser de entrada;
- `algoritmos.py`: Bellman-Ford, BFS, Edmonds-Karp e extração de vértices do corte;
- `simulacao.py`: lógica rodada a rodada;
- `relatorio.py`: formatação e escrita do relatório final;
- `entrada.txt`: exemplo padrão de entrada;
- `saida.txt`: saída gerada no exemplo padrão;
- `casos_teste/`: cenários para análise experimental e validação.

## Como executar

Da raiz do repositório:

```bash
python projeto/main.py projeto/entrada.txt
python projeto/main.py projeto/entrada.txt projeto/saida.txt
```

Dentro da pasta `projeto/`:

```bash
python main.py entrada.txt
python main.py entrada.txt saida.txt
```

Sem informar `saida.txt`, a simulação e o resumo final são impressos no terminal.
Se `saida.txt` for informado, o mesmo resumo também é salvo em arquivo.

## Formato da entrada

```text
n m
u1 v1 w1
u2 v2 w2
...
castelo
k porto1 porto2 ... portok
q pos1 pos2 ... posq
```

## Escolhas de projeto

- Bellman-Ford foi escolhido porque o problema permite pesos negativos.
- O grafo reverso permite calcular distâncias para todas as equipes com uma única execução por rodada.
- O min-cut usa vertex split e Edmonds-Karp com matriz de capacidades.
- Se a tentativa com as equipes iniciais falhar, o programa tenta reposicionar equipes no corte minimo.

## Cenários de teste sugeridos

```bash
cd projeto
python main.py casos_teste/01_insuficiente.txt
python main.py casos_teste/02_exato_k.txt
python main.py casos_teste/03_acima_k.txt
python main.py casos_teste/04_escapou.txt
python main.py casos_teste/06_sem_porto_alcancavel.txt
python main.py casos_teste/07_ciclo_negativo.txt
python main.py casos_teste/08_perseguicao_interceptacao.txt
python main.py casos_teste/09_rede_com_tres_equipes.txt
python main.py casos_teste/10_perseguicao_longa.txt
python main.py casos_teste/11_fuga_e_replanejamento.txt
```

Esses arquivos ajudam a cobrir o requisito de analise para:

- equipes insuficientes;
- número exato de equipes mínimas teóricas;
- equipes acima do mínimo;
- caso explícito de fuga (status ESCAPOU);
- ausência de porto alcançável a partir do castelo;
- detecção de ciclo negativo alcançável (entrada inválida);
- rejeição de entrada inválida em que castelo e porto coincidem;
- interceptação após múltiplas avaliações de rota;
- perseguição com mais equipes e mais profundidade no grafo;
- fuga longa com replanejamento automático no corte mínimo.

## Material de entrega

- Checklist e texto-base para relatório final: [RELATORIO_ENTREGA.md](RELATORIO_ENTREGA.md)
