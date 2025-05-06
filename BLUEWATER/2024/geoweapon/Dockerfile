FROM docker.osgeo.org/geoserver:2.26.x

ADD ./flag.txt /flag.txt
RUN GEOSERVER_ADMIN_USER=admin GEOSERVER_ADMIN_PASSWORD=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 50; echo) /opt/update_credentials.sh
ENTRYPOINT ["bash", "-c","/opt/startup.sh"]
