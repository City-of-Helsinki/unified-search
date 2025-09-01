# ===============================================
FROM registry.access.redhat.com/ubi10/nodejs-22 AS appbase
# ===============================================
# install yarn
USER root
RUN curl --silent --location https://dl.yarnpkg.com/rpm/yarn.repo | tee /etc/yum.repos.d/yarn.repo
RUN yum -y install yarn

WORKDIR /app

# Set HOME to a writable dir to overcome "Error: EACCES: permission denied, open /opt/app-root/src/.config/yarn"
ENV HOME=/app

# set our node environment, either development or production
# defaults to production, compose overrides this to development on build and run
ARG NODE_ENV=production
ENV NODE_ENV $NODE_ENV

# Yarn
ENV YARN_VERSION 1.22.22
RUN yarn policies set-version ${YARN_VERSION}

# Copy package.json and package-lock.json/yarn.lock files
COPY --chown=root:root package*.json *yarn* ./

COPY --chown=root:root docker-entrypoint.sh /entrypoint/docker-entrypoint.sh
ENTRYPOINT ["/entrypoint/docker-entrypoint.sh"]

# =============================
FROM appbase AS development_base
# =============================

# Set node environment to development to install all dependencies
ENV NODE_ENV=development
RUN yarn && yarn cache clean --force

# Enable hot reload by default by polling for file changes.
#
# NOTE: Can be disabled by setting CHOKIDAR_USEPOLLING=false in file `.env`
#       if hot reload works on your system without polling to save CPU time.
ARG CHOKIDAR_USEPOLLING=true
ENV CHOKIDAR_USEPOLLING=${CHOKIDAR_USEPOLLING}

COPY --chown=root:root . .

# =============================
FROM development_base AS development
# =============================

ARG DEBUG
ENV DEBUG $DEBUG

# Bake package.json start command into the image
USER default
CMD ["yarn", "start"]

# =============================
FROM development_base AS builder
# =============================

RUN yarn build

# =============================
FROM appbase AS production
# =============================

# Copy the built source files to this image
COPY --from=builder --chown=root:root /app/dist /app/dist

# Set node environment to production to install only main dependencies
ENV NODE_ENV=production
RUN yarn && yarn cache clean --force

EXPOSE 4000/tcp

# Bake package.json serve command into the image
USER default
CMD ["yarn", "serve"]
