from detector.apps import SQLiteOfflineDetectorApp
from glob import glob
import os
import sys

if __name__ == "__main__":
    """Inserisce i csv di output nella stessa cartella dei file audio"""
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <path>")
        exit(1)
    path = sys.argv[1]
    for filename in glob(os.path.join(path,"*.wav")):
        print(filename)
        SQLiteOfflineDetectorApp(filename).run()