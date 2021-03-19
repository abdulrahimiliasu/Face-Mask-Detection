import threading as th
import time as t


def tii(tim):
    for i in range(0, 10):
        print("Loop")
        t.sleep(tim)


t1 = th.Thread(target=tii, args=(2,))
t2 = th.Thread(target=tii, args=(1,))

t1.start()
t2.start()
