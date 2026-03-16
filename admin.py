import sqlite3
from flask import render_template, request, redirect, session
from main import app, get_db


DATABASE = "db/decuong.db"


# ======================
# ADMIN GIANG VIEN
# ======================
@app.route("/admin_gv_dashboard")
def admin_gv_dashboard():

    if "current_user" not in session:
        return redirect("/login")

    keyword = request.args.get("keyword")
    type_search = request.args.get("type")

    conn = get_db()
    cur = conn.cursor()

    query = """
    SELECT CanBo.MaQL,
           CanBo.TenGV,
           CanBo.SoHieu,
           CanBo.Email,
           CanBo.LoaiGV,
           CanBo.MaDV,
           DonVi.TenDV,
           CanBo.LaTruongKhoa
    FROM CanBo
    LEFT JOIN DonVi
    ON CanBo.MaDV = DonVi.MaDV
    WHERE 1=1
    """

    params = []

    if keyword and type_search:

        keyword = "%" + keyword + "%"

        if type_search == "MaQL":
            query += " AND CanBo.MaQL LIKE ?"

        elif type_search == "TenGV":
            query += " AND CanBo.TenGV LIKE ?"

        elif type_search == "LoaiGV":
            query += " AND CanBo.LoaiGV LIKE ?"

        params.append(keyword)

    cur.execute(query, params)

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

    if "current_user" not in session:
        return redirect("/login")

    keyword = request.args.get("keyword")
    type_search = request.args.get("type")

    conn = get_db()
    cur = conn.cursor()

    query = """
    SELECT HocPhan.MaHP,
           HocPhan.TenHP,
           HocPhan.SoTC,
           HocPhan.TrinhDo,
           HocPhan.MaDV,
           DonVi.TenDV
    FROM HocPhan
    LEFT JOIN DonVi
    ON HocPhan.MaDV = DonVi.MaDV
    WHERE 1=1
    """

    params = []

    if keyword and type_search:

        keyword = "%" + keyword + "%"

        if type_search == "MaHP":
            query += " AND HocPhan.MaHP LIKE ?"

        elif type_search == "TenHP":
            query += " AND HocPhan.TenHP LIKE ?"

        elif type_search == "TrinhDo":
            query += " AND HocPhan.TrinhDo LIKE ?"

        params.append(keyword)

    cur.execute(query, params)

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

@app.route("/admin/update_hocphan", methods=["POST"])
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