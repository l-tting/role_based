from models import app,db,Client,Barber,Admin,Appointments
from flask import request,redirect,url_for,jsonify
from werkzeug.security import generate_password_hash,check_password_hash

@app.route('/register_client',methods=['GET','POST'])
def register_client():
    if request.method== 'POST':
        data = request.json
        username = data['username']
        phone_number = data['phone']
        password = data['password']
        existing_client = db.session.query(Client).filter(Client.phone_number==phone_number).first()
        if existing_client:
            return jsonify({"Message":"User already exists please login"})
        hashed_password = generate_password_hash(password)
        new_client = Client(username=username,phone_number=phone_number,password=hashed_password)
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
        first_name = data['first_name']
        last_name = data['last_name']
        email = data['email']
        phone_number = data['phone']
        password = data["password"]
        existing_barber = db.session.query(Barber).filter(Barber.email==email).first()
        if existing_barber :
            return jsonify({"Message":"User already exists please login"})
        hashed_password = generate_password_hash(password)
        new_barber = Barber(first_name=first_name,last_name=last_name,email=email,phone_number=phone_number,password=hashed_password)
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

    
if __name__=="__main__":
    app.run(debug=True)

        
        
