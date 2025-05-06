FROM ruby:3.0

RUN apt-get update && apt-get install -y libidn11-dev build-essential

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' > /etc/apt/sources.list.d/google-chrome.list

RUN apt-get update -y && apt-get install -y google-chrome-stable

RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+') && \
    wget https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/ && \
    rm -rf chromedriver-linux64.zip chromedriver-linux64

WORKDIR /app

COPY Gemfile Gemfile.lock ./

RUN bundle install

RUN gem install rackup

COPY . .

CMD ["rackup", "--host", "0.0.0.0"]
