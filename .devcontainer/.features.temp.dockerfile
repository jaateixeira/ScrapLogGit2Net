FROM jb-devcontainer-scraploggit2net_claude_code_restricted:latest
COPY --from=jb-devcontainer-features-6c5d33c14e7a02bad4eb64c6f35f3c8c /tmp/jb-devcontainer-features /tmp/jb-devcontainer-features/
ENV PATH="/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ENV LANG="C.UTF-8"
ENV GPG_KEY="7169605F62C751356D054A26A821E680E5FA6305"
ENV PYTHON_VERSION="3.12.16"
ENV PYTHON_SHA256="b5796915dc45ff745cfb4e990a7e7c93d6f546328a102ce31448d69ebc37575c"
ENV PYTHONUNBUFFERED="1"
ENV PYTHONDONTWRITEBYTECODE="1"
ENV DEBIAN_FRONTEND="noninteractive"
ENV CLAUDE_CONFIG_DIR="/home/developer/.claude"
ENV DEVCONTAINER="true"
ENV _CONTAINER_USER="developer"
ENV _CONTAINER_USER_HOME="/home/developer"
ENV _REMOTE_USER="developer"
ENV _REMOTE_USER_HOME="/home/developer"

USER root
RUN chmod -R 0755 /tmp/jb-devcontainer-features/ghcr.io-anthropics-devcontainer-features-claude-code-1.0 \
&& cd /tmp/jb-devcontainer-features/ghcr.io-anthropics-devcontainer-features-claude-code-1.0 \
&& chmod +x ./devcontainer-feature-setup.sh \
&& ./devcontainer-feature-setup.sh