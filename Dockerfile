FROM python:3.11

WORKDIR /usr/src/app
SHELL ["/bin/bash", "-c"]
RUN chmod 777 /usr/src/app

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata

RUN apt-get -y update
RUN apt-get install -y python3 python3-pip software-properties-common mediainfo wget \
    git mkvtoolnix pv jq libmagic-dev unzip aria2 ffmpeg cmake

RUN git clone https://github.com/axiomatic-systems/Bento4.git
WORKDIR /usr/src/app/Bento4/cmakebuild

RUN apt install -y libprotobuf-dev protobuf-compiler

RUN cmake -DCMAKE_BUILD_TYPE=Release ..
RUN make
RUN make install

COPY requirements.txt .
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade Pillow
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
CMD ["bash", "start.sh"]
