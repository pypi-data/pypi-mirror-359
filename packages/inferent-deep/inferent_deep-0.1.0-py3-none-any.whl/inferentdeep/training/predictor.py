from dataclasses import dataclass
import logging
import numpy as np
import pandas as pd
import torch
from .preprocessor import Preprocessor
from .pytorch import evaluating

@dataclass
class ModelPackage:
    preprocessor: Preprocessor
    model: any
    metadata: dict

class Predictor:
    m = None

    def __init__(
        self, model_package: ModelPackage = None, model_path: str = None
    ):
        if model_package is not None:
            self.m = model_package
        elif model_path is not None:
            self.m = ModelPackage(None)

    def predict(
        self,
        xdata: pd.DataFrame,
        use_processed_featurelist=False,
        encode=True,
        scale=True,
    ):
        if not use_processed_featurelist:
            # reduce down to features in features list
            xdata = xdata[self.m.metadata["featurelist"]]
        else:
            xdata = xdata[self.m.preprocessor.processed_featurelist]

        # preprocess
        xdata = self.m.preprocessor.preprocess_x(
            xdata, encode=encode, scale=scale
        )

        # predict
        with evaluating(self.m.model), torch.no_grad():
            return self.m.model(torch.tensor(xdata, dtype=torch.float32))
