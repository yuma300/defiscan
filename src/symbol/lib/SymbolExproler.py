import requests
from binascii import unhexlify
from symbolchain.core.symbol.Network import Address, Network
from symbolchain.core.symbol.NetworkTimestamp import EPOCH_TIME
from symbolchain.core.CryptoTypes import PublicKey
import logging
import json
import sys
import os
from .base import BaseSymbolClass
from decimal import Decimal
from datetime import datetime,timezone,timedelta

logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())


def set_root_logger():
	root_logget = logging.getLogger(name=None)
	root_logget.setLevel(logging.INFO)
	stream_handler = logging.StreamHandler()
	stream_handler.setLevel(logging.INFO)
	root_logget.addHandler(stream_handler)


class SymbolExproler(BaseSymbolClass):
	_mosaic_id_dict = None # fast resolving name
	_public_key_dict = None # fast resolving self key
	# _node_url = None
	# # _node_url = "http://ngl-dual-001.symbolblockchain.io:3000"
	# def __init__(self,node_url=None):
	# 	if node_url != None:
	# 		# e.g. dhealth
	# 		self._node_url = node_url
	# 	else:
	# 		self._node_url = "http://ngl-dual-001.symbolblockchain.io:3000"
	# 	self.name = requests.get(self._node_url+f"/network").json()["name"]

	def get_harvests(self,address,pageNumber=1):
		node_url = self._node_url
		harvest_array=[]
		page_size = 20
		res = requests.get(node_url+f"/statements/transaction?targetAddress={address}&pageNumber={pageNumber}&order=desc&pageSize={page_size}")
		# logger.debug(res.json())
		for harvest in res.json()["data"]:
			for receipts in harvest["statement"]["receipts"]:
				if "targetAddress" in receipts:
					target_address = Address(unhexlify(receipts["targetAddress"]))
					if str(target_address) == address:
						logger.debug(f"{target_address}: {receipts['amount']}")
						harvest_array.append(harvest)
		if len(res.json()["data"]) == page_size:
			harvest_array += self.get_harvests(address,pageNumber=pageNumber+1)
		return harvest_array

	def get_transactions(self,address,pageNumber=1):
		transactions_array = []
		node_url = self._node_url
		page_size = 20
		res = requests.get(node_url+f"/transactions/confirmed?address={address}&pageNumber={pageNumber}&order=desc&pageSize={page_size}")
		# logger.info(res.json())
		# logger.debug(res.json())
		for transaction in res.json()["data"]:
			transactions_array.append(transaction)
		if len(res.json()["data"]) >= page_size:
			transactions_array += self.get_transactions(address,pageNumber=pageNumber+1)
		return transactions_array


	def get_symbol_names(self,mosaic_id)->list:
		if self._mosaic_id_dict == None:
			self._mosaic_id_dict = {}
		if mosaic_id in self._mosaic_id_dict:
			return self._mosaic_id_dict[mosaic_id]
		else:
			node_url = self._node_url
			res = requests.post(node_url+f"/namespaces/mosaic/names",json={"mosaicIds":[mosaic_id]})
			# logger.debug(res.json())
			mosaic_names = list(filter(lambda item: item['mosaicId'] == mosaic_id, res.json()["mosaicNames"]))[0]
			self._mosaic_id_dict[mosaic_id] = mosaic_names["names"]
			return mosaic_names["names"]


	def get_account_public_key(self,account_id):
		if self._public_key_dict == None:
			self._public_key_dict = {}
		if account_id in self._public_key_dict:
			return self._public_key_dict[account_id]
		else:
			node_url = self._node_url
			res = requests.get(node_url+f"/accounts/{account_id}").json()
			publick_key =  res["account"]["publicKey"]
			self._public_key_dict[account_id] = publick_key
			return publick_key


	def fee_calculator(self,transaction_hash)->int:
		node_url = self._node_url
		res = requests.get(node_url+f"/transactions/confirmed/{transaction_hash}").json()
		target_block_height = res["meta"]["height"]
		origin_blocksize = res["transaction"]["size"]
		res = requests.get(node_url+f"/blocks/{target_block_height}").json()
		total_fee = Decimal(res["meta"]["totalFee"])
		logger.debug(target_block_height)
		logger.debug(total_fee)
		logger.debug(origin_blocksize)
		# total_blocksize = 0
		def calc_total_blocksize(block_height,size=0,pageNumber=1)->int:
			page_size = 20
			res = requests.get(node_url+f"/transactions/confirmed?height={block_height}&pageNumber={pageNumber}&order=desc&pageSize={page_size}").json()
			for transaction in res["data"]:
				# transaction_hash = transaction["meta"]["hash"]
				size += transaction["transaction"]["size"]
			if len(res["data"]) == page_size:
				size += calc_total_blocksize(block_height,size=size,pageNumber=pageNumber+1)
			return size
		total_blocksize = calc_total_blocksize(target_block_height)
		ratio = Decimal(origin_blocksize) / Decimal(total_blocksize)
		logger.debug(f"ratio: {ratio}")
		fee = Decimal(total_fee) * ratio / Decimal("1"+"0"*6)
		logger.debug(fee)
		return fee


	def get_timestamp(self,block_height)->datetime:
		node_url = self._node_url
		res = requests.get(node_url+f"/blocks/{block_height}").json()
		unix_timestamp = timedelta(milliseconds=int(res["block"]["timestamp"]))
		dt = EPOCH_TIME + unix_timestamp # nemesis block + block time
		return dt


	def get_aggregate_transactions(self,transaction_hash):
		node_url = self._node_url
		res = requests.get(node_url+f"/transactions/confirmed/{transaction_hash}").json()
		# print(res)
		return res["transaction"]["transactions"]
