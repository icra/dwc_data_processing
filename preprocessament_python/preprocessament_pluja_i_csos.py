'''
  Preprocessament de dades provinents de la plataforma dwc (exportats per
  Sílvia B.)

  Carrega diversos fitxers excel i els ajunta, posant-los en una mateix taula.

  Documentació llegida:
    https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html
    https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
    https://docs.python.org/3/library/datetime.html

  Fitxers carregats:
    1. rain
    2. csos
'''
import datetime
import pandas as pd
import time

#start performance measure
t = time.process_time();

#-utilitats--------------------------------------------------------------------
# funció per carregar un arxiu .xlsx
# crea un "dataframe" (df)
def read_excel(path):
  df = pd.read_excel(path);
  return df;

# converteix un string en format "dd/mm/aaaa hh:MM:ss" a datetime
def parse_date(string):
  if(type(string)!=str): raise(f"'{string}' is not a string")
  return datetime.datetime.strptime(string,"%d/%m/%Y %H:%M:%S")
  #test
  #d = parse_date("14/10/2021 07:47:05");
  #print(d);

# comprova si una data concreta està dins un episodi de CSO
def check_cso(date_query, df):
  #date_query: datetime a comprovar
  #df: DataFrame (CSO data on es busca l'episodi)

  columns = df.columns; # noms columnes
  for i,row in df.iterrows(): #itera dataframe de csos
    date_start = row[columns[0]]; #string
    duration   = row[columns[1]]; #minutes

    date_start = parse_date(date_start) #converteix string a datetime
    date_end   = date_start + datetime.timedelta(minutes=duration); #datetime

    # date_query is inside this CSO episode
    if(date_start <= date_query and date_query <= date_end):
      #debug: print(f"CSO episode at [{date_query}], between [{date_start}] and [{date_end}]");
      return True;
      break;

  return False;

#------------------------------------------------------------------------------

#carrega fitxer csos
print("Carregant fitxer CSO...");
df_cso = read_excel('csos.xlsx');
print("Arxiu CSO carregat:", df_cso.head(),'\n')

#carrega fitxer pluja i elimina les dades amb zeros
print("Carregant fitxer RAIN...");
df_rain         = read_excel('rain.xlsx');
column_B        = df_rain.columns[1]; #string amb el nom de la columna B
filtre          = df_rain[column_B]>0; #filtre per les files on hi ha pluja (mm>0) a la columna B
df_rain_filtrat = df_rain[filtre];
print("Arxiu RAIN carregat:", df_rain_filtrat.head(),'\n')

'''Fes coincidir dades de pluja amb episodis de cso detectats'''
#nou fitxer amb 3 columnes buides
new_file={'date':[],'rain (mm)':[],'cso detected':[]};

cols = df_rain_filtrat.columns; #noms columnes dades pluja
for i,row in df_rain_filtrat.iterrows():
  date         = row[cols[0]]; #datetime
  mm_rain      = row[cols[1]]; #float
  cso_detected = check_cso(date, df_cso); #boolean

  #omple nou fitxer
  new_file['date'].append(date);
  new_file['rain (mm)'].append(mm_rain);
  new_file['cso detected'].append(cso_detected);

#crea nou excel
df = pd.DataFrame(new_file);
df.to_excel('nou_fitxer.xlsx', index=False);
print("Arxiu 'nou_fitxer.xlsx' creat correctament");

#end performance measure
elapsed_time = time.process_time()-t;
print(f"Elapsed time: {elapsed_time}")

#end
input("[+] Prem Enter per sortir")
