import unittest
import os
from cosmos_to_caaj.block import *
import json
from pathlib import Path

class TestBlock(unittest.TestCase):
  """verify Block works fine"""

  def test_get_swap_transacted(self):
    block_json = json.loads(Path('%s/../testdata/block_swap_within_batch_v4.json' % os.path.dirname(__file__)).read_text())
    block = Block(block_json)
    swap_transacted = block.get_swap_transacted(1, 18772, 15644)
    attributes = swap_transacted['attributes']
    self.assertEqual(swap_transacted['type'], 'swap_transacted')
    self.assertEqual(attributes[0]['key'], 'pool_id')
    self.assertEqual(attributes[0]['value'], '1')
    self.assertEqual(attributes[1]['key'], 'batch_index')
    self.assertEqual(attributes[1]['value'], '18772')
    self.assertEqual(attributes[2]['key'], 'msg_index')
    self.assertEqual(attributes[2]['value'], '15644')

  def test_get_deposit_to_pool(self):
    block_json = json.loads(Path('%s/../testdata/block_deposit_within_batch_v4.json' % os.path.dirname(__file__)).read_text())
    block = Block(block_json)
    deposit_to_pool = block.get_deposit_to_pool(1, 18772, 15644)
    attributes = deposit_to_pool['attributes']
    self.assertEqual(deposit_to_pool['type'], 'deposit_to_pool')
    self.assertEqual(attributes[0]['key'], 'pool_id')
    self.assertEqual(attributes[0]['value'], '5')
    self.assertEqual(attributes[1]['key'], 'batch_index')
    self.assertEqual(attributes[1]['value'], '18697')
    self.assertEqual(attributes[2]['key'], 'msg_index')
    self.assertEqual(attributes[2]['value'], '3298')


if __name__ == '__main__':
  unittest.main()