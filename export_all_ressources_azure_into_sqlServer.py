import pyodbc
import requests

# Define the database connection details
server = 'serverdb1010.database.windows.net'
database = 'db'
username = 'useradmin'
password = 'motdep@sse2023'

# Connect to the database
conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
conn = pyodbc.connect(conn_str)

# Check if the table exists
table_name = 't_azure_pricing'
table_exists = False
cursor = conn.cursor()
cursor.execute(f"SELECT COUNT(*) FROM sys.tables WHERE name = '{table_name}'")
if cursor.fetchone()[0] == 1:
    table_exists = True

# Create the table if it doesn't exist
if not table_exists:
    # Define the SQL script to create the table
    sql_script = '''
    CREATE TABLE t_azure_pricing (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        SKU VARCHAR(255),
        RetailPrice FLOAT,
        Currency VARCHAR(255),
        UnitOfMeasure VARCHAR(255),
        Region VARCHAR(255),
        Meter VARCHAR(255),
        ProductName VARCHAR(255),
        ServiceName VARCHAR(255),
        ServiceFamily VARCHAR(255)
    )
    '''
    
    # Execute the SQL script
    cursor.execute(sql_script)
    conn.commit()
    print(f"Table '{table_name}' created successfully.")
else:
    print(f"Table '{table_name}' already exists.")

# Retrieve pricing data from Azure Pricing API
api_url = "https://prices.azure.com/api/retail/prices?currencyCode='EUR'&api-version=2021-10-01-preview"
skip = 0
while True:
    response = requests.get(f"{api_url}&$skip={skip}")
    data = response.json()
    values = []
    for item in data['Items']:
        sku = item['armSkuName']
        price = float(item['retailPrice'])
        currency = item['currencyCode']
        uom = item['unitOfMeasure']
        region = item['location']
        meter = item['meterId']
        product_name = item['productName']
        service_name = item['serviceName']
        service_family = item['serviceFamily']
        values.append((sku, price, currency, uom, region, meter, product_name, service_name, service_family))
    if not values:
        break
    insert_query = "INSERT INTO t_azure_pricing (SKU, RetailPrice, Currency, UnitOfMeasure, Region, Meter, ProductName, ServiceName, ServiceFamily) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    cursor.executemany(insert_query, values)
    conn.commit()
    print(f"{cursor.rowcount} row(s) inserted successfully.")
    skip += 100

# Close the database connection
conn.close()
