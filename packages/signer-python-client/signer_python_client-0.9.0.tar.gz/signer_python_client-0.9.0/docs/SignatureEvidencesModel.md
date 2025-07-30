# SignatureEvidencesModel

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ip_address** | **str** |  | [optional] 
**authentication_types** | [**list[AuthenticationTypes]**](AuthenticationTypes.md) | A list containing the the authentication types used when signing the document. | [optional] 
**account_verified_email** | **str** | If the user was logged-in when he signed the document this is the verified email of his account.  If Lacuna.Signer.Api.Signature.EvidencesModel.AuthenticationTypes doesn&#x27;t contains Lacuna.Signer.Api.AuthenticationTypes.Login this will be null. | [optional] 
**authenticated_email** | **str** | The email to which the notification to sign the document was sent.  If Lacuna.Signer.Api.Signature.EvidencesModel.AuthenticationTypes doesn&#x27;t contains Lacuna.Signer.Api.AuthenticationTypes.Email this will be null. | [optional] 
**authenticated_phone_number_last_digits** | **str** | The last four digits of the phone number to which the SMS confirmation code was sent.  If Lacuna.Signer.Api.Signature.EvidencesModel.AuthenticationTypes doesn&#x27;t contains Lacuna.Signer.Api.AuthenticationTypes.SMS this will be null. | [optional] 
**authenticated_application** | [**ApplicationsApplicationDisplayModel**](ApplicationsApplicationDisplayModel.md) |  | [optional] 
**authenticated_selfie** | [**SignatureSelfieModel**](SignatureSelfieModel.md) |  | [optional] 
**authenticated_pix** | [**SignaturePixAuthenticationModel**](SignaturePixAuthenticationModel.md) |  | [optional] 
**liveness_data** | [**SignatureLiveness3dAuthenticationModel**](SignatureLiveness3dAuthenticationModel.md) |  | [optional] 
**geolocation** | [**SignatureGeolocationModel**](SignatureGeolocationModel.md) |  | [optional] 
**timestamp** | **datetime** |  | [optional] 
**evidences_sha256** | **str** | SHA-256 Hash (Base64 encoded) of the evidences JSON file | [optional] 
**authenticated_phone_number** | **str** | The phone number to which the SMS confirmation code was sent.  If Lacuna.Signer.Api.Signature.EvidencesModel.AuthenticationTypes doesn&#x27;t contains Lacuna.Signer.Api.AuthenticationTypes.SMS this will be null. | [optional] 
**file** | **str** | The evidences JSON file in bytes. | [optional] 
**file_ticket** | **str** | Ticket to download the evidences JSON file. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

