import os

try:
    import pandas as pd

    PANDAS = True
except ImportError:
    PANDAS = False

from ..base import Pipeline

class Tabular(Pipeline):
    def __init__(self, idcolumn=None, textcolumns=None, content=False):
        
        if not PANDAS:
            raise ImportError('Tabular pipeline is not available - install "pipeline" extra to enable')
        
        self.idcolumn = idcolumn
        self.textcolumns = textcolumns
        self.content = content

    def __call__(self, data):
        items = [data] if not isinstance(data, list) else data

        results = []
        dicts = []

        for item in items:
            if isinstance(item, str):
                _, extension = os.path.splitext(item)
                extension = extension.replace(".", "").lower()

                if extension == "csv":
                    df = pd.read_csv(item)

                results.append(self.process(df))

            if isinstance(item, dict):
                dicts.append(item)

            elif isinstance(item, list):
                df = pd.DataFrame(item)
                results.append(self.processd(df))
        
        if dicts:
            df = pd.DataFrame(dicts)
            results.extend(self.process(df))

        return results[0] if not isinstance(data, list) else results
    
    def process(self, df):
        rows = []

        columns = self.textcolumns
        if not columns:
            columns = list(df.columns)
            if self.idcolumn:
                columns.remove(self.idcolumn)

        for index, row in df.iterrows():
            uid = row[self.idcolumn] if self.idcolumn else index
            uid = uid if uid is not None else index
            text = self.concat(row, columns)

            rows.append((uid, text, None))

            if isinstance(self.content, list):
                row = {column: self.column(value) for column, value in row.to_dict().items() if column in self.content}
                rows.append((uid, row, None))
            elif self.content:
                row = {column: self.column(value) for column, value in row.to_dict().items()}
                rows.append(uid, row, None)
        return rows
    
    def concat(self, row, columns):
        parts = []
        for column in columns:
            column = self.column(row[column])
            if column:
                parts.append(str(column))

        return ". ".join(parts) if parts else None

    def column(self, value):
        return None if not isinstance(value, list) and pd.isnull(value) else value