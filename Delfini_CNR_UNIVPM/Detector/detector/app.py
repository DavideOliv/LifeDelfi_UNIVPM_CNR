from detector.datamanager import DataManager
from detector.datasources import *
from detector.pipelines import *
from detector.layers import *
from detector.processors import *
import threading

def check_task(processor: Processor, pipeline: Pipeline, data_manager: DataManager):
    while True:
        chunk = pipeline.get()
        if chunk is not None:
            result, data_dict = processor.check(chunk)
            data_manager.addRecord(data_dict)
        else:
            break
    data_manager.export_csv()


def fetch_task(n_samples: int, ds: DataSource, pipeline: Pipeline):
    while True:
        samples = ds.getChunk(n_samples)
        if samples.shape[0] < n_samples:
            pipeline.end()
            break
        else:
            pipeline.set(samples)


def offlineDetector(filename, SECONDS = 1, SR = 192000):
    """takes offline audio data from wavfile and process it with fifo pipeline"""
    N_SAMPLES = SECONDS * SR
    pl = FIFOPipeline()
    ds = WAVFileDataSource(filename)
    processor = Processor()
    processor.addLayer(FilterLayer("highpass", 30e3, SR))
    processor.addLayer(PeaksLayer(5, 50e-3*SR, 5*SECONDS))
    processor.addLayer(PeaksVarianceLayer(1000, 0.05))

    dm = DataManager(filename + ".csv")

    check_thread = threading.Thread(target=check_task, args=(processor, pl, dm))
    fetch_thread = threading.Thread(
        target=fetch_task, args=(N_SAMPLES, ds, pl))

    fetch_thread.start()
    check_thread.start()

    try:
        fetch_thread.join()
        check_thread.join()
    except:
        pl.end()

def fakeOnlineDetector(filename, SECONDS = 1, SR = 192000):
    """takes audio data from wavfile but with delay, simulating real time data acquisition"""
    N_SAMPLES = SECONDS * SR
    pl = OverwritingPipeline()
    ds = WAVFileDataSource(filename, delay_sec=SECONDS)
    processor = Processor()
    processor.addLayer(FilterLayer("highpass", 30e3, SR))
    processor.addLayer(PeaksLayer(5, 50e-3*SR, 5*SECONDS))
    processor.addLayer(PeaksVarianceLayer(1000, 0.05))

    check_thread = threading.Thread(target=check_task, args=(processor, pl))
    fetch_thread = threading.Thread(
        target=fetch_task, args=(N_SAMPLES, ds, pl))

    fetch_thread.start()
    check_thread.start()

    try:
        fetch_thread.join()
        check_thread.join()
    except:
        pl.end()


def onlineDetector(filename, SECONDS=1, SR=192000):
    """takes audio data from arecord source and uses overwriting pipeline"""
    N_SAMPLES = SECONDS * SR
    pl = OverwritingPipeline()
    ds = ARecordDataSource(SR)
    processor = Processor()
    processor.addLayer(FilterLayer("highpass", 30e3, SR))
    processor.addLayer(PeaksLayer(5, 50e-3*SR, 5*SECONDS))
    processor.addLayer(PeaksVarianceLayer(1000, 0.05))

    check_thread = threading.Thread(target=check_task, args=(processor, pl))
    fetch_thread = threading.Thread(
        target=fetch_task, args=(N_SAMPLES, ds, pl))

    fetch_thread.start()
    check_thread.start()

    try:
        fetch_thread.join()
        check_thread.join()
    except:
        pl.end()