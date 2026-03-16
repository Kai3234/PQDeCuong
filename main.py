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
    # Kiểm tra có tồn tại current_user trong session
    if 'current_user' in session:
        return render_template('base.html')
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Kiểm tra người dùng gửi form
    if request.method == 'POST':
        # Lấy dữ liệu từ HTML
        TenTK = request.form['txt_username']
        MK = request.form['txt_password']

        if check_exists(TenTK, MK):
            # Lấy ttin tài khoản từ db
            obj_user = get_obj_TaiKhoan(TenTK, MK)
            if int(obj_user[0]) > 0:
                # Tạo dictionary chứa thông tin của user
                obj_user = {
                    "MaTK": obj_user[0],
                    "TenTK": obj_user[1],
                    "MaGV": obj_user[3],
                    "LaAdmin": obj_user[4],
                    "LaTruongKhoa": 0,
                }

                # Kiểm tra user có là trưởng khoa không
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
    result = False
    # Khai bao bien de tro toi db
    conn = get_db()
    cursor = conn.cursor()

    sqlcommand = "SELECT * FROM TaiKhoan WHERE TenTK=? AND MK=?"
    cursor.execute(sqlcommand, (TenTK, MK))
    data = cursor.fetchall()

    # Nếu có ít nhất 1 bản ghi
    if len(data)>0:
        result = True
    conn.close()
    return result

# chạy trước mỗi request (mỗi khi người dùng truy cập một route)
@app.before_request
def update_truong_khoa():
    if 'current_user' in session:
        user = session['current_user']

        # Kiểm tra current user có là trưởng khoa
        if user["MaGV"] is not None:
            obj_CanBo = get_obj_CanBo(user["MaGV"])
            session['current_user']["LaTruongKhoa"] = obj_CanBo[6]
        else:
            session['current_user']["LaTruongKhoa"] = 0

        # Đánh dấu session đã bị thay đổi để Flask lưu lại
        session.modified = True

@app.route('/logout')
def logout():
    session.pop('current_user', None)
    # Loại bỏ current_user khỏi session
    return redirect(url_for('index'))


@app.route("/gv_dashboard")
def gv_dashboard():
    if "current_user" not in session:
        return redirect("/login")

    MaGV = session["current_user"]["MaGV"]

    keyword = request.args.get("keyword")
    type_search = request.args.get("type")

    conn = get_db()
    cursor = conn.cursor()

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
    # Lấy thông tin của giảng viên
    ThongTinCanBo = cursor.fetchone()

    query = """
    SELECT HocPhan.*, DonVi.TenDV, ThoiGian 
    FROM HocPhan
    JOIN PhanCongHC 
        ON HocPhan.MaHP = PhanCongHC.MaHP
    JOIN DonVi 
        ON HocPhan.MaDV = DonVi.MaDV
    WHERE PhanCongHC.MaGV = ?
    """


    params = [MaGV]

    # SEARCH
    if keyword and type_search:


        if type_search == "MaHP":
            query += " AND HocPhan.MaHP LIKE ?"

        elif type_search == "TenHP":
            query += " AND HocPhan.TenHP LIKE ?"

        elif type_search == "TenDV":
            query += " AND DonVi.TenDV LIKE ?"

        elif type_search == "ThoiGian":
            query += " AND PhanCongHC.ThoiGian LIKE ?"

        params.append("%" + keyword + "%")

    cursor.execute(query, params)

    dsHocPhan = cursor.fetchall()

    conn.close()

    return render_template(
        "gv_dashboard.html",
        dsHocPhan=dsHocPhan,
        ThongTinCanBo=ThongTinCanBo,
        keyword=keyword,
        type_search=type_search
    )

# Import tất cả các hàm, biến và route
from admin import *
from adminKhoa import *

if __name__ == '__main__':
    app.run(debug=True)

