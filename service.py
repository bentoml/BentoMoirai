import typing as t
import numpy as np
import pandas as pd
from pathlib import Path

import bentoml
from bentoml.validators import DataframeSchema


MODEL_SIZE = "large"  # {"small", "base", "large"}
MODEL_ID = f"Salesforce/moirai-1.0-R-{MODEL_SIZE}"

PRED_LEN = 20  # prediction length
CTX_LEN = 200  # context length
PATCH_SIZE = "auto"
BATCH_SIZE = 128


@bentoml.service(
    name="bentomoirai",
    traffic={
        "timeout": 300,
        "concurrency": 32,
    },
    resources={
        "gpu": 1,
        "gpu_type": "nvidia-tesla-t4",
    },
)
class Moirai:
    
    def __init__(self) -> None:
        import torch
        from uni2ts.model.moirai import MoiraiForecast, MoiraiModule
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = MoiraiForecast(
            module=MoiraiModule.from_pretrained(MODEL_ID),
            prediction_length=PRED_LEN,
            context_length=CTX_LEN,
            patch_size=PATCH_SIZE,
            num_samples=100,
            target_dim=1,
            feat_dynamic_real_dim=0,
            past_feat_dynamic_real_dim=0,
        ).to(self.device)
        self.predictor = self.model.create_predictor(batch_size=BATCH_SIZE)
        print("Model moirai loaded", "device:", self.device)


    @bentoml.api
    def forecast(self, df: t.Annotated[pd.DataFrame, DataframeSchema(orient="records")]) -> np.ndarray:
        from gluonts.dataset.pandas import PandasDataset
        from gluonts.dataset.split import split

        # the first column of DataFrame should be datetime
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.set_index("datetime")
        data_size = df.shape[0]
        ds = PandasDataset(dict(df))

        # use the entire dataset as test data
        train, test_template = split(
            ds, offset=-data_size
        )

        test_data = test_template.generate_instances(
            prediction_length=PRED_LEN,
            windows=data_size // PRED_LEN,
            distance=PRED_LEN,
        )

        predictor = self.model.create_predictor(batch_size=BATCH_SIZE)
        forecasts = predictor.predict(test_data.input)
        forecast = next(iter(forecasts))
        return forecast.samples


    @bentoml.api
    def forecast_csv(self, csv: Path) -> np.ndarray:
        df = pd.read_csv(csv)
        return self.forecast(df)
