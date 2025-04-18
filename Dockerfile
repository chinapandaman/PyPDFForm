FROM python:3.11-slim

WORKDIR /pypdfform

EXPOSE 8000

RUN apt-get update && \
    apt-get install -y make dos2unix bash-completion git

COPY . /pypdfform

RUN pip install -r requirements.txt

RUN echo "source /etc/profile" >> /root/.bashrc && \
    echo "[ -f /usr/share/bash-completion/bash_completion ] && . /usr/share/bash-completion/bash_completion" >> /root/.bashrc

RUN chmod +x entrypoint.sh && \
    dos2unix entrypoint.sh

ENTRYPOINT ["sh", "entrypoint.sh"]

CMD ["bash"]
