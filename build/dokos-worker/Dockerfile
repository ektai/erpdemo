ARG GIT_BRANCH=develop
ARG DOCKER_REGISTRY_PREFIX=dokidocker
ARG TAG=latest
FROM registry.gitlab.com/dokos/${DOCKER_REGISTRY_PREFIX}/dodock-worker:${TAG}

ARG GIT_BRANCH
RUN install_app erpnext https://gitlab.com/dokos/dokos ${GIT_BRANCH}

RUN chown -R dodock:dodock /home/dodock/dodock-bench /home/dodock/backups
