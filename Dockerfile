FROM cgd30/openslide:newv2
#extra
RUN apt-get -q install -y wget
RUN wget https://medistim.com/wp-content/uploads/2016/07/ttfm.dcm


RUN apt-get update
RUN apt-get -q install -y python3-pip vim

RUN pip3 install openslide-python
RUN python3 -c "o={id:'1'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is None:\n\tres='old openslide'\nelse:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"

RUN python3 -c "o={id:'2'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is not None:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"
#end extra

WORKDIR /var/www
RUN wget https://medistim.com/wp-content/uploads/2016/07/ttfm.dcm

RUN python3 -c "o={id:'2.1'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is None:\n\tres='old openslide'\nelse:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"


RUN python3 -c "o={id:'2.2'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is not None:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ="America/New_York"

RUN apt-get update
RUN python3 -c "o={id:'2.51'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is None:\n\tres='old openslide'\nelse:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"


RUN python3 -c "o={id:'2.52'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is not None:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"
RUN pip3 install openslide-python
RUN python3 -c "o={id:'2.6'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is None:\n\tres='old openslide'\nelse:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"


RUN python3 -c "o={id:'2.7'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is not None:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"
RUN apt-get -q update --fix-missing
RUN pip3 install openslide-python
RUN python3 -c "o={id:'2.8'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is None:\n\tres='old openslide'\nelse:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"


RUN python3 -c "o={id:'2.9'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is not None:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"
RUN apt-get -q install -y python3-pip vim

RUN pip3 install openslide-python
RUN python3 -c "o={id:'2.5'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is None:\n\tres='old openslide'\nelse:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"


RUN python3 -c "o={id:'3'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is not None:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"


RUN apt-get -q install -y openssl libcurl4-openssl-dev libssl-dev

RUN python3 -c "o={id:'3.05'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is None:\n\tres='old openslide'\nelse:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"


RUN python3 -c "o={id:'3.06'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is not None:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"

RUN apt-get -q install -y libvips

RUN python3 -c "o={id:'3.07'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is None:\n\tres='old openslide'\nelse:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"


RUN python3 -c "o={id:'3.08'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is not None:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"
RUN apt-get -q install -y libvips-dev


RUN python3 -c "o={id:'3.1'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is None:\n\tres='old openslide'\nelse:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"


RUN python3 -c "o={id:'3.2'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is not None:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"

RUN pip install pyvips
RUN pip install flask
RUN pip install gunicorn
RUN pip install greenlet
RUN pip install gunicorn[eventlet]

RUN python3 -c "o={id:'3.3'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is None:\n\tres='old openslide'\nelse:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"


RUN python3 -c "o={id:'3.4'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is not None:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"

run openssl version -a

ENV FLASK_ENV development

RUN mkdir -p /images/uploading


RUN python3 -c "o={id:'3.5'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is None:\n\tres='old openslide'\nelse:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"


RUN python3 -c "o={id:'3.6'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is not None:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"

COPY ./ ./


RUN python3 -c "o={id:'3.7'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is None:\n\tres='old openslide'\nelse:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"


RUN python3 -c "o={id:'3.8'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is not None:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"

RUN cp test_imgs/* /images/
RUN python3 -c "o={id:'3.83'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is None:\n\tres='old openslide'\nelse:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"


RUN python3 -c "o={id:'3.85'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is not None:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"

RUN pip3 install -r requirements.txt



RUN python3 -c "o={id:'3.995'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is None:\n\tres='old openslide'\nelse:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"


RUN python3 -c "o={id:'4'};exec(\"import openslide;\nif openslide.OpenSlide.detect_format('ttfm.dcm') is not None:\n\tres='new openslide'\n\",globals(),o);print(o['res'])"



EXPOSE 4000
EXPOSE 4001

#debug/dev only
ENV FLASK_APP SlideServer.py
CMD python3 -m flask run --host=0.0.0.0 --port=4000

# The Below BROKE the ability for users to upload images.
# # non-root user
# RUN chgrp -R 0 /var && \
#     chmod -R g+rwX /var && \
#     chgrp -R 0 /images/uploading && \
#     chmod -R g+rwX /images/uploading
#
# USER 1001

#prod only
#CMD gunicorn -w 4 -b 0.0.0.0:4000 SlideServer:app --timeout 400
