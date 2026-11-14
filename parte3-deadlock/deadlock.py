import threading, time, faulthandler, sys

faulthandler.enable()

LOCK_A = threading.Lock()
LOCK_B = threading.Lock()

def thread1():

    print("Thread 1: tentando adquirir o lock A")
    LOCK_A.acquire()
    print("Thread 1: em posse do lock A")

    print("Thread 1: dormindo por 50ms")
    time.sleep(0.05)
    print("Thread 1: acordou")

    print("Thread 1: tentando adquirir o lock B")
    LOCK_B.acquire()
    print("Thread 1: em posse do lock B")

    print("Thread 1: concluída")

    print("Thread 1: liberando o lock B")
    LOCK_B.release()

    print("Thread 1: liberando o lock A")
    LOCK_A.release()

def thread2():

    print("Thread 2: tentando adquirir o lock B")
    LOCK_B.acquire()
    print("Thread 2: em posse do lock B")

    print("Thread 2: dormindo por 50ms")
    time.sleep(0.05)
    print("Thread 2: acordou")

    print("Thread 2: tentando adquirir o lock A")
    LOCK_A.acquire()
    print("Thread 2: em posse do lock A")

    print("Thread 2: concluída")

    print("Thread 2: liberando o lock A")
    LOCK_A.release()

    print("Thread 2: liberando o lock B")
    LOCK_B.release()

if __name__ == "__main__":

    faulthandler.dump_traceback_later(timeout=5.0, repeat=False, file=sys.stderr, exit=True, max_threads=3)

    thread1 = threading.Thread(target=thread1)
    thread2 = threading.Thread(target=thread2)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()


# 3 funções, 2 para as threads e 1 para o main

# Exercício 3.B

# Pseudocódigo de referência (versão que trava)
# LOCK_A, LOCK_B = locks distintos
# Thread 1:
# adquirir(LOCK_A)
# dormir(50ms) // aumenta a chance do deadlock
# adquirir(LOCK_B)
# imprimir "T1 concluiu"
# liberar(LOCK_B)
# liberar(LOCK_A)

# Thread 2:
# adquirir(LOCK_B)
# dormir(50ms)
# adquirir(LOCK_A)
# imprimir "T2 concluiu"
# liberar(LOCK_A)
# liberar(LOCK_B)

# colocar cores, está dificil de diferenciar as pritns
# quando acaba fica confuso, apenas um " " sem falar nada, pra sair da keyboardinterrupt

# Soluções?:
# Algum jeito de depurar
# Um try catch, exit
# Algo relacionado a timmeout


# 19 -> LOCK_B.acquire()
# 42 -> LOCK_A.acquire()
# o outro era no join

# https://docs.python.org/3/library/threading.html
# https://docs.python.org/3/library/faulthandler.html 