FROM ghcr.io/astral-sh/uv:debian

WORKDIR /app

# Tsinghua mirror (China) – remove if you don’t need it
RUN mkdir -p /etc/uv
RUN touch /etc/uv/uv.toml
RUN printf '%s\n' \
    '[[index]]' \
    'url = "https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple"' \
    'default = true' \
    '' > /etc/uv/uv.toml

COPY pyproject.toml uv.lock .python-version .env ./
COPY soup/ ./soup/
COPY main.py ./

# Install exact dependencies (very fast because of layer caching)
RUN uv sync --frozen --no-cache

EXPOSE 42345
ENTRYPOINT ["uv", "run", "python", "main.py"]