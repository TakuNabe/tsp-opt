set -eux

PLATFORM=${1:-"dev_local_wsl2"}
TAG="tsp-opt"

BASEDIR=$(cd $(dirname $0); pwd)
cd $BASEDIR

MY_UID=$(id -u)
MY_GID=$(id -g)
MY_UNAME=$(id -un)
MY_GNAME="docker"

echo "Build image"
docker compose -p ${TAG}-${MY_UNAME} -f etc/docker/docker-compose_${PLATFORM}.yml build \
    --build-arg UID=$MY_UID \
    --build-arg GID=$MY_GID \
    --build-arg GROUPNAME=$MY_GNAME \

echo "Up container"
docker compose -p ${TAG}-${MY_UNAME} -f etc/docker/docker-compose_${PLATFORM}.yml up -d
