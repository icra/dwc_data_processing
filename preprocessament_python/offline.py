'''
  Join RAIN + LEVEL + TEMPERATURE_OFFLINE files + algoritme

  Columns of the new file:
    * FILE2 -- date
    * FILE2 -- rain mm
    * FILE3 -- RUE11 (mNN)
    * FILE3 -- RUE19/20 (mNN)
    * FILE5 -- temperature id device (i.e. 20641423)
    * FILE5 -- temperature id device (i.e. 10084446)
    * result algorithm detect CSOs
'''
#importa llibreries instal·lades
import datetime
import pandas as pd
import time
import sys
#importa mòduls locals
import interpolacio_fitxer_offline
import algoritme_detectar_csos

#start performance measure
t = time.process_time();

#xlsx filenames loaded and output filename
filenames={
  "rain"   :"RAIN.xlsx",
  "level"  :"LEVEL.xlsx",
  "offline":"TEMPERATURE_OFFLINE.xlsx",
  "output" :"output_file_offline_script.xlsx",
};

#default parameters for CSO detection: (see "Hofer et al 2018" paper)
parameters={
  "delta_T_CSO"   : 0.3, # ºC
  "f_sensor"      : 0.1, # ºC
  "t_delay_start" :   2, # minutes
  "t_delay_end"   :   4, # minutes
  "t_gap"         :  10, # minutes
};

#new file with column names (empty columns)
new_file={
  "date":[],
  "rain (mm)":[],
  "RUE11 (mNN)":[],
  "RUE19/20 (mNN)":[],
  #columns for offline sensors ids are added after the file is read
};

#-utilitats--------------------------------------------------------------------
# converteix un string en format "dd/mm/aaaa hh:MM:ss" a datetime
# retorna una variable tipus "datetime"
def parse_date(string):
  if(type(string)!=str): raise(f"'{string}' is not a string");
  return datetime.datetime.strptime(string,"%d/%m/%Y %H:%M:%S");

# carrega un arxiu .xlsx
# retorna un "dataframe" (df)
def read_excel(path, skiprows):
  df = pd.read_excel(path, skiprows=skiprows);
  return df;

# busca la dada de nivell (FILE3) basat en l'index del dataframe "df"
# aprofita que LEVEL i RAIN tenen el mateix index
def get_level(index, df):
  cols   = df.columns; # noms columnes
  level1 = df.at[index, cols[1]]; # mm
  level2 = df.at[index, cols[2]]; # mm
  return {"level1":level1,"level2":level2};

#append selected variables to new_file
def append_df_to_new_file(df,id_sensor):
  col_date = df.columns[1];
  for i,row in df.iterrows():
    new_file["date"     ].append(row[col_date]); #datetime
    new_file["rain (mm)"].append(None);
    new_file["RUE11 (mNN)"].append(None);
    new_file["RUE19/20 (mNN)"].append(None);
    for ith_id_sensor in ids_sensors:
      new_file[ith_id_sensor].append(row["Value"] if id_sensor==ith_id_sensor else None);

'''Funcions per carregar fitxers concrets'''
#Carrega fitxer RAIN i elimina les files amb zeros (FILE2)
def carrega_fitxer_RAIN_i_elimina_zeros():
  print(f"Llegint fitxer '{filenames['rain']}' (FILE2)...");
  df_rain         = read_excel(filenames["rain"],skiprows=[]);
  column_B        = df_rain.columns[1]; #agafa nom columna B
  filtre          = df_rain[column_B]>0; #només files on pluja>0 (columna B)
  df_rain_filtrat = df_rain[filtre];
  #mostra dataframe carregat
  print(df_rain_filtrat.head(),'\n');
  return df_rain_filtrat;

#Carrega fitxer LEVEL (FILE3)
def carrega_fitxer_LEVEL():
  print(f"Llegint fitxer '{filenames['level']}' (FILE3)...");
  df_level = read_excel(filenames["level"],skiprows=[0,1,2,3,4]);
  print(df_level.head(),'\n');
  return df_level;

#Carrega fitxer TEMPERATURE_OFFLINE (FILE5)
def carrega_fitxer_TEMPERATURE_OFFLINE():
  print(f"Llegint fitxer '{filenames['offline']}' (FILE5)...");
  df_offline = interpolacio_fitxer_offline.carrega(filenames['offline']);
  return df_offline;

#--------------------------------------------------------
df_rain_filtrat = carrega_fitxer_RAIN_i_elimina_zeros(); #DataFrame
df_level        = carrega_fitxer_LEVEL(); #DataFrame
df_offline      = carrega_fitxer_TEMPERATURE_OFFLINE(); #DataFrame

#add id_sensor columns to new_file
ids_sensors = df_offline.columns[1:];
for id_sensor in ids_sensors:
  new_file[id_sensor]=[];

#add df_offline data to new file
cols = df_offline.columns; #noms columnes dades pluja
for i,row in df_offline.iterrows():
  #append new rows to new_file
  new_file["date"          ].append(row[cols[0]]); #datetime
  new_file["rain (mm)"     ].append(None);
  new_file["RUE11 (mNN)"   ].append(None); #valor trobat FILE3
  new_file["RUE19/20 (mNN)"].append(None); #valor trobat FILE3

  #append empty values for each sensor id
  for id_sensor in ids_sensors:
    new_file[id_sensor].append(row[id_sensor]);

#merge rain data and level data to new file
print("Merging RAIN with LEVEL...")
cols = df_rain_filtrat.columns; #noms columnes dades pluja
for i,row in df_rain_filtrat.iterrows():
  date    = row[cols[0]]; #datetime
  mm_rain = row[cols[1]]; #float

  #get variables from FILE3 (LEVEL)
  level = get_level(i, df_level);

  #append new rows to new_file
  new_file["date"          ].append(row[cols[0]]); #datetime
  new_file["rain (mm)"     ].append(row[cols[1]]); #valor pluja
  new_file["RUE11 (mNN)"   ].append(level["level1"]); #valor trobat FILE3
  new_file["RUE19/20 (mNN)"].append(level["level2"]); #valor trobat FILE3

  #append empty values for each sensor id
  for id_sensor in ids_sensors: new_file[id_sensor].append(None);

#detecta episodis CSO amb algoritme Hofer et al 2018
print("Detectant episodis CSO...")
episodis_cso = algoritme_detectar_csos.detecta_episodis(df_offline,parameters);
print(episodis_cso);

#add new column "CSO episode": number of cso episode detected
new_file["CSO episode"]=[];

#afegeix una columna amb el numero d'episodi
def busca_episodi(date, episodis_cso):
  for i in range(len(episodis_cso)):
    ep = episodis_cso[i];
    start = ep["start"]; #datetime
    end   = ep["end"]; #datetime
    if(start <= date and date <= end):
      return i+1;
      break;
  return None

for date in new_file["date"]:
  num_of_episode = busca_episodi(date, episodis_cso);
  new_file["CSO episode"].append(num_of_episode);

'''Crea nou excel i ordena les dades per columna "Date"'''
df = pd.DataFrame(new_file);

print("Ordenant files per data...");
df.sort_values(by=["date"], inplace=True);

print("Creant nou fitxer .xlsx...")
df.to_excel(filenames["output"],index=False);
print(f"Arxiu '{filenames['output']}' creat correctament");

#end performance measure
elapsed_time = time.process_time()-t;
print(f"Elapsed time: {elapsed_time}")

#end
input("[+] Prem Enter per sortir")
