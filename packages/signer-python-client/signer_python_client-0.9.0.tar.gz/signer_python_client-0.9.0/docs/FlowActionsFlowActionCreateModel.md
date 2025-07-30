# FlowActionsFlowActionCreateModel

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user** | [**UsersParticipantUserModel**](UsersParticipantUserModel.md) |  | [optional] 
**sign_rule_users** | [**list[UsersParticipantUserModel]**](UsersParticipantUserModel.md) |  | [optional] 
**type** | [**FlowActionType**](FlowActionType.md) |  | [optional] 
**step** | **int** | The order in which this action should take place. | [optional] 
**number_required_signatures** | **int** | Number of required signatures (if type is SignRule) | [optional] 
**rule_name** | **str** | Name of the rule (if type is SignRule) | [optional] 
**allow_rule_flow_to_continue_if_refused** | **bool** | If true and the action is a Sign Rule, allows the document flow to continue while there are enough users that can fulfill the rule. | [optional] 
**title** | **str** | Title of the participant | [optional] 
**pre_positioned_marks** | [**list[DocumentMarkPrePositionedDocumentMarkModel]**](DocumentMarkPrePositionedDocumentMarkModel.md) |  | [optional] 
**allow_electronic_signature** | **bool** | Set to true if the electronic signature option should be available. (only if the type of the action is Signer or SignRule) | [optional] 
**require_sms_authentication_to_sign_electronically** | **bool** | Requires the user to confirm a code sent to his phone to sign electronically. (If AllowElectronicSignature is true) | [optional] 
**require_whatsapp_authentication_to_sign_electronically** | **bool** | Requires the user to confirm a code sent to his Whatsapp number to sign electronically. (If AllowElectronicSignature is true) | [optional] 
**require_authenticator_app_to_sign_electronically** | **bool** | Requires the user to enter a one-time password (OTP) to sign electronically. (If AllowElectronicSignature is true) | [optional] 
**require_selfie_authentication_to_sign_electronically** | **bool** | Requires the user to take a selfie to sign electronically. (If AllowElectronicSignature is true) | [optional] 
**require_datavalid_authentication_to_sign_electronically** | **bool** | Requires the user to take a selfie to sign electronically. This selfie will be validated by SERPRO&#x27;s Datavalid. (If AllowElectronicSignature is true) | [optional] 
**require_pix_authentication_to_sign_electronically** | **bool** | Requires the user to pay a Pix to sign electronically. (If AllowElectronicSignature is true) | [optional] 
**require_liveness_authentication_to_sign_electronically** | **bool** | Requires the user to perform a liveness test to sign electronically. (If AllowElectronicSignature is true) | [optional] 
**require_id_scan_authentication_to_sign_electronically** | **bool** | Requires the user to perform a photo id scan to sign electronically. (If AllowElectronicSignature is true) | [optional] 
**disable_email_authentication_to_sign_electronically** | **bool** | Disables e-mail authentication to sign electronically. This option can only be used if SMS or Whatsapp authentication was required. (If AllowElectronicSignature is true) | [optional] 
**required_certificate_type_to_sign** | [**CertificateTypes**](CertificateTypes.md) |  | [optional] 
**require_company_certificate** | **bool** | [DEPRECATED] Requires the user to sign the document with a company certificate (e.g. e-CNPJ). Please use RequiredCertificateHolderTypeToSign instead. | [optional] 
**required_company_identifier** | **str** | Requires the user to sign the document with a company certificate (e.g. e-CNPJ) that has the provided company identifier. | [optional] 
**required_certificate_holder_type_to_sign** | [**CertificateHolderTypes**](CertificateHolderTypes.md) |  | [optional] 
**xades_options** | [**FlowActionsXadesOptionsModel**](FlowActionsXadesOptionsModel.md) |  | [optional] 
**signature_initials_mode** | [**SignatureInitialsModes**](SignatureInitialsModes.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

