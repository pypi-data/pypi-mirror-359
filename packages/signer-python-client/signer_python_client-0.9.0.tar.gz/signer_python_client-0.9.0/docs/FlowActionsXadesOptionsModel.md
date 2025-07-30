# FlowActionsXadesOptionsModel

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**signature_type** | [**XadesSignatureTypes**](XadesSignatureTypes.md) |  | [optional] 
**element_to_sign_identifier_type** | [**XadesElementIdentifierTypes**](XadesElementIdentifierTypes.md) |  | [optional] 
**element_to_sign_identifier** | **str** | A string used to identify the element that should be signed.  If the Lacuna.Signer.Api.FlowActions.XadesOptionsModel.ElementToSignIdentifierType is Lacuna.Signer.Api.XadesElementIdentifierTypes.Id, this string is the Id of the element to be signed.  If the Lacuna.Signer.Api.FlowActions.XadesOptionsModel.ElementToSignIdentifierType is Lacuna.Signer.Api.XadesElementIdentifierTypes.XPath, this string is the XPath to the element to be signed. | [optional] 
**insertion_option** | [**XadesInsertionOptions**](XadesInsertionOptions.md) |  | [optional] 
**disable_x_path_transformation** | **bool** | By default the XPath transformation is applied in all XAdES signatures. You can set a flow action to not apply the transformation by setting this option to true.  WARNING: If you disable the XPath transformation the signatures might be considered invalid in some validators if the same XML element is signed multiple times. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

