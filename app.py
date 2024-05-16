import base64

from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# MongoDB bağlantı bilgileri
MONGODB_CONNECTION_STRING = "mongodb://localhost:27017/"
DATABASE_NAME = "bist_data"
COLLECTION_NAME = "user"  # Kullanıcı bilgilerinin kaydedileceği koleksiyon adı
COLLECTION_NAME2 = "candle_data"

# MongoDB istemcisini oluşturun
client = MongoClient(MONGODB_CONNECTION_STRING)
# MongoDB veritabanını alın
db = client[DATABASE_NAME]

# Koleksiyonu oluşturun (eğer zaten varsa, mevcut koleksiyonu alır)
collection = db[COLLECTION_NAME]
collection2 = db[COLLECTION_NAME2]

# Koleksiyonu oluşturmak için bir örnek belirleyelim
example_user = {
    'name': 'Example User',
    'email': 'example@example.com',
    'username': 'example_user',
    'password': 'example_password'
}

# Eğer koleksiyon henüz mevcut değilse oluşturun ve bir örnek kullanıcı ekleyin
if COLLECTION_NAME not in db.list_collection_names():
    db.create_collection(COLLECTION_NAME)
    collection.insert_one(example_user)


@app.route('/users-profile', methods=['GET', 'POST'])
def users_profile():
    if 'username' in session:
        if request.method == 'POST':
            # Profil güncelleme formundan verileri al
            full_name = request.form['fullName']
            about = request.form['about']
            company = request.form['company']
            job = request.form['job']
            country = request.form['country']
            address = request.form['address']
            phone = request.form['phone']
            email = request.form['email']
            twitter = request.form['twitter']
            facebook = request.form['facebook']
            instagram = request.form['instagram']
            linkedin = request.form['linkedin']

            # Profil resmini al ve base64 formatında kodla
            profile_image = request.files['profileImage']
            if profile_image:
                profile_image_base64 = base64.b64encode(profile_image.read()).decode('utf-8')
            else:
                profile_image_base64 = None

            # Veritabanında kullanıcı bilgilerini güncelle
            collection.update_one({'username': session['username']},
                                  {'$set': {'full_name': full_name,
                                            'about': about,
                                            'company': company,
                                            'job': job,
                                            'country': country,
                                            'address': address,
                                            'phone': phone,
                                            'email': email,
                                            'twitter': twitter,
                                            'facebook': facebook,
                                            'instagram': instagram,
                                            'linkedin': linkedin,
                                            'profile_image_base64': profile_image_base64}})

            # Güncellenmiş verilerle profil sayfasını yeniden oluştur
            return render_template('users-profile.html', full_name=full_name, about=about, company=company,
                                   job=job, country=country, address=address, phone=phone, email=email,
                                   twitter=twitter, facebook=facebook, instagram=instagram, linkedin=linkedin,
                                   profile_image_base64=profile_image_base64)

        # Kullanıcı adı ile veritabanından kullanıcı bilgilerini al
        user = collection.find_one({'username': session['username']})
        if user:
            full_name = user.get('name',)
            about = user.get('about', '')
            company = user.get('company', '')
            job = user.get('job', '')
            country = user.get('country', '')
            address = user.get('address', '')
            phone = user.get('phone', '')
            email = user.get('email', '')
            twitter = user.get('twitter', '')
            facebook = user.get('facebook', '')
            instagram = user.get('instagram', '')
            linkedin = user.get('linkedin', '')
            profile_image_base64 = user.get('profile_image_base64', None)

            return render_template('users-profile.html', full_name=full_name, about=about, company=company,
                                   job=job, country=country, address=address, phone=phone, email=email,
                                   twitter=twitter, facebook=facebook, instagram=instagram, linkedin=linkedin,
                                   profile_image_base64=profile_image_base64)
    return redirect(url_for('pages_login'))

@app.route('/')
def index():
    # Kullanıcı giriş yapmış mı kontrol etmek için session kontrolü yapılır
    if 'username' in session:
        user = collection.find_one({'username': session['username']})
        if user:
            full_name = user.get('name', 'Unknown')
            return render_template('index.html', full_name=full_name)
    return redirect(url_for('pages_login'))



@app.route('/pages_login', methods=['GET', 'POST'])
def pages_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # MongoDB'de kullanıcıyı kontrol et
        user = collection.find_one({'username': username, 'password': password})

        if user:
            # Kullanıcı doğruysa, oturum (session) oluştur ve index'a yönlendir
            session['username'] = username
            return redirect(url_for('index'))
        else:
            # Kullanıcı adı veya şifre hatalıysa, login sayfasına geri dön
            return render_template('pages_login.html', error=True)

    return render_template('pages_login.html', error=False)

@app.route('/pages_contact')
def pages_contact():
    if 'username' in session:
        user = collection.find_one({'username': session['username']})
        if user:
            full_name = user.get('name', 'Unknown')
            return render_template('pages_contact.html', full_name=full_name)
    return render_template('pages_contact.html')

@app.route('/pages_register', methods=['GET', 'POST'])
def pages_register():
    if request.method == 'POST':
        # Formdan gelen verileri al
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        terms = request.form.get('terms')  # Kullanıcının şartları kabul edip etmediğini kontrol etmek için

        # Veritabanına kullanıcıyı ekle
        new_user = {
            'name': name,
            'email': email,
            'username': username,
            'password': password
        }
        collection.insert_one(new_user)  # Verilerin burada eklenmesi gerekiyor

        # Kayıt işleminden sonra kullanıcıyı başka bir sayfaya yönlendir
        return redirect(url_for('pages_login'))

    return render_template('pages_register.html')

@app.route('/tables_general')
def tables_general():
    if 'username' in session:
        user = collection.find_one({'username': session['username']})
        if user:
            full_name = user.get('name', 'Unknown')
            return render_template('tables_general.html', full_name=full_name)
    return render_template('tables_general.html')


@app.route('/tables_data')
def tables_data():
    data = []
    # Her hisse senedi için son veriyi MongoDB'den al
    for symbol in collection2.distinct("symbol"):
        latest_data = collection2.find_one({"symbol": symbol}, sort=[("date", -1)])
        data.append(latest_data)

    # Kullanıcı bilgisini al
    if 'username' in session:
        user = collection.find_one({'username': session['username']})
        if user:
            full_name = user.get('name', 'Unknown')
            return render_template('tables_data.html', data=data, full_name=full_name)

    return render_template("tables_data.html", data=data)


if __name__ == '__main__':
    app.run(debug=True)

