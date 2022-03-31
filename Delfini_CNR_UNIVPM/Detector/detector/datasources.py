import numpy as np
import subprocess
import scipy.io.wavfile
import time

class DataSource:
    SAMPLE_TYPE = np.int16
    SAMPLE_BYTESIZE = np.dtype(SAMPLE_TYPE).itemsize

    # Metodo da overridare nelle sottoclassi
    def getChunk(self, n_samples: int) -> np.ndarray:
        return np.empty(n_samples, dtype=self.SAMPLE_TYPE)


class ARecordDataSource(DataSource):
    def __init__(self, sr: int, n_samples : int):
        SAMPLE_BITSIZE = self.SAMPLE_BYTESIZE*8
        self.sr = sr
        self.n_samples = n_samples
        self.process = subprocess.Popen(
            f'arecord -f S{SAMPLE_BITSIZE}_LE -r {sr} -c 1 -t raw', stdout=subprocess.PIPE, shell=True)

    # @OVERRIDE
    def getChunk(self) -> np.ndarray:
        n_bytes = self.SAMPLE_BYTESIZE * self.n_samples
        byte_chunk = self.process.stdout.read(n_bytes)
        assert len(byte_chunk) == n_bytes
        chunk = np.frombuffer(byte_chunk, dtype=self.SAMPLE_TYPE)
        assert chunk.shape[0] == self.n_samples
        return chunk

    # Distruttore che alla "morte" dell'istanza della classe va a terminare anche il processo
    def __del__(self):
        self.p.terminate()


class WAVFileDataSource(DataSource):
    def __init__(self, filename : str, n_samples : int, delay_sec : float = 0):
        self.sr, self.wavfile = scipy.io.wavfile.read(filename)
        self.n_samples = n_samples
        self.delay_sec = delay_sec
        self.offset = 0
    
    def getChunk(self) -> tuple[np.ndarray, float]:
        oldoffset = self.offset
        self.offset += self.n_samples
        if self.delay_sec > 0:
            time.sleep(self.delay_sec)  #simula delay campionamento
        chunk = self.wavfile[oldoffset:self.offset]
        if chunk.shape[0] != self.n_samples:
            return None, None
        else:
            return chunk, oldoffset/self.sr