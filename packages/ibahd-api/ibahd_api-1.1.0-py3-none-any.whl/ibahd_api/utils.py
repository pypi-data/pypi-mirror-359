# ------------------------------------------------------------------------------
# utils.py
#
# Copyright (c) 2025 iba AG
#
# Licensed under the MIT License. See LICENSE-MIT.txt for full license text.
# ------------------------------------------------------------------------------

import grpc
import json
from datetime import datetime, timezone
from decimal import Decimal

from ibahd_api import ibahd_api_pb2_grpc


# Constants
TICKS_OF_UNIX_EPOCH = 62_135_596_800  # ticks of "1970-01-01 T00:00:00.000000Z"

def get_api_params(quick_connect: str):
    '''
    Extracts the connection parameters from a quick_connect string, which can be retrieved in ibaHD Manager.

    :param quick_connect: Quick connect string from ibaHD Manager

    :return: certificate, api_key, hostname and port for the connection with the desired HD store
    '''
    api_params = json.loads(quick_connect)

    certificate = bytes(api_params['TlsServerCertificate'], encoding='utf-8')
    api_key = api_params['ApiKey']
    hostname = api_params['Host']
    port = api_params['Port']

    return certificate, api_key, hostname, port
    
def create_client(certificate, api_key, hostname, port):
	# Combine certificate and api_key to full credentials used for authentification
	tls_credentials = grpc.ssl_channel_credentials(certificate)
	api_key_credentials  = grpc.metadata_call_credentials(ApiKeyCallCredentials(api_key))  # apply api_key to every request made by the client
	combined_credentials = grpc.composite_channel_credentials(tls_credentials, api_key_credentials)

	# gRPC channel setup to connect to ibaHD-API endpoint in ibaHD-Server
	endpoint = f'{hostname}:{port}'
	options = [('grpc.max_receive_message_length', 2147483647)]  # increasing default message size (~4MB) recommended (c int32 max = 2147483647)

	# Open gRPC channel with previous defined server
	channel = grpc.secure_channel(endpoint, combined_credentials, options=options)

	# Instantiate ibahd-api client on the gRPC channel
	client = ibahd_api_pb2_grpc.HdApiServiceStub(channel)
	
	return client

# Helper class to apply the api key to each call
class ApiKeyCallCredentials(grpc.AuthMetadataPlugin):
    def __init__(self, apikey):
        self._apikey = apikey

    def __call__(self, context, callback):
        metadata = (('ibahdapi-apikey', self._apikey),)
        callback(metadata, None)

def convert_datetime_to_timestamp(datetime_str_utc: str) -> float:
    '''
    Converts the given datetime string into an unix timestamp with seconds as a base.
    Can handle precisions of up to 100 nanoseconds (1e-7 seconds).
    Leading zeros can be ommitted. Inverse operation to convert_timestamp_to_datetime.
    Note: Input needs to be in UTC time zone.

    Examples:
    convert_datetime_to_timestamp('2025-06-26 10:43:27.1205924') = 1750934607.1205924
    convert_datetime_to_timestamp('2025-6-6 0:3:7.4') = 1749168187.4
    x = 1750934607.1205924
    convert_datetime_to_timestamp(convert_timestamp_to_datetime(x)) = x
    '''
    seventh_digit = None
    if len(datetime_str_utc.split('.')[-1]) == 7:
        seventh_digit = Decimal(datetime_str_utc[-1])  # nanoseconds
        datetime_str_utc = datetime_str_utc[:-1]
    fmt = '%Y-%m-%d %H:%M:%S.%f'
    dt_utc = datetime.strptime(datetime_str_utc, fmt).replace(tzinfo=timezone.utc)    
    unix_timestamp_utc = Decimal(str(dt_utc.timestamp()))
    
    if seventh_digit is not None:
        unix_timestamp_utc += seventh_digit * Decimal("0.0000001")
    return float(unix_timestamp_utc)

def convert_timestamp_to_datetime(unix_timestamp_utc: float) -> str:
    '''
    Converts an unix timestamp with seconds as a base into a readable format.
    Can handle precisions of up to 100 nanoseconds (1e-7 seconds).
    Output might be padded with leading zeros. Inverse operation to convert_datetime_to_timestamp.
    Note: Input needs to be in UTC time zone.

    Examples:
    convert_timestamp_to_datetime(1750934607.1205924) = '2025-06-26 10:43:27.1205924'
    x = '2025-6-6 0:3:7.4'
    convert_timestamp_to_datetime(convert_datetime_to_timestamp(x)) = '2025-06-06 00:03:07.4000000'
    '''
    dt = datetime.fromtimestamp(int(unix_timestamp_utc))  # seconds
    micro = int((unix_timestamp_utc - int(unix_timestamp_utc)) * 1e6)  # microseconds
    seventh_digit = int((unix_timestamp_utc * 1e7) % 10)  # nanoseconds

    dt = dt.replace(microsecond=micro)
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f') + str(seventh_digit)
    
def convert_timestamp_to_ticks(unix_timestamp_utc: float) -> int:
    '''
    Converts an unix timestamp with seconds as a base into a ticks timestamp.
    Can handle precisions of 100 nanoseconds (1e-7 seconds).
    Inverse operation to convert_ticks_to_timestamp.
    Note: Input needs to be in UTC time zone.

    Examples:
    convert_timestamp_to_ticks(1750934607.1205924) = 638865314071205924
    x = 638865314071205924
    convert_timestamp_to_ticks(convert_ticks_to_timestamp(x)) = x
    '''
    ticks = (Decimal(str(unix_timestamp_utc)) + TICKS_OF_UNIX_EPOCH) * Decimal("1e7")
    return int(ticks)

def convert_ticks_to_timestamp(ticks: int) -> float:
    '''
    Converts a ticks timestamp into an unix timestamp with seconds as a base.
    Can handle precisions of 100 nanoseconds (1e-7 seconds).
    Inverse operation to convert_timestamp_to_ticks.
    Note: Input needs to be in UTC time zone.

    Examples:
    convert_ticks_to_timestamp(638865314071205924) = 1750934607.1205924
    x = 1750934607.1205924
    convert_ticks_to_timestamp(convert_timestamp_to_ticks(x)) = x
    '''
    unix_timestamp_utc = (Decimal(ticks) / Decimal("1e7")) - TICKS_OF_UNIX_EPOCH
    return float(unix_timestamp_utc)

def convert_datetime_to_ticks(datetime_str_utc: str) -> int:
    '''
    Converts the given datetime string into into a ticks timestamp.
    Can handle precisions of 100 nanoseconds (1e-7 seconds).
    Leading zeros can be ommitted. Inverse operation to convert_ticks_to_datetime.
    Note: Input needs to be in UTC time zone.

    Examples:
    convert_datetime_to_ticks('2025-04-13 01:02:03.4500000') = 638801029234500000
    convert_datetime_to_ticks('2025-4-13 1:2:3.45') = 638801029234500000
    x = '2025-4-13 1:2:3.45'
    convert_datetime_to_ticks(convert_ticks_to_datetime(x)) = '2025-04-13 01:02:03.4500000'
    '''
    timestamp_utc = convert_datetime_to_timestamp(datetime_str_utc)
    ticks = convert_timestamp_to_ticks(timestamp_utc)
    return ticks

def convert_ticks_to_datetime(ticks: int) -> str:
    '''
    Converts the given ticks timestamp into a readable format.
    Can handle precisions of 100 nanoseconds (1e-7 seconds).
    Inverse operation to convert_datetime_to_ticks.
    Note: Input needs to be in UTC time zone.

    Examples:
    convert_ticks_to_datetime(638801029234500000) = '2025-04-13 01:02:03.4500000'
    x = 638801029234500000
    convert_ticks_to_datetime(convert_datetime_to_ticks(x)) = x
    '''
    timestamp_utc = convert_ticks_to_timestamp(ticks)
    datetime_str_utc = convert_timestamp_to_datetime(timestamp_utc)
    return datetime_str_utc
