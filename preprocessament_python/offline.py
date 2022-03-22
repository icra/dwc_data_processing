'''
  Join RAIN + TEMPERATURE_OFFLINE files + algoritme

  Columns of the new file:
    * FILE2 -- date
    * FILE2 -- rain mm
    * FILE5 -- temperature id device (i.e. 20641423)
    * FILE5 -- temperature id device (i.e. 10084446)
    * resultat algoritme detectar CSOs
'''
import datetime
import pandas as pd
import time

#start performance measure
t = time.process_time();

#xlsx filenames loaded and output filename
filenames={
  "rain"   :"RAIN.xlsx",
  "offline":"TEMPERATURE_OFFLINE.xlsx",
  "output" :"output_file_offline_script.xlsx",
};

#new file with column names (empty columns)
new_file={"date":[],"rain (mm)":[]};

#-utilitats--------------------------------------------------------------------
# converteix un string en format "dd/mm/aaaa hh:MM:ss" a datetime
# retorna una variable tipus "datetime"
def parse_date(string):
  if(type(string)!=str): raise(f"'{string}' is not a string")
  return datetime.datetime.strptime(string,"%d/%m/%Y %H:%M:%S")

# carrega un arxiu .xlsx
# retorna un "dataframe" (df)
def read_excel(path, skiprows):
  df = pd.read_excel(path, skiprows=skiprows);
  return df;

#append selected variables to new_file
def append_df_to_new_file(df,id_sensor):
  col_date = df.columns[1];
  for i,row in df.iterrows():
    new_file["date"     ].append(row[col_date]); #datetime
    new_file["rain (mm)"].append(None);
    for ith_id_sensor in ids_sensors:
      new_file[ith_id_sensor].append(row["Value"] if id_sensor==ith_id_sensor else None);

#------------------------------------------------------------------------------
'''Carrega fitxer RAIN i elimina les files amb zeros (FILE2)'''
print(f"Llegint fitxer '{filenames['rain']}' (FILE2)...");
df_rain         = read_excel(filenames["rain"],skiprows=[]);
column_B        = df_rain.columns[1]; #agafa nom columna B
filtre          = df_rain[column_B]>0; #només files on pluja>0 (columna B)
df_rain_filtrat = df_rain[filtre];
#mostra dataframe carregat
print(df_rain_filtrat.head(),'\n')

'''Carrega fitxer TEMPERATURE_OFFLINE (FILE5)'''
print(f"Llegint fitxer '{filenames['offline']}' (FILE5)...");
df_offline = read_excel(filenames["offline"],skiprows=[]);
df_offline["Device"] = df_offline["Device"].apply(str); #converteix a string la columna (sobreescriu-la)
df_offline["Date"] = df_offline["Date"].apply(parse_date); #aplica "parse_date" a la columna (sobreescriu-la)
#mostra dataframe carregat
print(df_offline.head(),'\n');

#get unique sensor ids
ids_sensors = df_offline["Device"].unique();
print("Unique sensor ids:",ids_sensors)

#add new empty columns foreach id sensor
for id_sensor in ids_sensors:
  new_file[id_sensor]=[];

#create a dataframe for each sensor id
#and append it to new file
for id_sensor in ids_sensors:
  df = df_offline[df_offline["Device"]==id_sensor];
  append_df_to_new_file(df,id_sensor);

#add rain data to new file
cols = df_rain_filtrat.columns; #noms columnes dades pluja
for i,row in df_rain_filtrat.iterrows():
  date    = row[cols[0]]; #datetime
  mm_rain = row[cols[1]]; #float

  #append new rows to new_file
  new_file["date"     ].append(row[cols[0]]); #datetime
  new_file["rain (mm)"].append(row[cols[1]]); #valor pluja

  #append empty values for each sensor id
  for id_sensor in ids_sensors: new_file[id_sensor].append(None);

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
