#!/usr/bin/env python3
import requests
import json
import pandas as pd

def build_pricing_table(json_data, table_data):
    for item in json_data['Items']:
        meter = item['meterName']
        if 'productFamily' in item:
            product_family = item['productFamily']
        else:
            product_family = ''
        if 'productName' in item:
            product_name = item['productName']
        else:
            product_name = ''
        if 'serviceName' in item:
            service_name = item['serviceName']
        else:
            service_name = ''
        table_data.append([
            item['armSkuName'], 
            item['skuName'], 
            item['retailPrice'], 
            item['currencyCode'],
            item['unitOfMeasure'], 
            item['armRegionName'],
            item['tierMinimumUnits'],
            meter,
            product_family,
            product_name,
            service_name,
            item['unitPrice'],
            item['serviceName'],
            item['type'],
            item['serviceFamily']
        ])
        
def main():
    table_data = []
    table_data.append([
        'armSkuName',
        'skuName',
        'retailPrice',
        'currencyCode',
        'unitOfMeasure',
        'armRegionName', 
        'tierMinimumUnits',
        'Meter name',
        'Product Family',
        'Product Name', 
        'Service Name',
        'unitPrice',
        'serviceName',
        'type',
        'serviceFamily'
    ])
    
    api_url = "https://prices.azure.com/api/retail/prices?currencyCode='EUR'&api-version=2021-10-01-preview"
    query = "armRegionName eq 'northeurope' and priceType eq 'Consumption'"
    response = requests.get(api_url, params={'$filter': query})
    json_data = json.loads(response.text)
    
    build_pricing_table(json_data, table_data)
    nextPage = json_data['NextPageLink']
    
    while(nextPage):
        response = requests.get(nextPage)
        json_data = json.loads(response.text)
        nextPage = json_data['NextPageLink']
        build_pricing_table(json_data, table_data)

    df = pd.DataFrame(table_data[1:], columns=table_data[0])
    df.to_excel('AzurePrices.xlsx', index=False)
    print("Result saved to all_vms_and_storage_pricing.xlsx")
    
if __name__ == "__main__":
    main()


