FROM python:3.9-alpine3.13

# Make python directly print buffer
ENV PYTHONUNBUFFERED 1

# Don't write python bytecode
ENV PYTHONDONTWRITEBYTECODE 1

# Copy the pip requirements
COPY ./requirements.txt /tmp/requirements.txt

# Copy django site to app directory in container
COPY ./bitmind /app
WORKDIR /app

# Run a python virtual environment and upgrade pip
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    # Install postgresql
    apk add --update --no-cache postgresql-client && \
    # Install postgresql dependencies to temp dir
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev && \
    # Install pip requirements after dependencies
    /py/bin/pip install -r /tmp/requirements.txt && \
    # Remove build dependencies and temp files
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    # Create new non-root user
    adduser \
    --disabled-password \
    --no-create-home \
    django-user

# Set path variables
ENV PATH="/scripts:/py/bin:$PATH"

# Set default user
USER django-user