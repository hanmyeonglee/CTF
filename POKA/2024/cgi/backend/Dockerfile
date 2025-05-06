FROM httpd:2.4.46

RUN apt-get update

# cgi packages
RUN apt-get install -y wget make vim netcat curl
RUN apt-get install -y --fix-missing \
	libapache2-mod-perl2 \
	libfcgi-perl \
	libfcgi-bin \
	libcgi-pm-perl \
	libdbi-perl \
	libdbd-mysql-perl \
	cpanminus

# modsecurity packages
RUN apt-get install -y \
	build-essential \
	libcurl4-openssl-dev \
	libapache2-mod-php \
	libpcre3-dev \
	libxml2-dev \
	libssl-dev \
	libpcre3 \
	libxml2 \
	php \
	php-gd \
	php-mbstring \
	apache2-dev \
	apache2-bin && rm -rf /var/lib/apt/lists/*

# modsecurity install & setup
RUN wget https://github.com/SpiderLabs/ModSecurity/releases/download/v2.9.3/modsecurity-2.9.3.tar.gz && \
    tar -xzf modsecurity-2.9.3.tar.gz && \
    cd modsecurity-2.9.3 && \
    ./configure && \
    make && \
    make install && \
    cp modsecurity.conf-recommended /usr/local/apache2/conf/modsecurity.conf && \
    cd .. && rm -rf modsecurity-2.9.3 modsecurity-2.9.3.tar.gz

# httpd configure file copy
COPY ./httpd.conf /usr/local/apache2/conf/httpd.conf
RUN rm -rf /usr/local/apache2/cgi-bin/*

# cgi mode enable
RUN a2enmod cgi

# cgi script copy
COPY ./cgi-src/ /usr/local/apache2/cgi-bin
RUN chmod +x /usr/local/apache2/cgi-bin/*.cgi

COPY ./src/ /var/www/
RUN chmod -R 755 /var/www/

COPY ./flag.txt /flag.txt

EXPOSE 80

CMD ["httpd-foreground"]
