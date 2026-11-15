# TDE — Programação Concorrente

**Grupo:** 15
**Integrantes:** Mateus Grabarski de Mantova, Grazielle Claus de Almeida, Mariana Cordeiro Calado Silva.
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

### Como executar

```bash
cd parte3-deadlock
python deadlock.py  # versão com deadlock: trava e mostra diagnóstico
python deadlock-corrigido.py  # versão sem deadlock: roda normalmente sem nenhum travamento
```

### O problema — Deadlock

A Thread 1 adquire LOCK_A e depois o LOCK_B, enquanto a Thread 2 adquire LOCK_B e depois tenta adquirir LOCK_A. Thread 1 espera LOCK_B ser liberado enquanto Thread 2 espera LOCK_A ser liberado. Cada thread segura um lock enquanto espera o que a outra segura, resultando em um travamento dentro do processo.

### A solução — A antes de B

Usando hierarquia de recursos, todas as threads adquirem LOCK_A antes de LOCK_B, evitando a espera circular. A thread que chega primeiro ao LOCK_A (no log, a T1), ela começa adquirindo LOCK_A, dorme e depois pega o LOCK_B enquanto a Thread 2 fica esperando o LOCK_A da Thread 1 finalizar. Após finalizar, a Thread 1 libera os dois locks, e então a Thread 2 fica disponível para adquirir o LOCK_A, e depois o LOCK_B, continuando seu processo. Outro ponto é, como a ordem é a mesma para as duas threads, não acontece o travamento.

### Por que isso impede o ciclo?

Dentro da Thread 1, ela adquire primeiro LOCK_A, a thread dorme e depois adquire o LOCK_B, em paralelo a isso, a Thread 2 fica na espera dentro do acquire() do LOCK_A. Neste texto, "X ⇒ Y" significa que X espera algo que Y está segurando, e dentro da versão que trava, existem as duas setas ao mesmo tempo (T1 ⇒ T2 e T2 ⇒ T1), e isso forma o ciclo repetitivo. Já na versão corrigida, existe apenas T2 ⇒ T1: a T2 espera o LOCK_A, que a T1 segura. A seta T1 ⇒ T2 não existe, pois a T2 está bloqueada no primeiro lock e não segura nada, então a T1 não depende de nada da T2 para chegar aos `release()`. Sem essas duas setas, não há ciclo, e existe agora apenas uma seta: T2 ⇒ T1, T2 espera algo que T1 tem. O tempo de espera da Thread 2 fica entre as mensagens do log `Thread 2: tentando adquirir o lock A` e `Thread 2: em posse de lock A`. 

### As condições de Coffman

Para um deadlock acontecer, as quatro condições devem ocorrer ao mesmo tempo:

**Versão que trava (as quatro ocorrem):**

  • Exclusão mútua: T2 fica esperando no `acquire()` do LOCK_A enquanto a T1 segura;
  • Manter-e-esperar: T1 segura LOCK_A enquanto dorme e ainda vai pedir o LOCK_B, T2 segura LOCK_B enquanto dorme e ainda vai pedir o LOCK_A;
  • Não preempção: T1 só libera o LOCK_A chamando `release()`;
  • Espera circular: a T1 espera o LOCK_B (da T2), que espera o LOCK_A (da T1).

**Versão corrigida (uma é quebrada, três continuam):**

  • Exclusão mútua (continua): T2 fica esperando no `acquire()` do LOCK_A enquanto a T1 segura;
  • Manter-e-esperar (continua): T1 segura LOCK_A enquanto dorme e ainda vai pedir o LOCK_B;
  • Não preempção (continua): T1 só libera o LOCK_A chamando `release()`;
  • Espera circular (quebrada): como todas as threads pedem o LOCK_A antes do LOCK_B , a T2 espera no primeiro lock sem segurar nada, e o ciclo nunca se forma.

Com essa mudança dentro da versão corrigida, quebramos uma condição das 4 de Coffman, a Espera Circular, evitando um deadlock e escapando desse ciclo.

## Vídeo
