import logging
import binascii
from ruuvitag_sensor.data_formats import DataFormats
from ruuvitag_sensor.decoder import get_decoder
logging.basicConfig(level=logging.DEBUG)

def decode_ad5(inp: bytearray) -> dict:
    advert = {}
    inp = binascii.unhexlify(inp)
    inp = list(inp)
    advert["format"] = inp[0:1]
    advert["temperature"] = int.from_bytes(inp[1:3]) * .005
    advert["humidity"] = int.from_bytes(inp[3:5]) * .0025
    advert["pressure"] = (int.from_bytes(inp[5:7]) + 50000) / 100
    advert["acceleration_x"] = int.from_bytes(inp[7:9])
    advert["acceleration_y"] = int.from_bytes(inp[9:11])
    advert["acceleration_z"] = int.from_bytes(inp[11:13])
    advert["power_and_rec"] = inp[13:15]
    advert["movements"] = inp[15]
    advert["sequence"] = inp[16:18]
    return advert
# testdata = bytes.fromhex("043E2A0201030157168974A51F0201060303AAFE1716AAFE10F9037275752E76692F23416A5558314D417730C3")
# print(binascii.hexlify(testdata))
# full_data = "043E2A0201030157168974A51F0201060303AAFE1716AAFE10F9037275752E76692F23416A5558314D417730C3"
# full_data = b'1c1bFF990405115e5f4a6f790064000c03fca9363f9993c1fc9b69048bd0'.hex()
ad_data = b'05122f5e356f91016000b803b4aa96869ca4c1fc9b69048b'
full_data = "316331624646393930343035313136323631663836663931303036346666666330343034616139363433396334356331666339623639303438626431"
# full_data = binascii.unhexlify(full_data).hex()
# print(full_data)
# full_data = full_data[26:]
# for key in range(0,64):
#     full_data = "303531313363363037643666383130303663303030383033666361613136343139613965633166633962363930343862"
#     print(key)
#     full_data = full_data[key:]
# print(data)
# # convert_data returns tuple which has Data Format type and encoded data
# (data_format, encoded) = DataFormats.convert_data(full_data)
# print(data_format)
# print(data_format)
# sensor_data = get_decoder(data_format).decode_data(encoded)
sensor_data = decode_ad5(ad_data)
print(sensor_data)
# {'temperature': 25.12, 'identifier': '0', 'humidity': 26.5, 'pressure': 992.0}
b'05122f5e356f91016000b803b4aa96869ca4c1fc9b69048b'
b'05 122f 5e35 6f91 016000b803b4aa96869ca4c1fc9b69048b'

