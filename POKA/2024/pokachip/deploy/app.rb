require 'sinatra'
require 'idn'
require 'addressable/uri'
require 'securerandom'
require 'erb' 
require 'selenium-webdriver'  

set :bind, '0.0.0.0'

USERS = [
  { username: 'admin', domain: '포카칩.com', email: 'admin@포카칩.com', password: SecureRandom.hex(64) }
]

def normalize_domain(domain)
  unless domain.start_with?('http://', 'https://')
    domain = "http://#{domain}"
  end
  uri = Addressable::URI.parse(domain)
  uri.host || domain
end

def valid_domain?(domain)
  parsed_host = normalize_domain(domain).downcase
  !parsed_host.include?('포카칩.com')
end

def register_user(username, domain, password)
  email_domain = IDN::Idna.toUnicode(normalize_domain(domain))
  username = ERB::Util.html_escape(username)
  email_domain = ERB::Util.html_escape(email_domain)
  password = ERB::Util.html_escape(password)
  email = "#{username}@#{email_domain}"
  USERS << { username: username, domain: email_domain, email: email, password: password }
  email
end

def authenticate_user(email, password)
  USERS.find { |user| user[:email] == email && user[:password] == password }
end

def update_email(user, new_email)

  if new_email.chars.any? { |c| c.ord > 255 || '<>()'.include?(c) }
    return "Invalid characters in email."
  end

  new_email = IDN::Idna.toUnicode(new_email)
  new_email = new_email.chars.map { |c| (c.ord % 256).chr }.join
  user[:email] = new_email
  "Email updated successfully!"

end

def run_bot
  Thread.new do
    options = Selenium::WebDriver::Chrome::Options.new
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument('disable-gpu')
    options.add_argument('no-sandbox')
    options.add_argument('disable-dev-shm-usage')

    driver = Selenium::WebDriver.for(:chrome, options: options)
    driver.manage.timeouts.implicit_wait = 3
    driver.manage.timeouts.page_load = 10

    begin
      login_url = 'http://localhost:9292/login'
      driver.navigate.to(login_url)

      cookie = { name: 'flag', value: 'pokactf2024{**flag**}', domain: 'localhost', path: '/' }
      driver.manage.add_cookie(cookie)

      email_field = driver.find_element(name: 'email')
      password_field = driver.find_element(name: 'password')

      email_field.send_keys('admin@포카칩.com')
      password_field.send_keys(USERS.find { |user| user[:email] == 'admin@포카칩.com' }[:password])

      submit_button = driver.find_element(css: 'input[type="submit"]')
      submit_button.click

      sleep 2
      puts "Bot has been redirected to: #{driver.current_url}"

      sleep 2  
      current_url = driver.current_url
      puts "Final URL after redirects: #{current_url}"

    rescue => e
      puts e.message
    ensure
      driver.quit
    end
  end
end

get '/signup' do
  erb :signup
end

post '/signup' do
  username = params[:username]
  domain = params[:domain]
  password = params[:password]

  if valid_domain?(domain)
    email = register_user(username, domain, password)
    erb :success, locals: { email: email }
  else
    erb :signup, locals: { error: "The domain '#{normalize_domain(domain)}' is reserved or restricted." }
  end
end

get '/login' do
  erb :login
end

post '/login' do
  email = params[:email]
  password = params[:password]

  if user = authenticate_user(email, password)
    erb :user_list, locals: { user: user, users: USERS }
  else
    erb :login, locals: { error: "Invalid email or password." }
  end
end

post '/update_email' do
  current_user = authenticate_user(params[:email], params[:password])
  target_user = USERS.find { |u| u[:username] == params[:target_username] }

  if current_user && target_user && current_user[:email].end_with?('포카칩.com') && !target_user[:email].end_with?('포카칩.com')
    result = update_email(target_user, params[:new_email])
    run_bot if result == "Email updated successfully!"
    erb :user_list, locals: { user: current_user, users: USERS, message: result }
  else
    "Permission denied or invalid request."
  end
end

get '/' do
  erb :index
end

get '/user_list' do
  erb :user_list, locals: { users: USERS }
end
