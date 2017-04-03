from flask import Flask, render_template, request, g, redirect, url_for, session, flash

import sqlite3 as sql

from functools import wraps

import psycopg2

app = Flask(__name__)

app.secret_key = 'my precious'

# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            #flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    user_password = False

    if request.method == 'POST':

        db = get_db()  
        cur=db.cursor()     
        cur.execute("select * from administrator")
        rows= cur.fetchall();

        for row in rows:
            if request.form['username'] == row[2] and request.form['password'] == row[3]:
               user_password = True  

        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            user_password = True 

        if user_password:
            session['logged_in'] = True
            #flash('You were logged in.')
            return redirect(url_for('index'))
           
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('welcome'))

DATABASE = 'database.db'
def get_db():
    db = psycopg2.connect("dbname='database' user='postgres' host='localhost' password='580430'")
    
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/reservation')
@login_required
def admin():
    return render_template('reservations/index.html')

@app.route('/waitlist')
@login_required
def waitlist():
    return render_template('waitlist.html')


@app.route('/restaurant')
@login_required
def restaurant():
    return render_template('restaurant.html')

@app.route('/customer')
@login_required
def customer():
    return render_template('customer.html')

@app.route('/buslist')
@login_required
def buslist2():
    db = get_db()
    cur=db.cursor()
    if request.values.has_key('restaurant_id') and len(request.values['restaurant_id']) > 0:
        if request.values.has_key('waiting'):
            cur.execute("select * from waitlist WHERE restaurant_id=%s AND unlisted_at IS NULL ORDER BY listed_at", request.values['restaurant_id'])
        else:
            cur.execute("select * from waitlist WHERE restaurant_id=%s ORDER BY listed_at", request.values['restaurant_id'])
    else:
        if request.values.has_key('waiting'):
            cur.execute("select * from waitlist WHERE unlisted_at IS NULL ORDER BY listed_at")
        else:
            cur.execute("select * from waitlist ORDER BY listed_at")
    rows = cur.fetchall();
    return render_template("buslist/index.html", rows=rows)


@app.route('/customerlist')
@login_required
def list():
    con = get_db()
    cur = con.cursor()
    cur.execute("select * from customer")
    rows = cur.fetchall();
    return render_template("customerlist.html", rows=rows)



@app.route('/buslist')
@login_required
def retaurantlist():
    con = get_db()
    cur = con.cursor()
    cur.execute("select * from restaurant")
    rows = cur.fetchall();
    return render_template("buslist.html", rows=rows)

@app.route('/tablelist')
@login_required
def tablelist():
    con = get_db()
    cur = con.cursor()
    cur.execute("select restaurant.restaurant_id, restaurant.name, restaurant_table.table_id , restaurant_table.seats from restaurant_table, restaurant where restaurant_table.restaurant_id = restaurant.restaurant_id")
    rows = cur.fetchall();
    return render_template("tablelist.html", rows=rows)

@app.route('/waitlistlist')
@login_required
def waitlistlist():
    con = get_db()
    cur = con.cursor()
    cur.execute("select * from waitlist")
    rows = cur.fetchall();
    return render_template("waitlistlist.html", rows=rows)

@app.route('/adminlist')
@login_required
def adminlist():
    con = get_db()
    cur = con.cursor()
    cur.execute("select * from administrator")
    rows = cur.fetchall();
    return render_template("adminlist.html", rows=rows)

@app.route('/notificationlist')
@login_required
def notificationlist():
    con = get_db()
    cur = con.cursor()
    cur.execute("select * from notification")
    rows = cur.fetchall();
    return render_template("notificationlist.html", rows=rows)

@app.route('/partylist')
@login_required
def partylist():
    con = get_db()
    cur = con.cursor()
    cur.execute("select * from party")
    rows = cur.fetchall();
    return render_template("partylist.html", rows=rows)

@app.route('/enteradmin')
@login_required
def new_admin():
    return render_template('enteradmin.html', url = 'admin')


@app.route('/enterwaitlist')
@login_required
def new_waitlist():
    return render_template('enterwaitlist.html', url = 'index')


@app.route('/entercustomer', methods=['GET', 'POST'])
@login_required
def entercustomer():
    return render_template('entercustomer.html', url="customer")

@app.route('/enterparty')
@login_required
def new_party():
    return render_template('enterparty.html', url = 'waitlist')

@app.route('/enternotification')
@login_required
def new_notification():
    return render_template('enternotification.html', url = 'waitlist')


@app.route('/entermanage')
@login_required
def new_manage():
    return render_template('entermanage.html', url = 'admin')

@app.route('/entertable')
@login_required
def new_table():
    return render_template('entertable.html')




@app.route('/enterrestaurant')
@login_required
def new_restaurant():
    return render_template('enterrestaurant.html')

@app.route('/addrecadmin', methods=['POST', 'GET'])
@login_required
def addrecadmin():
    if request.method == 'POST':

        
        try:
            
            idn = request.form['id']
            email = request.form['email']
            nm = request.form['nm']
            pin= request.form['pin']
            

            with get_db() as con:
                cur = con.cursor()    
                cur.execute("INSERT INTO administrator VALUES (%s, %s, %s, %s)", (idn,email, nm, pin))
                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("enteradmin.html", msg=msg, url = "admin")
            con.close()

@app.route('/addrecparty', methods=['POST', 'GET'])
@login_required
def addrecparty():
    if request.method == 'POST':

        
        try:
            
            size = request.form['size']
            customer_id= request.form['customer_id']
            party_datetime= request.form['party_datetime']
            table_id= request.form['table_id']
            restaurant_id= request.form['restaurant_id']
            seated_datetime= request.form['seated_datetime']
            finish_at= request.form['finish_at']
          
            

            with get_db() as con:
                cur = con.cursor()    
                cur.execute("INSERT INTO party VALUES (%s, %s, %s, %s, %s, %s, %s)", (size, customer_id, party_datetime, table_id, restaurant_id, seated_datetime, finish_at))
                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("enterparty.html", msg=msg, url = "waitlist")
            con.close()

@app.route('/addrecwaitlist', methods=['POST', 'GET'])
@login_required
def addrecwaitlist():
    if request.method == 'POST':

        
        try:
            
            restaurant_id = request.form['restaurant_id']
            customer_id= request.form['customer_id']
            party_datetime= request.form['party_datetime']
            listed_at= request.form['listed_at']
            unlisted_at= request.form['unlisted_at']
          
            

            with get_db() as con:
                cur = con.cursor()    
                cur.execute("INSERT INTO waitlist VALUES (%s, %s, %s, %s, %s)", (restaurant_id, customer_id, party_datetime, listed_at, unlisted_at))
                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("enterwaitlist.html", msg=msg, url = "/")
            con.close()

@app.route('/addrecnotification', methods=['POST', 'GET'])
@login_required
def addrecnotification():
    if request.method == 'POST':    
        try:
            
            body= request.form['body']
            ntype= request.form['type']
            sent_at= request.form['sent_at']
            restaurant_id= request.form['restaurant_id']
            customer_id= request.form['customer_id']
  
            with get_db() as con:
                cur = con.cursor()    
                cur.execute("INSERT INTO notification VALUES (%s, %s, %s, %s, %s)", (body, ntype, sent_at, restaurant_id, customer_id))
                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("enternotification.html", msg=msg, url = "waitlist")
            con.close()

@app.route('/addrecmanage', methods=['POST', 'GET'])
@login_required
def addrecmanage():
    if request.method == 'POST':

        
        try:
            
            idn = request.form['admin_id']
            res_id = request.form['res_id']

            with get_db() as con:
                cur = con.cursor()    
                cur.execute("INSERT INTO manage VALUES (1, 1)")
                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("entermanage.html", msg=msg, url = "admin")
            con.close()


@app.route('/addreccustomer', methods=['POST', 'GET'])
@login_required
def addreccustomer():
    if request.method == 'POST':

        msg = "Record successfully added"
        try:
            idn= request.form['id']
            first_nm = request.form['first_nm']
            last_nm= request.form['last_nm']
            phone = request.form['phone']
            email = request.form['email']

            with get_db() as con:
                cur = con.cursor()    
                cur.execute("INSERT INTO customer VALUES (%s, %s, %s, %s, %s)", (idn,first_nm, last_nm, phone, email))
                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("entercustomer.html", msg=msg, url = "customer")
            con.close()

@app.route('/addrectable', methods=['POST', 'GET'])
@login_required
def addrectable():
    if request.method == 'POST':

        msg = "Record successfully added"
        try:
            table_id= request.form['table_id']
            seats= request.form['seats']
            restaurant_id = request.form['restarant_id']
            
           

            with get_db() as con:
                cur = con.cursor()    
                cur.execute("INSERT INTO restaurant_table VALUES (%s, %s, %s)", (table_id, seats, restaurant_id))
                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("entertable.html", msg=msg, url = "restaurant")
            con.close()


@app.route('/addrecrestaurant', methods=['POST', 'GET'])
@login_required
def addrecrestaurant():
    if request.method == 'POST':

        msg = "Record successfully added"
        try:
            
            idn = request.form['id']
            nm = request.form['nm']
            

            with get_db() as con:
                cur = con.cursor()    
                cur.execute("INSERT INTO restaurant VALUES (%s, %s)", (idn,nm))
                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("enterrestaurant.html", msg=msg, url = "restaurant")
            con.close()


@app.route('/searchtable', methods=['GET', 'POST'])
@login_required
def searchtable():
    if request.method == "POST":
        db = get_db()
        cur=db.cursor()
        restaurant_name= request.form['restaurant_name']
        seats= request.form['seats']
        cur.execute("select r.restaurant_id, r.name, rt.table_id, rt.seats from restaurant_table rt, restaurant r where rt.restaurant_id = r.restaurant_id and rt.seats >= %s ", [seats])
        rows= cur.fetchall();
        return render_template('searchtable.html', rows1 = rows)
    return render_template('searchtable.html', rows1 = [])

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == "POST":
        db = get_db()
        cur=db.cursor()
        customer_id= request.form['customer_id']
        cur.execute("select * from customer where customer_id= %s", [customer_id])
        rows= cur.fetchall();
        return render_template('search.html', rows1 = rows)
    return render_template('search.html', rows1 = [])
        
@app.route('/search2', methods=['GET', 'POST'])
@login_required
def search2():
    if request.method == "POST":
        db = get_db()
        cur=db.cursor()
        customer_id= request.form['customer_id']
        cur.execute("select * from customer where customer_id= %s", [customer_id])
        rows= cur.fetchall();
        return render_template('search.html', rows2 = rows)
    return render_template('search.html', rows2 = [])   


@app.route('/deleteadmin', methods=['POST', 'GET'])
@login_required
def deleteadmin():
    if request.method == 'POST':

        msg = "Record successfully Deleted"
        try:
            id_admin= request.form['id']
            print id_admin
        
            with get_db() as con:
                cur = con.cursor()    
                cur.execute("DELETE  from administrator where admin_id= %s ", (id_admin))
                con.commit()
                msg = "Record successfully Deleted"
        except:
            con.rollback()
            msg = "error in delete operation"

        finally:
            return render_template("result.html", msg=msg, url = "admin")
            con.close()

@app.route('/deletewaitlist', methods=['POST', 'GET'])
@login_required
def deletewaitlist():
    if request.method == 'POST':

        msg = "Record successfully Deleted"
        try:
            restaurant_id= request.form['restaurant_id']
            customer_id = request.form['customer_id']
            party_datetime = request.form['party_datetime']
         
            with get_db() as con:
                cur = con.cursor()    
                cur.execute("DELETE  from waitlist where restaurant_id= %s and customer_id = %s and party_datetime = %s ", (restaurant_id, customer_id, party_datetime))
                con.commit()
                msg = "Record successfully Deleted"
        except:
            con.rollback()
            msg = "error in delete operation"

        finally:
            return render_template("result.html", msg=msg, url = "/")
            con.close()

@app.route('/deleteparty', methods=['POST', 'GET'])
@login_required
def deleteparty():
    if request.method == 'POST':

        msg = "Record successfully Deleted"
        try:
            customer_id= request.form['customer_id']
            party_datetime= request.form['party_time']
        
            with get_db() as con:
                cur = con.cursor()    
                cur.execute("DELETE  from party where customer_id= %s AND party_datetime= %s", (customer_id, party_datetime))
                con.commit()
                msg = "Record successfully Deleted"
        except:
            con.rollback()
            msg = "error in delete operation"

        finally:
            return render_template("result.html", msg=msg, url = "waitlist")
            con.close()

@app.route('/deletenotification', methods=['POST', 'GET'])
@login_required
def deletenotification():
    if request.method == 'POST':

        msg = "Record successfully Deleted"
        try:
            
            sent_at= request.form['sent_at']
            restaurant_id= request.form['restaurant_id']
            customer_id= request.form['customer_id']
        
            with get_db() as con:
                cur = con.cursor()    
                cur.execute("DELETE  from notification where sent_at=%s AND restaurant_id =%s and customer_id= %s", (sent_at, restaurant_id, customer_id))
                con.commit()
                msg = "Record successfully Deleted"
        except:
            con.rollback()
            msg = "error in delete operation"

        finally:
            return render_template("result.html", msg=msg, url = "waitlist")
            con.close()

@app.route('/deleterestaurant', methods=['POST', 'GET'])
@login_required
def deleterestaurant():
    if request.method == 'POST':

        msg = "Record successfully Deleted"
        try:
            id_restaurant= request.form['id']
            with get_db() as con:
                cur = con.cursor()    
                cur.execute("DELETE FROM restaurant where restaurant_id= %s ", (id_restaurant))
                con.commit()
                msg = "Record successfully Deleted"
        except:
            con.rollback()
            msg = "error in delete operation"

        finally:
            return render_template("result.html", msg=msg, url ="restaurant")
            con.close()
    
@app.route('/deletetable', methods=['POST', 'GET'])
@login_required
def deletetable():
    if request.method == 'POST':

        #msg = "Record successfully Deleted"
        try:
            id_table= request.form['table_id']
            print id_table
         
        

            with get_db() as con:
                cur = con.cursor()    
                cur.execute("DELETE  from restaurant_table where table_id= %s ", (id_table))
                con.commit()
                msg = "Record successfully Deleted"
        except:
            con.rollback()
            msg = "error in delete operation"

        finally:
            return render_template("result.html", msg=msg, url = "restaurant")
            con.close()


@app.route('/deletecustomer', methods=['POST', 'GET'])
@login_required
def deletecustomer():
    if request.method == 'POST':

        msg = "Record successfully Deleted"
        try:
            id_admin= request.form['id']
            print id_admin
            
        

            with get_db() as con:
                cur = con.cursor()    
                cur.execute("DELETE  from customer where customer_id= %s ", (id_admin))
                con.commit()
                msg = "Record successfully Deleted"
        except:
            con.rollback()
            msg = "error in delete operation"

        finally:
            return render_template("result.html", msg=msg, url = "customer")
            con.close()



if __name__ == '__main__':
    app.run(debug=True)
