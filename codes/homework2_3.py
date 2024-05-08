import json
import pandas as pd

def save_table(ks,ts,modes,paths,rates_dic):
    tables = {}
    ks_l = [f'k={num}' for num in ks]
    ts_l = [f't={num}' for num in ts]
    for mode in modes:
        table = []
        for k in ks:
            row = []
            for t in ts:
                row.append(rates_dic[(k,t,mode)])
            table.append(row)
        tables[mode] = table
    for mode,path in zip(modes,paths):
        df = pd.DataFrame(tables[mode], columns=ts_l)
        df.index = ks_l
        df.to_excel(path)

if __name__ == '__main__':
    with open('rates.json', 'r') as json_file:
        rates = json.load(json_file)
    rates_dic ={}
    ks = [20,100,500,1000,3000]
    ts = [8,16,24,32]
    modes = ['以“词”为基本单元','以“字”为基本单元']
    paths = ['以“词”为基本单元.xlsx','以“字”为基本单元.xlsx']
    for rate in rates:
        rates_dic[(rate[1],rate[2],rate[3])] = rate[0]
    save_table(ks,ts,modes,paths,rates_dic)