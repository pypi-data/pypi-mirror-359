# Django SRAM

![Build status](https://gitlab.com/astron-sdc/django_sram/badges/main/pipeline.svg)
![Test coverage](https://gitlab.com/astron-sdc/django_sram/badges/main/coverage.svg)
<!-- ![Latest release](https://gitlab.com/astron-sdc/django_sram/badges/main/release.svg) -->

SURF Research Access Management integration for Django

## Installation
```
pip install django-sram
```

## Setup

One time template setup should include configuring the docker registry to regularly cleanup old images of
the CI/CD pipelines. And you can consider creating protected version tags for software releases:

1. [Cleanup Docker Registry Images](https://git.astron.nl/groups/templates/-/wikis/Cleanup-Docker-Registry-Images)
2. [Setup Protected Verson Tags](https://git.astron.nl/groups/templates/-/wikis/Setting-up-Protected-Version-Tags)

Once the cleanup policy for docker registry is setup you can uncomment the `docker push` comment in the `.gitlab-ci.yml`
file from the `docker_build` job. This will allow to download minimal docker images with your Python package installed.

## Usage
```python
from django_sram import cool_module

cool_module.greeter()   # prints "Hello World"
```

## Development

### Development environment

To setup and activte the develop environment run ```source ./setup.sh``` from within the source directory.

If PyCharm is used, this only needs to be done once.
Afterward the Python virtual env can be setup within PyCharm.

### Contributing
To contribute, please create a feature branch and a "Draft" merge request.
Upon completion, the merge request should be marked as ready and a reviewer
should be assigned.

Verify your changes locally and be sure to add tests. Verifying local
changes is done through `tox`.

```pip install tox```

With tox the same jobs as run on the CI/CD pipeline can be ran. These
include unit tests and linting.

```tox```

To automatically apply most suggested linting changes execute:

```tox -e format```

## License
This project is licensed under the Apache License Version 2.0
