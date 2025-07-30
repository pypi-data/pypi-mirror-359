# signer_client.FlowsApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**api_document_flows_get**](FlowsApi.md#api_document_flows_get) | **GET** /api/document-flows | List created flows.
[**api_document_flows_id_delete**](FlowsApi.md#api_document_flows_id_delete) | **DELETE** /api/document-flows/{id} | Deletes a flow.
[**api_document_flows_id_get**](FlowsApi.md#api_document_flows_id_get) | **GET** /api/document-flows/{id} | Retrieves flow details
[**api_document_flows_id_put**](FlowsApi.md#api_document_flows_id_put) | **PUT** /api/document-flows/{id} | Updates a flow.
[**api_document_flows_post**](FlowsApi.md#api_document_flows_post) | **POST** /api/document-flows | Creates a flow that can be used to create documents

# **api_document_flows_get**
> PaginatedSearchResponseDocumentFlowsDocumentFlowModel api_document_flows_get(q=q, limit=limit, offset=offset, order=order)

List created flows.

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
api_instance = signer_client.FlowsApi(signer_client.ApiClient(configuration))
q = 'q_example' # str | Query to filter items. (optional)
limit = 56 # int | Number of items to return. (optional)
offset = 56 # int | The offset of the searched page (starting with 0). (optional)
order = signer_client.PaginationOrders() # PaginationOrders |  (optional)

try:
    # List created flows.
    api_response = api_instance.api_document_flows_get(q=q, limit=limit, offset=offset, order=order)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FlowsApi->api_document_flows_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **q** | **str**| Query to filter items. | [optional] 
 **limit** | **int**| Number of items to return. | [optional] 
 **offset** | **int**| The offset of the searched page (starting with 0). | [optional] 
 **order** | [**PaginationOrders**](.md)|  | [optional] 

### Return type

[**PaginatedSearchResponseDocumentFlowsDocumentFlowModel**](PaginatedSearchResponseDocumentFlowsDocumentFlowModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_document_flows_id_delete**
> api_document_flows_id_delete(id)

Deletes a flow.

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
api_instance = signer_client.FlowsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 

try:
    # Deletes a flow.
    api_instance.api_document_flows_id_delete(id)
except ApiException as e:
    print("Exception when calling FlowsApi->api_document_flows_id_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)|  | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_document_flows_id_get**
> DocumentFlowsDocumentFlowDetailsModel api_document_flows_id_get(id)

Retrieves flow details

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
api_instance = signer_client.FlowsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 

try:
    # Retrieves flow details
    api_response = api_instance.api_document_flows_id_get(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FlowsApi->api_document_flows_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)|  | 

### Return type

[**DocumentFlowsDocumentFlowDetailsModel**](DocumentFlowsDocumentFlowDetailsModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_document_flows_id_put**
> api_document_flows_id_put(id, body=body)

Updates a flow.

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
api_instance = signer_client.FlowsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 
body = signer_client.DocumentFlowsDocumentFlowData() # DocumentFlowsDocumentFlowData |  (optional)

try:
    # Updates a flow.
    api_instance.api_document_flows_id_put(id, body=body)
except ApiException as e:
    print("Exception when calling FlowsApi->api_document_flows_id_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)|  | 
 **body** | [**DocumentFlowsDocumentFlowData**](DocumentFlowsDocumentFlowData.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_document_flows_post**
> DocumentFlowsDocumentFlowModel api_document_flows_post(body=body)

Creates a flow that can be used to create documents

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
api_instance = signer_client.FlowsApi(signer_client.ApiClient(configuration))
body = signer_client.DocumentFlowsDocumentFlowCreateRequest() # DocumentFlowsDocumentFlowCreateRequest |  (optional)

try:
    # Creates a flow that can be used to create documents
    api_response = api_instance.api_document_flows_post(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FlowsApi->api_document_flows_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**DocumentFlowsDocumentFlowCreateRequest**](DocumentFlowsDocumentFlowCreateRequest.md)|  | [optional] 

### Return type

[**DocumentFlowsDocumentFlowModel**](DocumentFlowsDocumentFlowModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

