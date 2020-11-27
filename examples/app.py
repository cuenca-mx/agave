from chalice import Chalice
from mongoengine import connect

from .chalicelib.resources import app as resources
from .chalicelib.resources import app_v2

DATABASE_URI = 'mongomock://localhost:27017/db'

app = Chalice(app_name='test_app')
app.register_blueprint(resources)
app.register_blueprint(app_v2)

connect(host=DATABASE_URI)


@app.route('/')
def health_check():
    return dict(greeting="I'm testing app!!!")
