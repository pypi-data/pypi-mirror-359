# FlowActionsFlowActionEditModel

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**flow_action_id** | **str** | The Id of the flow action being modified. | [optional] 
**step** | **int** | The new step of the action.  This must be greater or equal to the current pending step. | [optional] 
**participant_email_address** | **str** | The new email address of the action&#x27;s participant (if the type is Lacuna.Signer.Api.FlowActionType.Signer or Lacuna.Signer.Api.FlowActionType.Approver). | [optional] 
**rule_name** | **str** | The new rule name (if the type is Lacuna.Signer.Api.FlowActionType.SignRule). | [optional] 
**sign_rule_users** | [**list[FlowActionsSignRuleUserEditModel]**](FlowActionsSignRuleUserEditModel.md) | The rule users to be edited (if the type is Lacuna.Signer.Api.FlowActionType.SignRule). | [optional] 
**title** | **str** |  | [optional] 
**pre_positioned_marks** | [**list[DocumentMarkPrePositionedDocumentMarkModel]**](DocumentMarkPrePositionedDocumentMarkModel.md) |  | [optional] 
**signature_initials_mode** | [**SignatureInitialsModes**](SignatureInitialsModes.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

