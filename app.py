import streamlit as st
import mysql.connector
import pandas as pd
from streamlit_option_menu import option_menu

# إعداد الصفحة
st.set_page_config(page_title="E-Commerce Dashboard 🛍️", layout="wide")

# دالة الاتصال بقاعدة البيانات
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",  # غيّرها حسب إعدادك
        database="ECommerceDB"
    )

# شريط التنقل العلوي (Navigation)
st.markdown(
    """
    <style>
        .nav-container {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 20px;
        }
        .nav-item {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            text-decoration: none;
            padding: 8px 18px;
            border-radius: 10px;
            background-color: #f0f0f0;
        }
        .nav-item:hover {
            background-color: #ddd;
        }
        .active {
            background-color: #0078ff;
            color: white !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# -------- صفحة البيانات (Data) --------
def Data():
    st.title("🛍️ E-Commerce Dashboard - Data Page")

    try:
        conn = get_connection()
        st.success("✅ Connected to ECommerceDB successfully!")

        # عرض أسماء الجداول
        query = "SHOW TABLES;"
        tables = pd.read_sql(query, conn)

        st.subheader("📂 Available Tables")
        st.dataframe(tables)

        # اختيار جدول للعرض
        table_name = st.selectbox("📊 اختر جدول لعرضه", tables.values.flatten())

        if table_name:
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
            st.dataframe(df, use_container_width=True)

            # -------- Sidebar Filters --------
    finally:
        if 'conn' in locals():
            conn.close()

# -------- Visualization Page --------
# -------- Visualization Function --------
def Visualization():
    import streamlit as st
    import plotly.express as px
    import pandas as pd
    import mysql.connector
    import plotly.graph_objects as go

    st.title("📊 Visualization Page")

    # --- إعداد الاتصال بقاعدة البيانات ---
    st.sidebar.header("Database Connection")

    host = st.sidebar.text_input("Host", value="localhost")
    user = st.sidebar.text_input("User", value="root")
    password = st.sidebar.text_input("Password", type="password")
    database = st.sidebar.text_input("Database Name", value="ECommerceDB")

    if st.sidebar.button("🔗 Connect"):
        try:
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            st.success("✅ Connected to MySQL database successfully!")

            # --- تحميل البيانات من الجداول ---
            queries = {
                "categories": "SELECT * FROM Categories",
                "products": "SELECT * FROM Products",
                "orders": "SELECT * FROM Orders",
                "order_details": "SELECT * FROM OrderDetails",
                "customers": "SELECT * FROM Customers",
                "address": "SELECT * FROM Address",
                "calendar": "SELECT * FROM Calendar"
            }

            dataframes = {name: pd.read_sql(q, conn) for name, q in queries.items()}

            # --- دمج البيانات الرئيسية ---
            df = (
                dataframes["order_details"]
                .merge(dataframes["orders"], on="OrderID")
                .merge(dataframes["products"], on="ProductID")
                .merge(dataframes["categories"], on="CategoryID")
                .merge(
                    dataframes["calendar"].add_prefix("OrderDate_"),
                    left_on="OrderDateID",
                    right_on="OrderDate_DateID"
                )
            )

            st.subheader("Sales Analysis")

        # --- 1️⃣ إجمالي المبيعات حسب الشهر ---
            sales_by_month = df.groupby("OrderDate_MONTH")["TotalAmount"].sum().reset_index()

            # تخصيص الألوان
            colors = px.colors.qualitative.Set1

            # رسم البيانات باستخدام Plotly Express مع تخصيص الشكل
            fig1 = px.bar(
                sales_by_month,
                x="OrderDate_MONTH",
                y="TotalAmount",
                title="Total Sales per Month",
                text_auto=".2s",  # عرض النصوص التلقائية على الأعمدة
                color="OrderDate_MONTH",  # تخصيص الألوان حسب الشهر
                color_discrete_sequence=colors,  # تخصيص ألوان الأعمدة
            )

            # تخصيص النصوص التوضيحية (داخل الأعمدة)
            fig1.update_traces(
                textposition="inside",  # النصوص ستكون داخل الأعمدة
                textfont=dict(size=14, color="white")  # تخصيص الخط داخل الأعمدة
            )

            # تخصيص المحاور
            fig1.update_layout(
                xaxis_title="Month",
                yaxis_title="Total Sales",
                title_font_size=20,
                title_x=0.5,
                title_y=0.95,
                plot_bgcolor="rgba(0, 0, 0, 0)",
                paper_bgcolor="rgba(0, 0, 0, 0)",
                font=dict(
                    family="Arial, sans-serif",
                    size=12,
                    color="black"
                ),
                showlegend=False
            )

            # إضافة تفاعل مع المستخدم عند التمرير فوق الأعمدة
            fig1.update_traces(
                hoverinfo="x+y+text",  # يظهر التاريخ والمبيعات عند المرور بالفأرة
                hoverlabel=dict(
                    bgcolor="black",
                    font_size=14,
                    font_color="white"
                )
            )

    # عرض الرسم البياني باستخدام Streamlit
            st.plotly_chart(fig1, use_container_width=True)


                # --- 2️⃣ Pie Chart للمبيعات حسب الفئة ---
            sales_by_category = (
                df.groupby("CategoryName")["TotalAmount"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
        
            # تخصيص الألوان
            custom_colors = px.colors.sequential.Plasma
        
            # رسم الـ Pie Chart بشكل متطور مع تحسينات بصرية وتفاعلية
            fig2_pie = px.pie(
                sales_by_category,
                values="TotalAmount",
                names="CategoryName",
                title="Sales by Category",
                hole=0.4,  # لعمل شكل حلقي (Donut)
                color="CategoryName",  # تلوين كل قطاع بناءً على الفئة
                color_discrete_sequence=custom_colors,  # تخصيص الألوان
                hover_data=["CategoryName", "TotalAmount"],  # عرض تفاصيل إضافية عند التمرير
                labels={"TotalAmount": "Sales Amount", "CategoryName": "Category"}  # تحسين التسميات
            )
        
            # إضافة النسب المئوية داخل القطاعات
            fig2_pie.update_traces(
                textinfo="percent+label",  # عرض النسب المئوية مع الاسم
                textfont=dict(size=14, color="white"),  # تخصيص الخط داخل القطاعات
                pull=[0.1, 0.1, 0.1, 0.1] * (len(sales_by_category) // 4)  # تأثير عند المرور بالماوس (لزيادة التفاعل)
            )
        
            # تخصيص تصميم الشكل بشكل عام
            fig2_pie.update_layout(
                title_font_size=24,  # تغيير حجم خط العنوان
                title_x=0.5,  # توسيط العنوان
                title_y=0.95,  # رفع العنوان قليلًا
                plot_bgcolor="rgba(0, 0, 0, 0)",  # خلفية شفافة
                paper_bgcolor="rgba(0, 0, 0, 0)",  # خلفية الورقة شفافة
                font=dict(
                    family="Arial, sans-serif",  # نوع الخط
                    size=14,  # حجم الخط
                    color="black"  # لون النصوص
                ),
                showlegend=True,  # إظهار الأسطورة (Legend)
                legend_title="Categories",  # عنوان الأسطورة
                hoverlabel=dict(
                    bgcolor="rgba(0, 0, 0, 0.8)",  # خلفية للـ hover
                    font_size=16,  # حجم خط الـ hover
                    font_color="white"  # لون خط الـ hover
                ),
            )
        
            # إضافة نص في المنتصف (الجزء الحلقى) مثل "Total Sales"
            fig2_pie.add_annotation(
                text="Total Sales",  # النص الذي سيظهر في المنتصف
                x=0.5,  # توسيط النص في المنتصف
                y=0.5,  # توسيط النص عموديًا
                showarrow=False,  # عدم إظهار السهم
                font=dict(size=20, color="black"),  # تخصيص النص
                align="center",  # توسيط النص
            )
        
            # عرض الرسم البياني باستخدام Streamlit
            st.plotly_chart(fig2_pie, use_container_width=True)

            # --- 2️⃣.ب Line Chart لإجمالي المبيعات عبر السنوات ---
    # --- 3️⃣ إجمالي المبيعات حسب السنة ---
            sales_by_year = (
                df.groupby("OrderDate_YEAR")["TotalAmount"]
                .sum()
                .reset_index()
                .sort_values("OrderDate_YEAR")
            )

            # تحويل السنوات إلى أعداد صحيحة
            sales_by_year["OrderDate_YEAR"] = sales_by_year["OrderDate_YEAR"].astype(int)

            # رسم الخط مع تخصيصات متقدمة
            fig2_line = px.line(
                sales_by_year,
                x="OrderDate_YEAR",
                y="TotalAmount",
                markers=True,
                title="📈 Total Sales Over Years",
                color_discrete_sequence=["#1f77b4"]  # اختيار اللون الأساسي
            )

            # تخصيص سمك الخط
            fig2_line.update_traces(line=dict(width=4, dash="solid"), marker=dict(size=8, color="blue"))

            # إضافة خط الاتجاه العام (Trendline)
            trendline = go.Scatter(
                x=sales_by_year["OrderDate_YEAR"],
                y=sales_by_year["TotalAmount"].rolling(window=3).mean(),  # متوسط متحرك بسيط
                mode="lines",
                name="Trendline",
                line=dict(color="red", width=2, dash="dot")  # الخط سيكون متقطعًا
            )
            fig2_line.add_trace(trendline)

            # إضافة خط متوسط متحرك (مثال: 3 سنوات)
            moving_avg = go.Scatter(
                x=sales_by_year["OrderDate_YEAR"],
                y=sales_by_year["TotalAmount"].rolling(window=3).mean(),
                mode="lines",
                name="Moving Average (3 Years)",
                line=dict(color="orange", width=3)
            )
            fig2_line.add_trace(moving_avg)

            # تخصيص المحاور
            fig2_line.update_layout(
                title="📈 Total Sales Over Years",
                title_font_size=20,
                title_x=0.5,  # توسيط العنوان
                title_y=0.95,  # رفع العنوان
                xaxis_title="Year",
                yaxis_title="Total Sales",
                xaxis=dict(
                    tickmode="linear",  # تكرار المحور الأفقي كل سنة
                    tick0=sales_by_year["OrderDate_YEAR"].min(),
                    dtick=1,  # كل سنة تكون تابعة
                    showgrid=True,
                    gridcolor="lightgrey",  # لون الشبكة
                    zeroline=False  # إخفاء خط الصفر
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="lightgrey",  # لون الشبكة
                    zeroline=False  # إخفاء خط الصفر
                ),
                plot_bgcolor="rgba(0, 0, 0, 0)",  # خلفية شفافة
                paper_bgcolor="rgba(0, 0, 0, 0)",  # خلفية الورقة شفافة
                font=dict(
                    family="Arial, sans-serif",
                    size=14,
                    color="black"
                ),
                hoverlabel=dict(
                    bgcolor="black",
                    font_size=16,
                    font_color="white"
                ),
                showlegend=True,  # إظهار الأسطورة
                legend_title="Legend",
            )

            # تخصيص التفاعل عند المرور بالماوس
            fig2_line.update_traces(
                hoverinfo="x+y+text",  # عرض التفاصيل عند التمرير
                hoverlabel=dict(bgcolor="rgba(0, 0, 0, 0.8)", font_size=16, font_color="white")
            )

            # إضافة شرح عند التمرير على النقاط
            fig2_line.update_traces(
                text=sales_by_year["TotalAmount"].apply(lambda x: f"${x:,.2f}"),
                textposition="top center",
            )

            # عرض الرسم البياني باستخدام Streamlit
            st.plotly_chart(fig2_line, use_container_width=True)

            # --- 3️⃣ أفضل العملاء ---
            top_customers = (
                df.groupby("CustomerID")["TotalAmount"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
                .merge(dataframes["customers"], on="CustomerID")
            )
            top_customers["CustomerName"] = top_customers["FirstName"] + " " + top_customers["LastName"]

            fig3 = px.bar(
                top_customers,
                x="CustomerName",
                y="TotalAmount",
                title="Top 10 Customers",
                text_auto=".2s",
                color="TotalAmount"
        )
            st.plotly_chart(fig3, use_container_width=True)
            
            # --- Scatter Plot: Product Price vs Total Sales ---
            product_sales = df.groupby("ProductName")["TotalAmount"].sum().reset_index()
            product_price = df.groupby("ProductName")["UnitPrice"].mean().reset_index()
            scatter_df = product_sales.merge(product_price, on="ProductName")

            fig_scatter = px.scatter(
                scatter_df,
                x="UnitPrice",
                y="TotalAmount",
                size="TotalAmount",
                hover_name="ProductName",
                title="Product Price vs Total Sales",
                color="TotalAmount",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)


            
            
            # --- Box Plot: Price Distribution per Category ---
            fig_box = px.box(
                df,
                x="CategoryName",
                y="UnitPrice",
                color="CategoryName",
                title="Price Distribution per Category"
            )
            st.plotly_chart(fig_box, use_container_width=True)
            
            st.write("______________")
            st.write("## End of Dashboard")
            st.write("______________")
            st.write("## About")
            st.write(
                "#### This dashboard was created by [Eng. Mohamed Nasr](https://www.linkedin.com/in/medoox369)."
            )
            st.write("#### All ways to get to the code, Dashboard and Report: [Power BI](https://app.powerbi.com/view?r=eyJrIjoiMGEwNDg0MWUtOTY0My00N2Y4LThmYWEtZTY2M2JiNzU5MzE1IiwidCI6ImNmNzIyMWNkLTNiYzYtNDEwMS04NzYyLTU0ZjQ0ZjNiYzg5YSIsImMiOjl9) | [Excel](https://drive.google.com/file/d/1ZGGkW7aOA3yB67RCezqvcg64heiXlp68/view?usp=sharing) | [Report](https://docs.google.com/document/d/17wfT1_k_espW1u1Y-nqJzWZ5lPKsE-DN/edit?usp=sharing&ouid=116781748036556031868&rtpof=true&sd=true)")











            conn.close()

        except Exception as e:
            st.error(f"❌ Connection failed: {e}")


# -------- صفحة التقارير (Report) --------
import streamlit as st

def Report():
    st.title("🧾 Report Page")

    st.markdown("### 1. Categories")
    st.write("""
    - **CategoryID**: Unique identifier for each product category.  
    - **CategoryName**: Name of the product category (e.g., Electronics, Clothing).  
    """)

    st.markdown("### 1. Products")

    st.write("""
    - **ProductID**: Unique identifier for each product.  
    - **ProductName**: Name of the product.  
    - **CategoryID**: Links the product to its category.  
    - **Description**: Short text describing the product.  
    - **Price**: Unit price of the product.  
    - **StockQuantity**: Number of items available in inventory.  
    """)

    st.markdown("### 1. Orders")

    st.write("""
    - **OrderID**: Unique identifier for each order.  
    - **CustomerID**: Links to the customer who placed the order.  
    - **OrderDateID**: Links to the calendar date when the order was placed.  
    - **DeliveryDateID**: Links to the calendar date for delivery.  
    - **TotalAmount**: Total value of the order.  
    """)

    st.markdown("### 1. OrderDetails")

    st.write("""
    - **OrderDetailID**: Unique identifier for each order line.  
    - **OrderID**: Identifies which order this line belongs to.  
    - **ProductID**: Identifies the product being ordered.  
    - **Quantity**: Number of units ordered.  
    - **UnitPrice**: Price per unit at the time of purchase.  
    """)

    st.markdown("### 1. Customers")

    st.write("""
    - **CustomerID**: Unique identifier for each customer.  
    - **FirstName**: Customer’s first name.  
    - **LastName**: Customer’s last name.  
    - **Email**: Customer’s email address.  
    - **Phone**: Customer’s phone number.  
    - **AddressID**: Links to the customer’s address.  
    - **RegistrationDateID**: Links to the calendar date of registration.  
    """)

    st.markdown("### 1. Address")

    st.write("""
    - **AddressID**: Unique identifier for each address.  
    - **Address**: Full street address.  
    - **City**: City name.  
    - **Country**: Country name.  
    """)

    st.markdown("### 1. Calendar")

    st.write("""
    - **DateID**: Surrogate key for each date.  
    - **DATE**: Actual calendar date.  
    - **DAY**: Day of the month.  
    - **DAYOFWEEK**: Name or number of the weekday.  
    - **MONTH**: Month number.  
    - **YEAR**: Year in 4 digits.  
    """)

    st.markdown("### 1. Top_Customers_2024")
    st.write("""
    - **CustomerName**: Full name of the customer.  
    - **TotalAmount**: Total spending of the customer in 2024.  
    - **TotalOrders**: Number of orders placed by the customer in 2024.  
    """)
    st.markdown("---")

    # Report Introduction
    st.markdown("""
    # Financial Performance Sales Analysis
    In this report, we present a comprehensive analysis of sales performance across various dimensions. We cover sales by category, quarterly performance, product sales, geographic customer distribution, and more. The goal of this report is to provide in-depth insights into sales trends to help you make informed business decisions.
    """)

    st.markdown("---")
    
    # --- 1. Categories by Revenue ---
    st.markdown("### 1. Categories by Revenue")
    st.markdown("""
    The **Toys & Games** category is the highest performer in revenue, generating **49M**.
    Other top-performing categories include **Pet Supplies (29M)** and **Food & Groceries (28M)**.
    On the other hand, **Home & Kitchen** and **Health & Wellness** categories are among the lower-grossing categories.
    """)

    # Suggestion for Growth:
    st.markdown("""
    **Suggestion:** Focus more marketing efforts and product innovations on the **Toys & Games** category, as it is the highest revenue generator. Consider exploring seasonal promotions for **Home & Kitchen** and **Health & Wellness** to boost sales in these categories.
    """)

    st.markdown("---")
    
    # --- 2. Total Sales by Quarter ---
    st.markdown("### 2. Total Sales by Quarter")
    st.markdown("""
    Sales are fairly evenly distributed across the four quarters, indicating **stable, non-seasonal performance**.
    * **Q2** leads slightly with **26.04%** of total sales (66.73M).
    * **Q3** has the lowest share at **24.42%** of total sales (62.57M).
    * **Q1 (24.71%)** and **Q4 (24.82%)** show nearly identical sales volumes.
    """)

    # Suggestion for Growth:
    st.markdown("""
    **Suggestion:** Although the sales distribution is stable, explore strategies to boost Q3 performance, which shows the lowest sales share. Special campaigns or new product launches could help drive sales during the traditionally slower quarter.
    """)

    st.markdown("---")
    
    # --- 3. Sales Trend Over Time ---
    st.markdown("### 3. Sales Trend Over Time")
    st.markdown("""
    The sales show a **volatile trend** over the observed periods.
    * A peak occurred around period 3 with **23.5M**.
    * A notable dip was observed around period 7, hitting a low of **19.9M**.
    * Sales ended the 12th period at **20.8M**, showing a slight recovery from the low point.
    """)

    # Suggestion for Growth:
    st.markdown("""
    **Suggestion:** Investigate the causes of the dip in period 7. A deep dive into product performance or customer behavior during that period may provide insights to prevent similar drops in future periods. Additionally, improving customer retention strategies could help smooth out volatility.
    """)

    st.markdown("---")
    
    # --- 4. Top 8 Products by Sales ---
    st.markdown("### 4. Top 8 Products by Sales")
    st.markdown("""
    **Black Bean Spaghetti** is the top-selling product by a large margin, with **21.3M** in sales.
    Other top products include **Pest Control Traps (17.9M)** and **Magnetic Spice Container (17.6M)**.
    This suggests strong sales in niche food and home utility products.
    """)

    # Suggestion for Growth:
    st.markdown("""
    **Suggestion:** Given the strong sales of niche products like **Black Bean Spaghetti**, consider expanding the product range in this category, potentially introducing new variations or related items to capture a larger market share.
    """)

    st.markdown("---")
    
    # --- 5. Bottom 5 Products by Sales ---
    st.markdown("### 5. Bottom 5 Products by Sales")
    st.markdown("""
    The bottom 5 products show very low sales figures, all under **100K**.
    * **Natural Fruit Snacks** is the lowest at **96K**.
    * Other low performers include **Baby Monitor (80K)** and **Car Emergency Kit (73K)**.
    This suggests a potential need for review or removal of these low-volume SKUs.
    """)

    # Suggestion for Growth:
    st.markdown("""
    **Suggestion:** Consider running targeted promotions or bundling low-performing products with popular items to clear out excess stock. If sales remain low despite efforts, it might be time to phase out these products and focus on higher-demand items.
    """)

    st.markdown("---")
    
    # --- 6. Quantity by Category ---
    st.markdown("### 6. Quantity by Category")
    st.markdown("""
    The **Clothing** category leads in unit volume, with **202K** units sold.
    **Food & Groceries** follows with **175K** units, and **Books** comes next with **173K**.
    This suggests high volume movement for apparel and fast-moving consumer goods.
    """)

    # Suggestion for Growth:
    st.markdown("""
    **Suggestion:** Capitalize on the high sales volume in the **Clothing** category by launching seasonal collections or collaborating with influencers. Similarly, **Food & Groceries** could benefit from subscription models or expanding the range of fast-moving products.
    """)

    st.markdown("---")
    
    # --- 7. Top Stock Value by Category ---
    st.markdown("### 7. Top Stock Value by Category")
    st.markdown("""
    As with previous revenue reports, **Toys & Games** maintains the highest value at **49M**.
    Other high-value categories include **Pet Supplies (29M)** and **Food & Groceries (28M)**.
    This suggests that while **Clothing** moves the most units, **Toys & Games** generates the most financial value.
    """)

    # Suggestion for Growth:
    st.markdown("""
    **Suggestion:** Focus on optimizing inventory and stock levels in **Toys & Games**, as they drive the highest financial value. Additionally, consider increasing stock in categories like **Pet Supplies** and **Food & Groceries** to meet demand.
    """)

    st.markdown("---")
    
    # --- 8. Top 11 Products by Price ---
    st.markdown("### 8. Top 11 Products by Price")
    st.markdown("""
    **Black Bean Spaghetti** is the highest-priced item at **1737**.
    Other expensive products include **Magnetic Spice Container (1623)** and **Pest Control Traps (1527)**.
    On the lower end, **Lentil Pasta (458)** and **Car Vacuum (466)** are the least expensive items.
    """)

    # Suggestion for Growth:
    st.markdown("""
    **Suggestion:** Since higher-priced items like **Black Bean Spaghetti** are strong performers, consider premium packaging or exclusive deals to further boost their appeal. You could also introduce bundles with lower-priced products to encourage customers to purchase higher-end items.
    """)

    st.markdown("---")
    
    # --- 9. Bottom 6 Products by Quantity ---
    st.markdown("### 9. Bottom 6 Products by Quantity")
    st.markdown("""
    The bottom-performing products show extremely low quantities sold (ranging from **10.9K to 12.1K**).
    * **Car Emergency Kit** (12.1K) and **Natural Fruit Snacks** (11.6K) are at the top of the low-quantity list.
    These products may need promotional efforts or stock review.
    """)

    # Suggestion for Growth:
    st.markdown("""
    **Suggestion:** Consider a targeted promotional campaign or offer discounts on these low-performing products to increase their sales. If they still do not meet performance expectations, it may be beneficial to discontinue these items.
    """)

    st.markdown("---")
    
    # --- 10. Top Customer by Revenue ---
    st.markdown("### 10. Top Customer by Revenue")
    st.markdown("""
    **Marge MacKeller** is the highest-value customer with sales totaling **129.2K**.
    Other top customers include **Zacharia Weems (121.7K)** and **Brear Denty (116.4K)**.
    This shows a slightly concentrated customer base, with the top 9 customers contributing sales ranging from **129.2K to 105.4K**.
    """)

    # Suggestion for Growth:
    st.markdown("""
    **Suggestion:** Consider offering loyalty programs or exclusive offers to the top customers to encourage repeat purchases. It's also important to diversify the customer base to reduce dependency on a few high-value customers.
    """)

    st.markdown("---")
    
    # --- Conclusion ---
    st.markdown("""
    ## Conclusion
    Through this report, we have identified top-performing categories and products, as well as areas where sales can be improved. We also reviewed customer behavior and sales trends. Key recommendations include focusing on high-revenue categories, optimizing inventory management, and implementing targeted campaigns for low-performing products. 
    By leveraging these insights, we can strategically grow the business and improve overall profitability.
    """)
















# -------- صفحة التواصل (Contact) --------
def contact():    
    st.title("📞 Contact Page")
    st.write("لو عندك أي استفسار أو عايز تتواصل:")
    st.markdown("""
    - 📧 **Email:** medoox369gmail.com  
    - 🌐 **LinkedIn:** [Mohamed Nasr](https://www.linkedin.com/in/medoox369)
    - 📱 **WhatsApp:** [+201276977748](https://wa.me/+201276977748)
    """)

    st.write("## About")
    st.write(
        "##### This dashboard was created by [Eng. Mohamed Nasr](https://www.linkedin.com/in/medoox369)."
    )
    st.write("##### The data used in this dashboard is from [Eng.Ahmed Ali](https://www.linkedin.com/in/ahmedalitop1/).")
    st.write("### End of Project")
    st.write("______________")
    st.write("### Thank You :smile:")




def streamlit_menu():
    selected = option_menu(
        menu_title=None,
        options=["Data", "Visualization", "Report", "Contact"],
        icons=["bar-chart-line-fill", "book", "graph-up-arrow", "envelope"],
        menu_icon="cast",
        orientation="horizontal",
    )
    return selected


# Initialize session state
if "selected" not in st.session_state:
    st.session_state["selected"] = None

selected = streamlit_menu()

if selected != st.session_state["selected"]:
    st.session_state["selected"] = selected
if st.session_state["selected"] == "Data":
    Data()
elif st.session_state["selected"] == "Visualization":
    Visualization()
elif st.session_state["selected"] == "Report":
    Report()
elif st.session_state["selected"] == "Contact":
    contact()
