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
