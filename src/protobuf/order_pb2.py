# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: order.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0border.proto\"\x96\x03\n\x05Order\x12\n\n\x02id\x18\x01 \x01(\t\x12#\n\nline_items\x18\x02 \x03(\x0b\x32\x0f.Order.LineItem\x12!\n\x08\x63ustomer\x18\x03 \x01(\x0b\x32\x0f.Order.Customer\x12\x0e\n\x06status\x18\x04 \x01(\t\x12\x1f\n\x07\x66\x61\x63tory\x18\x05 \x01(\x0b\x32\x0e.Order.Factory\x12\x12\n\norder_date\x18\x06 \x01(\x03\x1ak\n\x08LineItem\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x12\n\nunit_price\x18\x03 \x01(\t\x12\x10\n\x08quantity\x18\x04 \x01(\x05\x12\r\n\x05price\x18\x05 \x01(\t\x12\x10\n\x08\x63urrency\x18\x06 \x01(\t\x1a\x33\n\x08\x43ustomer\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\r\n\x05\x65mail\x18\x03 \x01(\t\x1aR\n\x07\x46\x61\x63tory\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04\x63ity\x18\x03 \x01(\t\x12\r\n\x05state\x18\x04 \x01(\t\x12\x10\n\x08zip_code\x18\x05 \x01(\tb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'order_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_ORDER']._serialized_start = 16
  _globals['_ORDER']._serialized_end = 422
  _globals['_ORDER_LINEITEM']._serialized_start = 178
  _globals['_ORDER_LINEITEM']._serialized_end = 285
  _globals['_ORDER_CUSTOMER']._serialized_start = 287
  _globals['_ORDER_CUSTOMER']._serialized_end = 338
  _globals['_ORDER_FACTORY']._serialized_start = 340
  _globals['_ORDER_FACTORY']._serialized_end = 422
# @@protoc_insertion_point(module_scope)
