# Project Name: ir-example

## Original structure of the project

```bash
.
├── core
│   ├── core.py
│   ├── __init__.py
│   └── __pycache__
├── data
│   ├── database.py
│   ├── __init__.py
│   └── __pycache__
├── dataset
│   ├── podcastreviews.zip
│   ├── raw_data
│   │   ├── categories.json
│   │   ├── database.db
│   │   ├── podcasts.json
│   │   └── reviews.json
│   └── vectors
│       └── GoogleNews-vectors-negative300.bin.gz
├── dist
│   ├── example_ir-1.0.0-py3-none-any.whl
│   └── example_ir-1.0.0.tar.gz
├── Dockerfile
├── LICENSE
├── local.py
├── main.py
├── Makefile
├── model
│   ├── __init__.py
│   ├── model.py
│   └── __pycache__
├── pyproject.toml
├── README.md
├── requirements.txt
├── setup.py
├── tests
│   ├── __pycache__
│   ├── test_api_entities.py
│   ├── test_api.py
│   ├── test_coreapp.py
│   ├── test_database.py
│   ├── test.db
│   ├── test_end2end.py
│   └── test_model.py
└── utils
    ├── common.py
    ├── __init__.py
    └── __pycache__
```

## Prerequisites to run the project

- Have Python installed on the system.
- Have python-venv installed on the system.
- Use an OS that supports the make command (optional, but recommended to run it automatically).
- Work with the dataset as it is downloaded from Kaggle: [podcastreviews.zip](https://www.kaggle.com/datasets/thoughtvector/podcastreviews) saved in a dataset/ folder by default (this path can be provided as an input argument or env variable.
- Download the version of the vectors: [GoogleNews-vectors-negative300.bin.gz](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit?usp=sharing). Originally, the vectors are downloaded to directory /dataset/vectors/. Again, this path can be provided as an input argument or env variable.

## General considerations about the project

- The dataset is explored directly with DuckDB because: it is small <10 GB and we are assuming a large single-core machine, no parallel processing or batch processing.
- We are using a persistent connection to the file that contains the database. This is because we can use DuckDB's function that allows larger-than-memory workloads to be supported by spilling to disk to a tmp file.
- We discard results without average_rating or scraped_at timestamp.
- We are not performing any parsing or utility to consider the language of the database, we treat it like everything is in English.
- Be careful with RAM, here you need 2GB for GoogleNews and another 2GB to play with the dataset.
- Processing time is a major handicap, but there are 160,000 texts to convert to a vector_dict.
- Old database storage version, upgrade it is essential.
- The scraping took place on the days 2019-07-07, 2019-07-08, and 2019-07-09. It would be better to use review creation dates instead of these dates. We are aware of that, but this behaviour will be implemented in a future.
- Added unitary tests where integrations are mocked.
- Added end-to-end test where functionality, integration, and response are tested. Exact results cannot be checked because the nature of the Retrieval algorithm is not deterministic. If it is changed to be so, these responses could be tested.
- Async methods are implemented only for endpoint.
- Both the library and the API are bundled together. In a professional project, they would be separated, but here I wanted to put everything in the same repository.

## How to run the project

### Do you want to run it locally?

If you want to try the it locally, the best option is to use the "make" command. Using it without arguments will show you all the possible commands that can be executed.
If you run it locally, the entrypoint will be the `local.py` file (only for developtment use). Here you can provide a list of arguments through the argparse module. The documentation is included in the script.
If you want to test the REST API use the `make start-server` command. Here is an example of `curl` command to test the endpoint:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/search/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "I want to listen to a podcast about entertainment industry, focusing on videogames", 
  "top_n": 5,
  "min_score": 3.0,
  "max_score": 5.0,
  "min_date": "2019-07-07", 
  "max_date": "2019-07-09",
  "boost_mode": true,
  "verbose": false
}'
```

### Do you have Docker installed?

Great, then you only need to execute `make build` and `make run` and the endpoint will be deployed.

Then, you only need to make a request through, for example, the same `curl` example as indicated in the section above.

### What do I need to ensure the project works like a charm?

Just run the tests: `make test`. This will trigger both unitary and integration (end2end) tests.

### Can I install it as a library?

Of course, a release is already distributed on the Releases URL of the repository. But, if you want to create your own distribution, you will only need to execute `make package`. This will generate the installable `.whl` file.

### What about the workflows?

- There are implemented a couple of workflows for CI/CD purposes using Github actions. On each push to the dev branch, a CI step is performed in which we perform lint operations and also the testing part. We check for everything to be ok. Also, on each push or PR to the main branch, not only the CI step is completed but also a CD process in which we package the module and distribute it as a realease.
- How does the workflow work? It requires a connection with Kaggle to automatically download the dataset and the vectors (because these are external files). To avoid sharing secrets, if you fork the repo, you would need to add the KAGGLE_USERNAME and KAGGLE_KEY variables as secrets in your forked repository for it to work. These are obtained by generating an API KEY on Kaggle. With that, all the CI process is executed automatically.

## TODOs for the future

- The processing logic is slow. The slowest part is reloading the files (this can be preloaded for inferences and improve response time). The same with the dictionaries generated for the model. In this basic example, I haven't addressed this optimization part.
- Add system performance metrics and logs. In the future, utilization and performance metrics of the endpoint need to be added.
- Have exception management system and map the service, repository exceptions in the controller to HTTP errors.
- Add a Prometheus + Grafana + OpenTelemetry to see metrics and logs.
- Authentication, user security on the endpoint.
- In the GitHub Actions workflows, it could be extended to also build the image and upload it to a private registry, from where to deploy the server.
- The logging system is basic, printing information to the stdout. All logging could be stored in a file or, better yet, in an external platform like Grafana.
- Addition of validation by typing.
