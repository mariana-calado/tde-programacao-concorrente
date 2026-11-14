import threading, time

LOCK_A = threading.Lock()
LOCK_B = threading.Lock()

def thread_1_2(thread):

    print(f"{thread}: tentando adquirir o lock A")
    LOCK_A.acquire()
    print(f"{thread}: em posse de lock A")

    print(f"{thread}: dormindo por 50ms")
    time.sleep(0.05)

    print(f"{thread}: tentando adquirir o lock B")
    LOCK_B.acquire()
    print(f"{thread}: em posse de lock B")

    print(f"{thread}: concluída")

    print(f"{thread}: liberando o lock B")
    LOCK_B.release()

    print(f"{thread}: liberando o lock A")
    LOCK_A.release()

if __name__ == "__main__":

    thread1 = threading.Thread(target=thread_1_2, args=("Thread 1",))
    thread2 = threading.Thread(target=thread_1_2, args=("Thread 2",))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()


# 2 threads uma única função e uma main

# Exercício 3.B

# Regra global: sempre adquirir LOCK_A antes de LOCK_B,
# em TODAS as threads.
# Thread 1 e Thread 2:
# adquirir(LOCK_A)
# adquirir(LOCK_B)
# // secao critica
# liberar(LOCK_B)
# liberar(LOCK_A)

# T1 fica com ambos locks, T2 fica esperando T1 liberar LOCK_A. T1 libera ambos, e T2 pega o A e o B

# colocar cores, está dificil de diferenciar as pritns
