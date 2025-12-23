HELLO_WORLD = b"Hello world!\n"

def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    method = environ['REQUEST_METHOD']
    print(f"method: {method}")
    if method == 'GET':
        print(environ['QUERY_STRING'])
    elif method == 'POST':
        print(environ['wsgi.input'].read().decode('utf-8'))
        
    start_response(status, response_headers)
    return [HELLO_WORLD]

application = simple_app