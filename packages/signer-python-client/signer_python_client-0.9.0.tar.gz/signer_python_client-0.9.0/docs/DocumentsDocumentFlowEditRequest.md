# DocumentsDocumentFlowEditRequest

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**added_flow_actions** | [**list[FlowActionsFlowActionCreateModel]**](FlowActionsFlowActionCreateModel.md) | The actions to be added to the flow.  The FlowActionCreateModel.Step must be greater or equal to the current pending step. | [optional] 
**edited_flow_actions** | [**list[FlowActionsFlowActionEditModel]**](FlowActionsFlowActionEditModel.md) | The existing actions to be modified.  Flow actions that have already been completed or are partially completed cannot be edited. | [optional] 
**deleted_flow_action_ids** | **list[str]** | The Ids of flow actions to be deleted.  Flow actions that have already been completed or are partially completed cannot be deleted. | [optional] 
**added_observers** | [**list[ObserversObserverCreateModel]**](ObserversObserverCreateModel.md) | The observers to be added to the document. | [optional] 
**edited_observers** | [**list[ObserversObserverEditModel]**](ObserversObserverEditModel.md) | The existing observers to be modified. | [optional] 
**deleted_observer_ids** | **list[str]** | The Ids of observers to be deleted. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

