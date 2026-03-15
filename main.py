import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "felix_pham"

DB = "db/decuong.db"


# =============================
# DATABASE CONNECTION
# =============================
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


# =============================
# HOME
# =============================
@app.route("/")
def index():

    if "current_user" not in session:
        return render_template("welcome.html")

    user = session["current_user"]

    # admin hệ thống
    if user["LaAdmin"] == 1:
        return redirect("/admin_gv_dashboard")

    # giảng viên
    if user["MaGV"]:

        obj = get_obj_CanBo(user["MaGV"])

        if obj and obj["LaTruongKhoa"] == 1:
            return redirect("/adminKhoa_hocphan_dashboard")

        return redirect("/gv_dashboard")

    return redirect("/login")


# =============================
# LOGIN
# =============================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        TenTK = request.form["txt_username"]
        MK = request.form["txt_password"]

        user = get_obj_TaiKhoan(TenTK, MK)

        if user:

            session["current_user"] = {
                "MaTK": user["MaTK"],
                "TenTK": user["TenTK"],
                "MaGV": user["MaGV"],
                "LaAdmin": user["LaAdmin"],
            }

            return redirect("/")

    return render_template("login.html")


# =============================
# LOGOUT
# =============================
@app.route("/logout")
def logout():

    session.pop("current_user", None)
    return redirect("/")


# =============================
# GET USER
# =============================
def get_obj_TaiKhoan(TenTK, MK):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM TaiKhoan
        WHERE TenTK=? AND MK=?
        """,
        (TenTK, MK),
    )

    user = cursor.fetchone()

    conn.close()

    return user


# =============================
# GET CAN BO
# =============================
def get_obj_CanBo(MaGV):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM CanBo
        WHERE MaQL=?
        """,
        (MaGV,),
    )

    obj = cursor.fetchone()

    conn.close()

    return obj


# =============================
# ADMIN DASHBOARD
# =============================
@app.route("/admin_gv_dashboard")
def admin_gv_dashboard():

    if "current_user" not in session:
        return redirect("/login")

    if session["current_user"]["LaAdmin"] != 1:
        return "Không có quyền"

    return render_template("admin_gv_dashboard.html")


# =============================
# ADMIN HOC PHAN LIST
# =============================
@app.route("/admin_hocphan_list")
def admin_hocphan_list():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT HocPhan.*, DonVi.TenDV
        FROM HocPhan
        LEFT JOIN DonVi ON HocPhan.MaDV = DonVi.MaDV
        """
    )

    dsHocPhan = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_hocphan_list.html",
        dsHocPhan=dsHocPhan,
    )


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


# =============================
# GIANG VIEN DASHBOARD
# =============================
@app.route("/gv_dashboard")
def gv_dashboard():

    if "current_user" not in session:
        return redirect("/login")

    MaGV = session["current_user"]["MaGV"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT HocPhan.*
        FROM HocPhan
        JOIN PhanCongHC
        ON HocPhan.MaHP = PhanCongHC.MaHP
        WHERE PhanCongHC.MaGV=?
        """,
        (MaGV,),
    )

    dsHocPhan = cursor.fetchall()

    conn.close()

    return render_template(
        "gv_dashboard.html",
        dsHocPhan=dsHocPhan,
    )


# =============================
# RUN APP
# =============================
if __name__ == "__main__":
    app.run(debug=True)