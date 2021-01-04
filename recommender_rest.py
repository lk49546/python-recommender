from flask import Flask, request, jsonify
import recommender2
import settings
app = Flask(__name__)


@app.route('/api/users/<id>/recommendations')
def get_recommendations(id):
    qty = int(request.args.get('qty'))
    recommender2.get_recommendations(id, qty)
    resp = jsonify(success=True)
    return resp


@app.route('/api/init')
def do_init():
    settings.init()
    resp = jsonify(success=True)
    return resp


if __name__ == '__main__':
    settings.init()
    app.run()