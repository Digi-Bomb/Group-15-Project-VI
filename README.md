# Group-15-Project-VI

## Running the app (development)

- The app runs on port `5000` by default.

- To run locally using the virtualenv Python interpreter (recommended for development):

```bash
python -m app.app
```

- This runs the Flask development server. For production use, run behind a WSGI server (gunicorn/uwsgi) and configure a proper rate-limiter storage backend.

## Running in Docker

- Build and run with Docker:

```bash
docker build -t <image_name> .
docker run -p 5000:5000 <image_name>
```

Then open http://127.0.0.1:5000/ in your browser.
