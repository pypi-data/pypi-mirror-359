# DocumentFlowsDocumentFlowDetailsModel

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**are_actions_ordered** | **bool** |  | [optional] 
**flow_actions** | [**list[FlowActionsFlowActionCreateModel]**](FlowActionsFlowActionCreateModel.md) | The list of actions (signers and approvers) that will be in the document. | [optional] 
**observers** | [**list[ObserversObserverCreateModel]**](ObserversObserverCreateModel.md) |  | [optional] 
**id** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**creation_date** | **datetime** | The date the flow was created. | [optional] 
**update_date** | **datetime** | The date of the last update to the flow. | [optional] 
**created_by** | [**DocumentsCreatorModel**](DocumentsCreatorModel.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

