import sqlite3
from asyncio.windows_events import NULL

from flask import (Flask, render_template,
                   request, redirect,
                   session, url_for)

app = Flask(__name__)
app.secret_key = 'felix_pham'


DB = "db/decuong.db"


# =============================
# DATABASE CONNECTION
# =============================
# hoat dong nhu tuples and dictionaries
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


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
    # Khai bao bien tro toi db
    conn = get_db()
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

    # Khai bao bien tro toi db
    conn = get_db()
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
    # Khai bao bien de tro toi db
    conn = get_db()
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

@app.before_request
def update_truong_khoa():
    if 'current_user' in session:
        user = session['current_user']

        if user["MaGV"] is not None:
            obj_CanBo = get_obj_CanBo(user["MaGV"])
            session['current_user']["LaTruongKhoa"] = obj_CanBo[6]
        else:
            session['current_user']["LaTruongKhoa"] = 0

        session.modified = True

@app.route('/logout')
def logout():
    session.pop('current_user', None)
    # Remove 'username' from the session
    return redirect(url_for('index'))

# =============================
# ADMIN KHOA DASHBOARD
# =============================
@app.route("/adminKhoa_hocphan_dashboard")
def adminKhoa_hocphan_dashboard():

    if "current_user" not in session:
        return redirect("/login")

    MaGV = session["current_user"]["MaGV"]

    obj_canbo = get_obj_CanBo(MaGV)

    if not obj_canbo:
        return "Không tìm thấy cán bộ"

    MaDV = obj_canbo["MaDV"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
    """
    SELECT HocPhan.MaHP,
        HocPhan.TenHP,
        HocPhan.SoTC,
        HocPhan.TrinhDo,
        DonVi.TenDV
    FROM HocPhan
    LEFT JOIN DonVi
    ON HocPhan.MaDV = DonVi.MaDV
    WHERE HocPhan.MaDV=?
    """,
    (MaDV,),
    )

    dsHocPhan = cursor.fetchall()

    conn.close()

    return render_template(
        "adminKhoa_hocphan_dashboard.html",
        dsHocPhan=dsHocPhan,
    )


# =============================
# AUTHORIZE GIANG VIEN
# =============================
@app.route("/adminKhoa_hocphan_authorize/<MaHP>")
def adminKhoa_hocphan_authorize(MaHP):

    conn = get_db()
    cursor = conn.cursor()

    # =============================
    # LẤY THÔNG TIN HỌC PHẦN
    # =============================
    cursor.execute(
    """
    SELECT HocPhan.*,
           DonVi.TenDV
    FROM HocPhan
    LEFT JOIN DonVi
    ON HocPhan.MaDV = DonVi.MaDV
    WHERE HocPhan.MaHP=?
    """,
    (MaHP,)
    )

    hocphan = cursor.fetchone()


    # =============================
    # LẤY DANH SÁCH GIẢNG VIÊN
    # =============================
    cursor.execute(
    """
    SELECT CanBo.MaQL,
        CanBo.TenGV,
        CanBo.MaDV,
        CanBo.Email,
        CanBo.LoaiGV,
        CanBo.LaTruongKhoa,
        DonVi.TenDV
    FROM CanBo
    LEFT JOIN DonVi
    ON CanBo.MaDV = DonVi.MaDV
    """
    )
    dsCanBo = cursor.fetchall()


    # =============================
    # GIẢNG VIÊN ĐÃ ĐƯỢC PHÂN CÔNG
    # =============================
    cursor.execute(
    """
    SELECT MaGV
    FROM PhanCongHC
    WHERE MaHP=?
    """,
    (MaHP,)
    )

    dsDaChon = [x["MaGV"] for x in cursor.fetchall()]

    conn.close()

    return render_template(
        "adminKhoa_hocphan_authorize.html",
        hocphan=hocphan,
        dsCanBo=dsCanBo,
        dsDaChon=dsDaChon,
    )


# =============================
# SAVE AUTHORIZE
# =============================
@app.route("/adminKhoa_hocphan_authorize_save", methods=["POST"])
def adminKhoa_hocphan_authorize_save():

    MaHP = request.form["MaHP"]

    # lấy danh sách checkbox
    dsGV = request.form.getlist("MaGV[]")

    conn = get_db()
    cursor = conn.cursor()

    # xóa phân công cũ
    cursor.execute(
        """
        DELETE FROM PhanCongHC
        WHERE MaHP=?
        """,
        (MaHP,),
    )

    # insert mới
    for MaGV in dsGV:

        cursor.execute(
            """
            INSERT INTO PhanCongHC(MaGV,MaHP)
            VALUES (?,?)
            """,
            (MaGV, MaHP),
        )

    conn.commit()
    conn.close()

    return redirect("/adminKhoa_hocphan_dashboard")

@app.route("/gv_dashboard")
def gv_dashboard():
    if "current_user" not in session:
        return redirect("/login")

    MaGV = session["current_user"]["MaGV"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT HocPhan.*, DonVi.TenDV, ThoiGian 
        FROM HocPhan
        JOIN PhanCongHC 
            ON HocPhan.MaHP = PhanCongHC.MaHP
        JOIN DonVi 
            ON HocPhan.MaDV = DonVi.MaDV
        WHERE PhanCongHC.MaGV = ?
        """,
        (MaGV,),
    )

    dsHocPhan = cursor.fetchall()

    cursor.execute(
        """
        SELECT CanBo.*, DonVi.TenDV
        FROM CanBo
        JOIN DonVi 
            ON CanBo.MaDV = DonVi.MaDV
        WHERE MaQL = ?
        """,
    (MaGV,),
    )
    ThongTinCanBo = cursor.fetchone()


    conn.close()

    return render_template(
        "gv_dashboard.html",
        dsHocPhan=dsHocPhan,
        ThongTinCanBo=ThongTinCanBo,
    )

from admin import *

if __name__ == '__main__':
    app.run(debug=True)

