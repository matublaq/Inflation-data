#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openpyxl
#--- Web scriping ---
import requests
from bs4 import BeautifulSoup
#--- ------------ ---
from datetime import datetime, date, timedelta
#from googletrans import Translator 


# # <font style="font-size: 80px"><font color="yellow">C</font><font style="color: whitesmoke">onsume </font><font color="yellow">P</font><font style="color: whitesmoke">roduct </font><font color="yellow">I</font><font style="color: whitesmoke">ndex </font>(<font color="yellow">CPI</font>)</font>

# ### Getting data

# In[2]:


url = 'https://thedocs.worldbank.org/en/doc/1ad246272dbbc437c74323719506aa0c-0350012021/original/Inflation-data.xlsx'
local_path = '../../CSV crudo/InflationWorldData.xlsx'

response = requests.get(url)

if(response.status_code == 200):
    with open(local_path, 'wb') as file:
        file.write(response.content)
    print(f'Download success, status code {response.status_code}')
else:
    print(f'Download Error, status code {response.status_code}')


# In[3]:


#Inflation = pd.read_excel("../..//CSV crudo/InflationWorld.xlsx")
excel = "../../CSV crudo/InflationWorldData.xlsx"
sheets = openpyxl.load_workbook(excel) #https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG


# In[4]:


print(sheets.sheetnames)


# In[5]:


CPIa = pd.read_excel(excel, sheet_name="hcpi_a")


# ---

# ### <font style="color: yellow">Columns</font>

# In[6]:


CPIa.drop(columns=["Note", "IMF Country Code", "Indicator Type", "Series Name"], inplace=True)
CPIa.rename(columns={"Country Code":"Code"}, inplace=True)
CPIa[["Code", "Country"]] = CPIa[["Country", "Code"]]
CPIa.rename(columns={"Code":"Country", "Country":"Code"}, inplace=True) #If the name not exist previously to the function are not changed


# In[7]:


CPIa.columns = CPIa.columns.astype(str)


# In[8]:


len(CPIa["Country"])


# In[9]:


countryCount = {}
for i in CPIa["Country"]:
    if countryCount.get(i):
        countryCount[i] += 1
    else:
        countryCount[i] = 1

country_repeat = {k: v for k, v in countryCount.items() if(v>=2)}
print(country_repeat)


# In[10]:


CPIa.info()


# ---

# ### <font style="color: yellow"> This data-frame have something wrong elements? </font>

# In[11]:


nanCountry = CPIa[CPIa["Country"].isna() == True]
CPIa.drop(index=nanCountry.index, inplace=True)
CPIa.reset_index(inplace=True, drop=True)


# In[12]:


#CPIa.loc[CPIa["Country"] == "Angola", "1970"] = "Hello"
aux = CPIa.iloc[:, 2:]
dataFilter = aux.select_dtypes(exclude=["float"]).any()
dataFilter


# ---

# ### <font style="color: yellow"> Sorting the data </font>

# In[13]:


nanPorcent = {}
noData = []
for i in CPIa["Country"]:
    rowSelected = CPIa[CPIa["Country"] == i]
    if(rowSelected.isna().any().any()):
        nanPorcent[i] = rowSelected.iloc[:, 2:].isna().any().value_counts(normalize=True)[True]
        if(nanPorcent[i] == 1):
            noData.append(int(rowSelected.index.values[0]))
    else:
        nanPorcent[i] = 0.0

print(nanPorcent, "\n", noData)

#--- Del data ---#
for i in range(0, len(noData)):
    del nanPorcent[CPIa.iloc[noData[i]]["Country"]]
CPIa.drop(index=noData, inplace=True)
CPIa.reset_index(inplace=True, drop=True)


# In[14]:


nanPorcent = dict(sorted(nanPorcent.items(), key=lambda items: items[1], reverse=False))
newOrder = [x for x in nanPorcent]
aux_df = pd.DataFrame(columns=CPIa.columns)

for i in newOrder:
    rowSelected = CPIa[CPIa["Country"] == i]
    aux_df = pd.concat([aux_df, rowSelected], ignore_index=True)

aux_df = aux_df.round(2)
CPIa =  aux_df
CPIa


# ---

# # <font>Argentina compare between <font style="color: yellow">worlddata.info</font> and <font style="color: yellow">data.worldbank.org</font></font>

# In[15]:


argentinaInf1 = CPIa[CPIa["Country"] == "Argentina"]

#************ WEB scriping ************#
url = "https://www.datosmundial.com/america/argentina/inflacion.php" # English: "https://www.worlddata.info/america/argentina/inflation-rates.php" Spanish: "https://www.datosmundial.com/america/argentina/inflacion.php"
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')


# In[16]:


tr_items = soup.find_all('div', class_="tablescroller")[0].find_all('td')
print(tr_items)


# In[17]:


Argentina_data = {}

argYear = 1
argData = 2
yearActual = ""
for i in tr_items:
    argYear -= 1
    argData -= 1
    
    if(argYear == 0):
        Argentina_data[i.text] = 1
        yearActual = i.text    
        argYear = 5

    if(argData == 0):
        Argentina_data[yearActual] = i.text
        argData = 5
    
    else:
        pass

print(Argentina_data)


# In[18]:


for k, v in Argentina_data.items():
    Argentina_data[k] = float(v.split("%")[0].replace(".", "").replace(",", ".").strip()) #How to chage "2.313,96 and 3079.81"

print(Argentina_data)


# In[19]:


argWD = pd.DataFrame([Argentina_data])


# In[20]:


argWD["Code"] = "ARG"
argWD["Country"] = "Argentina"
print(argWD)
invert_columns = argWD.columns[: :-1] # sorted(newRow.columns, reverse=True)
newRow = argWD.reindex(columns = invert_columns)
newRow


# In[21]:


for counted, year in zip(range(1980, 2022), argWD.iloc[:, 2:]):
    if(counted == int(year)):
        pass
    else:
        print(counted, " nan")
        break


# In[22]:


newColumnName = '2015'
newColumnData = (argWD.loc[:, '2014'].values[0] + argWD.loc[:, '2016'].values[0])/2 #New column will have a avarage between 2014 and 2016
newColumnPosition = argWD.columns.get_loc('2014') + 1

print(newColumnName, newColumnData, newColumnPosition)


# In[23]:


argWD.insert(newColumnPosition, newColumnName, newColumnData)
argWD


# <font style="font-size: 50px; color: yellow">Comparation</font>

# In[24]:


argWB = CPIa[CPIa['Country'] == "Argentina"]
argWB = argWB.iloc[:, :2].join(argWB.iloc[:, 12:])

Argentinas = pd.concat([argWB, argWD], ignore_index=True)
Argentinas["Country"][0] = "ArgentinaWB"
Argentinas["Country"][1] = "ArgentinaWD"
Argentinas


# In[25]:


#ArgentinasTransposed = Argentinas.set_index('Country').T
#ArgentinasTransposed


# ## Graphic

# In[26]:


#ArgentinasTransposed = Argentinas.set_index('')


# In[27]:


plt.figure(figsize=(25, 8))

plt.plot(Argentinas.iloc[:, 2:].columns, Argentinas.iloc[:, 2:].values[0])
plt.plot()

plt.xlabel("Years")
plt.ylabel("Inflation")
plt.ylim(bottom=-10, top=200)

plt.title("Argentina Inflation")

plt.show()

print(Argentinas.loc[:, '1982': '1986'], '\n')
print(Argentinas.loc[:, '1987'], '\n')
print(Argentinas.loc[:, '1988': '1991'])


# In[28]:


plt.figure(figsize=(25, 6))

plt.bar(Argentinas.iloc[:, 2:].columns, Argentinas.iloc[:, 2:].values[0])

plt.xlabel("Years")
plt.ylabel("Inflation")
plt.ylim(bottom=-10, top=200)

plt.title("Argentina inflation")

plt.show()


# ---

# <font style="color: green; font-size: 35px">Save changes</font>

# In[29]:


CPIa.to_csv("Inflation.csv")


# In[30]:


CPIa

