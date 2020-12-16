from connection_to_db import engine
from db import Users, Menu, Review, Reservation, Order, Base, Prediction
from sqlalchemy.sql import select, update, join
from sqlalchemy import and_, or_, between, asc, desc, update
from sqlalchemy.orm import sessionmaker
import time
import numpy as np
import pandas as pd
import plotly.express as px
from flask import Flask, render_template, redirect, url_for, request, session
import datetime
from datetime import date, timedelta
from tensorflow import keras
import joblib
import hashlib

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "sashakovalenkoloh"
app.permanent_session_lifetime = timedelta(days = 5)

app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:1111@localhost/cafe"
app.config['WHOOSH_BASE'] = 'whoosh'
db = SQLAlchemy(app)

Base.metadata.create_all(engine)
Session_app = sessionmaker(bind=engine)
session_app = Session_app()



@app.route('/')
def main_page():
    if ('email' in session) and (session['email'] == 'admin'):
        return redirect('/admin_coment')
    return redirect('/menu')


@app.route('/sign_up',methods=['POST','GET'])
def regestration():
    session.pop("email", None)
    session.pop("name", None)
    if request.method == 'POST':
        session.permanent = True
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        birthday = request.form['birthday']
        try:
            password = hashlib.sha256(password.encode('ascii')).hexdigest()
            row = Users(name=name, email=email, password=password, birthday=birthday,
                        total_order_amount=0, discount=0)
            session_app.add(row)

            session_app.commit()
            session['email'] = email
            session['name'] = name
            return redirect('/menu')


        except:
            try:
                check = session_app.query(Users).filter_by(email=email).all()
                session_app.commit()
                if check != []:
                    return render_template("sign_up.html", action=2, name=None, email=None)
            except:
                return render_template("sign_up.html", action=1, name=None, email=None)


    else:
        return render_template("sign_up.html", name=None, email=None)



@app.route('/sign_in', methods=['POST','GET'])
def sign_in():
    session.pop("email", None)
    session.pop("name", None)

    if request.method == 'POST':
        email_text = request.form['email']
        password = request.form['password']
        password_text = hashlib.sha256(password.encode('ascii')).hexdigest()

        if (email_text == 'admin' and password == 'admin'):
            session.permanent = True
            session['name'] = 'admin'
            session['email'] = 'admin'
            return redirect('/admin_coment')
            #pwrd = admin
        elif (email_text == 'admin' and password != 'admin'):
            return render_template('sign_in.html', email=None, name=None, action=1)

        try:
            check = session_app.query(Users).filter_by(email=email_text, password=password_text).all()
            session_app.commit()
            if check != []:
                for i in check:
                    session.permanent = True
                    session['name'] = i.name
                    session['email'] = i.email
                    return redirect('/menu')
            else:
                return render_template('sign_in.html', email=None, name=None, action=1)


        except:
            return render_template('sign_in.html', email=None, name=None, action=1)
    else:
        return render_template('sign_in.html', email=None, name=None)

@app.route('/comments',methods=['POST','GET'])
def comment():
    if 'email' in session:
        email = session['email']
        name = session['name']
    else:
        email = None
        name = None
    if request.method == 'POST':
        if email != None:
            comment = request.form['comment']

            current_date = datetime.datetime.now()
            date = current_date.strftime("%d"), current_date.strftime("%b"), current_date.strftime("%Y")
            date = ' '.join(date)

            all = session_app.query(Review).all()
            i = 1
            for a in all:
                i = i+1

            row = Review(comment_id=i, name=name, email=email, comment=comment, date=date)
            session_app.add(row)
            query = session_app.query(Review).all()
            session_app.commit()
            return render_template('coment.html', comments=query, email=email, name=name)

        else:
            query = session_app.query(Review).all()
            return render_template('coment.html', comments=query, email=email, name=name, action=1)

    else:
        query = session_app.query(Review).all()

        return render_template('coment.html', comments=query, email=email,name=name)


@app.route('/reserv',methods=['POST','GET'])
def reserv():
    if 'email' in session:
        email = session ['email']
        name = session ['name']
    else:
        email = None
        name = None

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%Y-%m-%d")
    d = int(now.strftime("%d"))+5
    m = int(now.strftime("%m"))
    y = int(now.strftime("%Y"))
    if d<10:
        future = (f"{y}-{m}-0{d}")
    else:
        future = (f"{y}-{m}-{d}")
    if request.method == 'POST':
        if email != None:

            date = request.form['date']
            time = request.form['time']
            table = request.form['table']

            all = session_app.query(Reservation).all()
            list = []
            for a in all:
                list.append(a.reserv_id)

            if list == []:
                i = 1
            else:
                i = max(list)+1

            row = Reservation(reserv_id=i, name=name, email=email, table=table, date=date,
                              time=time, reserv_status='1')
            session_app.add(row)
            session_app.commit()
            return redirect('/menu')
        else:
            return render_template('reserv.html', email=email, name=name, c_time=current_time,
                                   c_date=current_date, future=future)
    else:
        try:
            check = session_app.query(Reservation).filter_by(email=email).all()
            session_app.commit()

            return render_template('reserv.html', email=email, name=name, check=check,
                                   c_time=current_time, c_date=current_date, future=future)
        except:
            return render_template('reserv.html', email=email, name=name,
                                   c_time=current_time, c_date=current_date, future=future)



@app.route('/menu',methods=['POST','GET'])
def menu():
    if 'email' in session:
        email = session['email']
        name = session['name']
    else:
        email = None
        name = None

    if request.method == 'POST':
        item_id = request.form['index']
        item = request.form['item']
        if email != None:

            all = session_app.query(Order).all()
            list = []
            for a in all:
                list.append(a.order_id)

            if list ==[]:
                i = 1
            else:
                i = max(list) + 1

            row = Order(order_id=i, email=email, item_id=item_id, item=item, order_status=0)
            session_app.add(row)
            session_app.commit()
            return render_template('menu.html', email=email,name=name )

        else:
            return render_template('menu.html', email=email)
    else:
        email = email

        return render_template('menu.html', email=email, name=name)






@app.route('/order', methods=['POST', 'GET'])
def order():
    if 'email' in session:
        email = session['email']
        name = session['name']
    else:
        email = None
        name = None

    if request.method == 'POST':
        delete = request.form['deletee']
        item = request.form['item']

        if delete == 'on':
            delete_query = session_app.query(Order).filter_by(email=email, item=item, order_status=0).first()
            session_app.delete(delete_query)
            session_app.commit()
            orders = session_app.query(Order).filter_by(email=email, order_status=0).all()
            order = []
            for i in orders:
                order.append(i.item_id)

            price = []
            for i in order:
                list = session_app.query(Menu).filter_by(item_id=i).all()
                for pric in list:
                    price.append(pric.price)

            names = []
            for it in orders:
                names.append(it.item)

            orders = np.stack((names, price), axis=1)
            orders_e = orders.tolist()
            summ = 0
            for i in price:
                summ = summ + i
            for i in session_app.query(Users).filter_by(email=email).all():
                if i.discount != '':
                    dis_sum = summ * (100 - i.discount) / 100
                else:
                    dis_sum = summ

            orders = np.stack((names, price), axis=1)
            return render_template('order.html', email=email, name=name, orders=orders_e, summ=summ, dis_sum=dis_sum)

        else:
            table = request.form['table']
            sale = request.form['sale']

            orders = session_app.query(Order).filter_by(email=email, order_status=0).all()
            order = []
            for i in orders:
                order.append(i.item_id)
            price = []
            for i in order:
                list = session_app.query(Menu).filter_by(item_id=i).all()
                for pric in list:
                    price.append(pric.price)
            summ = 0
            for i in price:
                summ = summ + i


            index = 1

            for i in session_app.query(Order).filter_by(email=email, order_status=0).all():
                i.table = table
                session_app.merge(i)
                i.order_status = index
                session_app.merge(i)
            orders = 'abs'
            add_orders_in_base()
            for i in session_app.query(Order).filter_by(email=email, order_status=1).all():
                if (float(sale) - float(summ)) == 0:
                    i.order_status = 21
                else:
                    i.order_status = 22
                session_app.merge(i)
            #add_orders_in_base()
            session_app.commit()

            return render_template('order.html', email=email, name=name, orders=orders)



    else:

        orders = session_app.query(Order).filter_by(email=email, order_status=0).all()

        order = []
        for i in orders:
            order.append(i.item_id)

        price = []
        for i in order:
            list = session_app.query(Menu).filter_by(item_id=i).all()
            for pric in list:
                price.append(pric.price)

        names =[]
        for it in orders:
            names.append(it.item)

        orders = np.stack((names, price), axis=1)
        orders = orders.tolist()
        summ = 0
        dis_sum = summ
        for i in price:
            summ = summ + i
        for i in session_app.query(Users).filter_by(email=email).all():
            if i.discount != '':
                dis_sum = summ * (100-i.discount)/100
            else:
                dis_sum = summ

        return render_template('order.html', email=email, name=name, orders=orders, summ=summ, dis_sum=dis_sum)


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if 'email' in session:
        email = session ['email']
        name = session ['name']
    else:
        email = None
        name = None
    if email == None:
        return redirect('/sign_up')
    if request.method == 'POST':
        new_name = request.form['name']
        new_email = request.form['email']
        new_password = request.form['password']
        new_birthday = request.form['birthday']
        if new_name != '':
            for i in session_app.query(Users).filter_by(email=email).all():
                i.name = new_name
                session_app.merge(i)
                session.pop("name", None)
                session['name'] = new_name
                session_app.commit()
        if new_email != '':
            for i in session_app.query(Users).filter_by(email=email).all():
                i.email = new_email
                session_app.merge(i)
                session.pop("email", None)
                session['email'] = new_email
                session_app.commit()
        if new_password != '':
            new_password = hashlib.sha256(new_password.encode('ascii')).hexdigest()
            for i in session_app.query(Users).filter_by(email=email).all():
                i.password = new_password
                session_app.merge(i)
                session_app.commit()
        if new_birthday != '':
            for i in session_app.query(Users).filter_by(email=email).all():
                i.birthday = new_birthday
                session_app.merge(i)
                session_app.commit()
        user = session_app.query(Users).filter_by(email=email).all()
        return render_template('profile.html', email=email, name=name, user=user)
    else:
        user = session_app.query(Users).filter_by(email=email).all()
        return render_template('profile.html', email=email, name=name, user=user)


def add_orders_in_base():
    email = session['email']
    list = []
    orders = session_app.query(Order).filter_by(email=email, order_status=1).all()
    for order in orders:
        list.append(order.item_id)
    summ = 0
    for i in list:
        price = session_app.query(Menu).filter_by(item_id=i).first()
        summ = summ + price.price


    for i in session_app.query(Users).filter_by(email=email).all():
        d = i.total_order_amount
        i.total_order_amount = d + summ
        total = d + summ
        session_app.merge(i)
        session_app.commit()

    if total >= 5000:
        for i in session_app.query(Users).filter_by(email=email).all():
            i.discount = 10
            session_app.merge(i)
            session_app.commit()

    if total >= 20000:
        for i in session_app.query(Users).filter_by(email=email).all():
            i.discount = 15
            session_app.merge(i)
            session_app.commit()



def only(l):
    n = []
    for i in l:
        if i not in n:
            n.append(i)
    return n

def data_get(user):
    data = []
    for i in user:
        for n in session_app.query(Users).filter_by(email=i).all():
            name = n.name
            email = n.email
            discount = n.discount
        goods = []
        item_id_1 = []
        item_id_2 = []
        table = []
        for dis in session_app.query(Users).filter_by(email=i).all():
            discount = dis.discount
        discount = (100 - discount)/100
        for o in session_app.query(Order).filter_by(email=i, order_status=21).all():
            goods.append(o.item)
            item_id_1.append(o.item_id)
            table.append(o.table)
        for o in session_app.query(Order).filter_by(email=i, order_status=22).all():
            goods.append(o.item)
            item_id_2.append(o.item_id)
            table.append(o.table)
        price_1 = []
        price_2 = []
        for item in item_id_1:
            for m in session_app.query(Menu).filter_by(item_id=item).all():
                price_1.append(m.price)
        for item in item_id_2:
            for m in session_app.query(Menu).filter_by(item_id=item).all():
                price_2.append(m.price * discount)
        price = sum(price_1) + sum(price_2)
        data.append([email, name, goods, price, table [0]])
    return data


@app.route('/admin_order', methods=['POST', 'GET'])
def admin_order():
    if (session ['email'] == 'admin'):
        if request.method == 'POST':
            delete = request.form['delete']
            item = request.form['item']
            current_date = datetime.datetime.now()
            date = current_date.strftime("%d"), current_date.strftime("%b"), current_date.strftime("%Y")
            date = ' '.join(date)
            if delete == 'on':
                delete_query = session_app.query(Order).filter_by(email=item).all()
                for i in delete_query:
                    session_app.delete(i)
                    session_app.commit()

                if (session_app.query(Prediction).filter_by(date=date).all() == []):
                    dq =[]
                    n = session_app.query(Prediction).all()
                    for i in n:
                        dq.append(i.id)
                    id = max(dq) + 1

                    new_row = Prediction(id=id, date=date, number=1)
                    session_app.add(new_row)
                    session_app.commit()
                else:
                    for i in session_app.query(Prediction).filter_by(date=date).all():
                        i.number = i.number + 1
                        session_app.merge(i)
                        session_app.commit()


            use = []
            users = session_app.query(Order).filter_by(order_status=21).all()
            for i in users:
                use.append(i.email)
            users = session_app.query(Order).filter_by(order_status=22).all()
            for i in users:
                use.append(i.email)

            user = only(use)
            data = data_get(user)
            return render_template('admin_order.html', data=data, email='admin', name='Admin')
        else:

            use = []
            users = session_app.query(Order).filter_by(order_status=21).all()
            for i in users:
                use.append(i.email)
            users = session_app.query(Order).filter_by(order_status=22).all()
            for i in users:
                use.append(i.email)
            user = only(use)

            data = data_get(user)
            if data != []:
                return render_template('admin_order.html', data=data, email='admin', name='Admin')
            else:
                return render_template('admin_order.html', data='no_orders', email='admin', name='Admin')
    else:
        return render_template('sign_in.html', email=None, name=None)


@app.route('/admin_coment')
def admin_coment():
    if (session['email'] == 'admin'):
        query = session_app.query(Review).all()
        return render_template('admin_coment.html', comments=query, email='admin', name='Admin')


@app.route('/admin_reserv',  methods=['POST', 'GET'])
def admin_reserv():
    if (session ['email'] == 'admin'):
        if request.method == 'POST':
            delete = request.form ['delete']
            item = request.form ['item']
            if delete == 'on':
                delete_query = session_app.query(Reservation).filter_by(email=item).first()
                session_app.delete(delete_query)
                session_app.commit()

            data = []
            reservation = session_app.query(Reservation).all()
            for client in reservation:
                name = client.name
                date = client.date
                time = client.time
                table = client.table
                email = client.email
                data.append([name, date, time, table, email])

            return render_template('admin_reserv.html', data=data, email='admin', name='Admin')
        else:
            data = []
            reservation = session_app.query(Reservation).all()
            for client in reservation:
                name = client.name
                date = client.date
                time = client.time
                table = client.table
                email = client.email
                data.append([name, date, time, table,email])
            if data != []:
                return render_template('admin_reserv.html', data=data, email='admin', name='Admin')
            else:
                return render_template('admin_reserv.html', data='no_data', email='admin', name='Admin')


@app.route('/admin_add_user', methods=['POST', 'GET'])
def add_user_to_base():
    if request.method == 'POST':
        session.permanent = True
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        birthday = request.form['birthday']
        try:
            password = hashlib.sha256(password.encode('ascii')).hexdigest()
            row = Users(name=name, email=email, password=password, birthday=birthday,
                        total_order_amount=0, discount=0)
            session_app.add(row)
            session_app.commit()
            user = session_app.query(Users).filter_by(email=email).all()
            return render_template("admin_add_user.html", name='Admin', email='admin', act='on', user=user)


        except:
            try:
                check = session_app.query(Users).filter_by(email=email).all()

                if check != None:
                    return render_template("admin_add_user.html", action=2, name='Admin', email='admin', act='off')
            except:
                #else:
                return render_template("admin_add_user.html", action=1, name='Admin', email='admin', act='off')
    else:
        return render_template("admin_add_user.html", name='Admin', email='admin', act='off')




def prediction(data, model,transformer_X,transformer_y):
    data_ = transformer_X.transform(data.reshape(-1, data.shape [-1])).reshape(data.shape)
    prediction = model.predict(data_)
    result = transformer_y.inverse_transform(prediction).astype('int32')
    return result

def plot():
    df = pd.read_csv("cafedata/y_predicted.csv")
    fig = px.line(df)
    #fig.show()
    return fig

@app.route('/admin_get_prediction', methods=['POST', 'GET'])
def add_get_prediction():
    if (session ['email'] == 'admin'):
        model = keras.models.load_model("cafedata/cafemodel")
        transformer_X = joblib.load("cafedata/x_transformer.joblib")
        transformer_y = joblib.load("cafedata/y_transformer.joblib")
        data = []
        da = session_app.query(Prediction).all()
        for i in da:
            data.append(i.number)
        data = data[-7:]
        data = np.array(data).reshape((7, 1, 1))
        answer = prediction(data, model,transformer_X,transformer_y)[0][0]
        if request.method == 'GET':
            return render_template("admin_get_prediction.html", name='Admin', email='admin', ans=answer)
        else:
            value = request.form['value']

            if value == 'on':
                fig = plot()
                fig.show()
                return render_template("admin_get_prediction.html", name='Admin', email='admin', ans=answer)

            return render_template("admin_get_prediction.html", name='Admin', email='admin', ans=answer)

@app.route('/error')
def error():
    if 'email' in session:
        email = session['email']
        name = session['name']
    else:
        email = None
        name = None
    return render_template('404.html', email=email, name=name)


@app.route('/<action>', methods=['GET'])
def actinfo(action):
    if action == "order.html":
        return redirect('/order')
    elif action == "menu.html":
        return redirect('/menu')
    elif action == "coment.html":
        return redirect('/comments')
    elif action == "profile.html":
        return redirect('/profile')
    elif action == "reserv.html":
        return redirect('/reserv')
    elif action == "sign_in.html":
        return redirect('/sign_in')
    elif action == "sign_up.html":
        return redirect('/sign_up')
    elif action == "admin_order.html":
        return redirect('/admin_order')
    elif action == "admin_coment.html":
        return redirect('/admin_coment')
    elif action == "admin_reserv.html":
        return redirect('/admin_reserv')
    elif action == "admin_add_user.html":
        return redirect('/admin_add_user')
    elif action == "admin_get_prediction.html":
        return redirect('/admin_get_prediction')
    else:
        return redirect('/error')


session_app.commit()

if __name__ == "__main__":
    app.run(port=5070, debug=True)