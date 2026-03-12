import sqlite3

from flask import (Flask, render_template,
                   request, redirect,
                   session, url_for)

app = Flask(__name__)
app.secret_key = 'felix_pham'

@app.route('/')
def index():
    # Check if 'username' key exists in the session
    if 'current_user' in session:
        username = session['current_user']['TenTK']
        return render_template('base.html')
    return 'Chào mừng! <a href="/login">Login</a>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        TenTK = request.form['txt_username']
        MK = request.form['txt_password']
        if check_exists(TenTK, MK):
            # Store 'username' in the session
            obj_user = get_obj_user(TenTK, MK)
            if int(obj_user[0]) > 0: # Neu ton tai ID
                obj_user = {
                    "id": obj_user[0],
                    "TenTK": obj_user[1],
                    "MaGV": obj_user[2],
                    "LaAdmin": obj_user[4],
                }
                session['current_user'] = obj_user

            return redirect(url_for('index'))
    # Trường hợp mặc định là vào trang login
    return render_template('login.html')

def get_obj_user(TenTK, MK):
    result = []
    sqldbname = 'db/decuong.db'
    # Khai bao bien tro toi db
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()

    #sqlcommand
    sqlcommand = "select * from TaiKhoan where TenTK = ? and MK = ? "
    cursor.execute(sqlcommand, (TenTK, MK))

    # return object
    obj_user = cursor.fetchone()
    if (len(obj_user)>0): # Moi doi tuong la 1 danh sach
        result = obj_user
    conn.close()
    return result


def check_exists(TenTK, MK):
    result = False;
    sqldbname = 'db/decuong.db'
    # Khai bao bien de tro toi db
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    # sqlcommand = "Select * from storages where "
    sqlcommand = "Select * from TaiKhoan where TenTK = '"+TenTK+"' and MK = '"+MK+"'"
    cursor.execute(sqlcommand)
    data = cursor.fetchall()
    print(type(data))
    if len(data)>0:
        result = True
    conn.close()
    return result

@app.route('/logout')
def logout():
    session.pop('current_user', None)
    # Remove 'username' from the session
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

