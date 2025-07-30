# DocumentsDocumentModel

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**checksum_md5** | **str** | MD5 checksum of the document&#x27;s file. | [optional] 
**is_deleted** | **bool** | True if the document is deleted. | [optional] 
**flow_actions** | [**list[FlowActionsFlowActionModel]**](FlowActionsFlowActionModel.md) | Signers and approvers of the document. | [optional] 
**observers** | [**list[ObserversObserverModel]**](ObserversObserverModel.md) | Observers of the document. | [optional] 
**attachments** | [**list[AttachmentsAttachmentModel]**](AttachmentsAttachmentModel.md) | Document attachments | [optional] 
**permissions** | [**DocumentsDocumentPermissionsModel**](DocumentsDocumentPermissionsModel.md) |  | [optional] 
**notified_emails** | **list[str]** |  | [optional] 
**key** | **str** |  | [optional] 
**hide_download_option_for_pending_documents** | **bool** |  | [optional] 
**id** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**filename** | **str** | The document&#x27;s file name. | [optional] 
**file_size** | **int** | The document&#x27;s file size in bytes. | [optional] 
**mime_type** | **str** | The document&#x27;s file mime type. | [optional] 
**has_signature** | **bool** | True if the document was already signed once. | [optional] 
**status** | [**DocumentStatus**](DocumentStatus.md) |  | [optional] 
**is_concluded** | **bool** | [DEPRECATED] True if all actions requested in the document are concluded. Please use Lacuna.Signer.Api.Documents.DocumentInfoModel.Status instead. | [optional] 
**folder** | [**FoldersFolderInfoModel**](FoldersFolderInfoModel.md) |  | [optional] 
**organization** | [**OrganizationsOrganizationInfoModel**](OrganizationsOrganizationInfoModel.md) |  | [optional] 
**creation_date** | **datetime** | The date the document was created. | [optional] 
**update_date** | **datetime** | The date of the last update to the document. This includes the following actions: moving to folder, signing, approving, deleting and editing the flow. | [optional] 
**expiration_date** | **datetime** | The expiration date of the document in the default timezone. | [optional] 
**expiration_date_without_time** | **str** | The expiration date without time: in yyyy-MM-dd format (useful for display purposes). | [optional] 
**created_by** | [**DocumentsCreatorModel**](DocumentsCreatorModel.md) |  | [optional] 
**description** | **str** |  | [optional] 
**force_cades_signature** | **bool** |  | [optional] 
**is_scanned** | **bool** | True if the document source was a scanning process. | [optional] 
**is_envelope** | **bool** | True if the document is an envelope (Lacuna.Signer.Api.Documents.CreateDocumentRequest.IsEnvelope). | [optional] 
**status_updated_by** | [**AgentsAgentModel**](AgentsAgentModel.md) |  | [optional] 
**status_update_reason** | **str** | The reason for the status update (see \&quot;StatusUpdatedBy\&quot; property). | [optional] 
**tags** | [**list[DocumentsDocumentTagModel]**](DocumentsDocumentTagModel.md) |  | [optional] 
**signature_type** | [**SignatureTypes**](SignatureTypes.md) |  | [optional] 
**security_context** | [**SecurityContextsSecurityContextSimpleModel**](SecurityContextsSecurityContextSimpleModel.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

