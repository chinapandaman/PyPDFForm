FROM python:3.12-slim

WORKDIR /pypdfform

EXPOSE 8000 8080

RUN apt-get update && \
    apt-get install -y make dos2unix bash-completion git libatomic1 poppler-utils imagemagick

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . /pypdfform

RUN uv pip install -U -r pyproject.toml --extra dev --system

RUN echo "source /etc/profile" >> /root/.bashrc && \
    echo "[ -f /usr/share/bash-completion/bash_completion ] && . /usr/share/bash-completion/bash_completion" >> /root/.bashrc

RUN chmod +x entrypoint.sh && \
    dos2unix entrypoint.sh

ENTRYPOINT ["sh", "entrypoint.sh"]

CMD ["bash"]
