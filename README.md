# Kedro-Universal-Catalog


## What is Kedro-Universal-Catalog?


Kedro-Universal-Catalog is a serving platform to host and serve entries from a 
[Kedro Data Catalog](https://docs.kedro.org/en/stable/data/#) config. It does not load the data, but rather, it provides
the instructions on *how* to load the data. This ensures that all of your current security features are left in place
and unaffected.

## Why do I need this?


Kedro-Universal-Catalog lets you define in a single place the instructions for loading a particular piece of data, this
will ensure that all of your users are using the correct and latest definition. It will also let them easily re-use data
across projects.  Best of all, it still works with [Kedro-Viz](https://github.com/kedro-org/kedro-viz)


## Getting Started


### Installation from source

```
pip install git+https://github.com/bpmeek/kedro-universal-catalog@main
```

### Initialize a new server

```
kedro-catalog init
```

This will create a new server with the following folder structure.

```
<catalog_name>
├── README.md
├── requirements.txt
└── <python_package>
    ├── __init__.py
    ├── conf
    │   └── base
    │       ├── catalog.yml
    │       └── serving.yml
    ├── main.py
    └── settings.py
```

### Update Data Catalog

Edit the file `<catalog_name>/<python_package>/conf/base/catalog.yml` to have it contain the datasets you wish to serve.
Make sure to add any dependencies for the dataset to `requirements.txt`

### Start the server

From the root directory of your catalog 

```
python <python_package>/main.py
```


### Add catalog entry to Project's catalog.yml

Example entry:
```yaml
cars:
  type: universal_catalog.UniversalCatalogDataset
  source_name: cars
  url: http://localhost:5000/
```

## Advanced usage

### Replace entire catalog

If you have a lot of datasets and don't want to define each one in your Kedro Project's catalog you can 
use `RemoteCatalog` instead.

In your Kedro project's `settings.py` add:

```python
from universal_catalog import RemoteCatalog
DATA_CATALOG_CLASS = RemoteCatalog
```

Then update `local/credentials.yml` to tell `RemoteCatalog` where to get your catalog from. Be sure to name the 
entry `remote_catalog` and have the key `url`.

```yaml
remote_catalog:
  url: http://127.0.0.1:8000/
```

When the `RemoteCatalog` is fetched it is merged with your project's `catalog.yml` with the project's catalog taking overwriting duplicate datasets.


## What if I don't use Kedro?

[Why you should](https://docs.kedro.org/en/stable/introduction/index.html). 

Kedro-Universal-Catalog can be used without 
using the Kedro framework by utilizing the code api, see the example below.

```python
from universal_catalog import UniversalCatalogDataset


dataset = UniversalCatalogDataset(
    source_name="cars",
    url="http://localhost:5000/",
)
data = dataset.load()
```
