# Creo una classe per gli errori
class ExamException(Exception):
    
    pass

class CSVFile():

    def __init__(self, name):
        
        # Setto il nome del file
        self.name = name
        
    def get_data(self):
        
        # Inizializzo una lista vuota per salvare tutti i dati
        data = []

        # Apro il file
        my_file = open(self.name, 'r')

        # Leggo il file linea per linea
        for line in my_file:
            
            # Faccio lo split di ogni linea sulla virgola
            elements = line.split(',')
            
            # Posso anche pulire il carattere di newline 
            # dall'ultimo elemento con la funzione strip():
            elements[-1] = elements[-1].strip()
            
            # p.s. in realta' strip() toglie anche gli spazi
            # bianchi all'inizio e alla fine di una stringa.

            # Se NON sto processando l'intestazione...
            if elements[0] != 'Date':
                    
                # Aggiungo alla lista gli elementi di questa linea
                data.append(elements)
        
        # Chiudo il file
        my_file.close()
        
        # Quando ho processato tutte le righe, ritorno i dati
        return data

    
# Creo da zero una classe per leggere il file
class CSVTimeSeriesFile(CSVFile):

    def get_data(self):

            # Apro il file in sola lettura
            # Controllo che il file esista e sia leggibile
            try:
                
                my_file = open(self.name, 'r')
                my_file.readline()
                
            except:
                
                raise ExamException('Errore, file inesistente o illeggibile')

            # Inizializzo una lista vuota per salvare tutti i dati
            data = []
            
            # Leggo il file linea per linea
            for line in my_file:
                
                # Faccio lo split di ogni linea sulla virgola
                elements = line.split(',')
                
                # Pulisco l'ultimo elemento dalla newline
                elements[-1] = elements[-1].strip()
    
                # Se NON sto processando l'intestazione...
                if elements[0] != 'epoch':
                    
                    # Mi assicuro che gli elementi siano almeno due
                    if len(elements) > 1:
                        
                        # Aggiungo alla lista gli elementi di questa linea
                        data.append(elements)
            
            # Chiudo il file
            my_file.close()
            
            # Ritorno i dati
            return data

def compute_daily_max_difference(time_list):

    # Inizializzo quello che sarà l'output ed un contatore per il num di rilevazioni a giornata
    out_list = []
    counter = 0

    # Inizializzo una variabile che nel caso di problemi negli input 
    # mi permetterà di passare all item successivo
    skip = False

    # Inizializzo una variabile per il controllo di epoch
    prev_epoch = 0
    
    # Creo un ciclo per ogni elemento nella mia lista
    for item in time_list:

        # Divido ogni elemento per epoch e temperatura
        raw_epoch = item[0]
        raw_temp = item[1]

        # Mi assicuro che epoch sia un intero
        try:
            epoch = int(float(raw_epoch))
        except:
            skip = True

        # Mi assicuro che l epoch corrente sia successiva alla precedente
        if prev_epoch >= epoch and skip == False:

            # Nel caso sia uguale
            if prev_epoch == epoch:

                raise ExamException('Errore, epoch duplicata: {}'.format(epoch))

            # Nel caso sia minore
            else:
            
                raise ExamException('Errore, un epoch non è ordinata: {}'.format(epoch))      

        # Mi assicuro che la temperatura sia un float
        try:
            temp = float(raw_temp)
        except:
            skip = True

        # Se skip è impostata a true la riga viene scartata e si passa alla successiva
        # Sennò il programma continua inalterato
        if skip == True:
            
            skip = False
            
        else:

            # Passati i controlli rinnovo prev_epoch
            prev_epoch = epoch
            
            if counter == 0:
                
                # Trovo la prima rilevazione del giorno 
                # Imposto la giornara su un intero 
                # Ogni rilevazione che inizia con quel intero farà riferimento a questa giornata
                day = int(epoch / 86400)
    
                # Imposto max e min alla prima temperatura rilevata
                daily_max = temp
                daily_min = temp
                counter = 1
                
            elif counter == 1 and int(epoch / 86400) != day:
                
                # Restituisco None perchè ho una sola rilvezione per quella giornata      
                out_list.append(None)
                
                # Imposto la giornara su un nuovo intero 
                day = int(epoch / 86400)    

                # Imposto max e min alla prima temperatura rilevata
                daily_max = temp
                daily_min = temp
                counter = 1
                
            elif int(epoch / 86400) == day:
                
                # Cambio il valore massimo se la rilevazione lo supera
                if daily_max < temp:
                    daily_max = temp
                    
                # Lo stesso vale per il minimo
                if daily_min > temp:
                    daily_min = temp
                    
                # Incremento il contatore per sapere che ho fatto più di una rilevazione
                counter += 1
    
            else:
                
                # Inserisco tra gli output escurione termica della giornata
                # Di almeno 2 registrazioni
                difference = daily_max - daily_min
                out_list.append(round(difference, 2))
                
                # Imposto la giornara su un nuovo intero 
                day = int(epoch / 86400)
    
                # Imposto max e min alla prima temperatura rilevata
                daily_max = temp
                daily_min = temp
                counter = 1

    # Aggiungo alla lista le rilevazioni dell ultima giornata
    # Sempre dopo aver controllato che ci sia più di una rilevazione
    if counter > 1:
        
        difference = daily_max - daily_min
        out_list.append(round(difference, 2))
        
    else:
        
        out_list.append(None)

    # Ritorno la lista con i valori delle temperature
    return out_list


    
# CORPO DEL PROGRAMMA
    
time_series_file = CSVTimeSeriesFile('data.csv')
time_series = time_series_file.get_data()
results = compute_daily_max_difference(time_series)

print(results)
