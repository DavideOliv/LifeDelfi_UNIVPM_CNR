import threading
from detector.datasources import DataSource
from detector.datamanagers import DataManager
from detector.pipelines import Pipeline
from detector.processors import Processor


class App:
    def __init__(self, ds : DataSource, pl : Pipeline, pr : Processor, dm : DataManager):
        self.ds = ds
        self.pl = pl
        self.pr = pr
        self.dm = dm

        self.check_task = threading.Thread(target=self.check_task)
        self.fetch_task = threading.Thread(target=self.fetch_task)

    def run(self):
        self.fetch_task.start()
        self.check_task.start()

        try:
            self.fetch_task.join()
            self.check_task.join()
        except:
            self.pl.end()


    def check_task(self):
        while True:
            chunk, initialProps = self.pl.get()
            if chunk is not None:
                result, data_dict = self.pr.check(chunk, initial_props=initialProps)
                self.dm.addRecord(data_dict)
            else:
                break
        self.dm.close()


    def fetch_task(self):
        while True:
            samples, initialProps = self.ds.getChunk()
            if samples is None:
                self.pl.end()
                break
            else:
                self.pl.set((samples, initialProps))