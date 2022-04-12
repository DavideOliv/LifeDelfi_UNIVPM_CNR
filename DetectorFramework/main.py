from detector.apps import SQLiteOfflineDetectorApp
from glob import glob
import os

if __name__ == "__main__":
    """Inserisce i csv di output nella stessa cartella dei file audio"""
    path = input("Enter path to wav files: ")
    for filename in glob(os.path.join(path,"*.wav")):
        print(filename)
        SQLiteOfflineDetectorApp(filename).run()