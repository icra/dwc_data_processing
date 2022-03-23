'''
  detect CSO episodes
  algorithm described in "Hofer et al 2018"
'''
import datetime
import pandas as pd

#utility: generate a datetime interval in minutes
def delta(minutes):
  return datetime.timedelta(minutes=minutes);

#algorithm in "Hofer et al 2018" paper
def detecta_episodis(readings, parameters):
  #"readings" is a Pandas DataFrame with 3 columns: date, T1 (ºC), T2 (ºC)
  #"parameters" is a dictionary with the 5 parameters needed (see below)

  #parameters: (see "Hofer et al 2018" paper)
  delta_T_CSO   = parameters["delta_T_CSO"  ]; # ºC
  f_sensor      = parameters["f_sensor"     ]; # ºC
  t_delay_start = delta(parameters["t_delay_start"]); # timedelta (minutes)
  t_delay_end   = delta(parameters["t_delay_end"  ]); # timedelta (minutes)
  t_gap         = delta(parameters["t_gap"        ]); # timedelta (minutes)

  #prepare data
  cso_timestamps = []; #auxiliar array for timestamps with a cso detected
  cso_episodes   = []; #array for cso episode detected (objects) (RETURN VALUE)
  cols           = readings.columns; #get names of columns from the dataframe

  for i,row in readings.iterrows():
    date = row[cols[0]]; #datetime
    TS1  = row[cols[1]]; #temperature sensor 1
    TS2  = row[cols[2]]; #temperature sensor 2

    diff_temp = abs(TS1-TS2+f_sensor);
    cso_detected = diff_temp <= delta_T_CSO;

    #append datetime to "cso_timestamps"
    if(cso_detected):
      cso_timestamps.append(date);

  #generate cso episodes, structure: {start,end}
  episode_start = 0; #null datetime
  episode_end   = 0; #null datetime

  for i in range(len(cso_timestamps)):
    curr_ts = cso_timestamps[i]; #current timestamp
    if(i==0):
      episode_start = curr_ts - t_delay_start;
      continue;

    if( (curr_ts - cso_timestamps[i-1]) > t_gap):
      episode_end = cso_timestamps[i-1] - t_delay_end; #datetime
      cso_episodes.append({
        "start": episode_start,
        "end": episode_end,
      });
      episode_start = curr_ts - t_delay_start; #datetime

  episode_end = cso_timestamps[-1] - t_delay_end; #datetime
  cso_episodes.append({
    "start": episode_start,
    "end":   episode_end,
  });

  return cso_episodes;

# TEST
'''
#default parameters: (see "Hofer et al 2018" paper)
parameters={
  "delta_T_CSO"   : 0.3, # ºC
  "f_sensor"      : 0.1, # ºC
  "t_delay_start" :   2, # minutes
  "t_delay_end"   :   4, # minutes
  "t_gap"         :  10, # minutes
};

# generate example data
# 3columns: datetime, TemperatureSensor_1, TemperatureSensor_2
day_0 = datetime.datetime(2000,1,1); #datetime: 2000-01-01 00:00:00
readings=pd.DataFrame([
  {"date":day_0,            "TS1":27.665, "TS2":25.362},
  {"date":day_0+delta(10),  "TS1":27.665, "TS2":25.326},
  {"date":day_0+delta(20),  "TS1":27.665, "TS2":25.326},
  {"date":day_0+delta(30),  "TS1":27.665, "TS2":25.322},
  {"date":day_0+delta(40),  "TS1":27.665, "TS2":25.322},
  {"date":day_0+delta(50),  "TS1":27.635, "TS2":25.321},
  {"date":day_0+delta(60),  "TS1":27.62 , "TS2":25.31 },
  {"date":day_0+delta(70),  "TS1":27.432, "TS2":24.985},
  {"date":day_0+delta(80),  "TS1":27.103, "TS2":24.789},
  {"date":day_0+delta(90),  "TS1":27.002, "TS2":24.521},
  {"date":day_0+delta(100), "TS1":26.589, "TS2":24.501},
  {"date":day_0+delta(110), "TS1":26.589, "TS2":24.423},
  {"date":day_0+delta(120), "TS1":26.232, "TS2":24.423},
  {"date":day_0+delta(130), "TS1":25.001, "TS2":24.321},
  {"date":day_0+delta(140), "TS1":23.985, "TS2":23.985},
  {"date":day_0+delta(150), "TS1":23.541, "TS2":23.541},
  {"date":day_0+delta(160), "TS1":23.541, "TS2":23.541},
  {"date":day_0+delta(170), "TS1":22.201, "TS2":22.201},
  {"date":day_0+delta(180), "TS1":22.201, "TS2":22.201},
  {"date":day_0+delta(190), "TS1":22.201, "TS2":22.201},
  {"date":day_0+delta(200), "TS1":22.201, "TS2":22.201},
  {"date":day_0+delta(210), "TS1":22.201, "TS2":22.201},
  {"date":day_0+delta(220), "TS1":22.001, "TS2":22.001},
  {"date":day_0+delta(230), "TS1":22.001, "TS2":22.001},
  {"date":day_0+delta(240), "TS1":21.321, "TS2":21.321},
  {"date":day_0+delta(250), "TS1":21    , "TS2":21    },
  {"date":day_0+delta(260), "TS1":20.301, "TS2":20.301},
  {"date":day_0+delta(270), "TS1":21.254, "TS2":20.541},
  {"date":day_0+delta(280), "TS1":21.541, "TS2":21.102},
  {"date":day_0+delta(290), "TS1":22,     "TS2":22,   },
  {"date":day_0+delta(300), "TS1":22,     "TS2":22,   },
  {"date":day_0+delta(310), "TS1":22.581, "TS2":22.123},
  {"date":day_0+delta(320), "TS1":23.541, "TS2":22.234},
  {"date":day_0+delta(330), "TS1":23.985, "TS2":22.342},
  {"date":day_0+delta(340), "TS1":24.025, "TS2":22.456},
  {"date":day_0+delta(350), "TS1":24.115, "TS2":22.56 },
  {"date":day_0+delta(360), "TS1":24.421, "TS2":22.689},
  {"date":day_0+delta(370), "TS1":24.422, "TS2":22.789},
  {"date":day_0+delta(380), "TS1":24.423, "TS2":23.012},
  {"date":day_0+delta(390), "TS1":24.451, "TS2":23.023},
  {"date":day_0+delta(400), "TS1":24.687, "TS2":23.23 },
  {"date":day_0+delta(410), "TS1":24.789, "TS2":23.421},
  {"date":day_0+delta(420), "TS1":24.891, "TS2":23.425},
  {"date":day_0+delta(430), "TS1":25.321, "TS2":23.521},
  {"date":day_0+delta(440), "TS1":25.456, "TS2":23.689},
  {"date":day_0+delta(450), "TS1":25.687, "TS2":23.899},
  {"date":day_0+delta(460), "TS1":25.687, "TS2":24.234},
  {"date":day_0+delta(470), "TS1":25.687, "TS2":24.332},
  {"date":day_0+delta(480), "TS1":25.781, "TS2":24.456},
  {"date":day_0+delta(490), "TS1":25.789, "TS2":24.512},
  {"date":day_0+delta(500), "TS1":25.961, "TS2":24.523},
  {"date":day_0+delta(510), "TS1":26.014, "TS2":24.561},
  {"date":day_0+delta(520), "TS1":26.251, "TS2":24.601},
  {"date":day_0+delta(530), "TS1":26.289, "TS2":24.701},
  {"date":day_0+delta(540), "TS1":26.335, "TS2":24.714},
  {"date":day_0+delta(550), "TS1":26.687, "TS2":24.715},
  {"date":day_0+delta(560), "TS1":26.689, "TS2":24.728},
  {"date":day_0+delta(570), "TS1":26.689, "TS2":24.729},
  {"date":day_0+delta(580), "TS1":26.891, "TS2":24.73 },
  {"date":day_0+delta(590), "TS1":26.911, "TS2":26.911},
  {"date":day_0+delta(600), "TS1":26.911, "TS2":26.911},
]);

#execute algorithm with the example data generated
episodes = detecta_episodis(readings, parameters);

#print episodes detected
for ep in episodes:
  print(ep)
  duration = ep["end"] - ep["start"];
  print("Episode duration:",duration,'\n');
#end
'''
