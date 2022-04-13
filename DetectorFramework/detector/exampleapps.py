from detector.datamanagers import *
from detector.datasources import *
from detector.pipelines import *
from detector.layers import *
from detector.processors import *
from detector.app import App
import datetime
import os


class OfflineDetectorApp(App):
    """Processa un file audio wav"""

    def __init__(self, filename, SECONDS=1, SR=192000):
        N_SAMPLES = SECONDS * SR
        ds = WAVFileDataSource(filename, N_SAMPLES)
        pl = FIFOPipeline()
        pr = Processor()
        pr.addLayer(FilterLayer("highpass", 30e3, SR))
        pr.addLayer(PeaksLayer(5, 50e-3*SR, 5*SECONDS))
        pr.addLayer(PeaksVarianceLayer(1000, 0.05))
        dm = CSVDataManager(
            filename + ".csv", {"filename": os.path.basename(filename), "datetime": os.path.basename(filename)[:15], "chunkLength": SECONDS})

        super().__init__(ds, pl, pr, dm)


class SQLiteOfflineDetectorApp(App):
    """Processa un file audio wav"""

    def __init__(self, filename, SECONDS=1, SR=192000):
        N_SAMPLES = SECONDS * SR
        ds = WAVFileDataSource(filename, N_SAMPLES)
        pl = FIFOPipeline()
        pr = Processor()
        pr.addLayer(FilterLayer("highpass", 30e3, SR))
        pr.addLayer(PeaksLayer(5, 50e-3*SR, 5*SECONDS))
        pr.addLayer(PeaksVarianceLayer(1000, 0.05))
        dm = SQLiteDataManager("offline.db", {"filename": os.path.basename(filename), "datetime": os.path.basename(filename)[:15], "chunkLength": SECONDS},
                               save_wave=True)

        super().__init__(ds, pl, pr, dm)


class FakeOnlineDetectorApp(App):
    """Processa un file audio wav, ma con delay simulando acquisizione dati real time"""

    def __init__(self, filename, SECONDS=1, SR=192000):
        N_SAMPLES = SECONDS * SR
        pl = OverwritingPipeline()
        ds = WAVFileDataSource(filename, N_SAMPLES, delay_sec=SECONDS)
        pr = Processor()
        pr.addLayer(FilterLayer("highpass", 30e3, SR))
        pr.addLayer(PeaksLayer(5, 50e-3*SR, 5*SECONDS))
        pr.addLayer(PeaksVarianceLayer(1000, 0.05))
        dm = SQLiteDataManager(
            "fakeonline.db", 
            {"filename": os.path.basename(filename), "datetime": os.path.basename(filename)[:15], "chunkLength": SECONDS},
            save_wave=True)

        super().__init__(ds, pl, pr, dm)


class OnlineDetectorApp(App):
    """Processa audio acquisito in tempo reale attraverso arecord"""

    def __init__(self, SECONDS=1, SR=192000):
        N_SAMPLES = SECONDS * SR
        pl = OverwritingPipeline()
        ds = ARecordDataSource(SR, N_SAMPLES)
        pr = Processor()
        pr.addLayer(FilterLayer("highpass", 30e3, SR))
        pr.addLayer(PeaksLayer(5, 50e-3*SR, 5*SECONDS))
        pr.addLayer(PeaksVarianceLayer(1000, 0.05))
        dm = SQLiteDataManager(
            "realtime.db", {"filename": "arecord", "datetime": datetime.datetime.now(
            ).strftime("%Y%m%d%H%M%S"), "chunkLength": SECONDS},
            save_wave=True)

        super().__init__(ds, pl, pr, dm)
