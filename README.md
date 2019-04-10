# Flask Demo

## Getting started

1. Install pipenv!
   `$ brew install pipenv`
2. Clone git repo
   `$ git clone https://github.com/andy-esch/flask-demo.git`
3. Change directory
   `$ cd flask-demo`
3. Setup python environment
   `$ pipenv --three`
4. Install packages
   `$ pipenv install --skip-lock`
5. Start up the virtual environment in a subshell
   `$ pipenv shell`
6. Run the app!
   `$ FLASK_APP=app.py FLASK_DEBUG=1 MPL_BACKEND='agg' flask run`

You'll see something like this in the terminal:
> * Serving Flask app "app.py"
> * Environment: production
>   WARNING: Do not use the development server in a production environment.
>   Use a production WSGI server instead.
> * Debug mode: off
> * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

Open up `http://127.0.0.1:5000/` in your browser.

Open up `http://127.0.0.1:5000/`

Once you're done:

1. Exit the virtual environment: `$ exit`
2. Delete the virtual environment: `$ pipenv --rm`
