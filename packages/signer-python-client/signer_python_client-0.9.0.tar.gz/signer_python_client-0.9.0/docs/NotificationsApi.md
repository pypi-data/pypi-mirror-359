# signer_client.NotificationsApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**api_notifications_flow_action_reminder_post**](NotificationsApi.md#api_notifications_flow_action_reminder_post) | **POST** /api/notifications/flow-action-reminder | Sends a reminder email to the user of a flow action. (if the action is pending)
[**api_users_notify_pending_post**](NotificationsApi.md#api_users_notify_pending_post) | **POST** /api/users/notify-pending | Sends a reminder email to the e-mails provided on request. Should be used after creating a batch of documents.

# **api_notifications_flow_action_reminder_post**
> api_notifications_flow_action_reminder_post(body=body)

Sends a reminder email to the user of a flow action. (if the action is pending)

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
api_instance = signer_client.NotificationsApi(signer_client.ApiClient(configuration))
body = signer_client.NotificationsCreateFlowActionReminderRequest() # NotificationsCreateFlowActionReminderRequest |  (optional)

try:
    # Sends a reminder email to the user of a flow action. (if the action is pending)
    api_instance.api_notifications_flow_action_reminder_post(body=body)
except ApiException as e:
    print("Exception when calling NotificationsApi->api_notifications_flow_action_reminder_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**NotificationsCreateFlowActionReminderRequest**](NotificationsCreateFlowActionReminderRequest.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_users_notify_pending_post**
> api_users_notify_pending_post(body=body)

Sends a reminder email to the e-mails provided on request. Should be used after creating a batch of documents.

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
api_instance = signer_client.NotificationsApi(signer_client.ApiClient(configuration))
body = signer_client.NotificationsEmailListNotificationRequest() # NotificationsEmailListNotificationRequest |  (optional)

try:
    # Sends a reminder email to the e-mails provided on request. Should be used after creating a batch of documents.
    api_instance.api_users_notify_pending_post(body=body)
except ApiException as e:
    print("Exception when calling NotificationsApi->api_users_notify_pending_post: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**NotificationsEmailListNotificationRequest**](NotificationsEmailListNotificationRequest.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

[ApiKey](../README.md#ApiKey)

### HTTP request headers

 - **Content-Type**: application/json-patch+json, application/json, text/json, application/*+json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

