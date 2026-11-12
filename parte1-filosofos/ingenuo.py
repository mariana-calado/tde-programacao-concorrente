import random
import threading
import time

N = 5
PAUSA_ENTRE_GARFOS = 1.0
TEMPO_SEM_PROGRESSO = 3.0

garfos = [threading.Lock() for _ in range(N)]
dono = [None] * N
esperando = [None] * N
estados = ["pensando"] * N

lock_print = threading.Lock()
inicio = ultimo_evento = time.perf_counter()


def log(p, mensagem):
    global ultimo_evento
    with lock_print:
        ultimo_evento = time.perf_counter()
        print(f"[{ultimo_evento - inicio:7.3f}s] P{p} {mensagem}", flush=True)


def mudar_estado(p, estado, detalhe=""):
    estados[p] = estado
    log(p, f"{estado.upper():<9} {detalhe}")


def pegar(p, g):
    esperando[p] = g
    garfos[g].acquire()
    esperando[p] = None
    dono[g] = p
    log(p, f"  pegou G{g}")


def soltar(g):
    dono[g] = None
    garfos[g].release()


def filosofo(p):
    esquerda, direita = (p - 1) % N, p

    while True:
        time.sleep(random.uniform(0.2, 1.0))

        mudar_estado(p, "com fome")
        pegar(p, esquerda)
        time.sleep(PAUSA_ENTRE_GARFOS)
        pegar(p, direita)

        mudar_estado(p, "comendo")
        time.sleep(random.uniform(0.2, 0.6))

        soltar(direita)
        soltar(esquerda)
        mudar_estado(p, "pensando", f"(soltou G{direita} e G{esquerda})")


def mostrar_diagnostico():
    print("\n" + "=" * 64)
    print(f"DEADLOCK! Nenhum filósofo progrediu nos últimos {TEMPO_SEM_PROGRESSO:.0f}s.")
    print("=" * 64)
    for p in range(N):
        g = esperando[p]
        print(f"  P{p} está {estados[p]}, segura G{dono.index(p)} "
              f"e espera G{g}, que está com P{dono[g]}")

    ciclo = [0]
    while True:
        ciclo.append(dono[esperando[ciclo[-1]]])
        if ciclo[-1] == ciclo[0]:
            break
    print("\n  Espera circular: " + " -> ".join(f"P{p}" for p in ciclo))

    print("\n  As 4 condições de Coffman estão presentes ao mesmo tempo:")
    print("   1. Exclusão mútua:  cada garfo só fica com um filósofo por vez")
    print("   2. Manter-e-esperar: cada um segura um garfo enquanto espera o outro")
    print("   3. Não preempção:   ninguém tira o garfo da mão do outro")
    print("   4. Espera circular: o ciclo acima")

    print("\n  Threads vivas (threading.enumerate()):")
    for t in threading.enumerate():
        print(f"   - {t.name}")
    print("=" * 64)


def main():
    print(f"Jantar dos Filósofos - VERSÃO INGÊNUA (N = {N})")
    print("Todos pegam primeiro o garfo da ESQUERDA e depois o da DIREITA.\n")

    for p in range(N):
        threading.Thread(target=filosofo, args=(p,), name=f"Filosofo-{p}", daemon=True).start()

    try:
        while time.perf_counter() - ultimo_evento < TEMPO_SEM_PROGRESSO:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário (não travou desta vez).")
        return

    mostrar_diagnostico()


if __name__ == "__main__":
    main()
