from chalice import Chalice

from tests.chalicelib import app as bp

app = Chalice(app_name='test_app')
app.experimental_feature_flags.update(['BLUEPRINTS'])
app.register_blueprint(bp)


@app.route('/')
def health_check():
    return dict(greeting="I'm testing app!!!")
