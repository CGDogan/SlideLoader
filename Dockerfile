FROM cgd30/openslide:newv6

WORKDIR /var/www
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ="America/New_York"

RUN apt-get update
RUN apt-get autoclean
RUn apt-get clean
RUN apt-get -q update --fix-missing
RUN apt-get -q install -y python3-pip vim

RUN apt-get -q install -y openssl libcurl4-openssl-dev libssl-dev

# Build libvips instead of installing libvips-dev from apt
RUN apt-get -q install -y libjpeg-turbo8-dev libexif-dev libgsf-1-dev libtiff-dev libfftw3-dev liblcms2-dev libpng-dev libmagickcore-dev libmagickwand-dev liborc-0.4-dev libopenjp2-7 libgirepository1.0-dev
WORKDIR /root/src
RUN git clone https://github.com/libvips/libvips.git --depth=1 --branch=8.14
RUN mkdir /root/src/libvips/build
WORKDIR /root/src/libvips
# Build without OpenSlide to open images with rather ImageMagick to handle
# images without pyramids
RUN meson setup -Dopenslide=disabled --buildtype release build
RUN meson compile -C build
RUN meson test -C build
RUN meson install -C build

# extracted from lines of "meson install" where .so.42 are installed. TODO: for amd64
ENV LD_LIBRARY_PATH="/usr/local/lib/aarch64-linux-gnu/:${LD_LIBRARY_PATH}"

RUN pip install pyvips --break-system-packages
RUN pip install flask --break-system-packages
RUN pip install gunicorn --break-system-packages
RUN pip install greenlet --break-system-packages
RUN pip install gunicorn[eventlet] --break-system-packages

run openssl version -a

# verify pyvips can call libvips
RUN python3 -c "import pyvips"

ENV FLASK_ENV development

RUN mkdir -p /images/uploading

COPY ./ ./

RUN cp test_imgs/* /images/

RUN pip3 install -r requirements.txt --break-system-packages


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
