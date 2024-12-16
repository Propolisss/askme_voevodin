from urllib.parse import parse_qs


def simple_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    start_response(status, headers)

    query_string = environ.get('QUERY_STRING', '')
    get_parameters = parse_qs(query_string)
    print(f'get parameters: {get_parameters}')

    body = b""
    try:
        content_length = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError, TypeError):
        content_length = 0

    while content_length > 0:
        chunk = environ['wsgi.input'].read(min(1024, content_length))
        if not chunk:
            break
        body += chunk
        content_length -= len(chunk)
    post_params = parse_qs(body.decode('utf-8'))
    print(f'post parameters: {post_params}')

    response = ['GET parameters:\n']
    for key, value in get_parameters.items():
        response.append(f'{key}: {value}\n')

    response.append('\nPOST parameters:\n')
    for key, value in post_params.items():
        response.append(f'{key}: {value}\n')

    return [''.join(response).encode('utf-8')]


application = simple_app
