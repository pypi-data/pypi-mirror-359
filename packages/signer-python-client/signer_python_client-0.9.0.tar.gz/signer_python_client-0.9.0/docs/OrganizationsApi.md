# signer_client.OrganizationsApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**api_organizations_users_get**](OrganizationsApi.md#api_organizations_users_get) | **GET** /api/organizations/users | List organization users
[**api_organizations_users_post**](OrganizationsApi.md#api_organizations_users_post) | **POST** /api/organizations/users | Adds a user to the organization
[**api_organizations_users_user_id_delete**](OrganizationsApi.md#api_organizations_users_user_id_delete) | **DELETE** /api/organizations/users/{userId} | Deletes a user from organization

# **api_organizations_users_get**
> PaginatedSearchResponseOrganizationsOrganizationUserModel api_organizations_users_get(q=q, limit=limit, offset=offset, order=order)

List organization users

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
api_instance = signer_client.OrganizationsApi(signer_client.ApiClient(configuration))
q = 'q_example' # str | Query to filter items. (optional)
limit = 56 # int | Number of items to return. (optional)
offset = 56 # int | The offset of the searched page (starting with 0). (optional)
order = signer_client.PaginationOrders() # PaginationOrders |  (optional)

try:
    # List organization users
    api_response = api_instance.api_organizations_users_get(q=q, limit=limit, offset=offset, order=order)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OrganizationsApi->api_organizations_users_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **q** | **str**| Query to filter items. | [optional] 
 **limit** | **int**| Number of items to return. | [optional] 
 **offset** | **int**| The offset of the searched page (starting with 0). | [optional] 
 **order** | [**PaginationOrders**](.md)|  | [optional] 

### Return type

[**PaginatedSearchResponseOrganizationsOrganizationUserModel**](PaginatedSearchResponseOrganizationsOrganizationUserModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_organizations_users_post**
> OrganizationsOrganizationUserModel api_organizations_users_post(body=body)

Adds a user to the organization

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
api_instance = signer_client.OrganizationsApi(signer_client.ApiClient(configuration))
body = signer_client.OrganizationsOrganizationUserPostRequest() # OrganizationsOrganizationUserPostRequest |  (optional)

try:
    # Adds a user to the organization
    api_response = api_instance.api_organizations_users_post(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling OrganizationsApi->api_organizations_users_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**OrganizationsOrganizationUserPostRequest**](OrganizationsOrganizationUserPostRequest.md)|  | [optional] 

### Return type

[**OrganizationsOrganizationUserModel**](OrganizationsOrganizationUserModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_organizations_users_user_id_delete**
> api_organizations_users_user_id_delete(user_id)

Deletes a user from organization

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
api_instance = signer_client.OrganizationsApi(signer_client.ApiClient(configuration))
user_id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 

try:
    # Deletes a user from organization
    api_instance.api_organizations_users_user_id_delete(user_id)
except ApiException as e:
    print("Exception when calling OrganizationsApi->api_organizations_users_user_id_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | [**str**](.md)|  | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

