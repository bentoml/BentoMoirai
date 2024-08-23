<div align="center">
    <h1 align="center">Serving Moirai with BentoML</h1>
</div>

[Moirai](https://arxiv.org/abs/2402.02592), the Masked Encoder-based Universal Time Series Forecasting Transformer is a Large Time Series Model pre-trained on [LOTSA data](https://huggingface.co/datasets/Salesforce/lotsa_data). This is a BentoML example project, demonstrating how to build a forecasting inference API for time-series data using [Moirai-1.0-R-Large](https://huggingface.co/Salesforce/moirai-1.0-R-large).

See [here](https://github.com/bentoml/BentoML/tree/main/examples) for a full list of BentoML example projects.

## Install dependencies

```bash
git clone https://github.com/bentoml/BentoMoirai.git
cd BentoMoirai

# Recommend Python 3.11
pip install -r requirements.txt
```

## Run the BentoML Service

We have defined a BentoML Service in `service.py`. Run `bentoml serve` in your project directory to start the Service.

```bash
$ bentoml serve .

2024-01-08T09:07:28+0000 [INFO] [cli] Prometheus metrics for HTTP BentoServer from "service:Moirai" can be accessed at http://localhost:3000/metrics.
2024-01-08T09:07:28+0000 [INFO] [cli] Starting production HTTP BentoServer from "service:Moirai" listening on http://localhost:3000 (Press CTRL+C to quit)
Model Moirai loaded device: cuda
```

The Service is accessible at [http://localhost:3000](http://localhost:3000/). You can interact with it using the Swagger UI or in other different ways:

CURL

```bash
curl -s \
     -X POST \
     -F 'csv=@data.csv' \
     http://localhost:3000/forecast_csv
```

Python client

```python
import bentoml
import pandas as pd

df = pd.read("data.csv")

with bentoml.SyncHTTPClient("http://localhost:3000") as client:
    result = client.forecast(df=df)
```

## Deploy to BentoCloud

After the Service is ready, you can deploy the application to BentoCloud for better management and scalability. [Sign up](https://www.bentoml.com/) if you haven't got a BentoCloud account.

Make sure you have [logged in to BentoCloud](https://docs.bentoml.com/en/latest/bentocloud/how-tos/manage-access-token.html), then run the following command to deploy it.

```bash
bentoml deploy .
```

Once the application is up and running on BentoCloud, you can access it via the exposed URL.
