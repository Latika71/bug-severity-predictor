"""
streamlit_app.py — Bug Severity Predictor UI
Login + Register + User Dashboard + Admin Panel
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Config ──
API_URL = "https://bug-severity-predictor-ucxb.onrender.com"   

st.set_page_config(
    page_title="Bug Severity Predictor",
    page_icon="🐛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS (teri purani CSS same rakhi hai) ──
st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252940);
        border-radius: 16px; padding: 20px;
        border: 1px solid #2e3250; text-align: center;
    }
    .severity-badge {
        display: inline-block; padding: 10px 28px;
        border-radius: 50px; font-size: 1.4rem;
        font-weight: 700; letter-spacing: 1px; margin: 10px 0;
    }
    .section-title {
        font-size: 1.1rem; color: #7c83a0; font-weight: 600;
        text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;
    }
    .result-card {
        background: linear-gradient(135deg, #1a1f35, #1e2540);
        border-radius: 20px; padding: 30px;
        border: 2px solid #3d4570; text-align: center;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    label { color: #c0c8e0 !important; font-size: 0.88rem !important; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════
# SESSION STATE — Login info store karo
# ════════════════════════════════════════

if "token"    not in st.session_state: st.session_state.token    = None
if "username" not in st.session_state: st.session_state.username = None
if "role"     not in st.session_state: st.session_state.role     = None
if "page"     not in st.session_state: st.session_state.page     = "login"

# ════════════════════════════════════════
# HELPER — Auth header banao
# ════════════════════════════════════════

def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def is_logged_in():
    return st.session_state.token is not None

# ════════════════════════════════════════
# PAGE — LOGIN / REGISTER
# ════════════════════════════════════════

def show_login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("## 🐛 Bug Severity Predictor")
        st.markdown("---")

        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        # ── LOGIN TAB ──
        with tab1:
            st.markdown("### Welcome back!")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")

            if st.button("Login →", use_container_width=True, type="primary"):
                if username and password:
                    try:
                        res = requests.post(f"{API_URL}/login", json={
                            "username": username,
                            "password": password
                        }, timeout=60)
                        data = res.json()
                        if res.status_code == 200 and data.get("success"):
                            st.session_state.token    = data["token"]
                            st.session_state.username = data["username"]
                            st.session_state.role     = data["role"]
                            st.session_state.page     = "predict"
                            st.rerun()
                        
                            
                        else:
                            st.error(f"❌ {data.get('detail', 'Login failed')}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("Username aur password dono bharo!")

        # ── REGISTER TAB ──
        with tab2:
            st.markdown("### Create Account")
            reg_user  = st.text_input("Username",        key="reg_user")
            reg_email = st.text_input("Email",           key="reg_email")
            reg_pass  = st.text_input("Password", type="password", key="reg_pass")
            reg_role = "customer"  # Register se sirf customer banta hai
            if st.button("Register →", use_container_width=True, type="primary"):
                if reg_user and reg_email and reg_pass:
                    try:
                        res = requests.post(f"{API_URL}/register", json={
                            "username": reg_user,
                            "email":    reg_email,
                            "password": reg_pass,
                            "role":     reg_role
                        }, timeout=60)
                        data = res.json()
                        if res.status_code == 200 and data.get("success"):
                            st.success ("✅ Account created successfully! Please login to continue.")
                        else:
                            st.error(f"❌ {data.get('detail', 'Registration failed')}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("Saari fields bharo!")

# ════════════════════════════════════════
# OPTIONS (teri purani wali same)
# ════════════════════════════════════════

OPTIONS = {
    'bug_type': ['APIFailure','AuthBypass','BufferOverflow','ConfigError',
                 'CrashOnLaunch','DataCorruption','Deadlock','FileNotFound',
                 'IncorrectCalculation','InfiniteLoop','LogicError','MemoryLeak',
                 'NetworkTimeout','NullPointerException','PerformanceDegradation',
                 'RaceCondition','SQLInjection','UIGlitch','UncaughtException','XSS'],
    'component': ['API_Gateway','Analytics','Authentication','CacheLayer',
                  'DataPipeline','Database','EmailService','FileStorage',
                  'Frontend','Notification','Payment','Reporting',
                  'Scheduler','SearchEngine','UserManagement'],
    'environment': ['Development','Production','QA','Staging','UAT'],
    'platform':    ['API','Android','Desktop','Web','iOS'],
    'operating_system': ['Android12','CentOS7','Ubuntu20','Windows10',
                         'Windows11','iOS16','macOS13'],
    'browser':     ['Chrome','Edge','Firefox','Mobile_App','N/A','Safari'],
    'reporter_role': ['Client','DevOps','Developer','End_User',
                      'Product_Manager','QA_Engineer'],
    'module':  ['Core','Integration','Internal','Plugin','ThirdParty'],
    'status':  ['Closed','In_Progress','Open','Reopened','Resolved'],
}

SEVERITY_COLORS = {
    'Critical':'#e74c3c','High':'#e67e22',
    'Medium':'#f1c40f','Low':'#2ecc71'
}
SEVERITY_EMOJI = {
    'Critical':'🔴','High':'🟠','Medium':'🟡','Low':'🟢'
}

# ════════════════════════════════════════
# PAGE — PREDICT (Customer)
# ════════════════════════════════════════

def show_predict_page():
    st.markdown("# 🔍 Bug Severity Predictor")
    st.markdown("Fill in bug details to get **AI-powered severity prediction.**")
    st.markdown("---")

    with st.form("predict_form"):
        st.markdown('<p class="section-title">🐛 Bug Information</p>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: bug_type  = st.selectbox("Bug Type",   OPTIONS['bug_type'])
        with c2: component = st.selectbox("Component",  OPTIONS['component'])
        with c3: module    = st.selectbox("Module",     OPTIONS['module'])

        st.markdown('<p class="section-title">🌐 Environment</p>', unsafe_allow_html=True)
        c4, c5, c6, c7 = st.columns(4)
        with c4: environment = st.selectbox("Environment",      OPTIONS['environment'])
        with c5: platform    = st.selectbox("Platform",         OPTIONS['platform'])
        with c6: os_val      = st.selectbox("Operating System", OPTIONS['operating_system'])
        with c7: browser     = st.selectbox("Browser",          OPTIONS['browser'])

        st.markdown('<p class="section-title">👤 Reporter</p>', unsafe_allow_html=True)
        c8, c9 = st.columns(2)
        with c8: reporter_role = st.selectbox("Reporter Role", OPTIONS['reporter_role'])
        with c9: status_val    = st.selectbox("Bug Status",    OPTIONS['status'])

        st.markdown('<p class="section-title">📈 Metrics</p>', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            affected_users    = st.number_input("Affected Users",   0, 100000, 100)
            reproduction_rate = st.slider("Reproduction Rate", 0, 100, 50)
        with m2:
            response_time_ms  = st.number_input("Response Time ms", 0, 60000, 500)
            memory_usage_mb   = st.number_input("Memory MB",        0, 32000, 512)
        with m3:
            cpu_usage_pct            = st.slider("CPU %",           0.0, 100.0, 50.0)
            business_impact_score    = st.slider("Business Impact", 1.0, 100.0, 50.0)
        with m4:
            fix_time_hours      = st.number_input("Fix Time hrs", 0, 500, 8)
            reopen_count        = st.number_input("Reopen Count", 0, 50,  0)

        st.markdown('<p class="section-title">🔒 Flags</p>', unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        with f1: sla_breached       = st.checkbox("SLA Breached")
        with f2: is_security        = st.checkbox("Security Related")
        with f3: customer_reported  = st.checkbox("Customer Reported")

        submitted = st.form_submit_button("🔍 Predict Severity", use_container_width=True, type="primary")

    if submitted:
        payload = {
            "bug_type": bug_type, "component": component,
            "environment": environment, "platform": platform,
            "operating_system": os_val, "browser": browser,
            "reporter_role": reporter_role, "module": module,
            "status": status_val,
            "affected_users": affected_users,
            "response_time_ms": response_time_ms,
            "business_impact_score": float(business_impact_score),
            "reproduction_rate": float(reproduction_rate),
            "memory_usage_mb": float(memory_usage_mb),
            "cpu_usage_pct": float(cpu_usage_pct),
            "fix_time_hours": float(fix_time_hours),
            "reopen_count": reopen_count,
            "sla_breached": int(sla_breached),
            "is_security_related": int(is_security),
            "customer_reported": int(customer_reported),
        }
        try:
            res  = requests.post(f"{API_URL}/predict",
                                 json=payload, headers=auth_headers(), timeout=60)
            data = res.json()

            if res.status_code == 401:
                st.error("❌ Session expire ho gaya! Dobara login karo.")
                st.session_state.token = None
                st.rerun()

            if data.get("success"):
                sev   = data["result"]["predicted_severity"]
                conf  = data["result"]["confidence"]
                color = SEVERITY_COLORS[sev]

                st.markdown(f"""
                <div class="result-card">
                    <p style="color:#7c83a0">Predicted Severity</p>
                    <div class="severity-badge" style="background:{color}22;color:{color};border:2px solid {color}">
                        {SEVERITY_EMOJI[sev]} {sev}
                    </div>
                    <p style="color:#fff;font-size:1.1rem">Confidence: <b>{conf:.1f}%</b></p>
                </div>
                """, unsafe_allow_html=True)

                # Probability chart
                probs   = data["result"]["all_probabilities"]
                prob_df = pd.DataFrame({
                    "Severity":    list(probs.keys()),
                    "Probability": list(probs.values()),
                    "Color":       [SEVERITY_COLORS[k] for k in probs.keys()]
                })
                fig = go.Figure(go.Bar(
                    x=prob_df["Probability"], y=prob_df["Severity"],
                    orientation='h',
                    marker_color=prob_df["Color"],
                    text=[f"{v:.1f}%" for v in prob_df["Probability"]],
                    textposition='outside'
                ))
                fig.update_layout(
                    title="Class Probabilities",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#c0c8e0', height=250,
                    margin=dict(l=10, r=60, t=40, b=10),
                    xaxis=dict(range=[0,110], showgrid=False),
                    yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig, use_container_width=True)

                actions = {
                    'Critical': "🚨 **Immediate!** Fix within **2 hours**. Escalate now.",
                    'High':     "⚠️ **High priority.** Fix within **24 hours**.",
                    'Medium':   "📌 **Next sprint.** Fix within **1 week**.",
                    'Low':      "📝 **Log & monitor.** Fix in upcoming release."
                }
                st.info(actions[sev])
            else:
                st.error(f"Error: {data.get('detail','Unknown')}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


# ════════════════════════════════════════
# PAGE — MY HISTORY (Customer)
# ════════════════════════════════════════

def show_my_history():
    st.markdown("# 📋 My Prediction History")
    st.markdown("---")

    limit = st.selectbox("Show last", [10, 20, 50, 100], index=1)

    try:
        res  = requests.get(f"{API_URL}/my-history?limit={limit}",
                            headers=auth_headers(), timeout=60)
        data = res.json()

        if res.status_code == 401:
            st.error("Session expire! Dobara login karo.")
            st.session_state.token = None
            st.rerun()

        if data.get("success") and data["data"]:
            df = pd.DataFrame(data["data"])

            # Filter
            sev_filter = st.multiselect("Filter by Severity",
                ['Critical','High','Medium','Low'],
                default=['Critical','High','Medium','Low'])

            df_filtered = df[df["predicted_severity"].isin(sev_filter)]
            total = len(df_filtered)

            # Cards — selected severities ke according
            if sev_filter:
                cols = st.columns(len(sev_filter))
                for col, sev in zip(cols, sev_filter):
                    count = len(df_filtered[df_filtered["predicted_severity"] == sev])
                    color = SEVERITY_COLORS[sev]
                    col.markdown(f"""
                        <div class="metric-card">
                            <p style="color:{color};font-size:1.3rem">{SEVERITY_EMOJI[sev]} {sev}</p>
                            <p style="color:#fff;font-size:2rem;font-weight:700">{count}</p>
                            <p style="color:#7c83a0;font-size:0.8rem">{round(count/total*100) if total else 0}%</p>
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("---")

            # Table
            display_cols = ['id','bug_type','component','environment',
                            'platform','predicted_severity','confidence','created_at']
            available = [c for c in display_cols if c in df_filtered.columns]

            def color_sev(val):
                return {
                    'Critical': 'background-color:#e74c3c22;color:#e74c3c',
                    'High':     'background-color:#e67e2222;color:#e67e22',
                    'Medium':   'background-color:#f1c40f22;color:#f1c40f',
                    'Low':      'background-color:#2ecc7122;color:#2ecc71',
                }.get(val, '')

            if len(df_filtered) > 0:
                styled = df_filtered[available].style.map(
                    color_sev, subset=['predicted_severity']
                ).format({'confidence': '{:.1f}%'})

                st.dataframe(styled, use_container_width=True, height=400)
                st.download_button("⬇️ Download CSV",
                    df_filtered.to_csv(index=False),
                    "my_predictions.csv", "text/csv",
                    key="download_my_history")
            else:
                st.info("Selected filters ke according koi prediction nahi mili.")
        else:
            st.info("Koi prediction nahi abhi tak! Pehle 🔍 Predict karo.")
    except Exception as e:
        st.error(f"Error loading history: {e}")



# ════════════════════════════════════════
# PAGE — MY DASHBOARD (Customer)
# ════════════════════════════════════════

def show_my_dashboard():
    st.markdown("# 📊 My Dashboard")
    st.markdown("---")

    try:
        res  = requests.get(f"{API_URL}/my-stats", headers=auth_headers(), timeout=60)
        hres = requests.get(f"{API_URL}/my-history?limit=100", headers=auth_headers(), timeout=60)
        stats  = res.json().get("stats", {})
        h_data = hres.json().get("data", [])

        if stats:
            df = pd.DataFrame(h_data)

            total = sum(stats.values())
            st.markdown(f"### Total Predictions: **{total}**")
            st.markdown("---")

            c1, c2 = st.columns(2)
            with c1:
                fig = go.Figure(go.Pie(
                    labels=list(stats.keys()),
                    values=list(stats.values()),
                    hole=0.6,
                    marker_colors=[SEVERITY_COLORS[k] for k in stats.keys()]
                ))
                fig.update_layout(
                    title="My Severity Distribution",
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#c0c8e0', height=320
                )
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                if "confidence" in df.columns:
                    fig2 = px.box(df, x="predicted_severity", y="confidence",
                        color="predicted_severity",
                        color_discrete_map=SEVERITY_COLORS,
                        title="My Confidence by Severity")
                    fig2.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#c0c8e0', height=320, showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Koi data nahi abhi! Pehle predict karo.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


# ════════════════════════════════════════
# PAGE — ADMIN DASHBOARD
# ════════════════════════════════════════

def show_admin_panel():
    st.markdown("# 🛡️ Admin Panel")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overall Stats",
        "📋 All Predictions",
        "👥 All Users",
        "🔐 Login Logs"
    ])

    # ── TAB 1: Overall Stats ──
    with tab1:
        try:
            res   = requests.get(f"{API_URL}/admin/stats",   headers=auth_headers(), timeout=60)
            hres  = requests.get(f"{API_URL}/admin/all-predictions?limit=200",
                                  headers=auth_headers(), timeout=60)
            stats  = res.json().get("stats", {})
            h_data = hres.json().get("data", [])

            if stats:
                df = pd.DataFrame(h_data)
                total = sum(stats.values())
                st.markdown(f"### 📦 Total Predictions: `{total}`")

                cols = st.columns(4)
                for col, sev in zip(cols, ['Critical','High','Medium','Low']):
                    count = stats.get(sev, 0)
                    color = SEVERITY_COLORS[sev]
                    col.markdown(f"""
                    <div class="metric-card">
                        <p style="color:{color};font-size:1.3rem">{SEVERITY_EMOJI[sev]} {sev}</p>
                        <p style="color:#fff;font-size:2rem;font-weight:700">{count}</p>
                        <p style="color:#7c83a0;font-size:0.8rem">{round(count/total*100) if total else 0}%</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")
                c1, c2 = st.columns(2)
                with c1:
                    fig = go.Figure(go.Pie(
                        labels=list(stats.keys()),
                        values=list(stats.values()),
                        hole=0.6,
                        marker_colors=[SEVERITY_COLORS[k] for k in stats.keys()]
                    ))
                    fig.update_layout(title="Severity Distribution",
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#c0c8e0', height=320)
                    st.plotly_chart(fig, use_container_width=True)

                with c2:
                    if "environment" in df.columns:
                        env_sev = pd.crosstab(df["environment"],
                                              df["predicted_severity"])
                        fig2 = px.imshow(env_sev,
                            color_continuous_scale='RdYlGn_r',
                            title="Environment vs Severity",
                            text_auto=True)
                        fig2.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='#c0c8e0', height=320)
                        st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    # ── TAB 2: All Predictions ──
    with tab2:
        try:
            
            limit_option = st.selectbox("Show last", [20, 50, 100, 200, "All"], key="admin_pred_limit")
            limit = 99999 if limit_option == "All" else limit_option
            res   = requests.get(f"{API_URL}/admin/all-predictions?limit={limit}",
                                  headers=auth_headers(), timeout=60)
            data  = res.json()

            if data.get("success") and data["data"]:
                df = pd.DataFrame(data["data"])
                display_cols = ['id','user_id','bug_type','component',
                                'environment','predicted_severity','confidence','created_at']
                available    = [c for c in display_cols if c in df.columns]

                def color_sev(val):
                    return {
                        'Critical':'background-color:#e74c3c22;color:#e74c3c',
                        'High':    'background-color:#e67e2222;color:#e67e22',
                        'Medium':  'background-color:#f1c40f22;color:#f1c40f',
                        'Low':     'background-color:#2ecc7122;color:#2ecc71',
                    }.get(val,'')

                styled = df[available].style.map(
                    color_sev, subset=['predicted_severity']
                ).format({'confidence': '{:.1f}%'})
                st.dataframe(styled, use_container_width=True, height=450)
                st.download_button("⬇️ Download All CSV",
                    df.to_csv(index=False), "all_predictions.csv", "text/csv")
            else:
                st.info("Koi prediction nahi abhi tak.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    # ── TAB 3: All Users ──
    with tab3:
        try:
            res  = requests.get(f"{API_URL}/admin/all-users", headers=auth_headers(), timeout=60)
            data = res.json()

            if data.get("success") and data["data"]:
                df = pd.DataFrame(data["data"])
                st.markdown(f"### 👥 Total Users: `{len(df)}`")

                # Role breakdown
                role_counts = df["role"].value_counts()
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("👤 Customers", role_counts.get("customer", 0))
                with c2:
                    st.metric("🛡️ Admins", role_counts.get("admin", 0))

                st.markdown("---")
                st.dataframe(df, use_container_width=True, height=400)
                st.download_button("⬇️ Download Users CSV",
                    df.to_csv(index=False), "all_users.csv", "text/csv")
            else:
                st.info("Koi user nahi abhi tak.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    # ── TAB 4: Login Logs ──
    with tab4:
        try:
            res  = requests.get(f"{API_URL}/admin/login-logs", headers=auth_headers(), timeout=60)
            data = res.json()

            if data.get("success") and data["data"]:
                df = pd.DataFrame(data["data"])
                st.markdown(f"### 🔐 Total Logins: `{len(df)}`")
                st.dataframe(df, use_container_width=True, height=400)
                st.download_button("⬇️ Download Logs CSV",
                    df.to_csv(index=False), "login_logs.csv", "text/csv")
            else:
                st.info("Koi login log nahi abhi tak.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


# ════════════════════════════════════════
# SIDEBAR + MAIN ROUTER
# ════════════════════════════════════════

if not is_logged_in():
    show_login_page()
else:
    with st.sidebar:
        st.markdown(f"## 🐛 Bug Severity\n### Predictor")
        st.markdown(f"👤 **{st.session_state.username}**")
        st.markdown(f"🏷️ Role: `{st.session_state.role}`")
        st.markdown("---")

        # Customer vs Admin ka alag menu
        if st.session_state.role == "admin":
            page = st.radio("Navigation", [
                "🔍 Predict",
                "📋 My History",
                "📊 My Dashboard",
                "🛡️ Admin Panel"
            ], label_visibility="collapsed")
        else:
            page = st.radio("Navigation", [
                "🔍 Predict",
                "📋 My History",
                "📊 My Dashboard",
            ], label_visibility="collapsed")

        st.markdown("---")

       
        

        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.token    = None
            st.session_state.username = None
            st.session_state.role     = None
            st.rerun()

    # ── Page routing ──
    if   page == "🔍 Predict":      show_predict_page()
    elif page == "📋 My History":   show_my_history()
    elif page == "📊 My Dashboard": show_my_dashboard()
    elif page == "🛡️ Admin Panel":  show_admin_panel()
