from concurrent.futures import ThreadPoolExecutor


class ThreadManager:
    """
    单例模式实现的线程池
    """
    def __init__(self, worker=2):
        self._thread_pool = ThreadPoolExecutor(max_workers=worker)
        self._max_workers = worker
        self._future_list = []

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(ThreadManager, cls).__new__(cls)
        return cls._instance

    def has_idle_worker(self):
        return len(self._future_list) != self._max_workers

    def add_with_callback(self, function, callback):
        if len(self._future_list) == self._max_workers:
            print("Thread pool no idle worker,please wait a moment")
            return False
        future = self._thread_pool.submit(function)
        future.add_done_callback(callback)
        self._future_list.append(future)
        return True

