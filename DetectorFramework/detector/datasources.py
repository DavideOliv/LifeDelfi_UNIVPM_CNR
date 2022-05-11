import matplotlib.pyplot as plt
import socket
import numpy as np
import subprocess
import scipy.io.wavfile
import time

class DataSource:
    SAMPLE_TYPE = np.int16
    SAMPLE_BYTESIZE = np.dtype(SAMPLE_TYPE).itemsize

    # Metodo da overridare nelle sottoclassi
    def getChunk(self) -> np.ndarray:
        raise NotImplementedError()


class ARecordDataSource(DataSource):
    def __init__(self, sr: int, n_samples : int):
        SAMPLE_BITSIZE = self.SAMPLE_BYTESIZE*8
        self.sr = sr
        self.n_samples = n_samples
        self.offset = 0
        self.process = subprocess.Popen(
            f'arecord -f S{SAMPLE_BITSIZE}_LE -r {sr} -c 1 -t raw', stdout=subprocess.PIPE, shell=True)

    def getChunk(self):
        n_bytes = self.SAMPLE_BYTESIZE * self.n_samples
        byte_chunk = self.process.stdout.read(n_bytes)
        assert len(byte_chunk) == n_bytes
        chunk = np.frombuffer(byte_chunk, dtype=self.SAMPLE_TYPE)
        assert chunk.shape[0] == self.n_samples
        toReturn = (chunk, {"offset":self.offset, "wave": byte_chunk})
        self.offset += (self.n_samples/self.sr)
        return toReturn

    # Distruttore che alla "morte" dell'istanza della classe va a terminare anche il processo
    def __del__(self):
        self.p.terminate()


class WAVFileDataSource(DataSource):
    def __init__(self, filename : str, n_samples : int, delay_sec : float = 0):
        self.sr, self.wavfile = scipy.io.wavfile.read(filename)
        self.n_samples = n_samples
        self.delay_sec = delay_sec
        self.offset = 0
    
    def getChunk(self):
        oldoffset = self.offset
        self.offset += self.n_samples
        if self.delay_sec > 0:
            time.sleep(self.delay_sec)  #simula delay campionamento
        chunk = self.wavfile[oldoffset:self.offset]
        if chunk.shape[0] != self.n_samples:
            return None, None
        else:
            return chunk, {"offset":oldoffset/self.sr, "wave": bytearray(chunk)}

class JackDataSource(DataSource):
    def __init__(self, host="127.0.0.1", port = 8888):
        size_of_float = 4
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socket.sendall(b"nframes")
        self.nframes = int(self.socket.recv(256).decode("utf8").split("\n")[0])
        self.socket.sendall(b"len")
        self.nblocks = int(self.socket.recv(256).decode('utf8').split("\n")[0])
        self.socket.sendall(b"rate")
        self.samplerate = int(self.socket.recv(256).decode('utf8').split("\n")[0])
        self.socket.sendall(b"seconds")
        self.seconds = int(self.socket.recv(256).decode('utf8').split("\n")[0])
        self.blocksize = size_of_float * self.nframes
        self.socket.sendall(b"dump")
        self.i = -1

    def getChunk(self):
        if self.i >= self.nblocks:
            return None, None
        chunk = np.frombuffer(s.recv(self.blocksize), dtype=np.float32)
        self.i += 1
        return chunk, {"offset":self.i/self.samplerate, "wave": chunk, "chunkLength": self.nframes}
