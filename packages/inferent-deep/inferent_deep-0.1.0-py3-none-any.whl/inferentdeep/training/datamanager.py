import logging
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
from .preprocessor import Preprocessor

class DataManager:
    """Takes a pd.DataFrame as input and manages it for training.

    Performs preprocessing tasks.
    """

    logger = logging.getLogger("DataManager")
    raw_data = None
    data = None
    preprocessor = None
    Xdf_train = None
    Xdf_vld = None
    Xdf_test = None
    ydf_train = None
    ydf_vld = None
    ydf_test = None
    X_train = None
    X_vld = None
    X_test = None
    y_train = None
    y_vld = None
    y_test = None

    def __init__(self, raw_data, label_col, clip_dict=None, seed=None):
        self.raw_data = raw_data.copy()
        self.xdata = raw_data.drop(columns=[label_col])
        self.ydata = raw_data[[label_col]]  # [[ ]] to return df, not series
        self.preprocessor = Preprocessor(clip_dict)
        self.seed = seed
        self.label_col = label_col

    def drop_nans(self):
        """performs bifurcated self.raw_data.dropna() with some logging"""
        nan_cols = [
            col
            for col in self.raw_data.columns
            if self.raw_data[col].isna().sum() > 0
        ]
        nans = self.raw_data[self.raw_data[nan_cols].isna().any(axis=1)]
        self.logger.info(
            "%s rows of data with NaNs: %s \n %s", len(nans), nan_cols, nans
        )
        self.xdata = self.xdata.drop(nans.index)
        self.ydata = self.ydata.drop(nans.index)

    def split(
        self, vld_size=0.1, tst_size=0.1, vld_shuffle=True, tst_shuffle=False
    ):
        """Splits into train, test, and validation"""
        if tst_size > 0:
            Xdf_temp, self.Xdf_test, ydf_temp, self.ydf_test = (
                train_test_split(
                    self.xdata,
                    self.ydata,
                    test_size=tst_size,
                    random_state=self.seed,
                    shuffle=tst_shuffle,
                )
            )
        else:
            self.Xdf_test, self.ydf_test = pd.DataFrame(), pd.DataFrame()
            Xdf_temp, ydf_temp = self.xdata, self.ydata

        self.Xdf_train, self.Xdf_vld, self.ydf_train, self.ydf_vld = (
            train_test_split(
                Xdf_temp,
                ydf_temp,
                test_size=vld_size / (1.0 - tst_size),
                random_state=self.seed,
                shuffle=vld_shuffle,
            )
        )

    def clip(self):
        self.xdata = self.preprocessor.clip(self.xdata)

    def encode(self, cols):
        self.xdata = self.preprocessor.register_categorical(self.xdata, cols)

    def normalize(self, scaler="minmax"):
        self.preprocessor.register_xscaler(self.Xdf_train, scaler)
        self.preprocessor.register_yscaler(self.ydf_train, scaler)

        self.X_train = self.preprocessor.xscaler.transform(self.Xdf_train)
        self.X_vld = self.preprocessor.xscaler.transform(self.Xdf_vld)
        self.X_test = (
            self.preprocessor.xscaler.transform(self.Xdf_test)
            if not self.Xdf_test.empty
            else np.array([])
        )
        self.y_train = self.preprocessor.yscaler.transform(self.ydf_train)
        self.y_vld = self.preprocessor.yscaler.transform(self.ydf_vld)
        self.y_test = (
            self.preprocessor.yscaler.transform(self.ydf_test)
            if not self.ydf_test.empty
            else np.array([])
        )
