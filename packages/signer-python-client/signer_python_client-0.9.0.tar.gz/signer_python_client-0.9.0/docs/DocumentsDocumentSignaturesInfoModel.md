# DocumentsDocumentSignaturesInfoModel

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**filename** | **str** |  | [optional] 
**mime_type** | **str** |  | [optional] 
**created_by** | [**DocumentsCreatorModel**](DocumentsCreatorModel.md) |  | [optional] 
**is_concluded** | **bool** | True if all actions requested in the document are concluded. | [optional] 
**is_file** | **bool** |  | [optional] 
**is_envelope** | **bool** |  | [optional] 
**creation_date** | **datetime** |  | [optional] 
**update_date** | **datetime** |  | [optional] 
**signers** | [**list[SignerModel]**](SignerModel.md) | List of who signed the document.  Each element in the list contains a validation result. | [optional] 
**status** | [**DocumentStatus**](DocumentStatus.md) |  | [optional] 
**type** | [**DocumentTypes**](DocumentTypes.md) |  | [optional] 
**signature_type** | [**SignatureTypes**](SignatureTypes.md) |  | [optional] 
**security_context** | [**SecurityContextsSecurityContextSimpleModel**](SecurityContextsSecurityContextSimpleModel.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

