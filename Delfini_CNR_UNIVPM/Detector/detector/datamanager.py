import pandas as pd

class DataManager:
    def __init__(self, filename):
        self.records = []
        self.filename = filename

    def addRecord(self, record):
        self.records.append(record)

    def export_csv(self):
        df = pd.DataFrame.from_records(self.records)
        df.to_csv(self.filename, index_label="index", float_format="%.2f")
