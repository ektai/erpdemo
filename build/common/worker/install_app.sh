#!/bin/bash

APP_NAME=${1}
APP_REPO=${2}
APP_BRANCH=${3}

cd /home/dodock/dodock-bench/

. env/bin/activate

cd ./apps

[ "${APP_BRANCH}" ] && BRANCH="-b ${APP_BRANCH}"

git clone --depth 1 -o upstream ${branch} ${APP_REPO} ${APP_NAME}
pip3 install --no-cache-dir -e /home/dodock/dodock-bench/apps/${APP_NAME}