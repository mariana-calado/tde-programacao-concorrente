import sys
import threading
import time

T = 8
M = 200_000

count = 0
sem = threading.Semaphore(1)


def incrementa(valor):
    return valor + 1


def tarefa():
    global count
    for _ in range(M):
        sem.acquire()
        try:
            tmp = count
            tmp = incrementa(tmp)
            count = tmp
        finally:
            sem.release()


def main():
    sys.setswitchinterval(1e-6)

    threads = [threading.Thread(target=tarefa) for _ in range(T)]

    inicio = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    tempo = time.perf_counter() - inicio

    esperado = T * M
    perdidos = esperado - count
    print(f"[Versão 2 - semáforo binário] T = {T}, M = {M:,}")
    print(f"esperado = {esperado:,} | obtido = {count:,} | tempo = {tempo:.3f} s")
    print("CORRETO" if perdidos == 0 else f"PERDEU {perdidos:,} incrementos")


if __name__ == "__main__":
    main()