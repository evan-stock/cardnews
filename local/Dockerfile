# 맥에서 GitHub Actions와 똑같은 환경(우분투 24.04)으로 렌더하기 위한 상자.
# 폰트 경로(/usr/share/fonts/...)·ffmpeg·크로미움이 Actions와 같아서 코드 수정 없이 같은 결과가 나온다.
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive PIP_BREAK_SYSTEM_PACKAGES=1 PYTHONUNBUFFERED=1 TZ=Asia/Seoul
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends \
      python3 python3-pip python3-venv ffmpeg fonts-noto-cjk fonts-noto-cjk-extra fonts-noto-color-emoji \
      git curl ca-certificates unzip tzdata && rm -rf /var/lib/apt/lists/*
RUN ln -sf /usr/bin/python3 /usr/local/bin/python
COPY requirements.txt /tmp/requirements.txt
RUN pip install -q -r /tmp/requirements.txt edge-tts "yt-dlp[default,curl-cffi]" \
 && python -m playwright install --with-deps chromium && rm -rf /var/lib/apt/lists/*
WORKDIR /work
