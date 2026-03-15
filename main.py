import sqlite3
from asyncio.windows_events import NULL

from flask import (Flask, render_template,
                   request, redirect,
                   session, url_for)

app = Flask(__name__)
app.secret_key = 'felix_pham'

@app.route('/')
def index():
    # Check if 'username' key exists in the session
    if 'current_user' in session:

        return render_template('base.html')
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        TenTK = request.form['txt_username']
        MK = request.form['txt_password']
        if check_exists(TenTK, MK):
            # Store 'username' in the session
            obj_user = get_obj_TaiKhoan(TenTK, MK)
            if int(obj_user[0]) > 0: # Neu ton tai ID
                obj_user = {
                    "MaTK": obj_user[0],
                    "TenTK": obj_user[1],
                    "MaGV": obj_user[3],
                    "LaAdmin": obj_user[4],
                    "LaTruongKhoa": 0,
                }

                if obj_user["MaGV"] is None:
                    obj_user["LaTruongKhoa"] = 0
                else:
                    obj_CanBo = get_obj_CanBo(obj_user['MaGV'])
                    obj_user["LaTruongKhoa"] = obj_CanBo[6]

                session['current_user'] = obj_user

            return redirect(url_for('index'))
    # Trường hợp mặc định là vào trang login
    return render_template('login.html')

def get_obj_TaiKhoan(TenTK, MK):
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

def get_obj_CanBo(MaGV):
    result = []
    sqldbname = 'db/decuong.db'

    # Khai bao bien tro toi db
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()

    # sqlcommand
    sqlcommand = "select * from CanBo where MaQL = ? "
    cursor.execute(sqlcommand, (MaGV,))

    # return object
    obj_CanBo = cursor.fetchone()
    if (len(obj_CanBo) > 0):  # Moi doi tuong la 1 danh sach
        result = obj_CanBo
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

@app.route("/admin_gv_dashboard")
def admin_gv_dashboard():
    return render_template("admin_gv_dashboard.html")

@app.route("/admin_hocphan_list")
def admin_hocphan_list():
    return render_template("admin_hocphan_list.html")

@app.route("/adminKhoa_hocphan_dashboard")
def adminKhoa_hocphan_dashboard():
    return render_template("adminKhoa_hocphan_dashboard.html")

@app.route("/gv_dashboard")
def gv_dashboard():
    return render_template("gv_dashboard.html")

if __name__ == '__main__':
    app.run(debug=True)

