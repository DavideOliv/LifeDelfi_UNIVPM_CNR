import threading

class Pipeline:
    def get(self):
        pass
    def set(self, data):
        pass
    def end(self):
        pass

class OverwritingPipeline(Pipeline):
    def __init__(self, warning_handler = None):
        self.data = None
        self.end_flag = False
        self.warning_handler = warning_handler
        self.ready = threading.Lock()
        self.ready.acquire()

    def get(self):
        if self.end_flag:
            return (None, None)
        else:
            self.ready.acquire()
            return self.data

    def set(self, data):
        self.data = data
        if (self.warning_handler and not self.ready.locked):
            self.warning_handler()
        else:
            self.ready.release()

    def end(self):
        self.end_flag = True
        self.ready.release()

class FIFOPipeline(Pipeline):
    def __init__(self):
        self.data = []
        self.end_flag = False
        self.ready = threading.Semaphore(0)

    def get(self):
        if self.end_flag and len(self.data) == 0:
            return (None, None)
        self.ready.acquire()
        return self.data.pop(0)

    def set(self, new_data):
        self.data.append(new_data)
        self.ready.release()

    def end(self):
        self.end_flag = True