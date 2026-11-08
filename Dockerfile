# Images are pinned to digests and updated by Dependabot, which only reads
# FROM lines, so uv is a named stage rather than a COPY --from image.
FROM ghcr.io/astral-sh/uv:0.13.7@sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490 AS uv

FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90

WORKDIR /pypdfform

EXPOSE 8000 8080

COPY --from=uv /uv /uvx /bin/

COPY . /pypdfform

RUN apt-get update && \
    apt-get install -y \
    make \
    dos2unix \
    bash-completion \
    git \
    libatomic1 \
    poppler-utils \
    imagemagick \
    sudo && \
    uv pip install -U -r pyproject.toml --all-extras --system && \
    uv pip install -e . --system && \
    groupadd -g 1000 pypdfform-dev && \
    useradd -u 1000 -g pypdfform-dev -m pypdfform-dev && \
    echo "pypdfform-dev ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/pypdfform-dev && \
    chmod 0440 /etc/sudoers.d/pypdfform-dev && \
    echo "source /etc/profile" >> /home/pypdfform-dev/.bashrc && \
    echo "if [ -f /usr/share/bash-completion/bash_completion ]; then" >> /home/pypdfform-dev/.bashrc && \
    echo "    . /usr/share/bash-completion/bash_completion" >> /home/pypdfform-dev/.bashrc && \
    echo "fi" >> /home/pypdfform-dev/.bashrc && \
    echo "if [ -f /usr/share/bash-completion/completions/git ]; then" >> /home/pypdfform-dev/.bashrc && \
    echo "    . /usr/share/bash-completion/completions/git" >> /home/pypdfform-dev/.bashrc && \
    echo "fi" >> /home/pypdfform-dev/.bashrc && \
    chmod +x entrypoint.sh && \
    dos2unix entrypoint.sh && \
    chown -R pypdfform-dev:pypdfform-dev /home/pypdfform-dev /pypdfform

USER pypdfform-dev

ENTRYPOINT ["bash", "entrypoint.sh"]

CMD ["bash"]
