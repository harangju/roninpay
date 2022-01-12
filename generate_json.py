import os
import sys
import json
import numpy as np
import pandas as pd
import xlwings as xw

max_payments = 1000

file = 'payments.xlsx'
try:
    wb = xw.Book(file)
except:
    print(f"Cannot open file '{file}'.")
    sys.exit(-1)
sheet = wb.sheets['Sheet1']
df = sheet[f"A2:J{max_payments}"].options(pd.DataFrame, index=False, header=True).value

payments = []
for i, row in df.iterrows():
    if row['from ronin address']=='' or pd.isnull(row['from ronin address']) or\
        row['private key']=='' or pd.isnull(row['private key']) or\
        row['to ronin address']=='' or pd.isnull(row['to ronin address']):
        continue
    payments.append({
        'Name': row['name'],
        'From': row['from ronin address'],
        'PrivateKey': row['private key'],
        'To': row['to ronin address'],
        'Amount': row['amount']
    })

with open('slp-payment-config.json', 'w') as f:
    json.dump(payments, f, indent=2)
