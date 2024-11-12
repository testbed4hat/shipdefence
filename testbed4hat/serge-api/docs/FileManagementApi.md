# serge_client.FileManagementApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_icon_icon_get**](FileManagementApi.md#get_icon_icon_get) | **GET** /getIcon/{icon} | Get icon
[**save_icon_post**](FileManagementApi.md#save_icon_post) | **POST** /saveIcon | Save icon
[**save_logo_post**](FileManagementApi.md#save_logo_post) | **POST** /saveLogo | Save a logo image
[**tiles_folder_zyx_get**](FileManagementApi.md#tiles_folder_zyx_get) | **GET** /tiles/{folder}/{z}/{y}/{x} | Get tile image

# **get_icon_icon_get**
> str get_icon_icon_get(icon)

Get icon

Retrieves an icon image by its filename.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.FileManagementApi()
icon = 'icon_example' # str | Filename of the icon to retrieve.

try:
    # Get icon
    api_response = api_instance.get_icon_icon_get(icon)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FileManagementApi->get_icon_icon_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **icon** | **str**| Filename of the icon to retrieve. | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: image/png, image/svg+xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **save_icon_post**
> InlineResponse20014 save_icon_post(body)

Save icon

Uploads an icon image (PNG or SVG) and saves it to the server.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.FileManagementApi()
body = serge_client.Object() # Object | 

try:
    # Save icon
    api_response = api_instance.save_icon_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FileManagementApi->save_icon_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Object**|  | 

### Return type

[**InlineResponse20014**](InlineResponse20014.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: image/png, image/svg+xml
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **save_logo_post**
> InlineResponse20015 save_logo_post(body)

Save a logo image

Uploads a logo image in PNG or SVG format and saves it to the server.

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.FileManagementApi()
body = serge_client.Object() # Object | 

try:
    # Save a logo image
    api_response = api_instance.save_logo_post(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FileManagementApi->save_logo_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Object**|  | 

### Return type

[**InlineResponse20015**](InlineResponse20015.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: image/png, image/svg+xml
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **tiles_folder_zyx_get**
> str tiles_folder_zyx_get(folder, z, y, x)

Get tile image

Returns a tile image based on the specified folder and coordinates

### Example
```python
from __future__ import print_function
import time
import serge_client
from serge_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = serge_client.FileManagementApi()
folder = 'folder_example' # str | Folder name
z = 'z_example' # str | Z coordinate
y = 'y_example' # str | Y coordinate
x = 'x_example' # str | X coordinate

try:
    # Get tile image
    api_response = api_instance.tiles_folder_zyx_get(folder, z, y, x)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FileManagementApi->tiles_folder_zyx_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **folder** | **str**| Folder name | 
 **z** | **str**| Z coordinate | 
 **y** | **str**| Y coordinate | 
 **x** | **str**| X coordinate | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: image/png, image/svg+xml

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

