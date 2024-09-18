#!/bin/bash

# 获取当前的 Git 标签名称
TAG_NAME=$(git describe --tags --abbrev=0)

# 如果需要，可以处理标签名称，例如替换无效字符
TAG_NAME=${TAG_NAME//\//-}

# 使用 Git 标签名称作为 Docker 镜像的标签
IMAGE_TAG="github_sentinel:${TAG_NAME}"

# 构建 Docker 镜像
docker build -t $IMAGE_TAG .

# 输出构建结果
echo "Docker 镜像已构建并打上标签: $IMAGE_TAG"