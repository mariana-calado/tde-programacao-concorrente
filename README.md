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

```bash
cd parte2-semaforo
python SemSincronizacao.py   # sem sincronização: perde incrementos Versão 1
python ComSemaforo.py        # com semáforo binário: valor correto Versão 2
```

Parâmetros: **T = 8** threads, **M = 200.000** incrementos por thread, valor esperado **T × M = 1.600.000**. Usando apenas a biblioteca padrão (`threading`, `time`, `sys`).

### O problema

T threads incrementam um contador global `count`, M vezes cada. Na Versão 1 não há proteção, na Versão 2 a seção crítica é protegida por um semáforo binário (`threading.Semaphore(1)`). O corpo do incremento é idêntico nas duas versões, então a única diferença é o `acquire()`/`release()`.

Para a corrida ficar reproduzível no CPython, o incremento foi separado em três passos (ler, somar, escrever), com a soma em uma função `incrementa()`, e o intervalo de troca de threads foi reduzido com `sys.setswitchinterval(1e-6)`. Isso não cria o problema, apenas o torna visível. Com o GIL, uma soma simples quase nunca é interrompida no meio. As duas versões usam a mesma configuração, para a comparação de tempo ser justa.

### Resultados

| Versão | Execução | Esperado | Obtido | Tempo (s) | Resultado |
|---|---|---|---|---|---|
| 1 – sem sincronização | 1 | 1.600.000 | 423,923 | 3.837 | PERDEU 1.176.077 |
| 1 – sem sincronização | 2 | 1.600.000 | 422,195 | 4.379 | PERDEU 1,177,805 |
| 1 – sem sincronização | 3 | 1.600.000 | 419,950 | 4.059 | PERDEU 1,180,050 |
| 2 – semáforo binário | 1 | 1.600.000 | 1.600.000 | 44.140 | CORRETO |
| 2 – semáforo binário | 2 | 1.600.000 | 1.600.000 | 41.881 | CORRETO |
| 2 – semáforo binário | 3 | 1.600.000 | 1.600.000 | 43.412 | CORRETO |

Logs de execução:

```
[Versão 1 - sem sincronização] T = 8, M = 200,000
esperado = 1,600,000 | obtido = 423,923 | tempo = 3.837 s
PERDEU 1,176,077 incrementos
```

```
[Versão 2 - semáforo binário] T = 8, M = 200,000
esperado = 1,600,000 | obtido = 1,600,000 | tempo = 44.140 s
CORRETO
```

### Por que a versão sem sincronização perde incrementos

`count = count + 1` parece uma operação só, mas são três passos: **ler** o valor, **somar** 1 e **escrever** o resultado. Se duas threads leem o mesmo valor antes de qualquer uma escrever, as duas calculam o mesmo resultado e a segunda escrita sobrescreve a primeira, então um incremento se perde (*lost update*). O trecho que lê e escreve o contador é uma **seção crítica** que não é atômica, e como o escalonador decide quando trocar de thread, o resultado muda a cada execução, algo que é típico de uma condição de corrida.

### Por que a versão com semáforo é correta

O semáforo foi criado com uma única permissão, então funciona como semáforo binário. Só a thread que conseguiu o `acquire()` executa a seção crítica, e as outras bloqueiam até o `release()`. Isso garante **exclusão mútua**, ou seja, os passos ler, somar e escrever de uma thread nunca se intercalam com os de outra, e o resultado é sempre T × M. O `release()` fica em um bloco `finally`, para a permissão ser devolvida mesmo se ocorrer uma exceção. Sem isso, as outras threads ficariam bloqueadas para sempre.

### Trade-off de throughput

A Versão 2 levou cerca de 11×(em média) o tempo da Versão 1 (44s contra 3,8s). A Versão 1 é mais rápida, mas o resultado está errado. O custo da Versão 2 vem de duas fontes:

- cada incremento paga `acquire()` e `release()`, num total de 1,6 milhão de aquisições;
- as 8 threads disputam um único recurso, então há contenção, a thread que não consegue a permissão bloqueia e precisa ser acordada pelo sistema operacional, e essa troca de contexto domina o tempo porque a seção crítica é muito pequena.

O tempo absoluto e a proporção entre as versões dependem da máquina, do sistema operacional e da versão do Python.”

### Justiça (fairness)

O `threading.Semaphore` do Python mantém uma fila de threads bloqueadas e, na prática, acorda em ordem de chegada, o que evita inanição. Justiça tem custo: mais trocas de contexto e menos throughput. Sem ela, uma thread que acabou de liberar poderia readquirir logo em seguida. Isso costuma ser mais rápido, mas pode deixar outras threads esperando indefinidamente. A documentação não promete essa ordem, então a justiça não é formal.

### Visibilidade e ordenação

Existem dois problemas distintos em memória compartilhada:
- **Atomicidade:** É o lost update descrito acima, que é resolvido pela exclusão mútua.
- **Visibilidade e ordenação:** É saber se a escrita de uma thread fica visível para as outras e em que ordem. Sem sincronização, o compilador, o interpretador e a CPU podem reordenar ou atrasar escritas, e nada garante que outra thread veja o valor atualizado.

No Java, o modelo de memória define a relação **happens-before**: o `release()` de um semáforo (ou o `unlock()` de um lock) acontece antes do `acquire()` seguinte, então tudo que a primeira thread escreveu na seção crítica fica visível para a próxima.

E em CPython, o efeito prático é o mesmo, por **barreiras implícitas**. O GIL garante que só uma thread execute bytecode por vez e é liberado e readquirido nas trocas de thread, o que funciona como barreira. Além disso, as primitivas de `threading` (`Lock`, `Semaphore`) fazem `release()` publicar as escritas e `acquire()` enxergá-las. Isso esconde boa parte do problema de visibilidade, mas é um detalhe da implementação CPython e não uma garantia da linguagem. Em builds sem GIL, a sincronização explícita passa a ser indispensável. O semáforo continua sendo o que torna o programa correto em qualquer cenário.

### Intervalo das trocas

Ao remover `sys.setswitchinterval(1e-6)` e usar o intervalo padrão do CPython (5 ms), a Versão 1 não perdeu incrementos(o valor obtido foi 1.600.000), e os tempos caíram para 0,15 s (Versão 1) e 2 s (Versão 2). Com esse intervalo, as threads quase nunca são interrompidas no meio do incremento, então a condição de corrida existe, mas raramente se manifesta. Por isso o sys.setswitchinterval(1e-6) foi mantido na demonstração: ele força trocas de thread frequentes e expõe a corrida, ao custo de tempos bem maiores. Isso mostra que a ausência de erro em uma execução não prova que o código está correto. Sem sincronização, o programa continua incorreto, ou seja, ele não garante o resultado mesmo quando acerta.

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

Logs completos dentro da pasta `parte3-deadlock/logs/`.

## Vídeo

https://youtu.be/AiYME7GanJA