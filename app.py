import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from models import setup_db, Movie, db_drop_and_create_all
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    """ uncomment at the first time running the app """
    db_drop_and_create_all()
    @app.route('/', methods=['GET'])
    def home():
        return jsonify({'message': 'Hello,hello, World!'})
    @app.route("/movies")
    def get_movies():
        try:
            movies = Movie.query.order_by(Movie.release_date).all()
            movie=[]
            movie=[mov.release_date for mov in movies]
            return jsonify(
                {
                    "success": True,
                    "movie name": movie
                }
            ), 200
        except:
            abort(500)
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "server error"
        }), 500
    return app
app = create_app()
if __name__ == '__main__':
    port = int(os.environ.get("PORT",5000))
    app.run(host='127.0.0.1',port=port,debug=True)