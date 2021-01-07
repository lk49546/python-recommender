from flask import Flask, request, jsonify
import recommender2
import settings
import threading
app = Flask(__name__)


@app.route('/api/users/<id>/recommendations')
def get_recommendations(id):
    qty = request.args.get('qty', default=10, type=int)
    recommender2.get_recommendations(id, qty)
    resp = jsonify(success=True)
    return resp


def do_init():
    settings.init()
    
@app.route('/api/init')
def init():
    threading.Thread(target=do_init).start()
    resp = jsonify(success=True)
    return resp

if __name__ == '__main__':
    settings.init()
    app.run()