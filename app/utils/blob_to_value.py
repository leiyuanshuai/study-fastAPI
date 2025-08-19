import msgpack
import binascii
from typing import Any

def decode_blob_data(blob_hex: str) -> Any:
  if blob_hex.startswith('0x'):
    blob_hex = blob_hex[2:]
  blob_bytes = binascii.unhexlify(blob_hex)
  return msgpack.unpackb(blob_bytes, raw=False)

# 示例使用
# blob_data = "0x94AD696E697469616C5F76616C7565A86E6F6465313A3733A96E6F6465323A313630A96E6F6465333A323135"
# decoded_value = decode_blob_data(blob_data)
# print(f"解码后的状态值: {decoded_value}")
