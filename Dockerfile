FROM python:3.12-slim

RUN groupadd -g 1000 pypdfform-dev && \
    useradd -u 1000 -g pypdfform-dev -m pypdfform-dev

WORKDIR /pypdfform

EXPOSE 8000 8080

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY ./pyproject.toml /pypdfform/pyproject.toml

COPY ./entrypoint.sh /pypdfform/entrypoint.sh

RUN apt-get update && \
    apt-get install -y make dos2unix bash-completion git libatomic1 poppler-utils imagemagick sudo && \
    uv pip install -U -r pyproject.toml --extra dev --system && \
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
