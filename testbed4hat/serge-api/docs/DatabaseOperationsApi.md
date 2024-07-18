# serge_client.DatabaseOperationsApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**all_dbs_get**](DatabaseOperationsApi.md#all_dbs_get) | **GET** /allDbs | Get all wargame names
[**bulk_docs_dbname_put**](DatabaseOperationsApi.md#bulk_docs_dbname_put) | **PUT** /bulkDocs/{dbname} | Bulk document update
[**clear_all_delete**](DatabaseOperationsApi.md#clear_all_delete) | **DELETE** /clearAll | Clear all databases
[**delete_db_name_delete**](DatabaseOperationsApi.md#delete_db_name_delete) | **DELETE** /delete/{dbName} | Delete database
[**get_wargame_id_get**](DatabaseOperationsApi.md#get_wargame_id_get) | **GET** /get/{wargame}/{id} | Get document for a specified wargame
[**replicate_replicate_dbname_get**](DatabaseOperationsApi.md#replicate_replicate_dbname_get) | **GET** /replicate/{replicate}/{dbname} | Replicate database
[**wargame_dbname_logs_get**](DatabaseOperationsApi.md#wargame_dbname_logs_get) | **GET** /{wargame}/{dbname}/logs | Get logs for a specific database within a wargame
[**wargame_dbname_logs_latest_get**](DatabaseOperationsApi.md#wargame_dbname_logs_latest_get) | **GET** /{wargame}/{dbname}/logs-latest | Get the latest logs for a specific database within a wargame
[**wargame_force_id_counter_get**](DatabaseOperationsApi.md#wargame_force_id_counter_get) | **GET** /{wargame}/{force}/{id}/counter | Get the message counter for a specified force in a wargame
[**wargame_get**](DatabaseOperationsApi.md#wargame_get) | **GET** /{wargame} | Retrieve all message documents for the specified wargame.
[**wargame_last_doc_id_get**](DatabaseOperationsApi.md#wargame_last_doc_id_get) | **GET** /{wargame}/lastDoc/{id} | Get the last document or documents since a specific ID
[**wargame_last_get**](DatabaseOperationsApi.md#wargame_last_get) | **GET** /{wargame}/last | Get the last wargame
[**wargame_list_get**](DatabaseOperationsApi.md#wargame_list_get) | **GET** /wargameList | Get wargame list
[**wargame_put**](DatabaseOperationsApi.md#wargame_put) | **PUT** /{wargame} | Update wargame
[**wargame_turns_get**](DatabaseOperationsApi.md#wargame_turns_get) | **GET** /{wargame}/turns | Get game turns for a specified wargame

# **all_dbs_get**
> InlineResponse2004 all_dbs_get()

Get all wargame names

Retrieves the names of all wargame databases.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseOperationsApi()

try:
    # Get all wargame names
    api_response = api_instance.all_dbs_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DatabaseOperationsApi->all_dbs_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2004**](InlineResponse2004.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **bulk_docs_dbname_put**
> InlineResponse2002 bulk_docs_dbname_put(body, dbname)

Bulk document update

Updates multiple documents in a specified database in bulk.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseOperationsApi()
body = NULL # list[object] | 
dbname = 'dbname_example' # str | Name of the database to update documents in.

try:
    # Bulk document update
    api_response = api_instance.bulk_docs_dbname_put(body, dbname)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DatabaseOperationsApi->bulk_docs_dbname_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**list[object]**](object.md)|  | 
 **dbname** | **str**| Name of the database to update documents in. | 

### Return type

[**InlineResponse2002**](InlineResponse2002.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **clear_all_delete**
> clear_all_delete()

Clear all databases

Resets all databases.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseOperationsApi()

try:
    # Clear all databases
    api_instance.clear_all_delete()
except ApiException as e:
    print("Exception when calling DatabaseOperationsApi->clear_all_delete: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_db_name_delete**
> InlineResponse2003 delete_db_name_delete(db_name)

Delete database

Deletes a specified database.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseOperationsApi()
db_name = 'db_name_example' # str | Name of the database to delete.

try:
    # Delete database
    api_response = api_instance.delete_db_name_delete(db_name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DatabaseOperationsApi->delete_db_name_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **db_name** | **str**| Name of the database to delete. | 

### Return type

[**InlineResponse2003**](InlineResponse2003.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_wargame_id_get**
> InlineResponse20012 get_wargame_id_get(wargame, id)

Get document for a specified wargame

Retrieves a document for the specified wargame and document ID.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseOperationsApi()
wargame = 'wargame_example' # str | The name of the wargame database.
id = 'id_example' # str | The ID of the document.

try:
    # Get document for a specified wargame
    api_response = api_instance.get_wargame_id_get(wargame, id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DatabaseOperationsApi->get_wargame_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **wargame** | **str**| The name of the wargame database. | 
 **id** | **str**| The ID of the document. | 

### Return type

[**InlineResponse20012**](InlineResponse20012.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replicate_replicate_dbname_get**
> str replicate_replicate_dbname_get(replicate, dbname)

Replicate database

Replicates data from an existing database to a new database.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseOperationsApi()
replicate = 'replicate_example' # str | Name of the new database to replicate data into.
dbname = 'dbname_example' # str | Name of the existing database to replicate data from.

try:
    # Replicate database
    api_response = api_instance.replicate_replicate_dbname_get(replicate, dbname)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DatabaseOperationsApi->replicate_replicate_dbname_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **replicate** | **str**| Name of the new database to replicate data into. | 
 **dbname** | **str**| Name of the existing database to replicate data from. | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **wargame_dbname_logs_get**
> InlineResponse2009 wargame_dbname_logs_get(wargame, dbname)

Get logs for a specific database within a wargame

Retrieves logs for a specified database within the specified wargame.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseOperationsApi()
wargame = 'wargame_example' # str | The name of the wargame.
dbname = 'dbname_example' # str | The name of the database within the wargame.

try:
    # Get logs for a specific database within a wargame
    api_response = api_instance.wargame_dbname_logs_get(wargame, dbname)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DatabaseOperationsApi->wargame_dbname_logs_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **wargame** | **str**| The name of the wargame. | 
 **dbname** | **str**| The name of the database within the wargame. | 

### Return type

[**InlineResponse2009**](InlineResponse2009.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **wargame_dbname_logs_latest_get**
> InlineResponse20011 wargame_dbname_logs_latest_get(wargame, dbname)

Get the latest logs for a specific database within a wargame

Retrieves the latest logs for a specified database within the specified wargame.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseOperationsApi()
wargame = 'wargame_example' # str | The name of the wargame.
dbname = 'dbname_example' # str | The name of the database within the wargame.

try:
    # Get the latest logs for a specific database within a wargame
    api_response = api_instance.wargame_dbname_logs_latest_get(wargame, dbname)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DatabaseOperationsApi->wargame_dbname_logs_latest_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **wargame** | **str**| The name of the wargame. | 
 **dbname** | **str**| The name of the database within the wargame. | 

### Return type

[**InlineResponse20011**](InlineResponse20011.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **wargame_force_id_counter_get**
> InlineResponse20010 wargame_force_id_counter_get(wargame, force, id)

Get the message counter for a specified force in a wargame

Retrieves the message counter for the specified force in the given wargame.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseOperationsApi()
wargame = 'wargame_example' # str | The name of the wargame database.
force = 'force_example' # str | The name of the force.
id = 'id_example' # str | The ID of the message.

try:
    # Get the message counter for a specified force in a wargame
    api_response = api_instance.wargame_force_id_counter_get(wargame, force, id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DatabaseOperationsApi->wargame_force_id_counter_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **wargame** | **str**| The name of the wargame database. | 
 **force** | **str**| The name of the force. | 
 **id** | **str**| The ID of the message. | 

### Return type

[**InlineResponse20010**](InlineResponse20010.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **wargame_get**
> InlineResponse200 wargame_get(wargame)

Retrieve all message documents for the specified wargame.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseOperationsApi()
wargame = 'wargame_example' # str | Name of the wargame to retrieve message documents for.

try:
    # Retrieve all message documents for the specified wargame.
    api_response = api_instance.wargame_get(wargame)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DatabaseOperationsApi->wargame_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **wargame** | **str**| Name of the wargame to retrieve message documents for. | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **wargame_last_doc_id_get**
> InlineResponse2007 wargame_last_doc_id_get(wargame, id)

Get the last document or documents since a specific ID

Retrieves the latest document or all documents since a specific ID for the specified wargame.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseOperationsApi()
wargame = 'wargame_example' # str | The name of the wargame database.
id = 'id_example' # str | The ID to retrieve documents since.

try:
    # Get the last document or documents since a specific ID
    api_response = api_instance.wargame_last_doc_id_get(wargame, id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DatabaseOperationsApi->wargame_last_doc_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **wargame** | **str**| The name of the wargame database. | 
 **id** | **str**| The ID to retrieve documents since. | 

### Return type

[**InlineResponse2007**](InlineResponse2007.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **wargame_last_get**
> InlineResponse2006 wargame_last_get(wargame)

Get the last wargame

Retrieves the last document for the specified wargame.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseOperationsApi()
wargame = 'wargame_example' # str | The name of the wargame database.

try:
    # Get the last wargame
    api_response = api_instance.wargame_last_get(wargame)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DatabaseOperationsApi->wargame_last_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **wargame** | **str**| The name of the wargame database. | 

### Return type

[**InlineResponse2006**](InlineResponse2006.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **wargame_list_get**
> InlineResponse2005 wargame_list_get()

Get wargame list

Retrieves a list of all wargame databases with their details.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseOperationsApi()

try:
    # Get wargame list
    api_response = api_instance.wargame_list_get()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DatabaseOperationsApi->wargame_list_get: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2005**](InlineResponse2005.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **wargame_put**
> InlineResponse2001 wargame_put(body, wargame)

Update wargame

Updates or creates a document in the specified wargame database.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseOperationsApi()
body = NULL # dict(str, object) | 
wargame = 'wargame_example' # str | The name of the wargame database to update.

try:
    # Update wargame
    api_response = api_instance.wargame_put(body, wargame)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DatabaseOperationsApi->wargame_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**dict(str, object)**](dict.md)|  | 
 **wargame** | **str**| The name of the wargame database to update. | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **wargame_turns_get**
> InlineResponse2008 wargame_turns_get(wargame)

Get game turns for a specified wargame

Retrieves all game turns for the specified wargame.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.DatabaseOperationsApi()
wargame = 'wargame_example' # str | The name of the wargame database.

try:
    # Get game turns for a specified wargame
    api_response = api_instance.wargame_turns_get(wargame)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DatabaseOperationsApi->wargame_turns_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **wargame** | **str**| The name of the wargame database. | 

### Return type

[**InlineResponse2008**](InlineResponse2008.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

