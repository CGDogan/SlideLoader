FROM cgd30/openslide:newv6

WORKDIR /var/www
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ="America/New_York"

RUN apt-get update
RUN apt-get -q update --fix-missing
RUN apt-get -q install -y python3-pip vim

RUN apt-get -q install -y openssl libcurl4-openssl-dev libssl-dev
RUN apt-get -q install -y libvips libvips-dev pipx

# https://stackoverflow.com/questions/75608323
RUN pipx install pyvips
RUN pipx install flask
RUN pipx install gunicorn
RUN pipx install greenlet
RUN pipx install gunicorn[eventlet]

run openssl version -a

ENV FLASK_ENV development

RUN mkdir -p /images/uploading

COPY ./ ./

RUN cp test_imgs/* /images/

RUN pip3 install -r requirements.txt


EXPOSE 4000
EXPOSE 4001

#debug/dev only
#ENV FLASK_APP SlideServer.py
#CMD python3 -m flask run --host=0.0.0.0 --port=4000

# The Below BROKE the ability for users to upload images.
# # non-root user
# RUN chgrp -R 0 /var && \
#     chmod -R g+rwX /var && \
#     chgrp -R 0 /images/uploading && \
#     chmod -R g+rwX /images/uploading
#
# USER 1001

#prod only
CMD gunicorn -w 4 -b 0.0.0.0:4000 SlideServer:app --timeout 400
