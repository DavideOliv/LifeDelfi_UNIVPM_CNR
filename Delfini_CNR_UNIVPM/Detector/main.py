from detector.apps import OfflineDetectorApp
from glob import glob
import os

if __name__ == "__main__":
    """Inserisce i csv di output nella stessa cartella dei file audio"""
    path = input("Enter path to wav files: ")
    for filename in glob(os.path.join(path,"*.wav")):
        print(filename)
        OfflineDetectorApp(filename).run()