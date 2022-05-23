from flask import Flask, json, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from os import environ
import asyncio
from settings import PRIVATE_KEY
import threading
from threading import Timer
app = Flask(__name__)
# app.config.from_pyfile('settings.py')
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cellframe'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
CORS(app)

with open('./abi_chain1.json', 'r') as myfile:
    abi_chain1 = myfile.read()
run1 = True

with open('./abi_chain2.json', 'r') as myfile:
    abi_chain2 = myfile.read()
run2 = True

with open('./abi_chain3.json', 'r') as myfile:
    abi_chain3 = myfile.read()
run3 = True

chainBlock1 = 1
chainBlock2 = 2
chainBlock3 = 3
if PRIVATE_KEY != None:
    # print(PRIVATE_KEY)
    url_chain1 = "https://rinkeby.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"
    w3_chain1 = Web3(HTTPProvider(url_chain1))
    address = w3_chain1.eth.account.privateKeyToAccount(PRIVATE_KEY).address
    w3_chain1.middleware_onion.inject(geth_poa_middleware, layer=0)
    conAddress_chain1 = '0x5f36b5Dad1d9d688E97D49AC4CdED849C14552b0'
    # conAddress = '0x7db1d851A842bE7745dAa2F2aa7181E5557cAC24'
    contract_chain1 = w3_chain1.eth.contract(
        address=conAddress_chain1, abi=abi_chain1)

    url_chain2 = "https://ropsten.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"
    w3_chain2 = Web3(HTTPProvider(url_chain2))
    w3_chain2.middleware_onion.inject(geth_poa_middleware, layer=0)
    conAddress_chain2 = '0x64BD65Bd2c631842FdB8b6694ce39E7cbfdC20d4'
    # conAddress = '0x7db1d851A842bE7745dAa2F2aa7181E5557cAC24'
    contract_chain2 = w3_chain2.eth.contract(
        address=conAddress_chain2, abi=abi_chain2)
    # token = contract_chain2.functions.deployBlockNum().call()
    # print(token)

    url_chain3 = "https://rinkeby.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"
    w3_chain3 = Web3(HTTPProvider(url_chain3))
    w3_chain3.middleware_onion.inject(geth_poa_middleware, layer=0)
    conAddress_chain3 = '0x97F0f241D592E133aF9Bb33d050D88B014E89a06'
    # conAddress = '0x7db1d851A842bE7745dAa2F2aa7181E5557cAC24'
    contract_chain3 = w3_chain3.eth.contract(
        address=conAddress_chain3, abi=abi_chain3)
    # print('nonce', w3_chain3.eth.getTransactionCount(address))
    tx = {
        'from': address,
        'nonce': w3_chain3.eth.getTransactionCount(address),
        'gas': 2000000,
        'gasPrice': w3_chain3.toWei('50', 'gwei')
    }
    # # transaction = contract.functions.setAdmin('0x866D57dE7DcC015ad26e34965659cC169be697F3').buildTransaction(tx)
    # transaction = contract.functions.applyTo(3, 'Flask', True, 1, 8, 'http://aaa', 'CELL', '0x421E4fDD21AA4100C43CF29e0b30DBf3Ea1A90fC').buildTransaction(tx)
    # signed_txn = w3.eth.account.signTransaction(transaction, private_key=PRIVATE_KEY)
    # tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    # w3.eth.waitForTransactionReceipt(tx_hash)
    # print('Updated contract admin: {}'.format(
    #     contract.functions.admin().call()
    # ))

    def rinkebyScan():
        global run1
        if run1:
            with app.app_context():
                cur = mysql.connection.cursor()
                cur.execute(
                    "SELECT fromblock FROM block WHERE id='" + str(chainBlock1) + "'")
                result = cur.fetchall()
                fromblock = result[0]['fromblock']
                print(fromblock)
            currentBlockNum = w3_chain1.eth.block_number
            apply_filter = contract_chain1.events.Apply.createFilter(
                fromBlock=fromblock + 1, toBlock=currentBlockNum).get_all_entries()
            bid_filter = contract_chain1.events.BID.createFilter(
                fromBlock=fromblock + 1, toBlock=currentBlockNum).get_all_entries()
            with app.app_context():
                cur = mysql.connection.cursor()
                cur.execute("UPDATE block SET fromblock = '" + str(currentBlockNum) +
                            "'" + "WHERE id ='" + str(chainBlock1) + "'")
                mysql.connection.commit()
            if(len(apply_filter) > 0):
                for apply in apply_filter:
                    auctionID = apply['args']['auctionID']
                    owner = apply['args']['participant']
                    projectName = str(apply['args']['project_name'].decode(
                        'utf-8')).replace('\x00', '')
                    crowdloan = apply['args']['project_type']
                    st_range = apply['args']['st_range']
                    end_range = apply['args']['end_range']
                    referenceUrl = str(apply['args']['metaURI'].decode(
                        'utf-8')).replace('\x00', '')
                    # tokenName = str(apply['args']['token_name'].decode(
                    #     'utf-8')).replace('\x00', '')
                    tokenAddr = apply['args']['sc_address']

                    print(auctionID, owner, projectName, crowdloan, st_range,
                          end_range, referenceUrl, tokenAddr)
                    with app.app_context():
                        cur = mysql.connection.cursor()
                        cur.execute("INSERT INTO project(auctionID, owner, projectName, crowdloan, st_range," +
                                    "end_range, referenceUrl, tokenaddr, projectState, chainId, totalScore," +
                                    "lastScore, lastBidder) VALUES('" +
                                    str(auctionID)+"','"+str(owner)+"','"+str(projectName)+"','" + str(crowdloan)+"','" +
                                    str(st_range)+"','" + str(end_range)+"','" + str(referenceUrl)+"','" +
                                    str(tokenAddr)+"','" + str(0) + "','" + str(4)+"','" + str(0)+"','" + str(0)+"','" +
                                    str('0x0000000000000000000000000') + "')")
                        mysql.connection.commit()
            if(len(bid_filter) > 0):
                for bid in bid_filter:
                    projectID = bid['args']['projectID']
                    bidder = bid['args']['bidder']
                    timestamp = bid['args']['timestamp']
                    amount = bid['args']['amount']
                    st_range = bid['args']['st_range']
                    end_range = bid['args']['end_range']
                    tokenAddress = bid['args']['tokenAddress']

                    print(projectID, bidder, timestamp, amount,
                          st_range, end_range, tokenAddress)
                    with app.app_context():
                        cur = mysql.connection.cursor()
                        cur.execute(
                            "SELECT totalScore FROM project WHERE id = '" + str(projectID) + "'")
                        result = cur.fetchall()
                        cur.execute("UPDATE project SET lastScore = '" + str(amount) + "'," + "totalScore = '" + str(int(result[0]['totalScore']) + amount) +
                                    "'," + "lastBidder = '" + bidder + "'" + "WHERE id ='" + str(projectID) + "'")
                        mysql.connection.commit()
                        cur.execute("INSERT INTO bidder(projectID, bidder, timestamp, amount, st_range, end_range, tokenAddress) VALUES('" +
                                    str(projectID)+"','"+str(bidder)+"','"+str(timestamp)+"','" + str(amount)+"','" + str(st_range)+"','" +
                                    str(end_range)+"','" + str(tokenAddress) + "')")
                        mysql.connection.commit()
                        cur.execute(
                            "SELECT auctionID, chainId FROM project WHERE id='" + str(projectID) + "'")
                        result = cur.fetchall()
                        auctionID = result[0]['auctionID']
                        chainId = result[0]['chainId']
                    tx = {
                        'from': address,
                        'nonce': w3_chain3.eth.getTransactionCount(address),
                        'gas': 2000000,
                        'gasPrice': w3_chain3.toWei('2', 'gwei')
                    }
                    transaction = contract_chain3.functions.addBid(
                        auctionID, projectID, bidder, timestamp, chainId, tokenAddress, amount).buildTransaction(tx)
                    signed_txn = w3_chain3.eth.account.signTransaction(
                        transaction, private_key=PRIVATE_KEY)
                    tx_hash = w3_chain3.eth.sendRawTransaction(
                        signed_txn.rawTransaction)
                    w3_chain3.eth.waitForTransactionReceipt(tx_hash)
            Timer(10, rinkebyScan).start()
    rinkebyScan()

    def ropstenScan():
        global run2
        if run2:
            with app.app_context():
                cur = mysql.connection.cursor()
                cur.execute(
                    "SELECT fromblock FROM block WHERE id='" + str(2) + "'")

                result = cur.fetchall()
                fromblock = result[0]['fromblock']
                print(fromblock)
            currentBlockNum = w3_chain2.eth.block_number
            apply_filter = contract_chain2.events.Apply.createFilter(
                fromBlock=fromblock + 1, toBlock=currentBlockNum).get_all_entries()
            bid_filter = contract_chain1.events.BID.createFilter(
                fromBlock=fromblock + 1, toBlock=currentBlockNum).get_all_entries()
            with app.app_context():
                cur = mysql.connection.cursor()
                cur.execute("UPDATE block SET fromblock = '" + str(currentBlockNum) +
                            "'" + "WHERE id ='" + str(chainBlock2) + "'")
                mysql.connection.commit()
            if(len(apply_filter) > 0):
                for apply in apply_filter:
                    auctionID = apply['args']['auctionID']
                    owner = apply['args']['participant']
                    projectName = str(apply['args']['project_name'].decode(
                        'utf-8')).replace('\x00', '')
                    crowdloan = apply['args']['project_type']
                    st_range = apply['args']['st_range']
                    end_range = apply['args']['end_range']
                    referenceUrl = str(apply['args']['metaURI'].decode(
                        'utf-8')).replace('\x00', '')
                    # tokenName = str(apply['args']['token_name'].decode(
                    #     'utf-8')).replace('\x00', '')
                    tokenAddr = apply['args']['sc_address']

                    print(auctionID, owner, projectName, crowdloan, st_range,
                          end_range, referenceUrl, tokenAddr)
                    with app.app_context():
                        cur = mysql.connection.cursor()
                        cur.execute("INSERT INTO project(auctionID, owner, projectName, crowdloan, st_range," +
                                    "end_range, referenceUrl, tokenaddr, projectState, chainId, totalScore," +
                                    "lastScore, lastBidder) VALUES('" +
                                    str(auctionID)+"','"+str(owner)+"','"+str(projectName)+"','" + str(crowdloan)+"','" +
                                    str(st_range)+"','" + str(end_range)+"','" + str(referenceUrl) + "','" +
                                    str(tokenAddr)+"','" + str(0) + "','" + str(4)+"','" + str(0)+"','" + str(0)+"','" +
                                    str('0x0000000000000000000000000') + "')")
                        mysql.connection.commit()
            if(len(bid_filter) > 0):
                for bid in bid_filter:
                    projectID = bid['args']['projectID']
                    bidder = bid['args']['bidder']
                    timestamp = bid['args']['timestamp']
                    amount = bid['args']['amount']
                    st_range = bid['args']['st_range']
                    end_range = bid['args']['end_range']
                    tokenAddress = bid['args']['tokenAddress']

                    print(projectID, bidder, timestamp, amount,
                          st_range, end_range, tokenAddress)
                    with app.app_context():
                        cur = mysql.connection.cursor()
                        cur.execute(
                            "SELECT totalScore FROM project WHERE id = '" + str(projectID) + "'")
                        result = cur.fetchall()
                        cur.execute("UPDATE project SET lastScore = '" + str(amount) + "'," + "totalScore = '" + str(int(result[0]['totalScore']) + amount)  +
                                    "'," + "lastBidder = '" + bidder + "'" + "WHERE id ='" + str(projectID) + "'")
                        mysql.connection.commit()
                        cur.execute("INSERT INTO bidder(projectID, bidder, timestamp, amount, st_range, end_range, tokenAddress) VALUES('" +
                                    str(projectID)+"','"+str(bidder)+"','"+str(timestamp)+"','" + str(amount)+"','" + str(st_range)+"','" +
                                    str(end_range)+"','" + str(tokenAddress) + "')")
                        mysql.connection.commit()
                        cur.execute(
                            "SELECT auctionID, chainId FROM project WHERE id='" + str(projectID) + "'")
                        result = cur.fetchall()
                        auctionID = result[0]['auctionID']
                        chainId = result[0]['chainId']
                    tx = {
                        'from': address,
                        'nonce': w3_chain3.eth.getTransactionCount(address),
                        'gas': 2000000,
                        'gasPrice': w3_chain3.toWei('2', 'gwei')
                    }
                    transaction = contract_chain3.functions.addBid(
                        auctionID, projectID, bidder, timestamp, chainId, tokenAddress, amount).buildTransaction(tx)
                    signed_txn = w3_chain3.eth.account.signTransaction(
                        transaction, private_key=PRIVATE_KEY)
                    tx_hash = w3_chain3.eth.sendRawTransaction(
                        signed_txn.rawTransaction)
                    w3_chain3.eth.waitForTransactionReceipt(tx_hash)
            Timer(10, ropstenScan).start()
    ropstenScan()

    def chainScan3():
        global run3
        if run3:
            auctionState = contract_chain3.functions.auctionState().call()
            print(auctionState)
            if (auctionState == 3):
                winnerProjectID = contract_chain3.functions.winnerProjectID().call()
                print("winnerProjectID", winnerProjectID)

                with app.app_context():
                    cur = mysql.connection.cursor()
                    cur.execute("UPDATE auction SET auctionState = '" + str(3) +
                                "'" + "WHERE activeState ='" + str(1) + "'")
                    mysql.connection.commit()
                    cur.execute("UPDATE project SET projectState = '" + str(4) +
                                "'" + "WHERE id ='" + str(winnerProjectID) + "'")
                run3 = False
            Timer(10, chainScan3).start()


@app.route('/api/getActiveAuctionUser', methods=['GET'])
def getActiveAuctionUser():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM auction WHERE activeState='" + str(1) + "'")
        result = cur.fetchall()

        if(len(result) > 0):
            cur.execute("SELECT * FROM project WHERE auctionID='" +
                        str(result[0]['id']) + "'" + "AND projectState = '" + str(1) + "'")
            # str(result[0]['id']) + "'" + "and projectState='" + str(0) + "'")
            result1 = cur.fetchall()
            result[0]['applicants'] = result1
            # print(result)
            return jsonify(result[0])
        else:
            return jsonify([])


@app.route('/api/addApproveProject', methods=['POST'])
def addApproveProject():
    if request.method == 'POST':
        auctionID = request.get_json()['auctionID']
        owner = request.get_json()['owner']
        projectName = request.get_json()['projectName']
        crowdloan = request.get_json()['crowdloan']
        st_range = request.get_json()['st_range']
        end_range = request.get_json()['end_range']
        referenceUrl = request.get_json()['referenceUrl']
        tokenAddr = request.get_json()['tokenAddr']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO project(auctionID, owner, projectName, crowdloan, st_range," +
                    "end_range, referenceUrl, tokenaddr, projectState, chainId, totalScore," +
                    "lastScore, lastBidder) VALUES('" +
                    str(auctionID)+"','"+str(owner)+"','"+str(projectName)+"','" + str(crowdloan)+"','" +
                    str(st_range)+"','" + str(end_range)+"','" + str(referenceUrl) + "','" +
                    str(tokenAddr)+"','" + str(1) + "','" + str(4)+"','" + str(0)+"','" + str(0)+"','" +
                    str('0x0000000000000000000000000') + "')")
        mysql.connection.commit()
        result = {
            'auctionID': auctionID,
            'owner': owner,
            'projectName': projectName,
            'crowdloan': crowdloan,
            'st_range': st_range,
            'end_range': end_range,
            'referenceUrl': referenceUrl,
            'tokenAddr': tokenAddr,
        }
        return jsonify(result)


@app.route('/api/getActiveAuctionAdmin', methods=['GET'])
def getActiveAuctionAdmin():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM auction WHERE activeState='" + str(1) + "'")
        result = cur.fetchall()

        if(len(result) > 0):
            cur.execute("SELECT * FROM project WHERE auctionID='" +
                        str(result[0]['id']) + "'")
            result1 = cur.fetchall()
            result[0]['applicants'] = result1
            # print(result)
            return jsonify(result[0])
        else:
            return jsonify([])


@app.route('/api/getFutureAuctionUser', methods=['GET'])
def getFutureAuctionUser():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM auction WHERE activeState='" + str(2) + "'")
        result = cur.fetchall()

        if(len(result) > 0):
            cur.execute("SELECT * FROM project WHERE auctionID='" +
                        str(result[0]['id']) + "'" + "and projectState='1'")
            result1 = cur.fetchall()
            result[0]['project'] = result1
            # print(result)
            return jsonify(result[0])
        else:
            return jsonify([])


@app.route('/api/getFutureAuctionAdmin', methods=['GET'])
def getFutureAuctionAdmin():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM auction WHERE activeState='" + str(2) + "'")
        result = cur.fetchall()

        if(len(result) > 0):
            cur.execute("SELECT * FROM project WHERE auctionID='" +
                        str(result[0]['id']) + "'")
            result1 = cur.fetchall()
            result[0]['project'] = result1
            # print(result)
            return jsonify(result[0])
        else:
            return jsonify([])


@app.route('/api/createActiveAuction', methods=['POST'])
def createActiveAuction():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM auction WHERE activeState='" + str(1) + "'")
        result = cur.fetchall()
        if(len(result) == 0):
            cur.execute(
                "SELECT * FROM auction WHERE activeState='" + str(2) + "'")
            result = cur.fetchall()
            print(request.get_json())
            if(len(result) > 0):
                cur.execute(
                    "UPDATE auction SET activeState = 1 WHERE activeState = 2")
            else:
                maxRange = request.get_json()['maxRange']
                minScore = request.get_json()['minimalCellSlotPrice']
                cur.execute("INSERT INTO auction(maxRange, minScore, activeState, auctionState) VALUES('" +
                            str(maxRange)+"','"+str(minScore)+"','"+str(1)+"','" + str(1)+"')")
                mysql.connection.commit()
                result = {
                    'maxRange': maxRange,
                    'minimalCellSlotPrice': minScore
                }
                print(result)
    return jsonify(result)


@app.route('/api/createFutureAuction', methods=['POST'])
def createFutureAuction():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM auction WHERE activeState='" + str(2) + "'")
        result = cur.fetchall()
        # print(len(result))
        if(len(result) > 0):
            return 'already exist'
        else:
            maxRange = request.get_json()['maxRange']
            minScore = request.get_json()['minimalCellSlotPrice']
            cur.execute("INSERT INTO auction(maxRange, minScore, activeState, auctionState) VALUES('" +
                        str(maxRange)+"','"+str(minScore)+"','"+str(2)+"','" + str(1)+"')")
            mysql.connection.commit()
            result = {
                'maxRange': maxRange,
                'minimalCellSlotPrice': minScore
            }
            print(result)
            return jsonify(result)


@app.route('/api/getPassedAuctions', methods=['GET'])
def getPassedAuctions():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM auction WHERE activeState='" + str(0) + "'")
        result = cur.fetchall()
        auctions = []
        for auction in result:
            print(auction['id'])
            cur.execute("SELECT * FROM project WHERE auctionID ='" +
                        str(auction['id']) + "'" + "AND (projectState = '" + str(4) + "'" + " OR projectState ='" + str(1) + "')")
            result1 = cur.fetchall()
            auctions.insert(0, result1)

        # print(result)
        return jsonify(auctions)


@app.route('/api/getWinners', methods=['GET'])
def getWinners():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM project WHERE projectState='" + str(4) + "'")
        result = cur.fetchall()
        # print(result)
        return jsonify(result)


@app.route('/api/startAuction', methods=['POST'])
def startAuction():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("UPDATE auction SET auctionState = '" + str(2) +
                    "'" + "WHERE activeState ='" + str(1) + "'")
        mysql.connection.commit()
        tx = {
            'from': address,
            'nonce': w3_chain3.eth.getTransactionCount(address),
            'gas': 2000000,
            'gasPrice': w3_chain3.toWei('2', 'gwei')
        }
        print(address)
        transaction = contract_chain3.functions.startAuction().buildTransaction(tx)
        signed_txn = w3_chain3.eth.account.signTransaction(
            transaction, private_key=PRIVATE_KEY)
        tx_hash = w3_chain3.eth.sendRawTransaction(
            signed_txn.rawTransaction)
        w3_chain3.eth.waitForTransactionReceipt(tx_hash)

    # return jsonify(result)
    return('Auction started')


@app.route('/api/finishAuction', methods=['POST'])
def finishAuction():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("UPDATE auction SET auctionState = '" + str(3) +
                    "'" + "WHERE activeState ='" + str(1) + "'")
        mysql.connection.commit()
        tx = {
            'from': address,
            'nonce': w3_chain3.eth.getTransactionCount(address),
            'gas': 2000000,
            'gasPrice': w3_chain3.toWei('2', 'gwei')
        }
        print(address)
        transaction = contract_chain3.functions.finishAuction().buildTransaction(tx)
        signed_txn = w3_chain3.eth.account.signTransaction(
            transaction, private_key=PRIVATE_KEY)
        tx_hash = w3_chain3.eth.sendRawTransaction(
            signed_txn.rawTransaction)
        w3_chain3.eth.waitForTransactionReceipt(tx_hash)
        global run3
        run3 = True
        chainScan3()
        return('Auction finished')


@app.route('/api/approveProject', methods=['POST'])
def approveProject():
    if request.method == 'POST':
        projectID = request.get_json()['projectID']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE project SET projectState = '" + str(1) +
                    "'" + "WHERE id ='" + str(projectID) + "'")
        mysql.connection.commit()

        result = {
            'projectID': projectID,
        }
        print(result)
        return jsonify(result)


@app.route('/api/declineProject', methods=['POST'])
def declineProject():
    if request.method == 'POST':
        projectID = request.get_json()['projectID']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE project SET projectState = '" + str(2) +
                    "'" + "WHERE id ='" + str(projectID) + "'")
        mysql.connection.commit()

        result = {
            'projectID': projectID,
        }
        print(result)
        return jsonify(result)


@app.route('/api/blockProject', methods=['POST'])
def blockProject():
    if request.method == 'POST':
        projectID = request.get_json()['projectID']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE project SET projectState = '" + str(3) +
                    "'" + "WHERE id ='" + str(projectID) + "'")
        mysql.connection.commit()

        result = {
            'projectID': projectID,
        }
        print(result)
        return jsonify(result)


if __name__ == '__main__':
    app.run(host='192.168.104.30', debug=True)
