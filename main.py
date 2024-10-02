from models import app,db,Client,Barber,Admin,Appointments
from flask import request,redirect,url_for,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps
from datetime import datetime,timedelta
import jwt
import secrets


app.secret_key = secrets.token_bytes(16)



@app.route('/register_client',methods=['GET','POST'])
def register_client():
    if request.method== 'POST':
        data = request.json
        name = data['name']
        phone_number = data['phone']
        password = data['password']
        existing_client = db.session.query(Client).filter(Client.phone_number==phone_number).first()
        if existing_client:
            return jsonify({"Message":"User already exists please login"})
        hashed_password = generate_password_hash(password)
        new_client = Client(name=name,phone_number=phone_number,password=hashed_password)
        db.session.add(new_client)
        db.session.commit()
        return jsonify({"Success":"Registration successfull"}),201
    elif request.method == 'GET':
        clients = db.session.execute(db.select(Client).order_by(Client.id)).scalars()
        client_data =[]
        for client in clients:
            client_data.append({
                "id":client.id,
                "username":client.username,
                "phone_number":client.phone_number
            })
        return jsonify({"Clients":client_data}),200
    
@app.route("/register_barber",methods=['GET','POST'])
def register_barber():
    if request.method == 'POST':
        data = request.json
        name = data['name']
        email = data['email']
        phone_number = data['phone']
        password = data["password"]
        existing_barber = db.session.query(Barber).filter(Barber.email==email).first()
        if existing_barber :
            return jsonify({"Message":"User already exists please login"})
        hashed_password = generate_password_hash(password)
        new_barber = Barber(name=name,email=email,phone_number=phone_number,password=hashed_password)
        db.session.add(new_barber)
        db.session.commit()
        return jsonify({"Success":"Registraion request successful"}),201
    
    elif request.method == "GET":
        barbers = db.session.execute(db.select(Barber).order_by(Barber.id)).scalars()
        barber_data = []
        for barber in barbers:
            barber_data.append({
                "id":barber.id,
                "first_name":barber.first_name,
                "last_name":barber.last_name,
                "email": barber.email,
                "phone_number":barber.phone_number,
            })
        return jsonify({"Barber_Data":barber_data}),200


@app.post('/login')
def login():
    data = request.json
    email = data['email']
    password = data['password']

    existing_user = ( db.session.query(Client).filter(Client.email==email).first() or
                      db.session.query(Barber).filter(Barber.email==email).first() or
                      db.session.query(Admin).filter(Admin.email==email).first() )
    if not existing_user:
        return jsonify({"Login failed":"Confirm login credentials"})
    try:
        if check_password_hash(existing_user.password,password):
            access_token = jwt.encode({"sub":existing_user.name,
                                       'role':existing_user.role,
                                       "exp":datetime.utcnow() + timedelta(minutes=30)},app.secret_key)
            return jsonify({"Message":"Login successfull","Access_Token":access_token}),201
        else:
            return jsonify({"Login failed":"Incorrect password"}),401
    except Exception as e:
        return jsonify({"Error creating access token":str(e)}),500


def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = request.headers.get("Authorization")
        if token is None:
            return jsonify({"Error":"Token is missing"}),403
        try:
            data = jwt.decode(token,app.secret_key,algorithms=['HS256'])
            current_user = data['sub']
            role = data['role']
            return f(current_user,role,*args,**kwargs)
        except:
            return jsonify({"Error":"Error decoding token,confirm your secret key"})
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = request.headers.get("Authorization")
        if token is None:
            return jsonify({"Message":"Token is missing"}),403
        try:
            data = jwt.decode(token,app.secret_key,algorithms=['HS256'])
            role = data['role']
            if role != 'admin':
                return jsonify({"Message":"Admin restricted!"}),403
        except Exception as e:
            return jsonify({"Error":"Error decoding token"})
    return decorated

@app.post("/add_admin")
@admin_required
def add_admin():
    try:
        data = request.json
        name = data['name']
        email= data['email']
        phone = data['phone']
        password = data['password']
        hashed_password = generate_password_hash(password)
        existing_admin = db.session.query(Admin).filter(Admin.email==email).first()
        if existing_admin:
            return jsonify({"Message":"Admin user already exists"}),400
        new_admin= Admin(name=name,email=email,phone_number=phone,password=hashed_password)
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({"Message":"Admin created successfully"}),201
    except Exception as e:
        return jsonify({"Error creating admin":str(e)}),500

@app.route('/booking',methods=['GET','POST'])
@token_required
def booking(user_id,role):
    if role != 'client':
        return jsonify({"Message":"Only clients can make appointments"}),403
    client = Client.query.get(user_id)
    if request.method =='POST':
        try:
            data = request.json
            if not client:
                return jsonify({"Message":"Client not found"}),404

            approved_barbers = Barber.query.filter(Barber.is_approved==True).all()

            barber_id = data['barber_id']
            appointment_date = data['date']
            appointment_time = data['time']
            
            appointment = Appointments(
                client_id = client.id,
                barber_id = barber_id,
                appointment_date=appointment_date,
                appointment_time=appointment_time
            )
            db.session.add(appointment)
            db.session.commit()
            return jsonify({"Message":"Appointment made successfully"}),201

        except Exception as e:
            return jsonify({"Error booking appointment":str(e)}),400
    elif request.method == 'GET':
        appointments = db.session.query(Appointments).filter(Appointments.client_id==client).all()


@app.post('/manage_barber')
def manage_barber():
    data = request.json
    barber_id = data['barber_id']
    action = data['action']
    print(barber_id)
    print(action)
    
    barber = Barber.query.get(barber_id)
    if not barber:
        return jsonify({"Error": "Barber not found"}), 404
    if action == 'approve':
        barber.is_approved = True
        db.session.commit()
        return jsonify({"Message":"Barber approved"}),201
    elif action == 'reject':
        db.session.delete(barber)
        return jsonify({"Message":"Barber application rejected"}),201
   

# @app.post("/register_admin")
# def reg_admin():
#     try:
#         data = request.json
#         name = data['name']
#         email= data['email']
#         phone = data['phone']
#         password = data['password']
#         hashed_password = generate_password_hash(password)
#         admin = Admin(name=name,email=email,phone_number=phone,password=hashed_password)
#         db.session.add(admin)
#         db.session.commit()
#         return jsonify({"Message":"Admin created successfully"}),201
#     except  Exception as e:
#         return jsonify({"Error creating admin":str(e)}),500











    
    








if __name__=="__main__":
    app.run(debug=True)

        
        
