# ==============================
FROM helsinkitest/python:3.9-slim AS appbase
# ==============================

ENV PYTHONUNBUFFERED 1

WORKDIR /app
RUN mkdir /entrypoint

RUN apt-install.sh \
    build-essential \
    libpq-dev \
    gdal-bin \
    netcat-traditional \
    pkg-config \
    python3-gdal \
    gcc \
    libc-dev \
    libsqlite3-mod-spatialite \
    && apt-cleanup.sh \
    build-essential \
    pkg-config

COPY --chown=appuser:appuser requirements.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

# install extra certificates
# rename certificates to *.crt because update-ca-certificates requires it
COPY --chown=appuser:appuser ./extra_certificates/entrust_l1k.cer /usr/local/share/ca-certificates/entrust_l1k.crt
RUN update-ca-certificates

COPY --chown=appuser:appuser docker-entrypoint.sh /entrypoint/docker-entrypoint.sh
ENTRYPOINT ["/entrypoint/docker-entrypoint.sh"]

# ==============================
FROM appbase AS staticbuilder
# ==============================

ENV VAR_ROOT /app
COPY --chown=appuser:appuser . /app
RUN SECRET_KEY="only-used-for-collectstatic" python manage.py collectstatic --noinput

# ==============================
FROM appbase AS development
# ==============================

COPY --chown=appuser:appuser requirements-dev.txt /app/requirements-dev.txt
RUN pip install --no-cache-dir -r /app/requirements-dev.txt \
    && pip install --no-cache-dir pip-tools

ENV DEV_SERVER=1

COPY --chown=appuser:appuser . /app/

USER appuser

EXPOSE 5000/tcp

# ==============================
FROM appbase AS production
# ==============================

COPY --from=staticbuilder --chown=appuser:appuser /app/static /app/static

COPY --chown=appuser:appuser requirements-prod.txt /app/requirements-prod.txt
RUN pip install --no-cache-dir -r /app/requirements-prod.txt

COPY --chown=appuser:appuser . /app/

# OpenShift write accesses issue
# db.sqlite3 is written to /app -directory
USER root
RUN chgrp 0 /app && chmod g+w /app

USER appuser

EXPOSE 5000/tcp
