

# Untuk menjalankan project ini ada beberapa langkah yang harus dijalani

1. Lakukan Fork/Clone
2. Aktifkan virtualenv
3. Kemudian install requirements(file requirements.txt)

# Set Environment Variables(dalam contoh ini menggunakan os linux dan python 2.7)

bash
$ export APP_SETTINGS="project.server.config.DevelopmentConfig"

# bila ingin menjalankan dalam mode production

$ export APP_SETTINGS="project.server.config.ProductionConfig"

# kemudian set SECRET_KEY

$ export SECRET_KEY="change_me"

# buat database

$ psql
 create database database_name
create database database_name_test
\q



#setelah itu lakukan migrasi

$ python manage.py create_db
$ python manage.py db init
$ python manage.py db migrate

# terakhir jalankan aplikasi

$ python manage.py runserver


# untuk pengujian

tanpa coverage:
$ python manage.py test


dengan coverage:
$ python manage.py cov

