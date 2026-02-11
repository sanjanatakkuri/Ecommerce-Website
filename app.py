from flask import Flask, render_template, request, url_for,session,redirect, Response
import pymysql
import smtplib
from email.message import EmailMessage
import random


app = Flask(__name__)

db_config={
    "host": "localhost",
    "user":"root",
    "password":"root",
    "database":"bookstore_1"
}

admin_email = 'sanjanatakkuri1@gmail.com'
admin_password = 'boam xthb hpqh ndjc'

def send_mail(to_email, body):    
    msg = EmailMessage()
    msg.set_content(body)
    msg['To'] = to_email
    msg['From'] = admin_email
    msg['Subject'] = 'OTP verification'
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(admin_email, admin_password)
        smtp.send_message(msg)

def get_connection():
    conn = pymysql.Connection(**db_config)    
    return conn

def db_init():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS PRODUCTS
        (PID INT PRIMARY KEY AUTO_INCREMENT,
         PNAME VARCHAR(30) NOT NULL,
         PIMAGE LONGBLOB NOT NULL,
         PCATEGORY VARCHAR(15) NOT NULL,
         PAPRICE INT NOT NULL,
         PDPRICE INT NOT NULL,
         PSTOCK INT NOT NULL            
        )
        ''')
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS USERS
        (
        USERID INT PRIMARY KEY AUTO_INCREMENT,
        USERNAME VARCHAR(30) NOT NULL,
        USERMAIL VARCHAR(40) NOT NULL,
        USERPHONE BIGINT NOT NULL,
        USERPASSWORD VARCHAR(15) NOT NULL
        )''')
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS CART
        (
        USERID INT NOT NULL,
        PID INT NOT NULL,
        QUANTITY INT NOT NULL
        )
        '''
    )   
    cursor.close()
    conn.close()
    
    
db_init()

@app.route('/home')
@app.route('/')
def home():    
    return render_template('home.html')

@app.route('/adminlogin1', methods = ['POST', 'GET'])
def adminlogin1():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')        
        if username == 'admin' and password == 'admin':
            return render_template('admin_dashboard.html')
        if username == 'admin' and password != 'admin':
            message =  'Incorrect Password'
        if username != 'admin' and password == 'admin':
            message =  'Incorrect Username'
        if username != 'admin' and password != 'admin':
            message =  'Invalid credentials' 
        return render_template('errorpage.html', message = message)     
    return render_template('admin_login.html')

@app.route('/admin_addproducts1')
def addproducts1():    
    return render_template('admin_addproducts.html')
    
@app.route('/add_products', methods = ['POST'])
def add_products():
    p_name = request.form.get('product_name')
    image = request.files.get('product_image')
    p_image = image.read()
    p_category = request.form.get('product_genre')
    p_actualprice = request.form.get('actual_price')
    p_disprice = request.form.get('discounted_price')
    p_stock = request.form.get('quantity')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO PRODUCTS
        (PNAME, PIMAGE, PCATEGORY, PAPRICE, PDPRICE, PSTOCK)
        VALUES
        (%s,%s,%s,%s,%s,%s)
        ''', (p_name, p_image, p_category, p_actualprice, p_disprice,p_stock)
    )
    conn.commit()
    cursor.close()
    conn.close()
    message = 'Product added successfully'
    return render_template('admin_addproducts.html', message = message)

@app.route('/admin_manageproducts1')
def manageproducts1():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM PRODUCTS
        '''
    )
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    
    books_lst = []
    for each in books:    
        books_lst.append(list(each))
    for each in books_lst:
        each[2] = url_for('product_img', pid = each[0])
        
    #[(1,python, image, self-help, 100, 20, 20), ()]
    return render_template('admin_manageproducts.html', details = books_lst)

@app.route('/product_img/<int:pid>')
def product_img(pid):
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        ''' SELECT PIMAGE FROM PRODUCTS
        WHERE PID = %s
        ''', (pid,)
    )
    p_image = cursor.fetchone()
    cursor.close()
    conn.close()
    return Response(p_image, mimetype='image/jpeg')

@app.route('/admin_deleteproduct/<int:pid>')
def deleteproduct(pid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        DELETE FROM PRODUCTS
        WHERE PID = %s
        ''', (pid)
    )
    conn.commit()
    cursor.close()
    conn.close()      
    return redirect(url_for('manageproducts1'))
    
@app.route('/user_signup1', methods = ['GET', 'POST']) 
def user_signup1():
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        
        if password != cpassword:
            msg = "Password validation failed"
            return render_template('errorpage.html', message = msg)
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT * FROM USERS
            WHERE USERMAIL = %s
            ''', (email,)
        )
        user = cursor.fetchone()
        if user:
            cursor.close()
            conn.close()
            msg = "Email already exists"
            return render_template('errorpage.html', message = msg)
        else:
            otp = str(random.randint(100000, 999999))
            body = f"Your OTP for verification is: {otp}"
            send_mail(email, body) 
            conn.commit()
            cursor.close()
            conn.close()       
            return render_template('otpverify.html',name = name, email = email, mobile = mobile,password = password, otp = otp )
    return render_template('user_signup.html')

@app.route('/user_signup3', methods = ['POST'])
def user_signup3():
    name = request.form.get('name')
    email = request.form.get('email')
    mobile = request.form.get('mobile')
    password = request.form.get('password')
    otp = request.form.get('otp')
    cotp = request.form.get('cotp')    
    if otp == cotp:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
                '''
                INSERT INTO USERS
                (USERNAME, USERMAIL, USERPHONE, USERPASSWORD)
                VALUES
                (%s,%s,%s,%s)
                ''', (name, email, mobile, password)
            )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('user_login1'))
    else:        
        msg = "Incorrect OTP"
        return render_template('otpverify.html', message = msg)
    
@app.route('/user_login1') 
def user_login1():    
    return render_template('user_login.html') 
   
@app.route('/user_login2', methods = ['POST'])
def user_login2():
    email = request.form.get('email')
    password = request.form.get('password')
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM USERS
        WHERE USERMAIL = %s
        AND USERPASSWORD = %s
        ''', (email, password)
    )
    user = cursor.fetchone()
    print(user)
    if user:
        cursor.execute(
            '''
            SELECT * FROM PRODUCTS
            WHERE PSTOCK > 0
            '''
        )
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        user_id = user[0]
        books_lst = []
        for each in products:    
            books_lst.append(list(each))
        for each in books_lst:
            each[2] = url_for('product_img', pid = each[0])
        print(user_id)   
        return render_template('user_home.html', products = books_lst, user_id = user_id)
    else:
        msg = "Invalid Credentials"
        cursor.close()
        conn.close()
        return render_template('errorpage.html', message = msg)

@app.route('/add_to_cart/<int:pid>/<int:userid>')
def add_to_cart(pid, userid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM CART
        WHERE PID = %s and USERID = %s
        ''',(pid, userid)
    )
    pr = cursor.fetchone()
    if pr:
        cursor.execute(
            '''
            UPDATE CART 
            SET QUANTITY = QUANTITY + 1
            WHERE PID = %s
            ''',(pid,)
        )
    else:
        cursor.execute(
            '''INSERT INTO CART
            VALUES
            (%s, %s, %s)
            ''', (userid, pid, 1)
        )
    cursor.execute(
        '''
        UPDATE PRODUCTS
        SET PSTOCK = PSTOCK -1
        WHERE PID = %s
        ''',(pid)
    )
    
    cursor.execute(
            '''
            SELECT * FROM PRODUCTS
            WHERE PSTOCK > 0
            '''
        )
    products = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    books_lst = []
    for each in products:    
        books_lst.append(list(each))
    for each in books_lst:
        each[2] = url_for('product_img', pid = each[0])
          
    return render_template('user_home.html', products = books_lst, user_id = userid)
 
@app.route('/shopping_cart/<int:userid>') 
def shopping_cart(userid):
    msg = ''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM CART 
        WHERE USERID = %s
        ''', (userid)
    )
    cart_details = []
    #[[[p_id, p_name, p_image, p_price],quantity],....]
    cart_products = cursor.fetchall()
    total = 0
    for pr in cart_products:
        product_details = []
        quantity = pr[2]
        pid = pr[1]
        cursor.execute(
            '''SELECT PNAME, PIMAGE, PDPRICE
            FROM PRODUCTS 
            WHERE PID = %s
            ''',(pid,)
        )
        result = cursor.fetchone()
        img = url_for('product_img', pid = pid) 
        product_details = [[pid, result[0],img, result[2]], quantity]
        total += result[2] *quantity
        cart_details.append(product_details)
    if cart_products == None:
        msg = "Your cart is empty. Add products for checkout"
    
    return render_template('shopping_cart.html', data = cart_details, user_id = userid, total = total, msg = msg )

@app.route('/delete_cart_item/<pid>/<userid>/<quantity>') 
def delet_cart_item(pid,userid,quantity):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''DELETE FROM CART
        WHERE PID = %s AND USERID = %s
        ''',(pid, userid)
    )
    cursor.execute(
        '''UPDATE PRODUCTS SET 
        PSTOCK = PSTOCK + %s
        ''',(quantity,)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('shopping_cart', userid = userid))

@app.route('/success/<userid>', methods = ['POST'])
def success(userid):    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''DELETE FROM CART WHERE 
        USERID = %s
        ''',(userid)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('shopping_cart', userid = userid))

@app.route('/user_login_updated/<int:userid>')
def user_login_updated(userid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
            '''
            SELECT * FROM PRODUCTS
            WHERE PSTOCK > 0
            '''
        )
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    books_lst = []
    for each in products:    
        books_lst.append(list(each))
    for each in books_lst:
        each[2] = url_for('product_img', pid = each[0])
           
    return render_template('user_home.html', products = books_lst, user_id = userid)
           
if __name__ == '__main__':
    app.run(debug = True, port = 5004)


