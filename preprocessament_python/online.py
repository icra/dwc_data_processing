'''
  Join RAIN + LEVEL + SELECTED_VARIABLES files

  Columns of the new file:
    * FILE2 -- date
    * FILE2 -- rain mm
    * FILE3 -- RUE11 (mNN)
    * FILE3 -- RUE19/20 (mNN)
    * FILE4 -- alarm capacitive (true_false)
    * FILE4 -- alarm cso (true_false)
    * FILE4 -- capacitive (true_false)
    * FILE4 -- temperature 1 (ºC)
    * FILE4 -- temperature 2 (ºC)
    * FILE4 -- alarm level (true/false)
    * FILE4 -- level (mm?)
'''
import datetime
import pandas as pd
import time

#start performance measure
t = time.process_time();

#xlsx filenames loaded and output filename
filenames={
  "rain"  : "RAIN.xlsx",
  "level" : "LEVEL.xlsx",
  "ssvv"  : "SELECTED_VARIABLES.xlsx",
  "output": "new_file.xlsx",
};

#new file, with column names (and empty values)
new_file={
  "date"            :[],
  "rain (mm)"       :[],
  "RUE11 (mNN)"     :[],
  "RUE19/20 (mNN)"  :[],
  "ALARM_CAPACITIVE":[],
  "CAPACITIVE"      :[],
  "ALARM_CSO"       :[],
  "TEMPERATURE_1"   :[],
  "TEMPERATURE_2"   :[],
  "ALARM_LEVEL"     :[],
  "LEVEL"           :[],
};

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

# busca la dada de nivell (FILE3) basat en l'index del dataframe "df"
# aprofita que LEVEL i RAIN tenen el mateix index
def get_level(index, df):
  cols   = df.columns; # noms columnes
  level1 = df.at[index, cols[1]]; # mm
  level2 = df.at[index, cols[2]]; # mm
  return {"level1":level1,"level2":level2};

#append selected variables to new_file
def append_df_to_new_file(df,col_name):
  col_date = df.columns[1];
  for i,row in df.iterrows():
    val = row['Value'];
    new_file["date"            ].append(row[col_date]); #datetime
    new_file["rain (mm)"       ].append(None);
    new_file["RUE11 (mNN)"     ].append(None);
    new_file["RUE19/20 (mNN)"  ].append(None);
    new_file["ALARM_CAPACITIVE"].append(val if col_name=="ALARM_CAPACITIVE" else None);
    new_file["ALARM_CSO"       ].append(val if col_name=="ALARM_CSO"        else None);
    new_file["ALARM_LEVEL"     ].append(val if col_name=="ALARM_LEVEL"      else None);
    new_file["CAPACITIVE"      ].append(val if col_name=="CAPACITIVE"       else None);
    new_file["LEVEL"           ].append(val if col_name=="LEVEL"            else None);
    new_file["TEMPERATURE_1"   ].append(val if col_name=="TEMPERATURE_1"    else None);
    new_file["TEMPERATURE_2"   ].append(val if col_name=="TEMPERATURE_2"    else None);

#------------------------------------------------------------------------------

'''Carrega fitxer RAIN i elimina les dades amb zeros (FILE2)'''
print(f"Llegint fitxer '{filenames['rain']}' (FILE2)...");
df_rain         = read_excel(filenames["rain"],skiprows=[]);
column_B        = df_rain.columns[1]; #string: nom columna B
filtre          = df_rain[column_B]>0; #només files on pluja>0 (columna B)
df_rain_filtrat = df_rain[filtre];
print(df_rain_filtrat.head(),'\n')

'''Carrega fitxer LEVEL (FILE3)'''
print(f"Llegint fitxer '{filenames['level']}' (FILE3)...");
df_level = read_excel(filenames["level"],skiprows=[0,1,2,3,4]);
print(df_level.head(),'\n')

'''Carrega fitxer SELECTED_VARIABLES (FILE4)'''
print(f"Llegint fitxer '{filenames['ssvv']}' (FILE4)...");
df_ssvv = read_excel(filenames["ssvv"],skiprows=[]);
#elimina les fileres amb l'string "false" a columna C
column_C        = df_ssvv.columns[2]; #string: nom columna C
filtre          = df_ssvv[column_C]!="false"; #només files on cela!="false"
df_ssvv         = df_ssvv[filtre]; #dataframe filtrat (sobreescriu original)
df_ssvv["Date"] = df_ssvv["Date"].apply(parse_date); #aplica "parse_date" a la columna (sobreescriu-la)
#mostra dataframe
print(df_ssvv.head(),'\n');

'''Separa dataframe "df_ssvv" per categories columna A'''
column_A                 = df_ssvv.columns[0]; #string: nom columna A
df_ssvv_ALARM_CAPACITIVE = df_ssvv[df_ssvv[column_A]=="ALARM_CAPACITIVE"];
df_ssvv_ALARM_CSO        = df_ssvv[df_ssvv[column_A]=="ALARM_CSO"];
df_ssvv_ALARM_LEVEL      = df_ssvv[df_ssvv[column_A]=="ALARM_LEVEL"];
df_ssvv_CAPACITIVE       = df_ssvv[df_ssvv[column_A]=="CAPACITIVE"];
df_ssvv_LEVEL            = df_ssvv[df_ssvv[column_A]=="LEVEL"];
df_ssvv_TEMPERATURE_1    = df_ssvv[df_ssvv[column_A]=="TEMPERATURE_1"];
df_ssvv_TEMPERATURE_2    = df_ssvv[df_ssvv[column_A]=="TEMPERATURE_2"];
#mostra DataFrames resultants
#print("DataFrame SELECTED_VARIABLES ALARM_CAPACITIVE:\n", df_ssvv_ALARM_CAPACITIVE.head(),'\n')
#print("DataFrame SELECTED_VARIABLES ALARM_CSO       :\n", df_ssvv_ALARM_CSO       .head(),'\n')
#print("DataFrame SELECTED_VARIABLES ALARM_LEVEL     :\n", df_ssvv_ALARM_LEVEL     .head(),'\n')
#print("DataFrame SELECTED_VARIABLES CAPACITIVE      :\n", df_ssvv_CAPACITIVE      .head(),'\n')
#print("DataFrame SELECTED_VARIABLES LEVEL           :\n", df_ssvv_LEVEL           .head(),'\n')
#print("DataFrame SELECTED_VARIABLES TEMPERATURE_1   :\n", df_ssvv_TEMPERATURE_1   .head(),'\n')
#print("DataFrame SELECTED_VARIABLES TEMPERATURE_2   :\n", df_ssvv_TEMPERATURE_2   .head(),'\n')

'''Merge RAIN data with LEVEL data'''
print("Merging RAIN with LEVEL...")
cols = df_rain_filtrat.columns; #noms columnes dades pluja
for i,row in df_rain_filtrat.iterrows():
  date    = row[cols[0]]; #datetime
  mm_rain = row[cols[1]]; #float

  #get variables from FILE3 (LEVEL)
  level = get_level(i, df_level);

  #append new rows to new_file
  new_file["date"            ].append(date); #datetime
  new_file["rain (mm)"       ].append(mm_rain); #valor pluja
  new_file["RUE11 (mNN)"     ].append(level["level1"]); #valor trobat FILE3
  new_file["RUE19/20 (mNN)"  ].append(level["level2"]); #valor trobat FILE3
  new_file["ALARM_CAPACITIVE"].append(None); #valor buit
  new_file["ALARM_CSO"       ].append(None); #valor buit
  new_file["ALARM_LEVEL"     ].append(None); #valor buit
  new_file["CAPACITIVE"      ].append(None); #valor buit
  new_file["LEVEL"           ].append(None); #valor buit
  new_file["TEMPERATURE_1"   ].append(None); #valor buit
  new_file["TEMPERATURE_2"   ].append(None); #valor buit

'''Afegeix dades SELECTED_VARIABLES al final de new_file'''
print("Appending SELECTED_VARIABLES...")
append_df_to_new_file(df_ssvv_ALARM_CAPACITIVE,"ALARM_CAPACITIVE");
append_df_to_new_file(df_ssvv_ALARM_CSO,       "ALARM_CSO");
append_df_to_new_file(df_ssvv_ALARM_LEVEL,     "ALARM_LEVEL");
append_df_to_new_file(df_ssvv_CAPACITIVE,      "CAPACITIVE");
append_df_to_new_file(df_ssvv_LEVEL,           "LEVEL");
append_df_to_new_file(df_ssvv_TEMPERATURE_1,   "TEMPERATURE_1");
append_df_to_new_file(df_ssvv_TEMPERATURE_2,   "TEMPERATURE_2");

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
