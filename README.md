# Fettler

[![image](https://img.shields.io/pypi/v/fettler.svg?style=flat)](https://pypi.python.org/pypi/fettler)
[![image](https://img.shields.io/github/license/long2ice/fettler)](https://github.com/long2ice/fettler)
[![pypi](https://github.com/long2ice/fettler/actions/workflows/pypi.yml/badge.svg)](https://github.com/long2ice/fettler/actions/workflows/pypi.yml)
[![ci](https://github.com/long2ice/fettler/actions/workflows/ci.yml/badge.svg)](https://github.com/long2ice/fettler/actions/workflows/ci.yml)

## Introduction

`Fettler` is a service that help you refresh redis cache automatically. By listening on MySQL binlog, you can refresh
redis cache in a timely manner and devoid of sensation or consciousness.

![architecture](./images/architecture.png)

## Install

Just install from pypi:

```shell
> pip install fettler
```

## Usage

### Config file

The example can be found in [config.yml](./config.yml).

### Run services

First you should run the services, which include `producer`, `consumer`.

#### Use `docker-compose`(recommended)

```shell
docker-compose up -d --build
```

Then the services is running.

#### Run manual

##### Run producer

The producer listens on MySQL binlog and send data changes to redis message queue.

```shell
> fettler produce

2021-03-17 23:10:23.228 | INFO     | fettler.producer:run:36 - Start producer success, listening on binlog from schemas ['test']....
```

##### Run consumer

The consumer consume message queue and delete invalid caches by data changes from binlog and refresh policy registered.

```shell
> fettler consume

2021-03-17 23:10:36.953 | INFO     | fettler.consumer:run:21 - Start consumer success, waiting for data changes and delete invalid caches...
```

##### Run both producer and consumer in one command

If you only need one consumer, you can just run the producer and consumer in one command.

```shell
> fettler start

2021-03-17 23:10:05.226 | INFO     | fettler.consumer:run:21 - Start consumer success, waiting for data changes and delete invalid caches...
2021-03-17 23:10:05.230 | INFO     | fettler.producer:run:36 - Start producer success, listening on binlog from schemas ['test']....
```

## Register cache refresh policy

See [examples](./examples) to see how to add cache refresh policy in you application.

## License

This project is licensed under the [Apache-2.0](./LICENSE) License.
