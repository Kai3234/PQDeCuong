from flask import session, redirect, render_template, request

from main import get_obj_CanBo, get_db, app


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

    keyword = request.args.get("keyword")
    type_search = request.args.get("type")

    conn = get_db()
    cursor = conn.cursor()

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
    WHERE HocPhan.MaDV=?
    """

    params = [MaDV]

    # SEARCH
    if keyword and type_search:

        if type_search == "TenDV":
            query += " AND DonVi.TenDV LIKE ?"
        else:
            query += f" AND HocPhan.{type_search} LIKE ?"

        params.append("%" + keyword + "%")

    cursor.execute(query, params)

    dsHocPhan = cursor.fetchall()

    conn.close()

    return render_template(
        "adminKhoa_hocphan_dashboard.html",
        dsHocPhan=dsHocPhan
    )


# =============================
# AUTHORIZE GIANG VIEN
# =============================
@app.route("/adminKhoa_hocphan_authorize/<MaHP>")
def adminKhoa_hocphan_authorize(MaHP):

    keyword = request.args.get("keyword")
    type_search = request.args.get("type")

    conn = get_db()
    cursor = conn.cursor()

    # =============================
    # THÔNG TIN HỌC PHẦN
    # =============================
    cursor.execute("""
        SELECT HocPhan.*, DonVi.TenDV
        FROM HocPhan
        LEFT JOIN DonVi ON HocPhan.MaDV = DonVi.MaDV
        WHERE HocPhan.MaHP=?
    """,(MaHP,))

    hocphan = cursor.fetchone()


    # =============================
    # QUERY GIẢNG VIÊN
    # =============================
    query = """
    SELECT CanBo.MaQL,
           CanBo.TenGV,
           CanBo.MaDV,
           CanBo.Email,
           CanBo.LoaiGV,
           CanBo.LaTruongKhoa,
           DonVi.TenDV
    FROM CanBo
    LEFT JOIN DonVi ON CanBo.MaDV = DonVi.MaDV
    WHERE 1=1
    """

    params = []


    # =============================
    # SEARCH
    # =============================
    if keyword and type_search:

        keyword = "%" + keyword + "%"

        if type_search == "TenDV":
            query += " AND DonVi.TenDV LIKE ?"
            params.append(keyword)

        elif type_search == "Email":
            query += " AND CanBo.Email LIKE ?"
            params.append(keyword)

        elif type_search == "TenGV":
            query += " AND CanBo.TenGV LIKE ?"
            params.append(keyword)

        elif type_search == "MaQL":
            query += " AND CanBo.MaQL LIKE ?"
            params.append(keyword)


    cursor.execute(query, params)

    dsCanBo = cursor.fetchall()


    # =============================
    # GIẢNG VIÊN ĐÃ PHÂN CÔNG
    # =============================
    cursor.execute("""
        SELECT MaGV
        FROM PhanCongHC
        WHERE MaHP=?
    """,(MaHP,))

    dsDaChon = [x["MaGV"] for x in cursor.fetchall()]


    conn.close()

    return render_template(
        "adminKhoa_hocphan_authorize.html",
        hocphan=hocphan,
        dsCanBo=dsCanBo,
        dsDaChon=dsDaChon
    )

# =============================
# SAVE AUTHORIZE
# =============================
@app.route("/adminKhoa_hocphan_authorize_save", methods=["POST"])
def adminKhoa_hocphan_authorize_save():

    MaHP = request.form["MaHP"]

    dsGV = request.form.getlist("MaGV[]")

    conn = get_db()
    cursor = conn.cursor()

    # XÓA PHÂN CÔNG CŨ
    cursor.execute("""
        DELETE FROM PhanCongHC
        WHERE MaHP=?
    """,(MaHP,))


    # THÊM PHÂN CÔNG MỚI
    for MaGV in dsGV:

        cursor.execute("""
            INSERT INTO PhanCongHC(MaGV,MaHP)
            VALUES (?,?)
        """,(MaGV,MaHP))


    conn.commit()
    conn.close()

    return redirect("/adminKhoa_hocphan_dashboard")
