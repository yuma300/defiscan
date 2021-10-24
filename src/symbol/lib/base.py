import requests

class BaseSymbolClass():
	_node_url = None
	# _node_url = "http://ngl-dual-001.symbolblockchain.io:3000"
	def __init__(self,node_url=None):
		if node_url != None:
			# e.g. dhealth
			self._node_url = node_url
		else:
			self._node_url = "http://ngl-dual-001.symbolblockchain.io:3000"
		self.name = requests.get(self._node_url+f"/network").json()["name"]
