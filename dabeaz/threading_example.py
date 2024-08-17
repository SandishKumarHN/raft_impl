import time
from threading import Thread, Event, Lock

def countdown(n):
    while n > 0:
        print('T-minus', n)
        time.sleep(1)
        n -= 1
        
def countup(stop):
    x = 0
    while x < stop:
        print('Up we go', x)
        time.sleep(1)
        x += 1

def main():
    t1 = Thread(target=countdown, args=[10])
    t2 = Thread(target=countup, args=[5])
    t1.start()
    t2.start()
    print('Waiting')
    t1.join()
    t2.join()
    print('Goodboy')


def waiter(evt):
    print("Yawn. I'm waiting")
    evt.wait()
    print("I'm awake")

def main1():
    evt = Event()
    for i in range(5):
        Thread(target=waiter, args=[evt]).start()
    time.sleep(10)
    evt.set()

data = {
    'a' : 1,
    'b' : 2,
    'c' : 3,
    'd': 4
}

data_lock = Lock()
def process_data():
    data_lock.acquire()
    for key, value in data.items():
        print(f'Key: {key}, Value: {value}')
        time.sleep(1)
    data_lock.release()

def main2():
    Thread(target=process_data).start()
    time.sleep(1)
    data_lock.acquire()
    data['a'] = 200
    data_lock.release()
    print(data)
main2()
# main1()
# main()
    
class Future:
    def __init__(self):
        self.evt = Event()
        self.value = None
    
    def set_result(self, value):
        self.value = value
        self.evt.set()
    
    def result(self):
        self.evt.wait()
        return self.value
def f(x, y, fut):
    time.sleep(10)
    fut.set_result(x + y)

def main3():
    fut = Future()
    Thread(target=f, args=[2, 3, fut]).start()
    print(fut.result())

main3()