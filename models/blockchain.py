import datetime
import hashlib  # accept only encoded string
import json
from db import db
from urllib.parse import urlparse
import requests


class blockChain():

    def __init__(self):
        self.chain = []
        # added before create block function since in create block function we are using the transaction list
        self.transactionList = []
        self.createBlock(proof=1, previousHash='0')
        self.nodes = set()

    def createBlock(self, proof, previousHash):
        block = {

            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previousHash': previousHash,
            'transactions': self.transactionList
        }
        self.transactionList = []  # empty list since block is created with all the transactions
        self.chain.append(block)
        return block

    def getPreviousBlock(self):
        return self.chain[-1]  # last index

    def proofOfWork(self, previousProof):

        newProof = 1
        checkProof = False

        while checkProof is False:

            hashOperation = hashlib.sha256(
                str(newProof**2 - previousProof**2).encode()).hexdigest()  # encode to

            if hashOperation[:4] == '0000':
                checkProof = True

            else:
                newProof = newProof+1

        return newProof

    def hash(self, block):  # return hash or the block

        encodedBlock = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(encodedBlock).hexdigest()

    def isChainValid(self, chain):

        previousBlock = chain[0]
        blockIndex = 1

        while blockIndex < len(chain):

            block = chain[blockIndex]

            if block['previousHash'] != self.hash(previousBlock):

                return False

            newProof = block['proof']
            previousProof = previousBlock['proof']
            hashOperation = hashlib.sha256(
                str(newProof**2 - previousProof**2).encode()).hexdigest()

            if hashOperation[:4] != '0000':
                return False

            previousBlock = block

            blockIndex += 1

        return True

    def addTransaction(self, sender, receiver, amount):
        self.transactionList.append({
            'receiver': receiver,
            'sender': sender,
            'amount': amount})

        previousBlock = self.getPreviousBlock()

        return previousBlock['index'] + 1

    def addNode(self, address):
        parsedURL = urlparse(address)

        self.nodes.add(parsedURL.netloc)  # unique identifier of nodes

    def replaceChain(self):  # consensus problem solved
        # called inside a specific node
        network = self.nodes
        longestChain = None
        maxLength = len(self.chain)

        for node in network:
            response = requests.get(f'http://{node}/getchain')

            if response.status_code == 200:
                lenOfTheChain = response.json()['length']

                chain = response.json()['chain']

                if lenOfTheChain > maxLength and self.isChainValid(chain):
                    maxLength = lenOfTheChain
                    longestChain = chain
        if longestChain:

            self.chain = longestChain

            return True
        return False
