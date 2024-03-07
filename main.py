from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
bootstrap = Bootstrap(app)

# MongoDB veritabanı bağlantısı
client = MongoClient('mongodb://localhost:27017/')
db = client['BorsaTakipSistemiDB']
uye_collection = db['uyeler']

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html', gecerli_kullanici=session.get('gecerli_kullanici'))

# Üye olma işlemi
@app.route('/uye-ol', methods=['GET', 'POST'])
def uye_ol():
    if request.method == 'POST':
        ad = request.form['ad']
        email = request.form['email']
        sifre = request.form['sifre']

        uye_data = {'ad': ad, 'email': email, 'sifre': sifre}
        result = uye_collection.insert_one(uye_data)

        if result.inserted_id:
            flash('Üye Olma İşleminiz Başarıyla Gerçekleşti', 'success')
            return redirect(url_for('giris_yap'))
        else:
            flash('Üye Olma İşlemi Gerçekleştirilemedi. Lütfen tekrar deneyiniz.', 'danger')

    return render_template('uye_ol.html')

# Giriş yapma işlemi
@app.route('/giris-yap', methods=['GET', 'POST'])
def giris_yap():
    if request.method == 'POST':
        # Kullanıcı giriş bilgilerini doğrula
        # Eğer doğru ise, kullanıcı oturumunu başlat
        # session['gecerli_kullanici'] = True
        return redirect(url_for('index'))  # Örnek olarak anasayfaya yönlendirme yapıldı
    return render_template('giris_yap.html')

# Diğer gerekli route'ları buraya ekleyebilirsiniz...

if __name__ == "__main__":
    app.run(debug=True)
