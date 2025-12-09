FROM alpine:latest
RUN apk add --no-cache wget

# Set working directory
WORKDIR /app

# Install uv (the fast Python package installer)
RUN wget -qO- https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY pyproject.toml uv.lock ./
COPY soup/ ./soup/
COPY .env ./

EXPOSE 42345

CMD ["uv", "run", "python", "-m", "soup.web.app"]
