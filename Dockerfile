FROM python:3.9.5-slim-buster

# install sudo 
RUN apt-get clean \
 && apt-get update -qq \
 && apt-get -qq -y full-upgrade \
 && apt-get install -y --no-install-recommends \
    sudo \
    coreutils \
    wget

# install chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb
RUN apt-get -y install ./google-chrome-stable_current_amd64.deb

# create user
RUN groupadd --gid 1000 user && \
    useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash user

# configure home directory
RUN mkdir /home/user/app
COPY app /home/user/app
ENV APP_HOME=/home/user/app

# install python app
RUN cd /home/user/app && \
    pip install --no-cache-dir .

# chown all the files to the app user
RUN chown -R "1000:1000" /home/user

# switch to user and start container
USER user
EXPOSE 8095
WORKDIR /home/user/app

# export env variables from .env-file
#SHELL ["/bin/bash", "-c"] 
#RUN source /home/user/app/.env && \
#    export EMAIL_FOR_QMIDPASS PASSWORD_FOR_QMIDPASS API_KEY_FOR_2CAPTCHA SENDER_EMAIL SENDER_PASSWORD REVEIVERS_EMAILS

CMD tail -f /dev/null

