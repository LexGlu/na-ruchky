FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONUNBUFFERED=1

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Install gettext
RUN apt-get install -y gettext

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Set work directory
COPY . /code
WORKDIR /code

# Copy uv configuration files
COPY pyproject.toml uv.lock /code/

# Sync the project into a new environment, using the frozen lockfile without dev dependencies
RUN uv sync --no-dev --frozen

# Copy the rest of the application code
COPY . /code

# Copy entrypoint script into the image
COPY ./entrypoint.sh /code/entrypoint.sh

# Make it executable
RUN chmod +x /code/entrypoint.sh

# Run the entrypoint script
ENTRYPOINT ["/code/entrypoint.sh"]
