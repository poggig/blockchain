# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 18:42:40 2021

@author: Gabri



Blockchain 101      following this tutorial https://www.koolstories.com/blog/build-your-first-blockchain-program
"""

#### modules necessary

# Proof of Work
import hashlib
import json

# Time stamp
from time import time

#API
from flask import Flask, jsonify, request
from textwrap import dedent
from uuid import uuid4


# define a Blockchain class
class Blockchain():
    
    def __init__(self): #with a constructor that sets a empty chain and a empty list of transactions
        
        self.chain = [] #empty chain
        
        self.current_transactions = [] # #empty transactions
        
        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)
        
    def new_block(self, proof, previous_hash = None): #creates a new block and adds to the existing chain
        """Create a new Block in the Blockchain
        proof: the proof given by the Proof of Work algorithm
        previous_hash (Optional) Hash of previous Block
        return: New Block"""
        
        
        block={ #a block is a dict which contains information
            'index': len(self.chain)+1, # the lenght of the chain is the lenght of the chain +1 bc we are adding 1
            'timestamp': time(), # the current time
            'proof':proof,
            previous_hash: previous_hash or self.hash(self.chain[-1]) # this I have to understand
            }
        self.current_transactions=[] #Reseet the current list of transactions

        self.chain.append(block) # append block to the chain

        return block
   
    def new_transaction(self, sender, recipient, amount): # new transaction and adds to the list of transactions
    
        """ Creates a new transaction to go into the next mined Block
                : sender" Address of the sender
                recipient: Address of the recipient
                amount: Amount
                
              returns: the index of the block that will hold this transaction
                                                              """
        self.current_transactions.append(
            
            {'sender':sender,
             'recipient':recipient,
             'amount':amount} #appends a dictionary with sender, recipient, amount
            )
    
        return self.last_block['index']+1 #why returns last block?
    @staticmethod
    
    def hash(block): # hash the block
           """The follow code will create a SHA-256 block hash and also ensure that the dictionary is ordered"""
           bloc_string = json.dumps(block, sort_keys=True).encode() #return equivalent json str of dictionary
           
           return hashlib.sha256(bloc_string).hexdigest() #???
       
    @property
    
    def last_block(self): # calls and returns the last block of the chain
    
        return self.chain[-1]
    
    
    ######################### Basic Proof of Work implementation

    def proof_of_work(self, last_proof):
        """ 
        Simple Proof of Work Algorithm:
            
            - Find a numper p such that hash (pp') contains leading 4 zeroes, where p is the previous p'
            - p is the previous proof, and p' is the new proof
            
            :param last_proof:
            : return: 
                                              
        
        
        """
        
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof +=1
        return proof
    
    @staticmethod
    
    def valid_proof(last_proof, proof):

        """Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof:  Previous Proof
        :param proof:  Current Proof
        :return:  True if correct, False if not."""

        guess = f'{last_proof}{proof}'.encode()
    
        guess_hash = hashlib.sha256(guess).hexdigest()
    
        return guess_hash[:4] == "0000"
    
    # End of the Blockchain class object
    
    
######################## API implementation 

# Instantiate our Node
    
app = Flask(__name__)
    
#Generate a globally unique address for this node
    
node_identifier = str(uuid4()).replace('-', '')
    
#Instatiate Blockchain

blockchain = Blockchain()

@app.route('/mine/new', methods=['GET'])
def mine():
    '''We will mine a new Block'''
    # run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof=  last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    
    # we reward ourselves for finding the proof.
    # Sender is '0' to mean, that this node has mined a new coin.
    blockchain.new_transaction(sender='0', recipient=node_identifier, amount=1)
    
    #Forge the new block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    response ={
        'message':'New Block Forged',
        'index': block['index'],
        'transactions':block['transactions'],
        'proof':block['proof'],
        'previous_hash':block['previous_hash']
        
        }
    return jsonify(response), 200



@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    '''We will add a new transaction'''
    values = request.get_json()
    
    #check that required fields are in the POST'ed data
    required =['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing Values', 400
    
    #Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    
    return jsonify(response), 201 

@app.route('/chain', methods=['GET'])
def full_chain():
    response={
        'chain':blockchain.chain,
        'lenght': len(blockchain.chain)
        }
    return jsonify(response), 200

    
if __name__ =='__main':
    app.run(host='0.0.0.0', port=5000)
            




