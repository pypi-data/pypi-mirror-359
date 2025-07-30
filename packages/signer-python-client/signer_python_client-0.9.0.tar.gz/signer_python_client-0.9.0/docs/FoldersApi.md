# signer_client.FoldersApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**api_folders_get**](FoldersApi.md#api_folders_get) | **GET** /api/folders | Retrieves all folders paginating the response
[**api_folders_id_delete_post**](FoldersApi.md#api_folders_id_delete_post) | **POST** /api/folders/{id}/delete | Deletes a folder.
[**api_folders_id_get**](FoldersApi.md#api_folders_id_get) | **GET** /api/folders/{id} | Retrieves the folder&#x27;s info.
[**api_folders_post**](FoldersApi.md#api_folders_post) | **POST** /api/folders | Creates a folder.

# **api_folders_get**
> PaginatedSearchResponseFoldersFolderInfoModel api_folders_get(q=q, limit=limit, offset=offset, order=order, filter_by_parent=filter_by_parent, parent_id=parent_id)

Retrieves all folders paginating the response

The Q parameter allows you to filter by folder name.

### Example
```python
from __future__ import print_function
import time
import signer_client
from signer_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = signer_client.Configuration()
configuration.api_key['X-Api-Key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Api-Key'] = 'Bearer'

# create an instance of the API class
api_instance = signer_client.FoldersApi(signer_client.ApiClient(configuration))
q = 'q_example' # str | Query to filter items. (optional)
limit = 56 # int | Number of items to return. (optional)
offset = 56 # int | The offset of the searched page (starting with 0). (optional)
order = signer_client.PaginationOrders() # PaginationOrders |  (optional)
filter_by_parent = false # bool | if true filters by the parentId parameter (optional) (default to false)
parent_id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | Id of the parent folder (optional)

try:
    # Retrieves all folders paginating the response
    api_response = api_instance.api_folders_get(q=q, limit=limit, offset=offset, order=order, filter_by_parent=filter_by_parent, parent_id=parent_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FoldersApi->api_folders_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **q** | **str**| Query to filter items. | [optional] 
 **limit** | **int**| Number of items to return. | [optional] 
 **offset** | **int**| The offset of the searched page (starting with 0). | [optional] 
 **order** | [**PaginationOrders**](.md)|  | [optional] 
 **filter_by_parent** | **bool**| if true filters by the parentId parameter | [optional] [default to false]
 **parent_id** | [**str**](.md)| Id of the parent folder | [optional] 

### Return type

[**PaginatedSearchResponseFoldersFolderInfoModel**](PaginatedSearchResponseFoldersFolderInfoModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_folders_id_delete_post**
> api_folders_id_delete_post(id, body=body)

Deletes a folder.

### Example
```python
from __future__ import print_function
import time
import signer_client
from signer_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = signer_client.Configuration()
configuration.api_key['X-Api-Key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Api-Key'] = 'Bearer'

# create an instance of the API class
api_instance = signer_client.FoldersApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | Id of the folder to be deleted
body = signer_client.FoldersFolderDeleteRequest() # FoldersFolderDeleteRequest |  (optional)

try:
    # Deletes a folder.
    api_instance.api_folders_id_delete_post(id, body=body)
except ApiException as e:
    print("Exception when calling FoldersApi->api_folders_id_delete_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)| Id of the folder to be deleted | 
 **body** | [**FoldersFolderDeleteRequest**](FoldersFolderDeleteRequest.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_folders_id_get**
> FoldersFolderOrganizationModel api_folders_id_get(id)

Retrieves the folder's info.

### Example
```python
from __future__ import print_function
import time
import signer_client
from signer_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = signer_client.Configuration()
configuration.api_key['X-Api-Key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Api-Key'] = 'Bearer'

# create an instance of the API class
api_instance = signer_client.FoldersApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | Folder id

try:
    # Retrieves the folder's info.
    api_response = api_instance.api_folders_id_get(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FoldersApi->api_folders_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)| Folder id | 

### Return type

[**FoldersFolderOrganizationModel**](FoldersFolderOrganizationModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_folders_post**
> FoldersFolderInfoModel api_folders_post(body=body)

Creates a folder.

### Example
```python
from __future__ import print_function
import time
import signer_client
from signer_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: ApiKey
configuration = signer_client.Configuration()
configuration.api_key['X-Api-Key'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['X-Api-Key'] = 'Bearer'

# create an instance of the API class
api_instance = signer_client.FoldersApi(signer_client.ApiClient(configuration))
body = signer_client.FoldersFolderCreateRequest() # FoldersFolderCreateRequest |  (optional)

try:
    # Creates a folder.
    api_response = api_instance.api_folders_post(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FoldersApi->api_folders_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**FoldersFolderCreateRequest**](FoldersFolderCreateRequest.md)|  | [optional] 

### Return type

[**FoldersFolderInfoModel**](FoldersFolderInfoModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

