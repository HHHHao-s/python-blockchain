import hashlib
import json
import time
from flask import Flask, jsonify, request
from uuid import uuid4
import requests
from urllib.parse import urlparse

class Blockchain:
    def __init__(self):
        """
            初始化一个链，
            初始化当前交易信息，
            添加第一笔交易，
            创建创世区块
        """
        self.chain = []
        self.current_transaction = []
        self.nodes = set()# 使用set来保存，可以避免重复添加
        transaction = {
            'receiver' : hashlib.sha256('God'.encode()).hexdigest(),
            'send' : 0,
            'amount'    : 1
        }
        self.current_transaction.append(transaction)
        self.new_block(1, 100)
        

    def new_block(self, proof, pre_hash=None):    
        """
            创建一个新的区块，并将当前交易信息加入至此区块
            :parma:  <int> proof 当前区块的proof值
                    (Optional) <str> pre_hash 前一个区块的hash值
            :return: <dict> block
        """
        # 创建一个区块
        block={
            'index': len(self.chain),
            'timestamp': time.time(),
            'transactions': self.current_transaction,
            'proof': proof,
            'pre_hash' : pre_hash
        }
        self.current_transaction = []# 清空交易信息 
        self.chain.append(block)

        return block

    def new_transtion(self, sender, receiver, amount):
        """
            创建一个交易信息，并准备加入下一个待挖区块
            :parma: <str> sender
                    <str> receiver
                    <int> amount
            :return: <int> index
        """
        transaction = {
            'sender' : sender,
            'receiver' : receiver,
            'amount'    : amount
        }
        self.current_transaction.append(transaction)
        return self.last_block['index']

    @staticmethod
    def hash(block):
        # hash一个区块
        """
            :parma: <dict> block
            :return: <str> block的16进制hash值
        """
        blockstring = json.dumps(block ,sort_keys=True).encode()
        return hashlib.sha256(blockstring).hexdigest()


    @property
    def last_block(self):
        """
            :return: <dict> block 链中最后一个block
        """
        return self.chain[-1]

    @staticmethod
    def validProof(nonce, pre_proof):
        """
            验证当前的nonce和上一个区块的pre_proof相结合是否满足条件
            :parma: <int> nonce,pre_proof
            :return: <Bool>
        """
        cur = str(nonce) + str(pre_proof)
        digest = hashlib.sha256(cur.encode()).hexdigest()
        return digest[:4] == '0000'

    def PoW(self,pre_proof):
        """
            找到一个proof,
            使之上一个区块的pre_proof相结合满足条件,
            :parma: <int> pre_proof
            :return: <int> proof
        """
        nonce = 0
        while True:
            if self.validProof(nonce,pre_proof):
                break
            nonce = nonce+1
        return nonce
    
    def register_node(self, address):
        """
        添加一个新的地址到网路邻居
        :param address: <str>地址 Eg. 'http://192.168.0.5:5000'
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        print(self.nodes)

    def valid_chain(self, chain):
        """
        确定一个区块链是否正确
        :param chain: <list>区块链
        :return: <bool>True if valid
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            # 检查hash值
            if block['pre_hash'] != self.hash(last_block):
                return False
            
            # 检查proof
            if not self.validProof(block['proof'],last_block['proof']):
                return False
            
            last_block = block
            current_index += 1
        
        return True

    def resolve_conflicts(self):
        """
        共识算法，解决区块链不同的问题，通过将我们的链
        替换成网络上最长的有效链
        :return: <bool>True 如果链被更换
        """
        neighbours = self.nodes
        new_chain = None
        # 只寻找比我们长的链
        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        
        if new_chain:
            self.chain = new_chain
            return True
        
        return False


app = Flask(__name__)

# 初始化一个唯一的id
node_identifier = str(uuid4()).replace('-','')

blockchain = Blockchain()

@app.route('/')
def index():
    return 'welcome'

@app.route('/chain')
def chain():
    response = {"chain":blockchain.chain, "length":len(blockchain.chain)}
    return jsonify(response), 200


@app.route('/mine', methods=['GET'])
def mine():
        """
            调用PoW算法
            奖励一个币
            创建一个block
        """
        proof = blockchain.PoW(blockchain.last_block['proof'])
        blockchain.new_transtion(
            sender='0',
            receiver=node_identifier,
            amount = 1,
        )
        block = blockchain.new_block(proof,blockchain.hash(blockchain.last_block))
        response = {
        'message': "we mine a new block",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'pre_hash': block['pre_hash'],
        }
        return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transtion_api():
    values = request.get_json()
    print(values)
    required = ['sender', 'receiver', 'amount']
    for k in required:
        if k not in values:
            return 'Missing values', 400
    
    index = blockchain.new_transtion(values['sender'], values['receiver'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index+1}'}
    return jsonify(response), 201

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    
    nodes = values.get('nodes')
    print(nodes)
    print("------")
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        print(node)
        blockchain.register_node(node)

    response={
        'mseeage': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes)
    } 
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(input('port:')))
    pass