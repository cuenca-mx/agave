from chalice import Chalice
from mongoengine import connect

from tests.chalicelib import app as bp

DATABASE_URI = 'mongomock://localhost:27017/db'

app = Chalice(app_name='test_app')
app.experimental_feature_flags.update(['BLUEPRINTS'])
app.register_blueprint(bp)

connect(host=DATABASE_URI)


@app.route('/')
def health_check():
    return dict(greeting="I'm testing app!!!")
