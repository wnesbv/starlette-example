import threading


def dummyfn(msg="foo"):
    print(msg)
threading.Timer(5, dummyfn).start()


def hours_to_write(happy_hours):
    return [happy_hours + 2, happy_hours + 4, happy_hours + 6]


print(hours_to_write(4))
