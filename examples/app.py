from chalice import Chalice
from mongoengine import connect

from .chalicelib.resources import app as resources

DATABASE_URI = 'mongomock://localhost:27017/db'

app = Chalice(app_name='test_app')
app.register_blueprint(resources)

connect(host=DATABASE_URI)


@app.route('/')
def health_check():
    return dict(greeting="I'm testing app!!!")
