from flask import Flask, render_template, request, redirect, session, url_for

import mysql.connector  as mysql #mysql-connector-python

import smtplib
from email.message import EmailMessage

import datetime as dt

##############################################################

app = Flask(__name__)

this = str(dt.datetime.now())
    
db = mysql.connect(host = "localhost", 
                   user = "root", 
                   password = "", 
                   database = "hostel")

command_handler = db.cursor(buffered = True) #?

def slash():
    if request.method == 'POST' and 'notu' in request.form:
        notu = request.form['notu']
        # print(notu)
        command_handler.execute("UPDATE users SET comment='{}' WHERE roll=%s".format(notu),(100,))
        db.commit()
    command_handler.execute("SELECT comment FROM users WHERE roll={}".format(100))
    nota = str(command_handler.fetchone()[0])
    # print(nota)
    # nota = nota[2:len(nota)-3]
    return nota

@app.after_request
def after_request(response):
    response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')   
    return response

@app.route('/', methods =['GET', 'POST'])
def login():
    if request.method=='POST' and ('pass' and 'un' in request.form):
        un = request.form['un']
        passw = request.form['pass']
        if un == "admin" and passw == "password":
            session['admin'] = 'admin'
            # login_user()
            return redirect(url_for('mainpg'))
    
    return render_template('login.html')

@app.route('/mainpg', methods = ['GET', 'POST'])
def mainpg():
    if 'admin' not in session:
        return redirect('/')
    else:
        return render_template('mainpage.html', dat = slash())
    
@app.route('/register', methods =['GET', 'POST'])
def register():
    if 'admin' not in session:
        return redirect('/')
    i=""
    if request.method == 'POST' and 'mail' in request.form:    
        fetch = ['username','mono','mail','roomno','place','p1name','p1mono','p1mail','admsm','admem','vhcno','locgrdno','edu','clg','comment','addr','feespaid']
        query_vals = []
            
        for i in range(0, len(fetch)):
            query_vals.append(request.form[fetch[i]])
        
        admstat=1
        rtdt='-'
        query_vals.append(admstat)
        query_vals.append(rtdt)
    
        command_handler.execute( "INSERT INTO users (username,mono,mail,roomno,place,p1name,p1mono,p1mail,admsm,admem,vhcno,locgrdno,edu,clg,comment,addr,feespaid,admstat,rtdt) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",query_vals)
        db.commit()
        command_handler.execute("SELECT roll FROM users WHERE username = %s",(query_vals[0],))
        i=command_handler.fetchone()
        i=str(i)
    return render_template('register.html', data=i[1:len(i)-2], dat=slash())
  
@app.route("/mail", methods = ['GET', 'POST'])
def mail():
    if 'admin' not in session:
        return redirect('/')
    if request.method == 'POST': 
        chk1 = request.form.get('p')
        chk2 = request.form.get('s')
        chk3 = request.form.get('a')
        roll = request.form['roll'].split()
        mailids = ""
        s1 = request.form['msg']
        if chk1 == '1' and chk3 == '1':
            command_handler.execute("SELECT p1mail FROM users")
            fetch = command_handler.fetchall()
            for i in range(0, len(fetch)):
                mailids = mailids + str(fetch[i][0]) + ','
    
        else:
            mailids=""
            if chk1=='1':
                for i in roll:
                    command_handler.execute("SELECT p1mail FROM users WHERE roll=%s",(i,))
                    j=command_handler.fetchone()
                    mailids = mailids + str(j[0]) + ','
            elif chk2=='1':
                for i in roll:
                    command_handler.execute("SELECT mail FROM users WHERE roll=%s",(i,))
                    j=command_handler.fetchone()
                    mailids = mailids + str(j[0]) + ','
            elif chk1=="1" and chk2=="1":
                for i in roll:
                    command_handler.execute("SELECT mail FROM users WHERE roll=%s",(i,))
                    j=command_handler.fetchone()
                    mailids = mailids + str(j[0]) + ','
                    command_handler.execute("SELECT p1mail FROM users WHERE roll=%s",(i,))
                    mailids = mailids + str(j[0]) + ','
    
        mailids=mailids[:-1]
    
        subject = request.form['subject']
        email_alert(subject,s1,mailids)
    return render_template("mail.html",dat=slash())
  
@app.route("/leave", methods = ['GET', 'POST'])
def leave():
    if 'admin' not in session:
        return redirect('/')
    tohtml = ""
    if request.method == 'POST' and 'roll' in request.form:
        rn=request.form.get('roll')
        command_handler.execute("SELECT p1mail FROM users WHERE roll=%s",(rn,))
        s2=command_handler.fetchone()
        command_handler.execute("SELECT username FROM users WHERE roll=%s",(rn,))
        un=command_handler.fetchone()
        # un=un[2:len(un)-3]
        un = str(un[0])
        n=request.form["nights"]
        where=request.form['where']
        why=request.form['why']
        date=request.form['rtdt']
        s1='{} has applied for a leave for {} nights and will be going to {}.\nreson: {}\nreturn date: {}'.format(un,n,where,why,date)
        email_alert("student applied for leave",s1,s2)
        query_val=(date,rn)
        command_handler.execute("UPDATE users SET rtdt=%s WHERE roll=%s",query_val)
        db.commit()  
    if request.method == 'POST' and 'rtroll' in request.form:
        rtroll=request.form['rtroll']
        command_handler.execute("SELECT rtdt FROM users WHERE roll=%s",(rtroll,))
        i=str(command_handler.fetchone())
        if i!='None':
            tohtml=i[2:len(i)-3]
            if request.method == 'POST' and 'finpro' in request.form:
                inp=request.form.get('ap')
                if inp=='1':
                    command_handler.execute("SELECT p1mail FROM users WHERE roll=%s",(rtroll,))
                    mail=command_handler.fetchone()
                    mail=str(mail)
                    mail=mail[2:len(mail)-3]
                    email_alert("Student reported late","student has reported today for last leave wherin he was supposed to return at {}".format(i),mail)    
                command_handler.execute("UPDATE users SET rtdt='-' WHERE roll={}".format(rtroll))
                db.commit()
    return render_template('leave.html',data=tohtml,dat=slash())

@app.route('/update', methods = ['GET', 'POST'])
def update():
    if 'admin' not in session:
        return redirect('/')
    out = []
    if request.method == 'POST' and 'roll' in request.form:
        roll = request.form['roll']
        command_handler.execute("SELECT * FROM users WHERE roll = %s",(roll,))
        out = command_handler.fetchall()
        if request.method == 'POST' and 'sub2' in request.form:
            
            fetch = ['username','mono','mail','roomno','place','p1name','p1mono','p1mail','admsm','admem','vhcno','locgrdno','edu','clg','comment','addr','feespaid','roll']
            query_vals = []
            
            for i in range(0, len(fetch)):
                query_vals.append(request.form[fetch[i]])
        
            command_handler.execute("UPDATE users SET username=%s,mono=%s,mail=%s,roomno=%s,place=%s,p1name=%s,p1mono=%s,p1mail=%s,admsm=%s,admem=%s,vhcno=%s,locgrdno=%s,edu=%s,clg=%s,comment=%s,addr=%s,feespaid=%s WHERE roll=%s", query_vals)
            db.commit()
            
            command_handler.execute("SELECT * FROM users WHERE roll = %s",(roll,))
            out = command_handler.fetchall()
    return render_template('update.html', data=out, dat=slash())

@app.route('/expenses', methods = ["GET","POST"])
def expenses():
    if 'admin' not in session:
        return redirect('/')
    if request.method == "POST":
        month = request.form['month']
        water = request.form['waterbill']
        # print(water)
        elec = request.form['electricitybill']
        # print(elec)
        taxes = request.form['taxes']
        # water = request.form['waterbill']
        sal = request.form['workersalaries']
        groc = request.form['groceries']
        maintain = request.form['maintenance']
        print(maintain,"jgvjyv")
        comm = request.form['comment']
        total = water + elec + taxes + sal + groc + maintain
        # total = 0
        values = (month, elec, water, taxes, sal, groc, maintain, comm, total)
        command_handler.execute("INSERT INTO expenses (month, ebill, wbill, tax, salary, food, maintenance, comment, total) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", values)
        db.commit()
    return render_template('expenses.html', dat = slash())

@app.route('/vac', methods = ["GET","POST"])
def vac():
    if 'admin' not in session:
        return redirect('/')
    loo = []
    months = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
    for i in range(0,3):
        command_handler.execute("SELECT * FROM users WHERE admem = %s", (months[int(this[6:7])+i-1],))
        out = command_handler.fetchall()
        for j in out:
            loo.append(j)
    return render_template('vac.html', dat = slash(), out = loo)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

def email_alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = ""
    msg['from'] = user
    password=""

    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()

if __name__ == "__main__":
    app.secret_key = 'seckey' #necessaryforsession
    app.run(host = "localhost", port = int("5000"), debug = True)