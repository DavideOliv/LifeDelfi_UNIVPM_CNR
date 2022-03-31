from detector.datamanager import DataManager
from detector.datasources import *
from detector.pipelines import *
from detector.layers import *
from detector.processors import *
import threading

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
            chunk = self.pl.get()
            if chunk is not None:
                result, data_dict = self.pr.check(chunk)
                self.dm.addRecord(data_dict)
            else:
                break
        self.dm.export_csv()


    def fetch_task(self):
        while True:
            samples = self.ds.getChunk()
            if samples is None:
                self.pl.end()
                break
            else:
                self.pl.set(samples)


class OfflineDetectorApp(App):
    """Processa un file audio wav"""
    def __init__(self, filename, SECONDS = 1, SR = 192000):
        N_SAMPLES = SECONDS * SR
        ds = WAVFileDataSource(filename, N_SAMPLES)
        pl = FIFOPipeline()
        pr = Processor()
        pr.addLayer(FilterLayer("highpass", 30e3, SR))
        pr.addLayer(PeaksLayer(5, 50e-3*SR, 5*SECONDS))
        pr.addLayer(PeaksVarianceLayer(1000, 0.05))
        dm = DataManager(filename + ".csv")

        super().__init__(ds, pl, pr, dm)


class FakeOnlineDetectorApp(App):
    """Processa un file audio wav, ma con delay simulando acquisizione dati real time"""
    def __init__(self, filename, SECONDS = 1, SR = 192000):
        N_SAMPLES = SECONDS * SR
        pl = OverwritingPipeline()
        ds = WAVFileDataSource(filename, N_SAMPLES, delay_sec=SECONDS)
        pr = Processor()
        pr.addLayer(FilterLayer("highpass", 30e3, SR))
        pr.addLayer(PeaksLayer(5, 50e-3*SR, 5*SECONDS))
        pr.addLayer(PeaksVarianceLayer(1000, 0.05))
        dm = DataManager(filename + ".csv")

        super().__init__(ds, pl, pr, dm)


class OnlineDetectorApp(App):
    """Processa audio acquisito in tempo reale attraverso arecord"""
    def __init__(self, filename, SECONDS=1, SR=192000):
        N_SAMPLES = SECONDS * SR
        pl = OverwritingPipeline()
        ds = ARecordDataSource(SR, N_SAMPLES)
        pr = Processor()
        pr.addLayer(FilterLayer("highpass", 30e3, SR))
        pr.addLayer(PeaksLayer(5, 50e-3*SR, 5*SECONDS))
        pr.addLayer(PeaksVarianceLayer(1000, 0.05))
        dm = DataManager(filename + ".csv")

        super().__init__(ds, pl, pr, dm)