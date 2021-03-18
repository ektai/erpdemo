FROM node:buster-slim

# Add dodock user
RUN useradd -ms /bin/bash dodock

# Create bench directories and set ownership
RUN mkdir -p /home/dodock/dodock-bench/sites /home/dodock/dodock-bench/apps/frappe \
    && chown -R dodock:dodock /home/dodock

# Download socketio and purge curl package
COPY build/dodock-socketio/package.json /home/dodock/dodock-bench/apps/frappe
ARG GIT_BRANCH=develop
RUN apt-get update && apt-get install -y curl \
    && cd /home/dodock/dodock-bench/apps/frappe \
    && curl "https://gitlab.com/dokos/dodock/-/raw/$GIT_BRANCH/socketio.js" \
        --output /home/dodock/dodock-bench/apps/frappe/socketio.js \
    && curl "https://gitlab.com/dokos/dodock/-/raw/$GIT_BRANCH/node_utils.js" \
        --output /home/dodock/dodock-bench/apps/frappe/node_utils.js \
    && apt-get purge -y curl && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN cd /home/dodock/dodock-bench/apps/frappe \
    && npm install --only=production \
    && node --version \
    && npm --version

# Setup docker-entrypoint
COPY build/dodock-socketio/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN ln -s /usr/local/bin/docker-entrypoint.sh / # backwards compat

WORKDIR /home/dodock/dodock-bench/sites

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["start"]
