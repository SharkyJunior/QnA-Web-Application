def app(environ, start_response):
    data = b"""<!DOCTYPE html>
<html>
<head><title>Dynamic Test</title></head>
<body>
<h1>Dynamic Content</h1>
<p>This is dynamic content from WSGI application.</p>
</body>
</html>"""
    
    status = '200 OK'
    response_headers = [
        ('Content-type', 'text/html'),
        ('Content-Length', str(len(data)))
    ]
    start_response(status, response_headers)
    return [data]