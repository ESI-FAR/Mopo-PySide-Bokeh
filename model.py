import pandas as pd

from PySide6.QtCore import QAbstractTableModel, Qt


class DF(QAbstractTableModel):
    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self.df = df

    def rowCount(self) -> int:
        return self.df.shape[0]

    def columnCount(self) -> int:
        return self.df.shape[1]

    def data(self, index, role) -> pd.DataFrame:
        return self.df

    @property
    def manufacturers(self):
        return sorted(self.df["manufacturer"].unique())

    @property
    def models(self):
        return sorted(self.df["model"].unique())

    @property
    def transmissions(self):
        return sorted(self.df["trans"].unique())

    @property
    def drives(self):
        return sorted(self.df["drv"].unique())

    @property
    def classes(self):
        return sorted(self.df["class"].unique())
