import pandas as pd
import datetime

'''
  carrega un fitxer .xlsx tipus FILE5
  separal per id sensor (crea noves columnes)
  interpola valors buits de cada sensor
  retorna nou dataframe
'''
def carrega(path):
  #new file with column names (empty columns)
  new_file={
    "date":[],
    #columns for offline sensors ids are added after the file is read
  };

  print(f"Llegint fitxer {path} (FILE5)...");
  df_offline = pd.read_excel(path,skiprows=[]);
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

    col_date = df.columns[1];
    for i,row in df.iterrows():
      new_file["date"].append(row[col_date]); #datetime
      for ith_id_sensor in ids_sensors:
        new_file[ith_id_sensor].append(row["Value"] if id_sensor==ith_id_sensor else None);

  #crea dataframe amb les noves columnes creades i ordena per "date"
  df = pd.DataFrame(new_file);
  df.sort_values(by=["date"], inplace=True);

  #elimina files amb 2 nans o més
  df_no_nans = df.dropna(thresh=2);
  print(df_no_nans);

  #interpola cada columna id_sensor
  dfi=[];
  for id_sensor in ids_sensors:
    df = interpola(df_no_nans, "date", id_sensor)
    dfi.append(df);

  #merge dataframes interpolated
  dfm = pd.merge_ordered(dfi[0],dfi[1],on="date",how="outer",fill_method="ffill")

  #retorna dataframe merged
  return dfm

'''UTILITATS'''
# converteix un string en format "dd/mm/aaaa hh:MM:ss" a datetime
# retorna una variable tipus "datetime"
def parse_date(string):
  if(type(string)!=str): raise(f"'{string}' is not a string")
  return datetime.datetime.strptime(string,"%d/%m/%Y %H:%M:%S")

# omple els valors buits de la columna "y" del dataframe (2 columnes: x,y)
def interpola(df, nom_col_x, nom_col_y):
  print(f"Interpolant columnes x:'{nom_col_x}', y:'{nom_col_y}'")

  #retalla dataframe
  cols = df.columns; #noms columnes
  cols_xy = df[[nom_col_x,nom_col_y]]; #selecciona columnes

  #find first index without nan to become index=0
  first_index = 0;
  cols=cols_xy.columns;

  for i,row in cols_xy.iterrows():
    d = row[cols[0]]; #date
    t = row[cols[1]]; #temperature
    if(pd.isnull(t)==False):
      first_index = i;
      break;

  #find last index without nan to become final index
  last_index = cols_xy.iloc[-1].name; #valor inicial
  for i,row in cols_xy[::-1].iterrows():
    d = row[cols[0]]; #date
    t = row[cols[1]]; #temperature
    if(pd.isnull(t)==False):
      last_index = i;
      break;

  #descarta dades fora del rang trobat (first_index, last_index)
  #a partir d'aqui sabem que el primer index i l'ultim tenen dada vàlida
  #per tant podem interpolar les dades intermèdies
  cols_xy = cols_xy.loc[first_index:last_index];

  #transforma a array
  values = cols_xy.values;

  for i in range(len(values)):
    arr = values[i];
    d = arr[0];
    t = arr[1];

    #si hi ha dada vàlida, next
    if(pd.isnull(t)==False): continue

    #find index of prev row with a valid number
    index_prev_row = i-1;
    while(pd.isnull(values[index_prev_row][1])):
      index_prev_row = index_prev_row-1;

    #find index of next row with a valid number
    index_next_row = i+1;
    while(pd.isnull(values[index_next_row][1])):
      index_next_row = index_next_row+1;

    #perform linear interpolation
    y_next = values[index_next_row][1];
    y_prev = values[index_prev_row][1];
    x_next = values[index_next_row][0].timestamp();
    x_prev = values[index_prev_row][0].timestamp();
    slope = (y_next-y_prev)/(x_next-x_prev);
    new_value = y_prev + slope*(d.timestamp() - x_prev);

    #modify array in place
    values[i][1] = new_value;

  #crea dataframe
  df_new = pd.DataFrame(values, columns=[nom_col_x,nom_col_y]);
  return df_new;

# TESTS
'''
df=carrega("TEMPERATURE_OFFLINE.xlsx")
print(df)
'''
