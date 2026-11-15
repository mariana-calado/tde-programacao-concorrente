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
