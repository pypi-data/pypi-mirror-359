# DocumentsCreateDocumentRequest

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**files** | [**list[FileUploadModel]**](FileUploadModel.md) | The files to submit. Each file will create a document. | 
**attachments** | [**list[AttachmentsAttachmentUploadModel]**](AttachmentsAttachmentUploadModel.md) | The attachments to submit. Each document will have the same attachments. | [optional] 
**xml_namespaces** | [**list[XmlNamespaceModel]**](XmlNamespaceModel.md) | Optional parameter for XML documents. This namespace will be used by all files in Lacuna.Signer.Api.Documents.CreateDocumentRequest.Files. | [optional] 
**is_envelope** | **bool** | If true, groups all files into a single document (the envelope). All files must be in PDF format. | [optional] 
**envelope_name** | **str** | The name of the document if the envelope option is enabled (see \&quot;IsEnvelope\&quot; property). | [optional] 
**participants_data_file** | [**UploadModel**](UploadModel.md) |  | [optional] 
**template_field_values** | **dict(str, str)** |  | [optional] 
**folder_id** | **str** | The id of the folder in which the document should be placed or null if it should not be placed in any specific folder. | [optional] 
**description** | **str** | A description to be added to the document(s). This will be presented to all participants in the document details screen and   in pending action notifications. | [optional] 
**flow_actions** | [**list[FlowActionsFlowActionCreateModel]**](FlowActionsFlowActionCreateModel.md) | The list of actions (signers and approvers) that will be in the document. | 
**observers** | [**list[ObserversObserverCreateModel]**](ObserversObserverCreateModel.md) |  | [optional] 
**disable_pending_action_notifications** | **bool** | If true the notifications of pending actions won&#x27;t be sent to the participants of the first step. | [optional] 
**disable_notifications** | **bool** | If true, no notifications will be sent to participants of this document. | [optional] 
**new_folder_name** | **str** | The name of a new folder to be created and associated to the document. If you do not wish to create a new folder you may set this as null. | [optional] 
**force_cades_signature** | **bool** | If this property is set to true, then the document will be signed using the CAdES format. | [optional] 
**notified_emails** | **list[str]** | The emails to notify when the document is concluded. | [optional] 
**additional_info** | [**DocumentsDocumentAdditionalInfoData**](DocumentsDocumentAdditionalInfoData.md) |  | [optional] 
**tags** | [**list[DocumentsDocumentTagData]**](DocumentsDocumentTagData.md) |  | [optional] 
**signature_type** | [**SignatureTypes**](SignatureTypes.md) |  | [optional] 
**security_context_id** | **str** |  | [optional] 
**template_id** | **str** |  | [optional] 
**expiration_date** | **datetime** | The expiration date of the document. Any time information will be discarded, as the expiration will be set   to the last time available for the chosen date in the default timezone. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

