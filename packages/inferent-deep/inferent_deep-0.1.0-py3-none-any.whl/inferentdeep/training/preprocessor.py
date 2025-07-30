import logging
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
import pandas as pd

class Preprocessor:
    """Class responsible for preprocessing data"""

    logger = logging.getLogger("Preprocessor")
    categorical_map = {}
    input_features = None
    processed_featurelist = None
    xencoder = None
    xscaler = None
    yscaler = None
    clip_dict = None

    def __init__(self, clip_dict=None):
        self.clip_dict = clip_dict

    def register_categorical(self, data, cols, one_hot=True):
        """adds categorical cols `cols` to a separate datastore

        Will replace cols with their one hot encoded values
        """
        # TODO: embeddings
        for col in cols:
            # Get categorical column
            cat = data[[col]]  # [[ ]] to return df not series
            if one_hot:
                self.xencoder = OneHotEncoder()
                self.xencoder.fit(cat)
                codes = self.xencoder.transform(cat).toarray()
                feature_names = self.xencoder.get_feature_names_out(
                    cat.columns
                )
                # `cat` is now the encoded categorical column
                cat = pd.DataFrame(
                    codes, columns=feature_names, index=cat.index
                ).astype(int)
                data = pd.concat(
                    [
                        data.drop(columns=[col]),
                        pd.DataFrame(
                            codes, columns=feature_names, index=cat.index
                        ).astype(int),
                    ],
                    axis=1,
                )
                self.categorical_map[col] = feature_names
            else:
                self.categorical_map[col] = col
        self.processed_featurelist = list(data.columns)
        return data

    def register_xscaler(self, xdata, scaler="minmax"):
        """normalizes data"""
        if scaler == "minmax":
            self.xscaler = MinMaxScaler()
            self.yscaler = MinMaxScaler()
        else:
            raise ValueError("Improper input for `scaler`.")

        self.xscaler.fit(xdata)

    def register_yscaler(self, ydata, scaler="minmax"):
        """normalizes data"""
        if scaler == "minmax":
            self.yscaler = MinMaxScaler()
        else:
            raise ValueError("Improper input for `scaler`.")

        self.yscaler.fit(ydata)

    def clip(self, xdata):
        for to_find, clip in self.clip_dict.items():
            cols = [col for col in xdata.columns if to_find in col]
            xdata[cols] = xdata[cols].clip(upper=clip)

        return xdata

    def preprocess_x(self, xdata, clip=True, encode=True, scale=True):
        if clip:
            xdata = self.clip(xdata)

        # Encoding
        if encode and len(self.categorical_map) > 0:
            cat = xdata[self.categorical_map.keys()]
            codes = self.xencoder.transform(cat).toarray()
            feature_names = self.xencoder.get_feature_names_out(cat.columns)
            cat = pd.DataFrame(
                codes, columns=feature_names, index=cat.index
            ).astype(int)
            xdata = pd.concat(
                [
                    xdata.drop(columns=[self.categorical_map.keys()]),
                    pd.DataFrame(
                        codes, columns=feature_names, index=cat.index
                    ).astype(int),
                ],
                axis=1,
            )

        # Scaling
        if scale:
            xdata = self.xscaler.transform(xdata)

        return xdata
