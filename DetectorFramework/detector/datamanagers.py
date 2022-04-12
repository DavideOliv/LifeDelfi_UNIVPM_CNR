import pandas as pd
import sqlite3

class DataManager:
    def addRecord(self, record) -> None:
        pass
    def close(self) -> None:
        pass

class CSVDataManager(DataManager):
    def __init__(self, output_filename, global_props = {}):
        self.records = []
        self.global_props = global_props
        self.filename = output_filename

    def addRecord(self, record):
        self.records.append(**self.global_props, **record)

    def close(self):
        df = pd.DataFrame.from_records(self.records)
        df.to_csv(self.filename, index_label="index", float_format="%.2f")

class SQLiteDataManager(DataManager):
    columns = [
        "filename",
        "datetime",
        "offset",
        "chunkLength",
        "classification",
        "nPeaks",
        "levelMax",
        "levelMin",
        "action",
        "filterJson",
        "statisticsJson",
        "wave"
    ]
    def __init__(self, filename, global_props={}):
        self.global_props = global_props
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS detections(
            id INTEGER PRIMARY KEY AUTOINCREMENT,      -- id univoco
            filename TEXT NOT NULL,                    -- il nome del file wav
            datetime REAL,                             -- data e ora della registrazione, convertito in float
            offset REAL,                               -- offset dell'evento estrapolato dall'inizio della registrazione
            chunkLength REAL,                          -- lunghezza del blocco salvato, in secondi
            classification TEXT,                       -- classificazione (click, pinger, scandaglio, altro)
            nPeaks INTEGER,                            -- numero di picchi contenuti nel blocco
            levelMax REAL,                             -- livello RMS del picco maggiore
            levelMin REAL,                             -- livello RMS del picco minore
            action TEXT,                               -- Azione intrapresa dall'algoritmo
            filterJson TEXT,                           -- Proprietà filtraggio applicato in JSON
            statisticsJson TEXT,                       -- Dati statistici sui picchi in formato JSON
            wave BLOB);                                -- il frammento in formato wave
            """)
        self.conn.commit()

    def addRecord(self, record):
        record.update(self.global_props)
        for c in self.columns:
            if c not in record.keys():
                record[c] = None
        
        self.cursor.execute("""
            INSERT INTO detections(filename, datetime, offset, chunkLength, classification, nPeaks, levelMax, levelMin, action, filterJson, statisticsJson, wave)
            VALUES(:filename, :datetime, :offset, :chunkLength, :classification, :nPeaks, :levelMax, :levelMin, :action, :filterJson, :statisticsJson, :wave)
            """, record)
        self.conn.commit()

    def close(self):
        self.conn.close()
