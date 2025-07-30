# DocumentsActionUrlRequest

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**identifier** | **str** | The identifier (CPF in Brazil or Cédula de Identidad in Ecuador/Paraguay) of the participant to whom you want to get the ticket. | [optional] 
**email_address** | **str** | The email of the participant to whom you want to get the ticket. | [optional] 
**require_email_authentication** | **bool** | If action is an electronic signature and this parameter is set to true, requires e-mail authentication with code in order to complete the signature. | [optional] 
**flow_action_id** | **str** | The ID of the flow action for which the ticket will be generated. It should only be provided if there are more than one pending action for the participant. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

