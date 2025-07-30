# TransactionsTransactionPriceModel

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**transaction_type** | [**TransactionTypes**](TransactionTypes.md) |  | 
**pricing_type** | [**TransactionPricingTypes**](TransactionPricingTypes.md) |  | 
**price** | **float** | Price of the transaction type (if Lacuna.Signer.Api.Transactions.TransactionPriceModel.PricingType is Lacuna.Signer.Api.TransactionPricingTypes.Simple) | [optional] 
**price_ranges** | [**list[TransactionsPriceRangeModel]**](TransactionsPriceRangeModel.md) | Price ranges of transaction type (if Lacuna.Signer.Api.Transactions.TransactionPriceModel.PricingType is Lacuna.Signer.Api.TransactionPricingTypes.Range) | [optional] 
**limit** | **int** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

