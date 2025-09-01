# Data collector (a.k.a. `sources` app)

Python Django application for fetching data from multiple sources
and storing it to Elasticsearch.

**Table of Contents**
<!-- DON'T EDIT THE TOC SECTION, INSTEAD RE-RUN md-toc TO UPDATE IT -->
<!--TOC-->

- [Requirements](#requirements)
- [Running](#running)
  - [With Docker & Docker compose](#with-docker--docker-compose)
  - [Without Docker](#without-docker)
- [Environments](#environments)
- [Data importers](#data-importers)
- [Keeping Python requirements up to date](#keeping-python-requirements-up-to-date)
- [Code linting & formatting](#code-linting--formatting)
- [Pre-commit hooks](#pre-commit-hooks)

<!--TOC-->

## Requirements

Requirements defined & provided by [Dockerfile](./Dockerfile):
- Python 3.12
- [GDAL](https://gdal.org/)

## Running

### With Docker & Docker compose

Because Docker compose handles more than just this app,
its use is described in the [repository root README](../README.md).

### Without Docker

Running this application without Docker is unsupported, but if you want to do it anyway
(with e.g. [uv](https://github.com/astral-sh/uv) to set up a virtual environment),
you can try to see what packages are required on top of the RedHat UBI 9 base image by
inspecting the layer history of the used Docker image, and looking for `dnf`, `yum` or `install`:
```bash
docker pull helsinki.azurecr.io/ubi9/python-312-gdal
docker history --no-trunc helsinki.azurecr.io/ubi9/python-312-gdal | grep -iE 'dnf|yum|install'
```
Good luck!

## Environments

Where is the Data Collector running?

Based on info from [kuva-unified-search](https://dev.azure.com/City-of-Helsinki/kuva-unified-search) Azure DevOps project:

- Review per PR (e.g. PR #321): https://kuva-unified-search-sources-pr321.api.dev.hel.ninja/
- Development: https://kuva-unified-search-sources.api.dev.hel.ninja/
- Testing: https://kuva-unified-search-sources.api.test.hel.ninja/
- Staging: https://kuva-unified-search-sources.api.stage.hel.ninja/
- Production: https://kuva-unified-search-sources.api.hel.ninja/

## Data importers

Data collector uses multiple different data importers to fetch data.

The data importers are documented in [Data Importers README](./ingest/README.md).

## Keeping Python requirements up to date

If you're using Docker, spin up the container using `docker compose up`
and go into it with `docker exec -it unified-search-sources-1 bash` first.

1. Install `pip-tools` to get `pip-compile` command:

   - `pip install pip-tools`

2. Add new packages to `requirements*.in` where wanted

3. Update `requirements*.txt` files:

   - `pip-compile requirements.in`
   - `pip-compile requirements-dev.in`
   - `pip-compile requirements-prod.in`

4. If you want to update dependencies to their newest versions, run:

   - `pip-compile --upgrade requirements.in`
   - `pip-compile --upgrade requirements-dev.in`
   - `pip-compile --upgrade requirements-prod.in`

5. To install Python requirements run:

   - `pip install -r requirements.txt`
   - `pip install -r requirements-dev.txt`
   - `pip install -r requirements-prod.txt`
   - Or if you're using Docker and the previous commands fail:
     - Spin down the container with `docker compose down`
     - Rebuild the container with `docker compose up --build` to take the package changes into account

## Code linting & formatting

This project uses [ruff](https://github.com/astral-sh/ruff) for Python code linting and formatting.
Ruff is configured through [pyproject.toml](./pyproject.toml).

Basic `ruff` commands:
 - Check linting & formatting:
   - `ruff check` (check linting)
   - `ruff format --check` (check formatting)
 - Fix linting & formatting:
   - `ruff check --fix` (fix linting, i.e. what `flake8` and `isort` did before)
   - `ruff format` (fix formatting, i.e. what `black` did before)

## Pre-commit hooks

Because [pre-commit](https://pre-commit.com/) does not support monorepos, it must be configured at repository root.

For this reason, see [repository root README.md](../README.md#pre-commit-hooks) for how to set up pre-commit hooks.
