import sqlite3
from flask import render_template, request, redirect
from main import app


DATABASE = "db/decuong.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ======================
# ADMIN GIANG VIEN
# ======================

@app.route("/admin_gv_dashboard")
def admin_gv_dashboard():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT CanBo.MaQL,
           CanBo.TenGV,
           CanBo.SoHieu,
           CanBo.Email,
           CanBo.MaDV,
           DonVi.TenDV,
           CanBo.LaTruongKhoa
    FROM CanBo
    LEFT JOIN DonVi
    ON CanBo.MaDV = DonVi.MaDV
    """)

    canbo_list = cur.fetchall()

    cur.execute("SELECT * FROM DonVi")
    donvi_list = cur.fetchall()

    conn.close()

    return render_template(
        "admin_gv_dashboard.html",
        canbo_list=canbo_list,
        donvi_list=donvi_list
    )


# ======================
# UPDATE GIANG VIEN
# ======================

@app.route("/update_giangvien", methods=["POST"])
def update_giangvien():

    MaQL = request.form["MaQL"]
    MaDV = request.form["MaDV"]

    LaTruongKhoa = request.form.get("LaTruongKhoa")

    if LaTruongKhoa:
        LaTruongKhoa = 1
    else:
        LaTruongKhoa = 0

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    UPDATE CanBo
    SET MaDV = ?, LaTruongKhoa = ?
    WHERE MaQL = ?
    """, (MaDV, LaTruongKhoa, MaQL))

    conn.commit()
    conn.close()

    return redirect("/admin_gv_dashboard")


# ======================
# ADMIN HOC PHAN
# ======================

@app.route("/admin_hocphan_list")
def admin_hocphan_list():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT HocPhan.MaHP,
           HocPhan.TenHP,
           HocPhan.SoTC,
           HocPhan.TrinhDo,
           HocPhan.MaDV,
           DonVi.TenDV
    FROM HocPhan
    LEFT JOIN DonVi
    ON HocPhan.MaDV = DonVi.MaDV
    """)

    hocphan_list = cur.fetchall()

    cur.execute("SELECT * FROM DonVi")
    donvi_list = cur.fetchall()

    conn.close()

    return render_template(
        "admin_hocphan_list.html",
        hocphan_list=hocphan_list,
        donvi_list=donvi_list
    )


# ======================
# UPDATE HOC PHAN
# ======================

@app.route("/update_hocphan", methods=["POST"])
def update_hocphan():

    MaHP = request.form["MaHP"]
    MaDV = request.form["MaDV"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    UPDATE HocPhan
    SET MaDV = ?
    WHERE MaHP = ?
    """, (MaDV, MaHP))

    conn.commit()
    conn.close()

    return redirect("/admin_hocphan_list")