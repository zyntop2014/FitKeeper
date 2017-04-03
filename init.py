import psycopg2

try:
    con = psycopg2.connect("dbname='database' user='postgres' host='localhost' password='580430'")
except:
    print "I am unable to connect to the database"



cur = con.cursor()

cur.execute('DROP TABLE IF EXISTS restaurant CASCADE')
cur.execute('DROP TABLE IF EXISTS customer CASCADE ')
cur.execute('DROP TABLE IF EXISTS restaurant')
cur.execute('DROP TABLE IF EXISTS administrator CASCADE')
cur.execute('DROP TABLE IF EXISTS restaurant_table CASCADE')
cur.execute('DROP TABLE IF EXISTS manage')
cur.execute('DROP TABLE IF EXISTS notification')
cur.execute('DROP TABLE IF EXISTS party CASCADE')
cur.execute('DROP TABLE IF EXISTS waitlist')


cur.execute('CREATE TABLE restaurant (restaurant_id INT primary key, name TEXT)')
cur.execute('CREATE TABLE customer (customer_id INT primary key, first_name TEXT, last_name TEXT, phone_number TEXT, customer_email TEXT NOT NULL, UNIQUE(customer_email))')
cur.execute('CREATE TABLE administrator (admin_id INT primary key, email TEXT NOT NULL, UNIQUE(email), user_name TEXT NOT NULL, UNIQUE(user_name), encypted_password TEXT)')
cur.execute('CREATE TABLE restaurant_table(table_id INT, seats INT NOT NULL CHECK (seats> 0), restaurant_id INT, PRIMARY KEY (table_id, restaurant_id), FOREIGN KEY (restaurant_id) REFERENCES restaurant ON DELETE CASCADE)')
cur.execute('CREATE TABLE manage(restaurant_id INT, admin_id INT, PRIMARY KEY (admin_id, restaurant_id), FOREIGN KEY (restaurant_id) REFERENCES restaurant, FOREIGN KEY (admin_id) REFERENCES administrator)')
cur.execute('CREATE TABLE notification(body TEXT NOT NULL, type TEXT NOT NULL, sent_at TIMESTAMP,restaurant_id INT , customer_id INT,  PRIMARY KEY (sent_at, restaurant_id, customer_id), FOREIGN KEY (restaurant_id) REFERENCES restaurant ON DELETE CASCADE, FOREIGN KEY (customer_id) REFERENCES customer ON DELETE CASCADE)')
cur.execute('CREATE TABLE party(size INT CHECK (size >0), customer_id INT, party_datetime TIMESTAMP, table_id INT, restaurant_id INT, seated_datetime TIMESTAMP, finished_at TIMESTAMP, PRIMARY KEY (party_datetime, customer_id), FOREIGN KEY (customer_id) REFERENCES customer ON DELETE CASCADE, FOREIGN KEY (table_id, restaurant_id) REFERENCES restaurant_table (table_id, restaurant_id)ON DELETE CASCADE)')
cur.execute('CREATE TABLE waitlist(restaurant_id INT, customer_id INT, party_datetime TIMESTAMP, listed_at TIMESTAMP NOT NULL, unlisted_at TIMESTAMP, PRIMARY KEY (party_datetime, customer_id, restaurant_id), FOREIGN KEY (party_datetime, customer_id) REFERENCES party (party_datetime, customer_id), FOREIGN KEY (restaurant_id) REFERENCES restaurant)')




con.commit()

con.close()
