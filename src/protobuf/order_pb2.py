# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: order.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0border.proto\"\xfb\x01\n\x05Order\x12\n\n\x02id\x18\x01 \x01(\t\x12#\n\nline_items\x18\x02 \x01(\x0b\x32\x0f.Order.LineItem\x12!\n\x08\x63ustomer\x18\x03 \x01(\x0b\x32\x0f.Order.Customer\x12\x0e\n\x06status\x18\x04 \x01(\t\x1aY\n\x08LineItem\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x12\n\nunit_price\x18\x03 \x01(\t\x12\x10\n\x08quantity\x18\x04 \x01(\x05\x12\r\n\x05price\x18\x05 \x01(\t\x1a\x33\n\x08\x43ustomer\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\r\n\x05\x65mail\x18\x03 \x01(\tb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'order_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _ORDER._serialized_start=16
  _ORDER._serialized_end=267
  _ORDER_LINEITEM._serialized_start=125
  _ORDER_LINEITEM._serialized_end=214
  _ORDER_CUSTOMER._serialized_start=216
  _ORDER_CUSTOMER._serialized_end=267
# @@protoc_insertion_point(module_scope)
