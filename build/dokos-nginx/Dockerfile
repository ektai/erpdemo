ARG NODE_IMAGE_TAG=12-buster-slim
ARG GIT_BRANCH=develop
ARG TAG=latest
ARG DOCKER_REGISTRY_PREFIX=dokidocker
FROM node:${NODE_IMAGE_TAG}

ARG GIT_BRANCH
COPY build/dokos-nginx/install_app.sh /install_app
RUN chmod +x /install_app && \
  apt-get update -y && \
  apt-get install build-essential git python2 -y && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

RUN /install_app erpnext https://gitlab.com/dokos/dokos ${GIT_BRANCH}

FROM registry.gitlab.com/dokos/${DOCKER_REGISTRY_PREFIX}/dodock-nginx:${TAG}

COPY --from=0 /home/dodock/dodock-bench/sites/ /var/www/html/
COPY --from=0 /rsync /rsync
RUN echo "erpnext" >> /var/www/html/apps.txt

VOLUME [ "/assets" ]

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
