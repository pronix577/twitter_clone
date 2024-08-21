FROM python:3.7

#RUN apt-get update && apt-get upgrade

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY src/ /app/
COPY ./static /usr/share/nginx/html/static
#COPY ./static /static/
COPY nginx.conf /etc/nginx/nginx.conf
#COPY uwsgi.ini /etc/uwsgi/uwsgi.ini
#COPY supervisord.ini /etc/supervisor/conf.d/supervisord.ini
EXPOSE 8000

WORKDIR /app

#CMD ["python3", "controllers.py"]
CMD ["uvicorn", "app:application", "--host", "0.0.0.0"]
#CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.ini"]
