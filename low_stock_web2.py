import csv
from flask import Flask, render_template, request
from datetime import datetime, timedelta

app = Flask(__name__)

missing_skus = []

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
    current_date = datetime.now().strftime("%Y-%m-%d")  # določitev datuma - za danes
    yesterday_date = datetime.now() - timedelta(days=1)     # izračun datuma za včeraj
    yesterday_date_str = yesterday_date.strftime("%Y-%m-%d")    # določitev datuma - za včeraj
    if request.method == 'POST':
        default_file = request.files['default_file']
        danasnje_stanje = f"stanje_dne_{current_date}.csv"  # poimenovanje datoteke z današnjim datumom
        if default_file:
            default_file.save(danasnje_stanje)      # shrani datoteko default0.csv v datoteko stanje_dne_(današnji datum).csv
            yesterday_file = f'stanje_dne_{yesterday_date_str}.csv'     # poimenovanje datoteke z vključenim včerajšnjim datumom
            missing_skus = compare_files("default0.csv", yesterday_file)
            if missing_skus:
                save_missing_skus(missing_skus)
                return render_template('result.html', missing_skus=missing_skus)
            else:
                return render_template('result.html', message="Od včeraj do danes zaloga nobenega od izdelkov na mojepivo.si ni padla na 0.")
        else:
            return render_template('index.html', message="Niste izbrali datoteke default0.csv.")

    return render_template('index.html', message=None)

@app.route('/save_missing_skus', methods=['POST'])
def save_missing_skus(missing_skus):
    # Datum, ki ga želite uporabiti za ime datoteke
    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"zero_inventory_on_{date}.csv"
 

    # Shranjevanje vsebine spremenljivke missing_skus v datoteko
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['SKU'])  # Primer vstavljanja glave (headerja)
        for sku in missing_skus:
            writer.writerow([sku])

    return 'File saved successfully'

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
