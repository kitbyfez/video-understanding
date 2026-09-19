#!/bin/bash
# Sync a built example into docs/ so GitHub Pages (/docs source) can serve it.
# Usage: publish_example.sh <example-dir-name>
set -e
rm -rf docs/example
mkdir -p docs/example
cp "$1/catalog.json" docs/example/
cp -r "$1/frames" docs/example/
echo "published $1 -> docs/example/"
