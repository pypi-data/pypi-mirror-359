# signer_client.MarksSessionsApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**api_marks_sessions_documents_post**](MarksSessionsApi.md#api_marks_sessions_documents_post) | **POST** /api/marks-sessions/documents | Creates a mark positioning session from a Document create request.
[**api_marks_sessions_id_get**](MarksSessionsApi.md#api_marks_sessions_id_get) | **GET** /api/marks-sessions/{id} | Retrieves session information.
[**api_marks_sessions_post**](MarksSessionsApi.md#api_marks_sessions_post) | **POST** /api/marks-sessions | Creates a mark positioning session by requiring only the necessary data.

# **api_marks_sessions_documents_post**
> DocumentMarkMarksSessionCreateResponse api_marks_sessions_documents_post(body=body)

Creates a mark positioning session from a Document create request.

The purpose of the positioning session is to allow users to visually position signer marks.  The result of the session is the same request provided while creating it but with the flowAction's prePositioned marks attribute  filled according to the positions selected for each action.      Result will be available by iFrame event when embedding the positioning session or by retrieving the session information via the GET API.

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
api_instance = signer_client.MarksSessionsApi(signer_client.ApiClient(configuration))
body = signer_client.DocumentsCreateDocumentRequest() # DocumentsCreateDocumentRequest |  (optional)

try:
    # Creates a mark positioning session from a Document create request.
    api_response = api_instance.api_marks_sessions_documents_post(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MarksSessionsApi->api_marks_sessions_documents_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**DocumentsCreateDocumentRequest**](DocumentsCreateDocumentRequest.md)|  | [optional] 

### Return type

[**DocumentMarkMarksSessionCreateResponse**](DocumentMarkMarksSessionCreateResponse.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_marks_sessions_id_get**
> DocumentMarkMarksSessionModel api_marks_sessions_id_get(id)

Retrieves session information.

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
api_instance = signer_client.MarksSessionsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | The session ID obtained when the session was created

try:
    # Retrieves session information.
    api_response = api_instance.api_marks_sessions_id_get(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MarksSessionsApi->api_marks_sessions_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)| The session ID obtained when the session was created | 

### Return type

[**DocumentMarkMarksSessionModel**](DocumentMarkMarksSessionModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_marks_sessions_post**
> DocumentMarkMarksSessionCreateResponse api_marks_sessions_post(body=body)

Creates a mark positioning session by requiring only the necessary data.

The purpose of the positioning session is to allow users to visually position signer marks.  The result of the session is the same request provided while creating it but with the flowAction's prePositioned marks attribute  filled according to the positions selected for each action.      Result will be available by iFrame event when embedding the positioning session or by retrieving the session information via the GET API.

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
api_instance = signer_client.MarksSessionsApi(signer_client.ApiClient(configuration))
body = signer_client.DocumentMarkMarksSessionCreateRequest() # DocumentMarkMarksSessionCreateRequest |  (optional)

try:
    # Creates a mark positioning session by requiring only the necessary data.
    api_response = api_instance.api_marks_sessions_post(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MarksSessionsApi->api_marks_sessions_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**DocumentMarkMarksSessionCreateRequest**](DocumentMarkMarksSessionCreateRequest.md)|  | [optional] 

### Return type

[**DocumentMarkMarksSessionCreateResponse**](DocumentMarkMarksSessionCreateResponse.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

