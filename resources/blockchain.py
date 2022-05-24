from array import array
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from flask import Flask, jsonify, make_response, request
from itsdangerous import json
from models.blockchain import blockChain
from uuid import uuid4

blockchain = blockChain()

nodeAddress = str(uuid4()).replace('-', '')


class mineBlock(Resource):

    # @jwt_required()
    def get(self):

        previousBlock = blockchain.getPreviousBlock()

        previousProof = previousBlock['proof']

        proof = blockchain.proofOfWork(previousProof)

        previousHash = blockchain.hash(previousBlock)

        blockchain.addTransaction(
            sender=nodeAddress, receiver='Akarsh', amount=1)

        newBlock = blockchain.createBlock(proof, previousHash)

        response = {'message': "Congratulation You MINED your block",
                    'index': newBlock['index'],
                    'timestamp': newBlock['timestamp'],
                    'transactions': newBlock['transactions'],
                    'proof': newBlock['proof'],
                    'previousHash': newBlock['previousHash']}

        return make_response(jsonify(response), 200)


class getChain(Resource):

    def get(self):
        response = {'chain': blockchain.chain,
                    'length': len(blockchain.chain)}

        return make_response(jsonify(response), 200)


class checkValidity(Resource):
    def get(self):
        isvalid = blockchain.isChainValid(blockchain.chain)

        if isvalid:
            return make_response(jsonify({'message': 'The chain is valid'}), 200)
        else:
            return make_response(jsonify({'message': 'The chain is invalid'}), 200)


class addTransactions(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('sender',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )
    parser.add_argument('receiver',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )
    parser.add_argument('amount',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )

    def post(self):
        json = addTransactions.parser.parse_args()

        transactionKeys = ['sender', 'receiver', 'amount']

        if not all(key in json for key in transactionKeys):
            return 'Some elements of the transactions are missing', 400

        index = blockchain.addTransaction(
            json['sender'], json['receiver'], json['amount'])

        response = {
            'message': f'The transaction will be added to the block {index}!'}

        return make_response(jsonify(response), 201)


class changeNodesInNetwork(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('nodes',
                        action='append',
                        required=True,
                        help="This field cannot be left blank!"
                        )

    def post(self):
        json = changeNodesInNetwork.parser.parse_args()

        print(json)

        nodes = json.get('nodes')
        print(nodes)

        if nodes is None:
            return 'No node', 400

        for node in nodes:
            blockchain.addNode(node)

        response = {'message': 'Nodes are added, Akoin blockchain now contains the nodes',
                    'totalNodes': list(blockchain.nodes)}

        return make_response(jsonify(response), 201)


class UpdateChain(Resource):
    def get(self):
        isChainReplaced = blockchain.replaceChain()

        if isChainReplaced:
            response = {'message': 'the node had different chains hence Chain is replaced by the longest',
                        'newChain': blockchain.chain}
        else:
            response = {'message': 'The chain is longest.',
                        'actualChain': blockchain.chain}
        return make_response(jsonify(response), 200)
