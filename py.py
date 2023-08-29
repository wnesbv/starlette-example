import threading
def dummyfn(msg="foo"):
    print(msg)
threading.Timer(5, dummyfn).start()
