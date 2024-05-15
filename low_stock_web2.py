import csv
from flask import Flask, render_template, request
from datetime import datetime, timedelta
import os
import glob

app = Flask(__name__)

vzorec = 'stanje_dne_*.csv'

def newest_csv_file(vzorec):
    trenutna_mapa = os.getcwd()
    pot_do_datotek = os.path.join(trenutna_mapa, vzorec)
    sez_datotek = glob.glob(pot_do_datotek)
    if not sez_datotek:
        return None
    najnovejsa_datoteka = max(sez_datotek, key=os.path.getctime)
    return najnovejsa_datoteka



def read_csv(file_name):
    data = []
    with open(file_name, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)
    return data

def compare_files(default_file, yesterday_file):
    default_data = read_csv(default_file)
    yesterday_data = read_csv(yesterday_file)
    default_skus = [row[3] for row in default_data]
    yesterday_skus = [row[3] for row in yesterday_data]

    missing_skus = list(set(default_skus) - set(yesterday_skus))

    return missing_skus

@app.route('/', methods=['GET', 'POST'])
def index():
    current_date = datetime.now().strftime("%Y-%m-%d")  # določitev datuma - za današnjo datoteko
    najnovejsa_datoteka = newest_csv_file(vzorec)
    print("Najnovejša datoteka:", najnovejsa_datoteka)  # kontrola, katero datoteko je našel kot zadnjo - izpis le v terminalu
    if request.method == 'POST':
        default_file = request.files['default_file']    # prebere datoteko, vnešeno v formi v index.html in jo zapiše v default_file
        danasnje_stanje = f"stanje_dne_{current_date}.csv"  # poimenovanje datoteke z današnjim datumom
        if default_file:
            default_file.save(danasnje_stanje)      # shrani prebrano datoteko (default0.csv ipd.) v datoteko stanje_dne_(current_date).csv
            missing_skus = compare_files(danasnje_stanje, najnovejsa_datoteka)
            if missing_skus:
                save_missing_skus(missing_skus)     # shrani missing_skus 
                return render_template('result.html', najnovejsa_datoteka=najnovejsa_datoteka, missing_skus=missing_skus)    # če missing_skus obstaja, potem prikaže skuje preko results.html
            else:
                return render_template('result.html', najnovejsa_datoteka=najnovejsa_datoteka, message="Od včeraj do danes zaloga nobenega od izdelkov na mojepivo.si ni padla na 0.")
        else:
            return render_template('index.html', message="Niste izbrali datoteke z današnjim stanjem sku z zalogo 0.")

    return render_template('index.html', message=None)

@app.route('/save_missing_skus', methods=['POST'])
def save_missing_skus(missing_skus):
    # Datum, ki ga želite uporabiti za ime datoteke
    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"new_zero_inventory_on_{date}.csv"
    # Shranjevanje vsebine spremenljivke missing_skus v datoteko:
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['SKU'])  # Primer vstavljanja glave (headerja)
        for sku in missing_skus:
            writer.writerow([sku])

    return 'File saved successfully'

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
