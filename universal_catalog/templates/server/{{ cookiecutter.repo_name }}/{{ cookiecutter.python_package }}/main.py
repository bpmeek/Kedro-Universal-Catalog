from fastapi import FastAPI, Response

import uvicorn

from universal_catalog.core import (
    UniversalCatalog,
    load_catalog,
    Datasets,
    load_server_settings,
)

from settings import CONFIG_LOCATION

app = FastAPI()


CATALOG: UniversalCatalog = load_catalog(CONFIG_LOCATION)


@app.get("/")
async def root():
    catalog_yml = CATALOG.config_string()
    return Response(content=catalog_yml)


@app.post("/dataset/")
async def get_record(dataset_name: Datasets):
    dataset = CATALOG.get_entry(dataset_name.name)
    return dataset


@app.post("/catalog/")
async def get_catalog():
    catalog = CATALOG.get_catalog()
    return catalog


if __name__ == "__main__":
    load_catalog(CONFIG_LOCATION)
    server_settings = load_server_settings(CONFIG_LOCATION)
    uvicorn.run(app, **server_settings)
