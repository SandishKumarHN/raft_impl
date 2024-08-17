from threading import Thread
import queue
import time


def producer(q):
    for i in range(10):
        print('Producing', i)
        q.put(i)
        time.sleep(1)
    q.put(None)
    print('Producer done')

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print('Consuming', item)
    print('Consumer goodbye')

def main():
    q = queue.Queue()
    t1 = Thread(target=producer, args=[q])
    t2 = Thread(target=consumer, args=[q])
    t1.start()
    t2.start()
    print('Waiting....')
    t1.join()
    t2.join()
    print('Done')

main()