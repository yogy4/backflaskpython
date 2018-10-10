# project/server/auth/views.py


from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from project.server import bcrypt, db
from project.server.models import User, BlacklistToken, Product, Distributor

auth_blueprint = Blueprint('auth', __name__)


class RegisterAPI(MethodView):
    """
    Ini berisi method untuk registrasi
    """

    def post(self):
        # mengambil data
        post_data = request.get_json()
        # kemudian check apakah user sudah ada
        user = User.query.filter_by(email=post_data.get('email')).first()
        if not user:
            try:
                user = User(
                    email=post_data.get('email'),
                    password=post_data.get('password')
                )
                # bila belum maka masukan user baru
                db.session.add(user)
                db.session.commit()
                # bila input berhasil maka akan menampilkan token
                auth_token = user.encode_auth_token(user.id)
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully registered.',
                    'auth_token': auth_token.decode()
                }
                return make_response(jsonify(responseObject)), 201
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': 'Some error occurred. Please try again.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            return make_response(jsonify(responseObject)), 202


class LoginAPI(MethodView):
    """
    Ini berisi method untuk login user
    """
    def post(self):
        # mendapatkan data
        post_data = request.get_json()
        try:
            # mengambil data user beserta password yang diinput
            user = User.query.filter_by(
                email=post_data.get('email')
            ).first()
            if user and bcrypt.check_password_hash(
                user.password, post_data.get('password')
            ):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode()
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'User does not exist.'
                }
                return make_response(jsonify(responseObject)), 404
        except Exception as e:
            print(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            return make_response(jsonify(responseObject)), 500


class UserAPI(MethodView):
    """
    Ini berisi method untuk objek user
    """
    def get(self):
        # method ini diproteksi dengan token jadi pertama kali yang harus diambil oleh system adalah token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                responseObject = {
                    'status': 'success',
                    'data': {
                        'user_id': user.id,
                        'email': user.email,
                        'admin': user.admin,
                        'registered_on': user.registered_on
                    }
                }
                return make_response(jsonify(responseObject)), 200
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 401


class LogoutAPI(MethodView):
    """
    Ini berisi method untuk logout
    """
    def post(self):
        # method ini bisa dijalankan bila login berhasil 
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                # ini untuk menandai bahwa token telah diblacklist
                blacklist_token = BlacklistToken(token=auth_token)
                try:
                    # menginputkan token
                    db.session.add(blacklist_token)
                    db.session.commit()
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged out.'
                    }
                    return make_response(jsonify(responseObject)), 200
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': e
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': resp
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 403


class ProductAPI(MethodView):
    """
    Ini berisi method untuk objek product dan untuk mengakses perlu login terlebih dahulu
    """
    def post(self):
        # pertama ambil token
        auth_header = request.headers.get('Authorization')
        # bila token belum expired maka inputan bisa dikirim
        post_data = request.get_json()
        # sebelum inputan dimasukan dalam tabel dicek terlebih dahulu apakah inputan sudah ada atau belum
        product = Product.query.filter_by(nama=post_data.get('nama')).first()

        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token and not product:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
            
                try:
                    # masukan inputan ke dalam tabel products
                    product = Product(
                    nama=post_data.get('nama'),
                    harga=post_data.get('harga'),
                    jumlah=post_data.get('jumlah')
                )
                    db.session.add(product)
                    db.session.commit()
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully insert.'
                    }
                    return make_response(jsonify(responseObject)), 200
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': e
                    }
                    return make_response(jsonify(responseObject)), 401
            else:
                responseObject = {
                    'status': 'fail',
                    'message': resp
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 403

    def get(self):
        # method ini untuk menampilkan data product dan diproteksi dengan token 
        
        auth_header = request.headers.get('Authorization')
        isi = []
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
                resp = User.decode_auth_token(auth_token)
                if not isinstance(resp, str):
           
                    p = Product.query.all()
                    
                    for tampil in p:
                        responseObject = {
                            'status': 'success',
                            'data': {
                                'product_id': tampil.id,
                                'nama': tampil.nama,
                                'harga': tampil.harga,
                                'jumlah': tampil.jumlah,
                            }
                        }
                        isi.append(responseObject)
                   

                    return make_response(jsonify(isi)), 200
                   
                responseObject = {
                    'status': 'fatal',
                    'message': resp
                }
                isi.append(responseObject)
            
                return make_response(jsonify(responseObject)), 401
                

            
           
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
           
            return make_response(jsonify(responseObject)), 401

class DistributorAPI(MethodView):
    """
    Ini berisi method untuk objek distributor dan diproteksi dengan token maka harus login terlebih dahulu
    """
    def post(self):
        # ambil token
        auth_header = request.headers.get('Authorization')
        # bila token valid maka bisa mengirim inputan
        post_data = request.get_json()
        # ini untuk mengechek apakah inputan sudah ada atau belum dalam database
        distributor = Distributor.query.filter_by(nama=post_data.get('perusahaan')).first()

        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token and not distributor:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
            
                try:
                    # masukan inputan
                    distributor = Distributor(
                    nama=post_data.get('perusahaan'),
                    harga=post_data.get('barang')
                    
                    )
                    db.session.add(distributor)
                    db.session.commit()
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully insert.'
                    }
                    return make_response(jsonify(responseObject)), 200
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': e
                    }
                    return make_response(jsonify(responseObject)), 401
            else:
                responseObject = {
                    'status': 'fail',
                    'message': resp
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 403

    def get(self):
        # method ini untuk menampilkan data distributor
        auth_header = request.headers.get('Authorization')
        isi = []
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
                resp = User.decode_auth_token(auth_token)
                if not isinstance(resp, str):
                    p = Distributor.query.all()
                    for tampil in p:
                        responseObject = {
                            'status': 'success',
                            'data': {
                                'distributor_id': tampil.id,
                                'perusahaan': tampil.perusahaan,
                                'barang': tampil.barang,
                                
                            }
                        }
                        isi.append(responseObject)
                    

                    return make_response(jsonify(isi)), 200
                   
                responseObject = {
                    'status': 'fatal',
                    'message': resp
                }
                isi.append(responseObject)
           
                return make_response(jsonify(responseObject)), 401
               

            
           
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            
            return make_response(jsonify(responseObject)), 401


# mendefinisikan api
registration_view = RegisterAPI.as_view('register_api')
login_view = LoginAPI.as_view('login_api')
user_view = UserAPI.as_view('user_api')
logout_view = LogoutAPI.as_view('logout_api')
product_view = ProductAPI.as_view('product_view')
distributor_view = DistributorAPI.as_view('distributor_view')
# membuat endpoint untuk api
auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/status',
    view_func=user_view,
    methods=['GET']
)
auth_blueprint.add_url_rule(
    '/auth/logout',
    view_func=logout_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/product',
    view_func=product_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/product/list',
    view_func=product_view,
    methods=['GET']
)
auth_blueprint.add_url_rule(
    '/distributor',
    view_func=distributor_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/distributor',
    view_func=distributor_view,
    methods=['GET']
)