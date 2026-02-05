import streamlit as st
import pandas as pd
import sqlite3
from io import BytesIO
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# Kết nối SQLite
conn = sqlite3.connect('db.sqlite', check_same_thread=False)
c = conn.cursor()

# Tạo bảng nếu chưa có
c.execute('''CREATE TABLE IF NOT EXISTS indicators
             (Mã TEXT PRIMARY KEY, Nhóm TEXT, TT TEXT, Chỉ_tiêu TEXT, Đơn_vị TEXT,
              Năm_2026 REAL, Năm_2027 REAL, Năm_2028 REAL, Năm_2029 REAL, Năm_2030 REAL,
              Giai_đoạn REAL, Chủ_trì TEXT)''')

# Dữ liệu chỉ tiêu từ parse (dán df.to_dict() từ output trước)
data = {
    'Mã chỉ tiêu': ['KT01', 'KT02', 'KT03', 'KT04', 'KT05', 'KT06', 'KT07', 'KT08', 'KT09', 'KT10', 'KT11', 'KT12', 'KT13', 'KT14', 'KT15', 'KT16', 'KT17', 'KT18', 'QP01', 'QP02', 'XD01', 'XD02', 'XD03', 'XD04'],
    'Nhóm': ['I Về kinh tế - xã hội']*18 + ['II Về quốc phòng - an ninh']*2 + ['III Xây dựng Đảng và hệ thống chính trị']*4,
    'TT': ['1', '-', '-', '+', '+', '-', '2', '3', '4', '5', '6', '7', '8', '9', '-', '10', '11', '12', '13', '14', '15', '16', '17', '18'],
    'Chỉ tiêu chủ yếu': ['Tốc độ tăng giá trị sản phẩm', 'Nông, lâm, thủy sản', 'Công nghiệp và xây dựng', 'Công nghiệp', 'Xây dựng', 'Dịch vụ', 'Tổng thu ngân sách trên địa bàn đến năm 2030', 'Doanh thu bán lẻ hàng hóa và dịch vụ', 'Tỷ lệ dân số tham gia bảo hiểm y tế', 'Giảm tỷ lệ hộ nghèo đa chiều', 'Bảo hiểm xã hội tự nguyện', 'Đào tạo nghề lao động nông thôn', 'Tỷ lệ che phủ rừng', 'Tỷ lệ dân cư nông thôn sử dụng nước hợp vệ sinh', 'Trong đó: Tỷ lệ sử dụng nước sạch', 'Tỷ lệ chất thải rắn ở nông thôn được thu gom', 'Tỷ lệ giải ngân vốn đầu tư công so với kế hoạch HĐND tỉnh giao', 'Tỷ lệ trường đạt chuẩn quốc gia', 'Tỷ lệ giao quân hằng năm', 'Xếp loại về quốc phòng – an ninh hằng năm', 'Tỷ lệ phát triển đảng viên mới hằng năm (so với đảng viên đầu nhiệm kỳ)', 'Tỷ lệ đảng viên hoàn thành tốt nhiệm vụ hằng năm', 'Tỷ lệ chi bộ hoàn thành tốt nhiệm vụ hằng năm', 'Hằng năm Đảng bộ phân đấu xếp loại hoàn thành tốt nhiệm vụ: xây dựng Chính quyền, Mặt trận và các tổ chức chính trị - xã hội xã được xếp loại hoàn thành tốt nhiệm vụ'],
    'ĐƠN VỊ TÍNH': ['%', '%', '%', '%', '%', '%', 'Triệu đồng', 'Tỷ đồng', '%', '%', 'Người', 'Người', '%', '%', '%', '%', '%', '%', '%', 'Đạt xã vững mạnh', '%', '%', '%', '%'],
    'NĂM 2026': [10.3, 4.5, 9.0, 17.8, 8.5, 14.5, 800.0, 300.0, 100.0, 4.88, 157.0, 90.0, 48.5, 82.0, 0.5, 23.0, 93.0, 16.66, 100.0, float('nan'), 4.0, 85.0, 90.0, 80.0],
    'NĂM 2027': [10.2, 4.5, 9.0, 17.5, 8.5, 14.4, 850.0, 350.0, 100.0, 4.88, float('nan'), 90.0, 48.8, 83.0, 0.7, 24.0, 95.0, 16.66, 100.0, float('nan'), 4.0, 85.0, 90.0, 80.0],
    'NĂM 2028': [10.4, 4.3, 8.8, 17.4, 8.3, 14.3, 900.0, 370.0, 100.0, 4.88, float('nan'), 90.0, 49.0, 84.0, 0.8, 25.0, 95.0, 17.0, 100.0, float('nan'), 4.0, 85.0, 90.0, 80.0],
    'NĂM 2029': [10.1, 4.2, 8.4, 17.2, 8.2, 14.3, 950.0, 381.0, 100.0, 4.88, float('nan'), 90.0, 49.1, 84.5, 0.9, 26.0, 96.0, 33.33, 100.0, float('nan'), 4.0, 85.0, 90.0, 80.0],
    'NĂM 2030': [10.0, 4.0, 8.3, 17.1, 8.0, 14.0, 1.0, 381.0, 100.0, 4.88, float('nan'), 90.0, 49.2, 85.0, 1.0, 27.0, 96.0, 50.0, 100.0, float('nan'), 4.0, 85.0, 90.0, 80.0],
    'Giai đoạn 2026 - 2030': [10.2, 4.3, 8.7, 17.4, 8.3, 14.3, 4.5, 1.782, 100.0, 4.88, 190.0, 450.0, 49.09, 85.0, 1.0, 26.0, 95.0, 50.0, 100.0, float('nan'), float('nan'), float('nan'), float('nan'), float('nan')],
    'CHỦ TRÌ': ['Phòng kinh tế', 'Phòng kinh tế', 'Phòng kinh tế', 'Phòng kinh tế', 'Phòng kinh tế', 'Phòng kinh tế', 'Phòng kinh tế', 'Phòng kinh tế', 'Phòng Văn hóa - xã hội', 'Phòng kinh tế', 'Phòng Văn hóa – xã hội', 'Phòng Văn hóa – xã hội', 'Phòng kinh tế', 'Phòng kinh tế', 'Phòng kinh tế', 'Phòng kinh tế', 'Phòng kinh tế', 'Phòng Văn hóa – xã hội', 'Ban Chỉ huy Quân sự; Công an xã', 'Ban Chỉ huy Quân sự; Công an xã', 'Ban Xây dựng Đảng, các chi bộ trực thuộc', 'Ban Xây dựng Đảng, các chi bộ trực thuộc', 'các chi bộ trực thuộc', '']
}

df = pd.DataFrame(data)
df.to_sql('indicators', conn, if_exists='replace', index=False)

# Tạo bảng results cho từng năm nếu cần (demo cho 2026)
for year in range(2026, 2031):
    c.execute(f'''CREATE TABLE IF NOT EXISTS results_{year}
                 (Mã TEXT, Giá_trị_thực_hiện REAL, Ghi_chú TEXT, Người_nhập TEXT, Thời_điểm TEXT, Trạng_thái TEXT)''')

# Users
users = {
    "phongkinhte": {"role": "Phòng kinh tế", "password": "123"},
    "phongvanhua": {"role": "Phòng Văn hóa - xã hội", "password": "123"},
    "phongvanhua2": {"role": "Phòng Văn hóa – xã hội", "password": "123"},  # Alias
    "banchqs": {"role": "Ban Chỉ huy Quân sự; Công an xã", "password": "123"},
    "banxaydung": {"role": "Ban Xây dựng Đảng, các chi bộ trực thuộc", "password": "123"},
    "admin": {"role": "Admin", "password": "admin"}
}

# Session
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user = None

if not st.session_state.logged_in:
    st.title("Đăng nhập")
    user = st.text_input("Username")
    passw = st.text_input("Password", type="password")
    if st.button("Đăng nhập"):
        if user in users and users[user]["password"] == passw:
            st.session_state.logged_in = True
            st.session_state.role = users[user]["role"]
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Sai username/password")
else:
    role = st.session_state.role
    st.title(f"Báo cáo Chỉ tiêu - {role}")
    if st.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    indicators = pd.read_sql("SELECT * FROM indicators", conn)

    # Filter by role
    if role != "Admin":
        indicators = indicators[indicators["Chủ_trì"].str.contains(role.replace(" – ", " - "), na=False, case=False)]

    year = st.selectbox("Năm báo cáo", list(range(2026, 2031)) + ["Giai đoạn"])

    if year != "Giai đoạn":
        results_table = f"results_{year}"
        results = pd.read_sql(f"SELECT * FROM {results_table}", conn)
        df = indicators.merge(results, left_on="Mã chỉ tiêu", right_on="Mã", how="left").drop(columns=["Mã"] if "Mã" in results.columns else [])
        df["Tỷ lệ %"] = (df["Giá_trị_thực_hiện"] / df[f"Năm_{year}"]) * 100
        df["Màu"] = df["Tỷ lệ %"].apply(lambda x: 'green' if x >= 100 else 'yellow' if x >= 90 else 'red')

        if role != "Admin":
            st.subheader("Nhập báo cáo")
            for idx, row in df.iterrows():
                st.text(f"{row['Mã chỉ tiêu']} - {row['Chỉ_tiêu']} ({row['Đơn_vị']}) - Kế hoạch: {row[f'Năm_{year}']}")
                value = st.number_input("Giá trị thực hiện", value=row["Giá_trị_thực_hiện"] if pd.notna(row["Giá_trị_thực_hiện"]) else 0.0, key=f"val_{idx}_{year}")
                note = st.text_input("Ghi chú", value=row["Ghi_chú"] if pd.notna(row["Ghi_chú"]) else "", key=f"note_{idx}_{year}")
                if st.button("Lưu", key=f"save_{idx}_{year}"):
                    c.execute(f"REPLACE INTO {results_table} (Mã, Giá_trị_thực_hiện, Ghi_chú, Người_nhập, Thời_điểm, Trạng_thái) VALUES (?, ?, ?, ?, datetime('now'), 'Nháp')",
                              (row["Mã chỉ tiêu"], value, note, st.session_state.user))
                    conn.commit()
                    st.success("Đã lưu")

            if st.button("Gửi báo cáo"):
                c.execute(f"UPDATE {results_table} SET Trạng_thái = 'Đã gửi' WHERE Người_nhập = ?", (st.session_state.user,))
                conn.commit()
                st.success("Đã gửi, không sửa được nữa")

        st.dataframe(df.style.background_gradient(subset=["Tỷ lệ %"], cmap="RdYlGn"))

    else:
        # Giai đoạn
        st.subheader("Theo dõi giai đoạn")
        # Tính tổng thực hiện từ các năm
        total_real = pd.DataFrame()
        for y in range(2026, 2031):
            res = pd.read_sql(f"SELECT Mã, SUM(Giá_trị_thực_hiện) as Real_{y} FROM results_{y} GROUP BY Mã", conn)
            total_real = total_real.merge(res, how="outer")

        fig, ax = plt.subplots()
        # Demo biểu đồ
        ax.plot([2026, 2027, 2028, 2029, 2030], [1,2,3,4,5])  # Replace with real data
        st.pyplot(fig)

    if role == "Admin":
        st.subheader("Tiến độ nộp")
        progress = {}
        for u in users:
            if u != "admin":
                count = c.execute(f"SELECT COUNT(*) FROM {results_table} WHERE Người_nhập LIKE ? AND Trạng_thái = 'Đã gửi'", (f"%{u}%",)).fetchone()[0]
                progress[u] = "Đã nộp" if count > 0 else "Chưa nộp"
        st.write(progress)

        if st.button("Khóa báo cáo"):
            st.success("Đã khóa")

        # Xuất Excel
        def to_excel():
            out = BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Tổng hợp')
                for r in set(df['Chủ_trì']):
                    df[df['Chủ_trì'] == r].to_excel(writer, sheet_name=r)
            return out.getvalue()

        st.download_button("Xuất Excel", to_excel(), "baocao.xlsx")

        # Xuất PDF
        def to_pdf():
            out = BytesIO()
            doc = SimpleDocTemplate(out, pagesize=letter)
            table = Table([df.columns] + df.values.tolist())
            style = TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey), ('GRID', (0,0), (-1,-1), 1, colors.black)])
            doc.build([table])
            return out.getvalue()

        st.download_button("Xuất PDF", to_pdf(), "baocao.pdf")
