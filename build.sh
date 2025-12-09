docker build \
  --build-arg https_proxy=http://127.0.0.1:1081 \
  --build-arg http_proxy=http://127.0.0.1:1081 \
  --build-arg HTTPS_PROXY=http://127.0.0.1:1081 \
  --build-arg HTTP_PROXY=http://127.0.0.1:1081 \
  -t camesoup .