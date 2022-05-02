import re
from datetime import timedelta, datetime
import bs4
import pandas as pd
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Stock_price
from app.config import BaseConfig

engine=create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

company='PZU'
start_date='2020-01-10'
end_date='2022-03-10'
dt_start_date=datetime.strptime(start_date, '%Y-%m-%d').date()
rsi_length=14
start_date_before=dt_start_date-timedelta(days=rsi_length)

price_df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
price_df_rsi = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])


interval='day'
result = session.query(Stock_price.trade_date, Stock_price.open,
                                                            Stock_price.high, Stock_price.low, Stock_price.close,
                                                            Stock_price.volume).filter(
                Stock_price.name == company, Stock_price.trade_date.between(start_date, end_date)).all()

for column, i in zip(price_df.columns, range(len(result))):
    price_df[column] = [x[i] for x in result]

URL = "https://mrjbq7.github.io/ta-lib/func_groups/momentum_indicators.html"
page = requests.get(URL)
indicators=[]
cols=[]
soup = bs4.BeautifulSoup(page.content, "html.parser")
results = soup.find('div',id="main_content_wrap")
func_elements=results.find_all('pre')
strings_args=['open','high','low','close','volume']
args=[]

def match(input_string, string_list):
    words = re.findall(r'\w+', input_string)
    return [word for word in words if word in string_list]
for func in func_elements:
    res=func.text.strip()
    sentence = re.sub(r"\s+", "", res, flags=re.UNICODE)
    func_name=re.findall(r'=(.*)\(',sentence,re.M)
    args_all=re.search(r'\((.*?)\)',sentence).group(1)
    args_list=args_all.split(',')

    arg=[x for x in args_list if x in strings_args]
    args.append(arg)
    col=sentence.split('=')
    col_name=col[0].split(',')
    cols.append(col_name)

    indicators.append(func_name[0])

list_of_dicts=[]
col_func=[]
for i in range(len(indicators)):
    col_f=[]
    for j in range(len(cols[i])):
        col_name=str(indicators[i])+'-'+str(cols[i][j])
        col_f.append(col_name)
    col_func.append(col_f)

for name,col,arg in zip(indicators,col_func,args):
    ind_dict={}
    ind_dict['name']=name
    ind_dict['cols']=col
    ind_dict['arg']=arg
    dict_to_append=ind_dict.copy()
    list_of_dicts.append(dict_to_append)


result_dict={}

cols_calc=[]
to_calc_all=[]
to_calc_2=[]
indicators_ta=[]
for name in indicators:

    name='ta.'+name
    indicators_ta.append(name)



for dict in list_of_dicts:
    to_calc=[]


    for i in range(len(dict['arg'])):


        price=price_df[dict['arg'][i].capitalize()]
        to_calc.append(price)
    for i in range(len(dict['cols'])):
        if len(dict['cols'])==1:
            price_df[dict['cols'][i]]=locals()[dict['name']](*to_calc)
        else:
            price_df[dict['cols'][i]] = locals()[dict['name']](*to_calc)[i]

    to_calc_all.append(to_calc)






indicators_df=price_df.copy()
indicators_df.drop(indicators_df.iloc[:,0:6],inplace=True, axis=1)

nan_count_dict={}
for col in indicators_df.columns:
    nan_count=indicators_df[col].isna().sum()
    f=str(col).split('-')[0]

    if f in indicators:

        nan_count_dict[f]=nan_count

cols_df=[]
for i in range(len(cols)):
    col_to_add=[]
    if 'real' in cols[i]:
        c=str(indicators[i]).lower()
        col_to_add.append(c)
    else:
        for j in range(len(cols[i])):
            col_to_add.append(cols[i][j])
    cols_df.append(col_to_add)

func_dict=dict.fromkeys(indicators)

nest_val=['name','cols','period','args']
list_to_convert=list(map(list,zip(indicators,cols_df,args,list(nan_count_dict.values()))))

for i in range(len(indicators)):
    nest_dict=dict.fromkeys(nest_val)
    nest_dict['name']=list_to_convert[i][0]
    nest_dict['cols'] = list_to_convert[i][1]
    nest_dict['args'] = list_to_convert[i][2]
    nest_dict['period'] = list_to_convert[i][3]
    func_dict[indicators[i]]=nest_dict

print(func_dict)

#with open("func_dict.json", "w") as outfile:
    #json.dump(func_dict, outfile, cls=NumpyEncoder)




def get_df_name(df):
    name =[x for x in globals() if globals()[x] is df][0]
    return name
