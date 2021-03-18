#!/bin/bash

APP_NAME=${1}
APP_REPO=${2}
APP_BRANCH=${3}

[ "${APP_BRANCH}" ] && BRANCH="-b ${APP_BRANCH}"

mkdir -p /home/dodock/dodock-bench/sites/assets
cd /home/dodock/dodock-bench
echo -e "frappe\n${APP_NAME}" > /home/dodock/dodock-bench/sites/apps.txt

mkdir -p apps
cd apps
git clone --depth 1 ${BRANCH} https://gitlab.com/dokos/dodock frappe
git clone --depth 1 ${BRANCH} ${APP_REPO} ${APP_NAME}

cd /home/dodock/dodock-bench/apps/erpnext
yarn
yarn production --app ${APP_NAME}
yarn install --production=true

mkdir -p /home/dodock/dodock-bench/sites/assets/${APP_NAME}
cp -R /home/dodock/dodock-bench/apps/${APP_NAME}/${APP_NAME}/public/* /home/dodock/dodock-bench/sites/assets/${APP_NAME}

# Add frappe and all the apps available under in dodock-bench here
echo "rsync -a --delete /var/www/html/assets/frappe /assets" > /rsync
echo "rsync -a --delete /var/www/html/assets/${APP_NAME} /assets" >> /rsync
chmod +x /rsync

rm /home/dodock/dodock-bench/sites/apps.txt
