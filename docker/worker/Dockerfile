ARG GIT_BRANCH=master
ARG TAG=latest
FROM registry.gitlab.com/dokos/dokidocker/dokos-worker:${TAG}

ARG GIT_BRANCH
RUN install_app erpnext https://gitlab.com/dokos/tierslieux ${GIT_BRANCH}

RUN chown -R dodock:dodock /home/dodock/dodock-bench /home/dodock/backups