FROM python:3.8

RUN mkdir app/
WORKDIR /app/


# install dependencies

COPY /pyproject.toml /app/pyproject.toml

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install

COPY . .

