# serge_client.DatabaseManagementApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_db_get**](DatabaseManagementApi.md#delete_db_get) | **GET** /deleteDb | Delete a database
[**download_all_get**](DatabaseManagementApi.md#download_all_get) | **GET** /downloadAll | Download all databases
[**download_wargame_get**](DatabaseManagementApi.md#download_wargame_get) | **GET** /download/{wargame} | Download wargame database

# **delete_db_get**
> delete_db_get(db)

Delete a database

Deletes a database specified by the query parameter

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseManagementApi()
db = 'db_example' # str | Name of the database to delete

try:
    # Delete a database
    api_instance.delete_db_get(db)
except ApiException as e:
    print("Exception when calling DatabaseManagementApi->delete_db_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **db** | **str**| Name of the database to delete | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **download_all_get**
> str download_all_get()

Download all databases

Downloads all databases in a zip format

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseManagementApi()

try:
    # Download all databases
    api_response = api_instance.download_all_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DatabaseManagementApi->download_all_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/zip

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **download_wargame_get**
> str download_wargame_get(wargame)

Download wargame database

Downloads a wargame database in zip format

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseManagementApi()
wargame = 'wargame_example' # str | Name of the SQLite file to download

try:
    # Download wargame database
    api_response = api_instance.download_wargame_get(wargame)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DatabaseManagementApi->download_wargame_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **wargame** | **str**| Name of the SQLite file to download | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/zip

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

