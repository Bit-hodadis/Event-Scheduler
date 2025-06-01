import threading

_thread_local = threading.local()


def set_current_user(user):
    _thread_local.user = user


def set_current_ip(ip):
    _thread_local.ip = ip


def get_current_user():
    return getattr(_thread_local, "user", None)


def get_current_ip():
    return getattr(_thread_local, "ip", None)
