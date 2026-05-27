from urllib.parse import parse_qs


def application(environ, start_response):
    method = environ.get('REQUEST_METHOD', 'GET')

    get_params = parse_qs(environ.get('QUERY_STRING', ''))

    post_params = {}
    if method == 'POST':
        try:
            length = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            length = 0
        if length:
            body = environ['wsgi.input'].read(length)
            post_params = parse_qs(body.decode('utf-8'))

    def fmt(params):
        if not params:
            return '<em>нет параметров</em>'
        rows = ''.join(
            f'<tr><td><b>{k}</b></td><td>{", ".join(v)}</td></tr>'
            for k, v in params.items()
        )
        return f'<table border="1" cellpadding="6">{rows}</table>'

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Simple WSGI</title>
  <style>
    body {{ font-family: Arial, sans-serif; padding: 2rem; background: #f4f7fc; }}
    .card {{ background: #fff; border-radius: 12px; padding: 2rem; max-width: 600px;
             margin: auto; box-shadow: 0 4px 12px rgba(0,0,0,.08); }}
    h1 {{ color: #2c3e66; }} h2 {{ color: #555; font-size: 1rem; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 1rem; }}
    td {{ padding: 6px 10px; }}
    input, button {{ padding: 6px 12px; margin: 4px; border-radius: 6px; border: 1px solid #ccc; }}
    button {{ background: #0d6efd; color: #fff; border: none; cursor: pointer; }}
  </style>
</head>
<body>
<div class="card">
  <h1>Simple WSGI App</h1>
  <h2>GET-параметры</h2>
  {fmt(get_params)}
  <h2>POST-параметры</h2>
  {fmt(post_params)}
  <hr>
  <h2>Тестовая форма (POST)</h2>
  <form method="POST">
    <input name="username" placeholder="username">
    <input name="email" placeholder="email">
    <button type="submit">Submit</button>
  </form>
</div>
</body>
</html>"""

    body = html.encode('utf-8')
    start_response('200 OK', [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(body))),
    ])
    return [body]
