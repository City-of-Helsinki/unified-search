# ==============================
# FIXME(US-204): Use build-278157 (2025-11-10) as build-279912 (2025-11-17) fails
#                See https://helsinkisolutionoffice.atlassian.net/browse/US-204
FROM helsinki.azurecr.io/ubi9/python-312-gdal AS appbase
# ==============================

ENV PYTHONUNBUFFERED 1

WORKDIR /app
RUN mkdir /entrypoint

COPY --chown=root:root --chmod=755 requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

# chmod=755 = rwxr-xr-x i.e. owner can read, write and execute, group and others can read and execute.
#
# Related to SonarCloud security hotspot docker:S6470 i.e.
# "Recursively copying context directories is security-sensitive" i.e.
# https://rules.sonarsource.com/docker/RSPEC-6470/
# see .dockerignore for info on what is not copied here:
COPY --chown=root:root --chmod=755 . /app/

# Make sure db.sqlite3 under /app/db_data is writable by the application.
# Needed by e.g. `python manage.py ingest_data administrative_division`.
RUN mkdir -p /app/db_data \
    && chown -R default:root /app/db_data \
    && chmod -R g+w /app/db_data

# Make sure files under /app/data/ are writable by the application.
# Needed by e.g. `python manage.py ingest_data administrative_division`.
RUN mkdir -p /app/data \
    && chown -R default:root /app/data \
    && chmod -R g+w /app/data

COPY --chown=root:root --chmod=755 docker-entrypoint.sh /entrypoint/docker-entrypoint.sh
ENTRYPOINT ["/entrypoint/docker-entrypoint.sh"]

# ==============================
FROM appbase AS staticbuilder
# ==============================

ENV STATIC_ROOT /app/static
RUN SECRET_KEY="only-used-for-collectstatic" python manage.py collectstatic --noinput

# ==============================
FROM appbase AS development
# ==============================

ENV DEV_SERVER=1

COPY --chown=root:root --chmod=755 requirements-dev.txt /app/requirements-dev.txt
RUN pip install --no-cache-dir -r /app/requirements-dev.txt \
    && pip install --no-cache-dir pip-tools \
    && dnf clean all

# Allow .pytest_cache writing so running pytest in container won't warn about cache writing failure:
RUN mkdir -p /app/.pytest_cache \
    && chown -R default:root /app/.pytest_cache \
    && chmod -R g+w /app/.pytest_cache

USER default

EXPOSE 5001/tcp

# ==============================
FROM appbase AS production
# ==============================

COPY --from=staticbuilder --chown=root:root --chmod=755 /app/static /app/static

COPY --chown=root:root --chmod=755 requirements-prod.txt /app/requirements-prod.txt

RUN pip install --no-cache-dir -r /app/requirements-prod.txt \
    && dnf clean all

USER default

EXPOSE 5001/tcp
