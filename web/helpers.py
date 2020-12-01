from datetime import datetime
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from web3 import Web3, HTTPProvider
from django.conf import settings
import os
import math
from eth_utils import to_hex
from django.core.mail import send_mail
import time

def makeBurnAddress(t):
	pass

# rpc_user and rpc_password are set in the bitcoin.conf file
rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(settings.OLD_TAO_RPC_USERNAME, settings.OLD_TAO_RPC_PASSWORD, settings.OLD_TAO_RPC))
w3 = Web3(Web3.HTTPProvider(settings.TAO_RPC))

def getLastBlock():
	info = rpc_connection.getinfo()
	block = rpc_connection.getblockbynumber(info['blocks'])
	return info['blocks'],datetime.utcfromtimestamp(int(block['time'])).strftime('%Y-%m-%d %H:%M:%S')

def getMoneySupply():
	info = rpc_connection.getinfo()
	return info['moneysupply']

def onRpcError():
	rpc_connection.close()
	rpc_connection = AuthServiceProxy("http://%s:%s@%s"%(settings.OLD_TAO_RPC_USERNAME, settings.OLD_TAO_RPC_PASSWORD, settings.OLD_TAO_RPC))

def getExodusAddress(username): 
	#rpc_connection.walletpassphrase(settings.OLD_TAO_WALLET_PASSWORD,5)
	addr = rpc_connection.getnewaddress(username)
	return addr

def verifyTransaction(tx_id):
	while 1 != 0:
		try:
			x = rpc_connection.gettransaction(tx_id)
			if x is not None:
				return x 
			else:
				return None
		except:
			time.sleep(1)

def sendTransaction(username,amt,rec):
	balance = w3.fromWei(w3.eth.getBalance(settings.SWAP_ADDR),'ether')
	amount_in_wei = int(math.ceil(amt * 1000000000000000000))
	if amount_in_wei > w3.toWei(balance,'ether'):
		# shit, not enough in hot wallet
		subject = "EXODUS TRANSFER EXCEEDS WALLET"
		message = ("Wallet balance: {0} TAO\n\nRequested: {1} TAO\n\nAddress: {2}").format(balance, w3.fromWei(amount_in_wei,'ether'),username)
		send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, settings.MAILER_LIST, fail_silently=False)
		return False
	nonce = w3.eth.getTransactionCount(w3.toChecksumAddress(settings.SWAP_ADDR))
	transaction = {
		'to' : w3.toChecksumAddress(username),
		'value' : amount_in_wei,
		'gas': 21000,
		'gasPrice' : w3.toWei('15', 'gwei'),
		'nonce': nonce,
		'chainId': 558
	}
	if os.getenv('SWAP_PK') is not None:
		signed = w3.eth.account.sign_transaction(transaction, os.getenv('SWAP_PK'))
	else:
		signed = w3.eth.account.sign_transaction(transaction, settings.SWAP_PK)
	tx_id = to_hex(w3.eth.sendRawTransaction(signed.rawTransaction))
	if tx_id is not None:
		from .models import TaoSent
		sent = TaoSent.objects.create(tao_rec=rec,amt=amt,owner=rec.owner,tx_id=tx_id)
		sent.save()
		balance = w3.fromWei(w3.eth.getBalance(settings.SWAP_ADDR),'ether')
		subject = "Exodus Transfer"
		message = ("Wallet balance after transfer: {0} TAO\n\nRequested: {1} TAO\n\nAddress: {2}").format(balance, w3.fromWei(amount_in_wei,'ether'),username)
		send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, settings.MAILER_LIST, fail_silently=False)
		if balance < 200000:
			subject = "REFILL EXODUS WALLET"
			balance = w3.fromWei(w3.eth.getBalance(settings.SWAP_ADDR),'ether')
			message = ("Wallet balance: {0} TAO").format(balance)
			send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, settings.MAILER_LIST, fail_silently=False)
		return sent
	else:
		return False
