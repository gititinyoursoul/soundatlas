#!/usr/bin/env sh
set -eu

git config --global --replace-all safe.directory /workspace
git config --global credential.useHttpPath true
git config --global core.autocrlf true
git config --global core.filemode false
