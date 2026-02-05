import urllib.request, urllib.error
urls = ['http://127.0.0.1:5000/','http://127.0.0.1:5000/register','http://127.0.0.1:5000/login','http://127.0.0.1:5000/notes','http://127.0.0.1:5000/booking','http://127.0.0.1:5000/rsvp']
for u in urls:
    try:
        with urllib.request.urlopen(u, timeout=5) as r:
            body = r.read(800).decode('utf-8', errors='replace')
            print(f"URL: {u} -> {r.status}\n{body.splitlines()[:12]}\n---\n")
    except urllib.error.HTTPError as e:
        print(f"URL: {u} -> HTTP {e.code}\n{e.reason}\n---\n")
    except Exception as ex:
        print(f"URL: {u} -> ERROR: {ex}\n---\n")
