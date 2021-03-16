FROM python:3
RUN mkdir -p /fettler
WORKDIR /fettler
COPY pyproject.toml poetry.lock /fettler/
RUN pip3 install poetry
ENV POETRY_VIRTUALENVS_CREATE false
RUN poetry install --no-root
COPY . /fettler
RUN poetry install
