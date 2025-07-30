# signer_client.UploadApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**api_uploads_bytes_post**](UploadApi.md#api_uploads_bytes_post) | **POST** /api/uploads/bytes | Uploads a file by sending a JSON request with the bytes in Base 64 format.
[**api_uploads_post**](UploadApi.md#api_uploads_post) | **POST** /api/uploads | Uploads a file by sending a multipart/form-data request

# **api_uploads_bytes_post**
> UploadsUploadBytesModel api_uploads_bytes_post(body=body)

Uploads a file by sending a JSON request with the bytes in Base 64 format.

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
api_instance = signer_client.UploadApi(signer_client.ApiClient(configuration))
body = signer_client.UploadsUploadBytesRequest() # UploadsUploadBytesRequest |  (optional)

try:
    # Uploads a file by sending a JSON request with the bytes in Base 64 format.
    api_response = api_instance.api_uploads_bytes_post(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UploadApi->api_uploads_bytes_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**UploadsUploadBytesRequest**](UploadsUploadBytesRequest.md)|  | [optional] 

### Return type

[**UploadsUploadBytesModel**](UploadsUploadBytesModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_uploads_post**
> FileModel api_uploads_post(file=file)

Uploads a file by sending a multipart/form-data request

The id returned by this API should be used as paremeter to other APIs.  You may also use the location property to display a preview of the uploaded file.

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
api_instance = signer_client.UploadApi(signer_client.ApiClient(configuration))
file = '/path/to/file' # file |  (optional)

try:
    # Uploads a file by sending a multipart/form-data request
    api_response = api_instance.api_uploads_post(file=file)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UploadApi->api_uploads_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | [**file**](.md)|  | [optional] 

### Return type

[**FileModel**](FileModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

