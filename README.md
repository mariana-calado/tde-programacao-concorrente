# TDE — Programação Concorrente

**Grupo:** ...
**Integrantes:** Nome (@usuario), ...
**Linguagem:** Python 3.10+

## Como executar

## Parte 1 — Jantar dos Filósofos

```bash
cd parte1-filosofos
python ingenuo.py      # versão ingênua: trava e mostra o diagnóstico
python hierarquia.py   # versão corrigida: roda 15 s e mostra o resumo
```

### O problema

Cinco filósofos alternam entre pensar e comer. Para comer, cada um precisa dos dois garfos ao seu lado, que são compartilhados com os vizinhos. Cada filósofo é uma `Thread` e cada garfo é um `Lock`. O filósofo `p` usa os garfos `(p-1) mod 5` (esquerda) e `p` (direita).

### Por que a versão ingênua trava

Todos pegam primeiro a esquerda e depois a direita. Se os cinco pegam a esquerda ao mesmo tempo, cada um espera o garfo que está com o vizinho, e ninguém come. As quatro condições de Coffman aparecem juntas: **exclusão mútua** (um garfo por vez), **manter-e-esperar** (segura um e espera o outro), **não preempção** (ninguém toma o garfo do outro) e **espera circular** (P0 → P1 → … → P0). Uma pausa de 1 s entre os garfos faz o deadlock aparecer em segundos.

```
DEADLOCK! Nenhum filósofo progrediu nos últimos 3s.
  P0 está com fome, segura G4 e espera G0, que está com P1
  P1 está com fome, segura G0 e espera G1, que está com P2
  ...
  P4 está com fome, segura G3 e espera G4, que está com P0
  Espera circular: P0 -> P1 -> P2 -> P3 -> P4 -> P0
```

### Solução: hierarquia de recursos

Todo filósofo pega **primeiro o garfo de menor número**. Isso nega a **espera circular**: num ciclo, cada um esperaria um garfo de número maior que o que já tem, e os números cresceriam até voltar ao início, o que é impossível. Na prática, só o P0 muda de ordem (G0 → G4 em vez de G4 → G0).

```
primeiro = min(esquerda, direita);  segundo = max(esquerda, direita)
repetir:
    pensar()
    estado <- "com fome"
    adquirir(primeiro);  adquirir(segundo)
    estado <- "comendo";  comer()
    liberar(segundo);  liberar(primeiro)
    estado <- "pensando"
```

### Justiça

Depois de comer, o filósofo solta os garfos e vai pensar. Enquanto isso, o vizinho que já esperava pega o garfo, então ninguém come sempre antes dos outros. No resumo, todos comeram um número parecido de vezes:

```
 Filósofo | Refeições | Maior espera
    P0    |     11    |   0.77s
    P1    |     11    |   1.01s
    P2    |     11    |   0.91s
    P3    |     12    |   0.72s
    P4    |     12    |   0.78s
```

Logs completos em `parte1-filosofos/logs/`.

## Parte 2 — Threads e semáforos
## Parte 3 — Deadlock
## Vídeo