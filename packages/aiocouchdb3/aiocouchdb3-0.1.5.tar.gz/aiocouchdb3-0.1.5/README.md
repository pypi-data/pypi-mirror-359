# Async I/O for CouchDB built on [aiohttp](https://docs.aiohttp.org/en/stable/)

This project is based on the (seemingly) unmaintained
[aiocoucdb](https://github.com/aio-libs/aiocouchdb) but is **not** a drop-in
replacement for that project.

## Example

Using `aiocouchdb3` is pretty easy.

```python
import aiocouchdb3 as couchdb

user_jwt = get_user_jwt()
async with couchdb.connect() as client:
    async with client.with_token(user_jwt) as session:
        for db in await session.all_dbs:
            print(await db.info)
```

## Features

- Allows authentication for both username/password and JWT

## Contribute

Thanks for considering adding your skills to improve this library.
Please review the [Contributor Covenant Code of Conduct](./COC.md).
You must comply with it to contribute to `aiocouchdb3`.

### Set up your local development environment

Check [`.python-version`](./.python-version) for the minimum version
of Python supported by `aiocouchdb3`. Install that and use it to create a
Poetry environment.

Install dependencies with

```sh 
poetry install --all-extras
```

You must provide both mocked and integration tests when contributing. Get 
a CouchDB v3 instance up and running. (If you use Docker, see the following
section about using Docker to run a properly configured CouchDB v3 instance.)

### Running tests 

There are two kinds of tests in the project found the `./tests` directory.

* `./tests/mocked` contain proper unit tests isolated from the execution 
  environment.
* `./tests/integration` contain integration tests that rely on a running
  instance of CouchDB. To run these copy `./test.env` to `./.test.env`
  and provide values for the two empty keys in it (and modify the other
  two if you want to).

  ```env 
  # Copy this file to .test.env and provide values for your
  # instance of CouchDB
  COUCHDB_USER =
  COUCHDB_PASSWORD =
  COUCHDB_DB_BASE_URL = http://locahost:5984
  COUCHDB_JWT_SECRET = devsecret
  ```

  There's a Docker compose file in [`tests`](./tests/docker-compose.yaml)
  available for you to use if you want to use that.

  ```sh 
  docker compose --env-file .test.env -f tests/docker-compose/docker-compose.yaml up
  ```

  Run the tests with

  ```sh 
  poetry run pytest
  ```

  If you want to run the tests while you're developing

  ```sh 
  poetry run ptw .
  ```
