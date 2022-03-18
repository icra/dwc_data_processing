INSTRUCCIONS PER AGRUPAR ELS DIFERENTS FITXERS XLSX
---------------------------------------------------
1. Fitxer 1: "online.py" -> file2 (rain), file3 (nivell), file4 (selected variables)
  - noms columnes:
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

2. Fitxer 2: "offline.py" -> file2 (rain), file5(t1,t2) i aplicar algoritme
  - noms columnes:
    * FILE2 -- date
    * FILE2 -- rain mm
    * FILE5 -- id device (i.e. 20641423)
    * FILE5 -- value (ºC)
    * FILE5 -- id device (i.e. 10084446)
    * FILE5 -- value (ºC)
    * resultat algoritme detectar CSOs
