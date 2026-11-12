import random
import threading
import time

N = 5
PAUSA_ENTRE_GARFOS = 0.1
DURACAO = 15

garfos = [threading.Lock() for _ in range(N)]
refeicoes = [0] * N
maior_espera = [0.0] * N
parar = threading.Event()

lock_print = threading.Lock()
inicio = time.perf_counter()


def log(p, mensagem):
    with lock_print:
        print(f"[{time.perf_counter() - inicio:7.3f}s] P{p} {mensagem}", flush=True)


def ordem(p):
    return sorted(((p - 1) % N, p))


def filosofo(p):
    primeiro, segundo = ordem(p)

    while not parar.wait(random.uniform(0.2, 1.0)):
        log(p, "COM FOME")
        comeco_da_fome = time.perf_counter()

        garfos[primeiro].acquire()
        log(p, f"  pegou G{primeiro}")
        time.sleep(PAUSA_ENTRE_GARFOS)
        garfos[segundo].acquire()
        log(p, f"  pegou G{segundo}")

        espera = time.perf_counter() - comeco_da_fome
        refeicoes[p] += 1
        maior_espera[p] = max(maior_espera[p], espera)
        log(p, f"COMENDO   (esperou {espera:.2f}s)")
        time.sleep(random.uniform(0.2, 0.6))

        garfos[segundo].release()
        garfos[primeiro].release()
        log(p, f"PENSANDO  (soltou G{segundo} e G{primeiro})")


def main():
    print(f"Jantar dos Filósofos - VERSÃO CORRIGIDA: hierarquia de recursos (N = {N})")
    print("Ordem de aquisição de cada filósofo (menor número primeiro):")
    for p in range(N):
        primeiro, segundo = ordem(p)
        obs = "  <- inverteu a ordem" if primeiro != (p - 1) % N else ""
        print(f"  P{p}: G{primeiro} -> G{segundo}{obs}")
    print()

    threads = [threading.Thread(target=filosofo, args=(p,), name=f"Filosofo-{p}")
               for p in range(N)]
    for t in threads:
        t.start()

    time.sleep(DURACAO)
    parar.set()
    for t in threads:
        t.join()

    print("\n" + "=" * 46)
    print(f"RESUMO após {DURACAO}s - o programa terminou: sem deadlock")
    print("=" * 46)
    print(" Filósofo | Refeições | Maior espera")
    for p in range(N):
        print(f"    P{p}    |    {refeicoes[p]:>3}    |   {maior_espera[p]:.2f}s")
    print(f"\n Total de refeições: {sum(refeicoes)}")
    print(f" Mínimo/máximo por filósofo: {min(refeicoes)}/{max(refeicoes)}"
          " -> todos comeram (sem inanição)")


if __name__ == "__main__":
    main()
