# ==============================
FROM helsinki.azurecr.io/ubi9/python-39-gdal AS appbase
# ==============================

ENV PYTHONUNBUFFERED 1

WORKDIR /app
RUN mkdir /entrypoint

COPY --chown=root:root requirements.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY --chown=root:root docker-entrypoint.sh /entrypoint/docker-entrypoint.sh
ENTRYPOINT ["/entrypoint/docker-entrypoint.sh"]

# ==============================
FROM appbase AS staticbuilder
# ==============================

ENV STATIC_ROOT /app/static
COPY --chown=root:root . /app
RUN SECRET_KEY="only-used-for-collectstatic" python manage.py collectstatic --noinput

# ==============================
FROM appbase AS development
# ==============================

ENV DEV_SERVER=1

COPY --chown=root:root requirements-dev.txt /app/requirements-dev.txt
RUN pip install --no-cache-dir -r /app/requirements-dev.txt \
    && pip install --no-cache-dir pip-tools \
    && dnf clean all

COPY --chown=root:root . /app/

# Allow .pytest_cache writing so running pytest in container won't warn about cache writing failure:
RUN mkdir -p /app/.pytest_cache \
    && chown -R root:root /app/.pytest_cache \
    && chmod -R g+w /app/.pytest_cache

USER default

EXPOSE 5000/tcp

# ==============================
FROM appbase AS production
# ==============================

COPY --from=staticbuilder --chown=root:root /app/static /app/static

COPY --chown=root:root requirements-prod.txt /app/requirements-prod.txt

RUN pip install --no-cache-dir -r /app/requirements-prod.txt \
    && dnf clean all

COPY --chown=root:root . /app/

# OpenShift write accesses issue
# db.sqlite3 is written to /app -directory
USER root
RUN chgrp root /app && chmod g+w /app

USER default

EXPOSE 5000/tcp
