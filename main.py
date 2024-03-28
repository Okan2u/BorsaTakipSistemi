from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_bootstrap import Bootstrap
from pymongo import MongoClient
from threading import Thread
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
bootstrap = Bootstrap(app)

client = MongoClient('mongodb://localhost:27017/')
db = client['BorsaTakipSistemiDB']
uye_collection = db['uyeler']
fiyat_collection = db['fiyatlar']

def veri_cikar():
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument("--incognito")
    chromeOptions.add_argument("--headless")
    driver = webdriver.Chrome(options=chromeOptions)
    driver.delete_all_cookies()

    driver.get("https://tr.tradingview.com/chart/?symbol=FX_IDC%3AUSDTRY")
    driver.implicitly_wait(3)

    # Koleksiyonda sadece bir belge tutma
    doc_id = 1
    while True:
        fiyat_bilgisi = driver.find_element(By.XPATH,
        "/html/body/div[2]/div[6]/div/div[2]/div[1]/div[1]/div[2]/div[2]/div/div[2]/div[2]/span[1]/span[1]").text
        # MongoDB'deki belgeyi güncelleme
        fiyat_collection.update_one(
            {'_id': doc_id},  # Belgeyi bulmak için _id kullanılır
            {'$set': {'fiyat': fiyat_bilgisi}},  # Yeni fiyat bilgisini ayarla
            upsert=True  # Belge bulunamazsa yeni belge eklenir
        )
        sleep(3)

@app.route('/')
def index():
    # MongoDB'den anlık fiyatı çekme
    fiyat_verisi = fiyat_collection.find_one({'_id': 1})
    if fiyat_verisi:
        dolar_detaylari = fiyat_verisi.get('fiyat')
    else:
        dolar_detaylari = "Veri bulunamadı"

    # HTML sayfasına fiyat verisini ileterek render etme
    return render_template('index.html', dolar_detaylari=dolar_detaylari, gecerli_kullanici=session.get('gecerli_kullanici', False))

@app.route('/fiyat_güncelle')
def fiyat_güncelle():
    fiyat_verisi = fiyat_collection.find_one({'_id': 1})
    if fiyat_verisi:
        dolar_detaylari = fiyat_verisi.get('fiyat')
    else:
        dolar_detaylari = "Veri bulunamadı"

    return jsonify(dolar_detaylari=dolar_detaylari)

@app.route('/uye-ol', methods=['GET', 'POST'])
def uye_ol():
    if request.method == 'POST':
        ad = request.form['ad']
        email = request.form['email']
        sifre = request.form['sifre']

        uye_data = {'ad': ad, 'email': email, 'sifre': sifre}
        result = uye_collection.insert_one(uye_data)

        if result.inserted_id:
            return redirect(url_for('giris_yap'))
        else:
            flash('Üye Olma İşlemi Gerçekleştirilemedi. Lütfen tekrar deneyiniz.', 'danger')

    return render_template('uye_ol.html')

@app.route('/giris-yap', methods=['GET', 'POST'])
def giris_yap():
    if request.method == 'POST':
        session['gecerli_kullanici'] = True
        flash('Giriş Yapma İşlemi Başarılı', 'success')
        return redirect(url_for('index'))

    return render_template('giris_yap.html')

@app.route('/cikis-yap')
def cikis_yap():
    session.pop('gecerli_kullanici', None)
    flash('Oturumunuz kapatıldı', 'info')
    return redirect(url_for('index'))

if __name__ == "__main__":
    veri_cikar_thread = Thread(target=veri_cikar)
    veri_cikar_thread.start()
    app.run(debug=True)
