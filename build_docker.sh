#!/bin/bash
set -e

# Variables
PODMAN_REPO="wingardl/rl_exp"
DOCKERFILE="rl_exp.Dockerfile"
TAG="latest"

# Optional: Check if Podman is logged in (uncomment if needed)
# if ! podman login --get-login | grep -q "Username:"; then
#     echo "You must be logged in to Docker Hub. Run 'podman login docker.io' first."
#     exit 1
# fi

echo "Building image ${PODMAN_REPO}:${TAG} using ${DOCKERFILE}..."
podman build -f "${DOCKERFILE}" -t "${PODMAN_REPO}:${TAG}" .

echo "Pushing image ${PODMAN_REPO}:${TAG} to Docker Hub..."
podman push "${PODMAN_REPO}:${TAG}"

echo "Done!"