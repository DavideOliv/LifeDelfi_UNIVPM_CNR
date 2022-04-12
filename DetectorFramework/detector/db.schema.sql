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
