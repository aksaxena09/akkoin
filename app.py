from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt import JWT

# when we import a file in python it runs the file.
from security import authenticate, identity
from resources.user import userRegister
from resources.blockchain import *
from db import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
# every change istracked which is turne off
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Akarsh'
api = Api(app)
db.init_app(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWT(app, authenticate, identity)  # /auth new endpoint

api.add_resource(mineBlock, '/mineBlock')
api.add_resource(checkValidity, '/checkValidity')
api.add_resource(getChain, '/getchain')
api.add_resource(userRegister, '/register')
api.add_resource(addTransactions, '/addTransactions')
api.add_resource(changeNodesInNetwork, '/addNewNode')
api.add_resource(UpdateChain, '/replaceChain')

# because if we import app file anywhere it will not get run.
if __name__ == '__main__':

    # debug opens html page during errors to show good error message and reruns app after saved changes
    app.run(port=5000, debug=True)
