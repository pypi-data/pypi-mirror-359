# SignerModel

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**subject_name** | **str** |  | [optional] 
**email_address** | **str** |  | [optional] 
**issuer_name** | **str** |  | [optional] 
**identifier** | **str** |  | [optional] 
**company_name** | **str** |  | [optional] 
**company_identifier** | **str** |  | [optional] 
**is_electronic** | **bool** |  | [optional] 
**is_timestamp** | **bool** |  | [optional] 
**signing_time** | **datetime** |  | [optional] 
**certificate_thumbprint** | **str** |  | [optional] 
**evidences** | [**SignatureEvidencesModel**](SignatureEvidencesModel.md) |  | [optional] 
**attribute_certificates** | [**list[CertificatesAttributeCertificateInfoModel]**](CertificatesAttributeCertificateInfoModel.md) |  | [optional] 
**validation_results** | [**ValidationResultsModel**](ValidationResultsModel.md) |  | [optional] 
**validity_start** | **datetime** |  | [optional] 
**validity_end** | **datetime** |  | [optional] 
**signature_timestamps** | [**list[TimestampModel]**](TimestampModel.md) |  | [optional] 
**archive_timestamps** | [**list[TimestampModel]**](TimestampModel.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

