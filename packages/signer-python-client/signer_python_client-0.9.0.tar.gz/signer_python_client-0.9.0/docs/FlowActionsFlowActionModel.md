# FlowActionsFlowActionModel

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**creation_date** | **datetime** |  | [optional] 
**pending_date** | **datetime** |  | [optional] 
**update_date** | **datetime** |  | [optional] 
**user** | [**UsersParticipantUserModel**](UsersParticipantUserModel.md) |  | [optional] 
**number_required_signatures** | **int** | Number of required signatures if type is SignRule | [optional] 
**sign_rule_users** | [**list[FlowActionsSignRuleUserModel]**](FlowActionsSignRuleUserModel.md) | Users that are allowed to sign if type is SignRule | [optional] 
**marks** | [**list[DocumentMarkDocumentMarkPositionModel]**](DocumentMarkDocumentMarkPositionModel.md) |  | [optional] 
**allow_electronic_signature** | **bool** | True if the electronic signature option is available for this action (only if the type of the action is Signer or SignRule) | [optional] 
**require_email_authentication_to_sign_electronically** | **bool** | Requires the user to confirm a code sent to his e-mail to sign electronically. (If Lacuna.Signer.Api.FlowActions.FlowActionModel.AllowElectronicSignature is true)  This requirement is not enforced if the user is logged in or was authenticated by an application (embedded signature mode). | [optional] 
**require_sms_authentication_to_sign_electronically** | **bool** | Requires the user to confirm a code sent to his phone to sign electronically. (If Lacuna.Signer.Api.FlowActions.FlowActionModel.AllowElectronicSignature is true) | [optional] 
**require_whatsapp_authentication_to_sign_electronically** | **bool** | Requires the user to confirm a code sent to his Whatsapp number to sign electronically. (If Lacuna.Signer.Api.FlowActions.FlowActionModel.AllowElectronicSignature is true) | [optional] 
**require_authenticator_app_to_sign_electronically** | **bool** | Requires the user to enter a one-time password (OTP) to sign electronically. (If Lacuna.Signer.Api.FlowActions.FlowActionModel.AllowElectronicSignature is true) | [optional] 
**require_selfie_authentication_to_sign_electronically** | **bool** | Requires the user to take a selfie to sign electronically. (If Lacuna.Signer.Api.FlowActions.FlowActionModel.AllowElectronicSignature is true) | [optional] 
**require_datavalid_authentication_to_sign_electronically** | **bool** | Requires the user to take a selfie to sign electronically. This selfie will be validated by SERPRO&#x27;s Datavalid. (If Lacuna.Signer.Api.FlowActions.FlowActionModel.AllowElectronicSignature is true) | [optional] 
**require_pix_authentication_to_sign_electronically** | **bool** | Requires the user to pay a Pix to sign electronically. The payer&#x27;s CPF must be the same as that of the user who will be signing. (If Lacuna.Signer.Api.FlowActions.FlowActionModel.AllowElectronicSignature is true) | [optional] 
**require_liveness_authentication_to_sign_electronically** | **bool** | Requires the user to perform a liveness test to sign electronically.  (If Lacuna.Signer.Api.FlowActions.FlowActionModel.AllowElectronicSignature is true) | [optional] 
**require_id_scan_authentication_to_sign_electronically** | **bool** | Requires the user to perform a photo id scan to sign electronically.  (If Lacuna.Signer.Api.FlowActions.FlowActionModel.AllowElectronicSignature is true) | [optional] 
**required_certificate_type_to_sign** | [**CertificateTypes**](CertificateTypes.md) |  | [optional] 
**require_company_certificate** | **bool** | [DEPRECATED] The user is required to sign the document with a company certificate (e.g. e-CNPJ). Please use Lacuna.Signer.Api.FlowActions.FlowActionModel.RequiredCertificateHolderTypeToSign instead. | [optional] 
**required_company_identifier** | **str** | The user is required to sign the document with a company certificate (e.g. e-CNPJ) that has the provided company identifier. | [optional] 
**required_certificate_holder_type_to_sign** | [**CertificateHolderTypes**](CertificateHolderTypes.md) |  | [optional] 
**refusal_reason** | **str** |  | [optional] 
**signature_initials_mode** | [**SignatureInitialsModes**](SignatureInitialsModes.md) |  | [optional] 
**is_electronic** | **bool** |  | [optional] 
**allow_rule_flow_to_continue_if_refused** | **bool** |  | [optional] 
**type** | [**FlowActionType**](FlowActionType.md) |  | [optional] 
**status** | [**ActionStatus**](ActionStatus.md) |  | [optional] 
**step** | **int** |  | [optional] 
**rule_name** | **str** | Name of the rule if type is SignRule | [optional] 
**title** | **str** | Title of the participant | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

