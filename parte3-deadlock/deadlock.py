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