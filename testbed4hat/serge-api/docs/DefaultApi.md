# serge_client.DefaultApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_ip_get**](DefaultApi.md#get_ip_get) | **GET** /getIp | Get IP address

# **get_ip_get**
> InlineResponse20013 get_ip_get()

Get IP address

Returns the IP address of the request

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DefaultApi()

try:
    # Get IP address
    api_response = api_instance.get_ip_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_ip_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse20013**](InlineResponse20013.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

