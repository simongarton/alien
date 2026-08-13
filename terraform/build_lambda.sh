#!/usr/bin/env bash
# Assembles the Lambda deployment package into .build/lambda:
# Pillow is compiled inside the official AWS SAM build image so the
# binary wheel matches the Lambda runtime, not the host machine, then
# the handler and the src/ modules it depends on are copied in alongside it.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$SCRIPT_DIR/.build/lambda"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

docker run --rm \
  --platform linux/amd64 \
  -v "$PROJECT_ROOT/lambda:/var/task/lambda_src:ro" \
  -v "$BUILD_DIR:/var/task/build" \
  public.ecr.aws/sam/build-python3.13 \
  /bin/sh -c "pip install --no-cache-dir -r /var/task/lambda_src/requirements.txt -t /var/task/build"

cp "$PROJECT_ROOT/lambda/handler.py" "$BUILD_DIR/"
cp "$PROJECT_ROOT/src/alien_generator.py" "$BUILD_DIR/"
cp "$PROJECT_ROOT/src/image_painter.py" "$BUILD_DIR/"
cp "$PROJECT_ROOT/src/alien_json_to_text.py" "$BUILD_DIR/"
