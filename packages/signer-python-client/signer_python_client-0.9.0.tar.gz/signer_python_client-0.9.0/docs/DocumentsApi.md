# signer_client.DocumentsApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**api_documents_batch_folder_post**](DocumentsApi.md#api_documents_batch_folder_post) | **POST** /api/documents/batch/folder | Moves a batch of documents to a folder.
[**api_documents_get**](DocumentsApi.md#api_documents_get) | **GET** /api/documents | Retrieves the documents of the organization paginating the response.
[**api_documents_id_action_url_post**](DocumentsApi.md#api_documents_id_action_url_post) | **POST** /api/documents/{id}/action-url | Retrieves an URL to redirect the user to the first pending action of the document.
[**api_documents_id_cancellation_post**](DocumentsApi.md#api_documents_id_cancellation_post) | **POST** /api/documents/{id}/cancellation | Cancels the document by providing a reason for the cancellation.
[**api_documents_id_content_b64_get**](DocumentsApi.md#api_documents_id_content_b64_get) | **GET** /api/documents/{id}/content-b64 | Downloads a specific version type of the document encoding the bytes in Base 64 format.
[**api_documents_id_content_get**](DocumentsApi.md#api_documents_id_content_get) | **GET** /api/documents/{id}/content | Downloads a specific version type of the document.
[**api_documents_id_delete**](DocumentsApi.md#api_documents_id_delete) | **DELETE** /api/documents/{id} | Deletes a specific document using it&#x27;s id.
[**api_documents_id_envelope_versions_post**](DocumentsApi.md#api_documents_id_envelope_versions_post) | **POST** /api/documents/{id}/envelope/versions | Adds a new version for an envelope.
[**api_documents_id_flow_post**](DocumentsApi.md#api_documents_id_flow_post) | **POST** /api/documents/{id}/flow | Updates the document&#x27;s flow.
[**api_documents_id_folder_post**](DocumentsApi.md#api_documents_id_folder_post) | **POST** /api/documents/{id}/folder | Moves a document to a folder.
[**api_documents_id_get**](DocumentsApi.md#api_documents_id_get) | **GET** /api/documents/{id} | Retrieves the document&#x27;s details.
[**api_documents_id_notified_emails_put**](DocumentsApi.md#api_documents_id_notified_emails_put) | **PUT** /api/documents/{id}/notified-emails | Updates the document&#x27;s notified emails
[**api_documents_id_refusal_post**](DocumentsApi.md#api_documents_id_refusal_post) | **POST** /api/documents/{id}/refusal | Refuses a document by providing a reason for the refusal.
[**api_documents_id_signatures_details_get**](DocumentsApi.md#api_documents_id_signatures_details_get) | **GET** /api/documents/{id}/signatures-details | Retrieves the details of the document&#x27;s signatures.
[**api_documents_id_ticket_get**](DocumentsApi.md#api_documents_id_ticket_get) | **GET** /api/documents/{id}/ticket | Generates a URL (ticket) to download a specific version type of the document.
[**api_documents_id_versions_post**](DocumentsApi.md#api_documents_id_versions_post) | **POST** /api/documents/{id}/versions | Adds a new version for the document.
[**api_documents_keys_key_signatures_get**](DocumentsApi.md#api_documents_keys_key_signatures_get) | **GET** /api/documents/keys/{key}/signatures | Validates each signature in a document using the verification code
[**api_documents_post**](DocumentsApi.md#api_documents_post) | **POST** /api/documents | Creates one or multiple documents.
[**api_documents_validate_signatures_post**](DocumentsApi.md#api_documents_validate_signatures_post) | **POST** /api/documents/validate-signatures | Validates each signature in the uploaded document

# **api_documents_batch_folder_post**
> list[BatchItemResultModel] api_documents_batch_folder_post(body=body)

Moves a batch of documents to a folder.

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
body = signer_client.DocumentsMoveDocumentBatchRequest() # DocumentsMoveDocumentBatchRequest |  (optional)

try:
    # Moves a batch of documents to a folder.
    api_response = api_instance.api_documents_batch_folder_post(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_batch_folder_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**DocumentsMoveDocumentBatchRequest**](DocumentsMoveDocumentBatchRequest.md)|  | [optional] 

### Return type

[**list[BatchItemResultModel]**](BatchItemResultModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_get**
> PaginatedSearchResponseDocumentsDocumentListModel api_documents_get(is_concluded=is_concluded, status=status, folder_id=folder_id, folder_type=folder_type, document_type=document_type, filter_by_document_type=filter_by_document_type, filter_by_pending_signature=filter_by_pending_signature, query_type=query_type, participant_q=participant_q, participant_query_type=participant_query_type, tags=tags, is_deleted=is_deleted, q=q, limit=limit, offset=offset, order=order)

Retrieves the documents of the organization paginating the response.

You may filter the documents by folder and document type.

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
is_concluded = true # bool | (DEPRECATED) Please use \"Status\" parameter instead. Set to true to list concluded documents, false to list pending documents. (optional)
status = signer_client.DocumentFilterStatus() # DocumentFilterStatus | Filters by document status. Will override the \"IsConcluded\" property. (optional)
folder_id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str |  (optional)
folder_type = signer_client.FolderType() # FolderType |  (optional)
document_type = signer_client.DocumentTypes() # DocumentTypes |  (optional)
filter_by_document_type = true # bool | True if the documents should be filtered by type, use documentType to specify the document type.  If you want to filter only documents without a type, set this parameter to true and the documentType to null. (optional)
filter_by_pending_signature = true # bool | True if documents should be filtered only for those that have FlowAction of the type Signer or SignRule (optional)
query_type = signer_client.DocumentQueryTypes() # DocumentQueryTypes |  (optional)
participant_q = 'participant_q_example' # str | Query to filter by participant (optional)
participant_query_type = signer_client.ParticipantQueryTypes() # ParticipantQueryTypes |  (optional)
tags = 'tags_example' # str | Label/value pairs are separated by \"|\" (optional) and Tags separated by \",\". Only the first 10 pairs will be considered.  To search by tag value only, do not use the \"|\". (optional)
is_deleted = true # bool | Returns deleted documents that had the specified document status when deleted. (optional)
q = 'q_example' # str | Query to filter items. (optional)
limit = 56 # int | Number of items to return. (optional)
offset = 56 # int | The offset of the searched page (starting with 0). (optional)
order = signer_client.PaginationOrders() # PaginationOrders |  (optional)

try:
    # Retrieves the documents of the organization paginating the response.
    api_response = api_instance.api_documents_get(is_concluded=is_concluded, status=status, folder_id=folder_id, folder_type=folder_type, document_type=document_type, filter_by_document_type=filter_by_document_type, filter_by_pending_signature=filter_by_pending_signature, query_type=query_type, participant_q=participant_q, participant_query_type=participant_query_type, tags=tags, is_deleted=is_deleted, q=q, limit=limit, offset=offset, order=order)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **is_concluded** | **bool**| (DEPRECATED) Please use \&quot;Status\&quot; parameter instead. Set to true to list concluded documents, false to list pending documents. | [optional] 
 **status** | [**DocumentFilterStatus**](.md)| Filters by document status. Will override the \&quot;IsConcluded\&quot; property. | [optional] 
 **folder_id** | [**str**](.md)|  | [optional] 
 **folder_type** | [**FolderType**](.md)|  | [optional] 
 **document_type** | [**DocumentTypes**](.md)|  | [optional] 
 **filter_by_document_type** | **bool**| True if the documents should be filtered by type, use documentType to specify the document type.  If you want to filter only documents without a type, set this parameter to true and the documentType to null. | [optional] 
 **filter_by_pending_signature** | **bool**| True if documents should be filtered only for those that have FlowAction of the type Signer or SignRule | [optional] 
 **query_type** | [**DocumentQueryTypes**](.md)|  | [optional] 
 **participant_q** | **str**| Query to filter by participant | [optional] 
 **participant_query_type** | [**ParticipantQueryTypes**](.md)|  | [optional] 
 **tags** | **str**| Label/value pairs are separated by \&quot;|\&quot; (optional) and Tags separated by \&quot;,\&quot;. Only the first 10 pairs will be considered.  To search by tag value only, do not use the \&quot;|\&quot;. | [optional] 
 **is_deleted** | **bool**| Returns deleted documents that had the specified document status when deleted. | [optional] 
 **q** | **str**| Query to filter items. | [optional] 
 **limit** | **int**| Number of items to return. | [optional] 
 **offset** | **int**| The offset of the searched page (starting with 0). | [optional] 
 **order** | [**PaginationOrders**](.md)|  | [optional] 

### Return type

[**PaginatedSearchResponseDocumentsDocumentListModel**](PaginatedSearchResponseDocumentsDocumentListModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_id_action_url_post**
> DocumentsActionUrlResponse api_documents_id_action_url_post(id, body=body)

Retrieves an URL to redirect the user to the first pending action of the document.

This API will return an URL that allows an user to sign or approve the document without having to wait to receive an email notification.      If the document has multiple pending actions, this API will return the URL of the first pending action for the matched user.      After the action has been completed, you may call this API again to retrieve the URL for the next action (if any).      Please note that using the URL returned will be recorded in the evidences of the action as an Application Authentication.  

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | Document Id
body = signer_client.DocumentsActionUrlRequest() # DocumentsActionUrlRequest |  (optional)

try:
    # Retrieves an URL to redirect the user to the first pending action of the document.
    api_response = api_instance.api_documents_id_action_url_post(id, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_id_action_url_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)| Document Id | 
 **body** | [**DocumentsActionUrlRequest**](DocumentsActionUrlRequest.md)|  | [optional] 

### Return type

[**DocumentsActionUrlResponse**](DocumentsActionUrlResponse.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_id_cancellation_post**
> api_documents_id_cancellation_post(id, body=body)

Cancels the document by providing a reason for the cancellation.

<b>CAUTION: This action cannot be reverted.</b>

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 
body = signer_client.DocumentsCancelDocumentRequest() # DocumentsCancelDocumentRequest |  (optional)

try:
    # Cancels the document by providing a reason for the cancellation.
    api_instance.api_documents_id_cancellation_post(id, body=body)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_id_cancellation_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)|  | 
 **body** | [**DocumentsCancelDocumentRequest**](DocumentsCancelDocumentRequest.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_id_content_b64_get**
> DocumentsDocumentContentModel api_documents_id_content_b64_get(id, type=type)

Downloads a specific version type of the document encoding the bytes in Base 64 format.

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | Document id
type = signer_client.DocumentDownloadTypes() # DocumentDownloadTypes | The version type to download (optional)

try:
    # Downloads a specific version type of the document encoding the bytes in Base 64 format.
    api_response = api_instance.api_documents_id_content_b64_get(id, type=type)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_id_content_b64_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)| Document id | 
 **type** | [**DocumentDownloadTypes**](.md)| The version type to download | [optional] 

### Return type

[**DocumentsDocumentContentModel**](DocumentsDocumentContentModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_id_content_get**
> api_documents_id_content_get(id, type=type)

Downloads a specific version type of the document.

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | Document id
type = signer_client.DocumentDownloadTypes() # DocumentDownloadTypes | The version type to download (optional)

try:
    # Downloads a specific version type of the document.
    api_instance.api_documents_id_content_get(id, type=type)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_id_content_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)| Document id | 
 **type** | [**DocumentDownloadTypes**](.md)| The version type to download | [optional] 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_id_delete**
> api_documents_id_delete(id)

Deletes a specific document using it's id.

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | Document id

try:
    # Deletes a specific document using it's id.
    api_instance.api_documents_id_delete(id)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_id_delete: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)| Document id | 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_id_envelope_versions_post**
> api_documents_id_envelope_versions_post(id, body=body)

Adds a new version for an envelope.

The flow of the document will be restarted.

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 
body = signer_client.DocumentsEnvelopeAddVersionRequest() # DocumentsEnvelopeAddVersionRequest |  (optional)

try:
    # Adds a new version for an envelope.
    api_instance.api_documents_id_envelope_versions_post(id, body=body)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_id_envelope_versions_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)|  | 
 **body** | [**DocumentsEnvelopeAddVersionRequest**](DocumentsEnvelopeAddVersionRequest.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_id_flow_post**
> FlowActionsDocumentFlowEditResponse api_documents_id_flow_post(id, body=body)

Updates the document's flow.

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | Id of the document
body = signer_client.DocumentsDocumentFlowEditRequest() # DocumentsDocumentFlowEditRequest |  (optional)

try:
    # Updates the document's flow.
    api_response = api_instance.api_documents_id_flow_post(id, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_id_flow_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)| Id of the document | 
 **body** | [**DocumentsDocumentFlowEditRequest**](DocumentsDocumentFlowEditRequest.md)|  | [optional] 

### Return type

[**FlowActionsDocumentFlowEditResponse**](FlowActionsDocumentFlowEditResponse.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_id_folder_post**
> api_documents_id_folder_post(id, body=body)

Moves a document to a folder.

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 
body = signer_client.DocumentsMoveDocumentRequest() # DocumentsMoveDocumentRequest |  (optional)

try:
    # Moves a document to a folder.
    api_instance.api_documents_id_folder_post(id, body=body)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_id_folder_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)|  | 
 **body** | [**DocumentsMoveDocumentRequest**](DocumentsMoveDocumentRequest.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_id_get**
> DocumentsDocumentModel api_documents_id_get(id)

Retrieves the document's details.

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | Document id

try:
    # Retrieves the document's details.
    api_response = api_instance.api_documents_id_get(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)| Document id | 

### Return type

[**DocumentsDocumentModel**](DocumentsDocumentModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_id_notified_emails_put**
> api_documents_id_notified_emails_put(id, body=body)

Updates the document's notified emails

The notified emails are the ones that will be notified after the document is concluded.

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | Id of the document
body = signer_client.DocumentsDocumentNotifiedEmailsEditRequest() # DocumentsDocumentNotifiedEmailsEditRequest |  (optional)

try:
    # Updates the document's notified emails
    api_instance.api_documents_id_notified_emails_put(id, body=body)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_id_notified_emails_put: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)| Id of the document | 
 **body** | [**DocumentsDocumentNotifiedEmailsEditRequest**](DocumentsDocumentNotifiedEmailsEditRequest.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_id_refusal_post**
> api_documents_id_refusal_post(id, body=body)

Refuses a document by providing a reason for the refusal.

The document's flow will pause and can only be resumed by adding a new version of the document (see <a href=\"#operations-Documents-post_api_documents__id__versions\">Add Version API</a>).

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 
body = signer_client.RefusalRefusalRequest() # RefusalRefusalRequest |  (optional)

try:
    # Refuses a document by providing a reason for the refusal.
    api_instance.api_documents_id_refusal_post(id, body=body)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_id_refusal_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)|  | 
 **body** | [**RefusalRefusalRequest**](RefusalRefusalRequest.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_id_signatures_details_get**
> DocumentsDocumentSignaturesInfoModel api_documents_id_signatures_details_get(id)

Retrieves the details of the document's signatures.

This will perform the same validations as verifying the document signatures using the verification code.

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | The Id of the document

try:
    # Retrieves the details of the document's signatures.
    api_response = api_instance.api_documents_id_signatures_details_get(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_id_signatures_details_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)| The Id of the document | 

### Return type

[**DocumentsDocumentSignaturesInfoModel**](DocumentsDocumentSignaturesInfoModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_id_ticket_get**
> TicketModel api_documents_id_ticket_get(id, type=type, preview=preview)

Generates a URL (ticket) to download a specific version type of the document.

The URL does not require authentication and will be available for 1 hour.    <ul><li><b>Original</b>: the original file provided when the document was created.</li><li><b>OriginalWithMarks</b>: the original file with all marks added (for example when an user approves the document and includes its signature image).</li><li><b>PrinterFriendlyVersion</b>: if the original document is PDF, the version with marks and a appended signature manifest, otherwise a PDF file with the signature manifest.</li><li><b>Signatures</b>: if the original document is PDF, the signed PDF file, otherwise the .p7s file.</li></ul>

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | Document id
type = signer_client.DocumentTicketType() # DocumentTicketType | The version type to download (optional)
preview = false # bool | If true, when downloading the document, the response will not include the name of the file (useful when embedding the document inside a web page for previewing) (optional) (default to false)

try:
    # Generates a URL (ticket) to download a specific version type of the document.
    api_response = api_instance.api_documents_id_ticket_get(id, type=type, preview=preview)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_id_ticket_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)| Document id | 
 **type** | [**DocumentTicketType**](.md)| The version type to download | [optional] 
 **preview** | **bool**| If true, when downloading the document, the response will not include the name of the file (useful when embedding the document inside a web page for previewing) | [optional] [default to false]

### Return type

[**TicketModel**](TicketModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_id_versions_post**
> api_documents_id_versions_post(id, body=body)

Adds a new version for the document.

The flow of the document will be restarted.       If the document was created as an envelope, please use the <a href=\"#operations-Documents-post_api_documents__id__envelope_versions\">Add Envelope Version API</a>

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 
body = signer_client.DocumentsDocumentAddVersionRequest() # DocumentsDocumentAddVersionRequest |  (optional)

try:
    # Adds a new version for the document.
    api_instance.api_documents_id_versions_post(id, body=body)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_id_versions_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | [**str**](.md)|  | 
 **body** | [**DocumentsDocumentAddVersionRequest**](DocumentsDocumentAddVersionRequest.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_keys_key_signatures_get**
> DocumentsDocumentSignaturesInfoModel api_documents_keys_key_signatures_get(key)

Validates each signature in a document using the verification code

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
key = 'key_example' # str | The verification code presented in the document

try:
    # Validates each signature in a document using the verification code
    api_response = api_instance.api_documents_keys_key_signatures_get(key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_keys_key_signatures_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| The verification code presented in the document | 

### Return type

[**DocumentsDocumentSignaturesInfoModel**](DocumentsDocumentSignaturesInfoModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_post**
> list[DocumentsCreateDocumentResult] api_documents_post(body=body)

Creates one or multiple documents.

Before calling this API you need to upload the file(s) using the <a href=\"#operations-Upload-post_api_uploads\">Upload API</a> or the <a href=\"#operations-Upload-post_api_uploads_bytes\">Upload Bytes API</a>.       When creating a big batch of documents, it is recommended to send multiple requests instead of one big request. For instance, if you want to create 100 documents,   send 10 requests of 10 documents. In this case it is recommended to use the disablePendingActionNotifications option and, when all requests are finished, use the   <a href=\"#operations-Notifications-post_api_users_notify_pending\">users/notify-pending API</a> to notify participants.      Returns a list of ids of each document created.

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
body = signer_client.DocumentsCreateDocumentRequest() # DocumentsCreateDocumentRequest |  (optional)

try:
    # Creates one or multiple documents.
    api_response = api_instance.api_documents_post(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**DocumentsCreateDocumentRequest**](DocumentsCreateDocumentRequest.md)|  | [optional] 

### Return type

[**list[DocumentsCreateDocumentResult]**](DocumentsCreateDocumentResult.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_documents_validate_signatures_post**
> list[SignerModel] api_documents_validate_signatures_post(body=body)

Validates each signature in the uploaded document

Before calling this API you need to upload the file using the <a href=\"#operations-Upload-post_api_uploads\">Upload API</a> or the <a href=\"#operations-Upload-post_api_uploads_bytes\">Upload Bytes API</a>.

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
api_instance = signer_client.DocumentsApi(signer_client.ApiClient(configuration))
body = signer_client.SignatureSignaturesInfoRequest() # SignatureSignaturesInfoRequest |  (optional)

try:
    # Validates each signature in the uploaded document
    api_response = api_instance.api_documents_validate_signatures_post(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DocumentsApi->api_documents_validate_signatures_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SignatureSignaturesInfoRequest**](SignatureSignaturesInfoRequest.md)|  | [optional] 

### Return type

[**list[SignerModel]**](SignerModel.md)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: text/plain, application/json, text/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

