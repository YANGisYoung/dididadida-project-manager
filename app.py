# -*- coding: utf-8 -*-
"""
============================================================
  “嘀嘀嗒嘀嗒”项目管理系统
  机械工程博士生的一站式管理平台：项目 / 实验 / 论文
  技术栈：Streamlit + Supabase (Auth + Postgres + Storage) + Plotly
============================================================
"""

import os
import uuid
import datetime as dt

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

# ------------------------------------------------------------
# 0. 页面基础设置（必须是本文件第一行 st 命令）
# ------------------------------------------------------------
st.set_page_config(
    page_title="嘀嘀嗒嘀嗒 · 项目管理系统",
    page_icon="⏱️",
    layout="wide",               # 宽屏布局：左侧列表 + 右侧详情
)

# ------------------------------------------------------------
# 1. 读取密钥配置（本地用 .env，部署到云端用 Streamlit Secrets，两种都兼容）
# ------------------------------------------------------------
load_dotenv()  # 本地运行时读取 .env 文件

def get_config(key: str):
    """优先读云端 Secrets，读不到再读本地环境变量"""
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key)

SUPABASE_URL = get_config("SUPABASE_URL")
SUPABASE_KEY = get_config("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("⚠️ 没有找到 Supabase 密钥！请检查 .env 文件（本地）或 Secrets 配置（云端）。")
    st.stop()

# ------------------------------------------------------------
# 2. 初始化 Supabase 客户端（整个 App 共用一个连接）
# ------------------------------------------------------------
@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

sb = get_supabase()

# ------------------------------------------------------------
# 3. 主题配色（温暖 / 高级 / 简洁；深色浅色可切换）
# ------------------------------------------------------------
THEMES = {
    "light": {  # 浅色：暖米白 + 陶土橙
        "bg":        "#FAF6F0",
        "sidebar":   "#F3EBE0",
        "text":      "#3D3229",
        "accent":    "#C4743B",
        "accent_h":  "#A95F2C",
        "card":      "#FFFFFF",
        "border":    "#E6DACA",
        "btn_text":  "#FFFFFF",
    },
    "dark": {   # 深色：暖棕黑 + 琥珀
        "bg":        "#1E1915",
        "sidebar":   "#292118",
        "text":      "#EDE3D5",
        "accent":    "#D9985F",
        "accent_h":  "#E8AE7E",
        "card":      "#2B231B",
        "border":    "#463A2C",
        "btn_text":  "#1E1915",
    },
}

if "theme" not in st.session_state:
    st.session_state.theme = "light"

def apply_theme():
    """根据当前主题注入自定义 CSS"""
    t = THEMES[st.session_state.theme]
    st.markdown(f"""
    <style>
      /* 全局背景与文字 */
      .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
      [data-testid="stSidebar"] {{ background-color: {t['sidebar']}; }}
      [data-testid="stSidebar"] * {{ color: {t['text']}; }}
      h1, h2, h3, h4, h5, p, span, label, .stMarkdown {{ color: {t['text']}; }}

      /* 标题着重色 */
      h1 {{ color: {t['accent']} !important; }}

      /* 按钮 */
      .stButton > button {{
          background-color: {t['accent']};
          color: {t['btn_text']};
          border: none; border-radius: 8px;
          padding: 0.35rem 1rem; font-weight: 600;
      }}
      .stButton > button:hover {{ background-color: {t['accent_h']}; }}

      /* 输入框、下拉框 */
      .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb],
      .stNumberInput input, .stDateInput input {{
          background-color: {t['card']} !important;
          color: {t['text']} !important;
          border-color: {t['border']} !important;
      }}

      /* 分隔线 */
      hr {{ border-color: {t['border']}; }}

      /* Expander 卡片感 */
      [data-testid="stExpander"] {{
          background-color: {t['card']};
          border: 1px solid {t['border']};
          border-radius: 10px;
      }}
    </style>
    """, unsafe_allow_html=True)

apply_theme()

# ------------------------------------------------------------
# 4. 登录状态管理（st.session_state）
# ------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None          # 当前登录用户对象
if "access_token" not in st.session_state:
    st.session_state.access_token = None  # 登录凭证（页面刷新后恢复会话用）
if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None

def restore_session():
    """页面每次 rerun 时，用保存的 token 恢复 Supabase 登录态（保证 RLS 权限正常）"""
    if st.session_state.access_token and st.session_state.refresh_token:
        try:
            sb.auth.set_session(st.session_state.access_token,
                                st.session_state.refresh_token)
        except Exception:
            pass

def auth_page():
    """登录 / 注册页面"""
    st.title("⏱️ 嘀嘀嗒嘀嗒 · 项目管理系统")
    st.caption("项目 · 实验 · 论文，一站式管理")
    st.divider()

    tab_login, tab_reg = st.tabs(["🔑 登录", "📝 注册"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("邮箱")
            pwd = st.text_input("密码", type="password")
            ok = st.form_submit_button("登录", use_container_width=True)
        if ok:
            try:
                res = sb.auth.sign_in_with_password({"email": email, "password": pwd})
                st.session_state.user = res.user
                st.session_state.access_token = res.session.access_token
                st.session_state.refresh_token = res.session.refresh_token
                st.rerun()
            except Exception as e:
                st.error(f"登录失败：{e}")

    with tab_reg:
        with st.form("reg_form"):
            email = st.text_input("邮箱", key="reg_email")
            pwd = st.text_input("密码（至少 6 位）", type="password", key="reg_pwd")
            ok = st.form_submit_button("注册并登录", use_container_width=True)
        if ok:
            try:
                res = sb.auth.sign_up({"email": email, "password": pwd})
                if res.session:  # 已关闭邮箱验证时，注册即登录
                    st.session_state.user = res.user
                    st.session_state.access_token = res.session.access_token
                    st.session_state.refresh_token = res.session.refresh_token
                    st.rerun()
                else:
                    st.info("注册成功！请到邮箱点击验证链接后再登录。")
            except Exception as e:
                st.error(f"注册失败：{e}")

# ------------------------------------------------------------
# 5. 通用小工具
# ------------------------------------------------------------
def uid() -> str:
    """当前用户 ID"""
    return st.session_state.user.id

def upload_image(file, folder: str):
    """把上传的图片存进 Supabase Storage 的 images 桶，返回公开链接"""
    if file is None:
        return None
    ext = file.name.split(".")[-1].lower()
    path = f"{uid()}/{folder}/{uuid.uuid4().hex}.{ext}"
    sb.storage.from_("images").upload(
        path, file.getvalue(), {"content-type": file.type or "image/png"}
    )
    return sb.storage.from_("images").get_public_url(path)

def fmt_date(s):
    """数据库里的日期字符串 → date 对象（容错）"""
    if not s:
        return None
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except Exception:
        return None

# ============================================================
# 模块一：项目管理（左列表 + 右详情）
# ============================================================
STAGES = ["方案设计", "详细设计", "加工调试", "已结项"]

def fetch_projects():
    return (sb.table("projects").select("*")
            .eq("user_id", uid())
            .order("created_at", desc=True)
            .execute().data)

def auto_timeline(project_id: str, deadline: dt.date):
    """新建项目时，按截止日期自动生成三个阶段的时间安排（之后可手动调整）"""
    start = dt.date.today()
    total = max((deadline - start).days, 7)      # 至少 7 天，避免除零/负数
    p1_end = start + dt.timedelta(days=int(total * 0.3))
    p2_end = start + dt.timedelta(days=int(total * 0.7))
    rows = [
        {"project_id": project_id, "phase_name": "方案设计",
         "start_date": str(start),  "end_date": str(p1_end)},
        {"project_id": project_id, "phase_name": "详细设计",
         "start_date": str(p1_end), "end_date": str(p2_end)},
        {"project_id": project_id, "phase_name": "加工调试",
         "start_date": str(p2_end), "end_date": str(deadline)},
    ]
    sb.table("timeline").insert(rows).execute()

def page_projects():
    st.header("📁 项目管理")

    # ---------- 新建项目 ----------
    with st.expander("➕ 新建项目", expanded=False):
        with st.form("new_project"):
            name = st.text_input("项目名称 *")
            source = st.text_input("客户 / 来源")
            deadline = st.date_input("截止日期",
                                     value=dt.date.today() + dt.timedelta(days=90))
            stage = st.selectbox("当前阶段", STAGES)
            ok = st.form_submit_button("创建项目")
        if ok:
            if not name.strip():
                st.warning("项目名称不能为空")
            else:
                res = sb.table("projects").insert({
                    "user_id": uid(), "name": name.strip(),
                    "source": source.strip(), "deadline": str(deadline),
                    "stage": stage,
                }).execute()
                auto_timeline(res.data[0]["id"], deadline)  # 自动生成甘特图数据
                st.success(f"项目「{name}」已创建，并已自动生成阶段时间线！")
                st.rerun()

    projects = fetch_projects()
    if not projects:
        st.info("还没有项目，点击上方「新建项目」开始吧！")
        return

    # ---------- 左右分栏布局 ----------
    col_list, col_detail = st.columns([1, 2.2], gap="large")

    with col_list:
        st.subheader("我的项目")
        # 用单选框当项目列表，右侧据此展示详情
        options = {f"{p['name']}（{p['stage']}）": p["id"] for p in projects}
        chosen = st.radio("点击选择项目", list(options.keys()), label_visibility="collapsed")
        pid = options[chosen]

    with col_detail:
        proj = next(p for p in projects if p["id"] == pid)
        show_project_detail(proj)

def show_project_detail(p: dict):
    """右侧详情区：基本信息 + BOM + 甘特图 + 文件链接"""
    st.subheader(f"📌 {p['name']}")

    # ----- 基本信息（可修改阶段与截止日期） -----
    with st.form(f"proj_edit_{p['id']}"):
        c1, c2, c3 = st.columns(3)
        new_stage = c1.selectbox("当前阶段", STAGES,
                                 index=STAGES.index(p["stage"]) if p["stage"] in STAGES else 0)
        new_deadline = c2.date_input("截止日期",
                                     value=fmt_date(p["deadline"]) or dt.date.today())
        c3.write(f"**客户/来源：** {p.get('source') or '—'}")
        save = st.form_submit_button("💾 保存修改")
    if save:
        sb.table("projects").update(
            {"stage": new_stage, "deadline": str(new_deadline)}
        ).eq("id", p["id"]).execute()
        st.success("已保存")
        st.rerun()

    if st.button("🗑️ 删除此项目（含 BOM、时间线、链接）", key=f"del_proj_{p['id']}"):
        sb.table("projects").delete().eq("id", p["id"]).execute()  # 数据库已设级联删除
        st.rerun()

    st.divider()

    # ----- BOM 清单 -----
    st.markdown("#### 🔩 BOM 物料清单")
    bom = (sb.table("bom_items").select("*")
           .eq("project_id", p["id"]).execute().data)
    bom_df = pd.DataFrame(bom) if bom else pd.DataFrame(
        columns=["part_name", "material", "qty", "supplier", "status"])
    if not bom_df.empty:
        bom_df = bom_df[["part_name", "material", "qty", "supplier", "status"]]

    edited_bom = st.data_editor(
        bom_df,
        num_rows="dynamic",          # 可直接在表格里增删行
        use_container_width=True,
        key=f"bom_editor_{p['id']}",
        column_config={
            "part_name": st.column_config.TextColumn("零件名", required=True),
            "material":  st.column_config.TextColumn("材质"),
            "qty":       st.column_config.NumberColumn("数量", min_value=0, step=1),
            "supplier":  st.column_config.TextColumn("供应商"),
            "status":    st.column_config.SelectboxColumn(
                             "状态", options=["待采购", "已采购"]),
        },
    )
    if st.button("💾 保存 BOM", key=f"save_bom_{p['id']}"):
        sb.table("bom_items").delete().eq("project_id", p["id"]).execute()
        rows = []
        for _, r in edited_bom.iterrows():
            if pd.notna(r.get("part_name")) and str(r["part_name"]).strip():
                rows.append({
                    "project_id": p["id"],
                    "part_name": str(r["part_name"]).strip(),
                    "material":  str(r.get("material") or ""),
                    "qty":       int(r.get("qty") or 0),
                    "supplier":  str(r.get("supplier") or ""),
                    "status":    r.get("status") or "待采购",
                })
        if rows:
            sb.table("bom_items").insert(rows).execute()
        st.success("BOM 已保存")
        st.rerun()

    st.divider()

    # ----- 进度甘特图 -----
    st.markdown("#### 📊 阶段进度甘特图")
    tl = (sb.table("timeline").select("*")
          .eq("project_id", p["id"])
          .order("start_date").execute().data)
    tl_df = pd.DataFrame(tl) if tl else pd.DataFrame(
        columns=["phase_name", "start_date", "end_date"])
    if not tl_df.empty:
        # 甘特图需要 datetime 类型；DateColumn 在编辑器里只显示日期部分
        tl_df["start_date"] = pd.to_datetime(tl_df["start_date"])
        tl_df["end_date"] = pd.to_datetime(tl_df["end_date"])
        tl_df = tl_df[["phase_name", "start_date", "end_date"]]

    edited_tl = st.data_editor(
        tl_df,
        num_rows="dynamic",
        use_container_width=True,
        key=f"tl_editor_{p['id']}",
        column_config={
            "phase_name": st.column_config.TextColumn("阶段名称", required=True),
            "start_date": st.column_config.DateColumn("开始日期"),
            "end_date":   st.column_config.DateColumn("结束日期"),
        },
    )
    if st.button("💾 保存时间线", key=f"save_tl_{p['id']}"):
        sb.table("timeline").delete().eq("project_id", p["id"]).execute()
        rows = []
        for _, r in edited_tl.iterrows():
            if pd.notna(r.get("phase_name")) and str(r["phase_name"]).strip():
                sd, ed = r.get("start_date"), r.get("end_date")
                rows.append({
                    "project_id": p["id"],
                    "phase_name": str(r["phase_name"]).strip(),
                    # 空日期存 NULL；有日期只取 YYYY-MM-DD 部分
                    "start_date": None if pd.isna(sd) else str(sd)[:10],
                    "end_date":   None if pd.isna(ed) else str(ed)[:10],
                })
        if rows:
            sb.table("timeline").insert(rows).execute()
        st.success("时间线已保存")
        st.rerun()

    if not edited_tl.empty:
        gantt = edited_tl.dropna(subset=["start_date", "end_date"]).copy()
        if not gantt.empty:
            fig = px.timeline(
                gantt, x_start="start_date", x_end="end_date",
                y="phase_name", color="phase_name",
                color_discrete_sequence=["#C4743B", "#D9985F", "#8A7360", "#B5836B"],
            )
            fig.update_yaxes(autorange="reversed", title="")
            fig.update_xaxes(title="")
            fig.update_layout(showlegend=False, height=320,
                              plot_bgcolor="rgba(0,0,0,0)",
                              paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ----- 文件链接（多条：标题 + 链接） -----
    st.markdown("#### 🔗 文件链接（百度网盘 / CAD 图纸）")
    links = (sb.table("project_links").select("*")
             .eq("project_id", p["id"])
             .order("created_at").execute().data)
    for lk in links:
        c1, c2 = st.columns([5, 1])
        c1.markdown(f"🔗 [{lk['title']}]({lk['url']})")
        if c2.button("删除", key=f"del_link_{lk['id']}"):
            sb.table("project_links").delete().eq("id", lk["id"]).execute()
            st.rerun()

    with st.form(f"new_link_{p['id']}"):
        c1, c2 = st.columns(2)
        lt = c1.text_input("链接标题（如：装配图v3）")
        lu = c2.text_input("链接地址（https://...）")
        ok = st.form_submit_button("添加链接")
    if ok:
        if lt.strip() and lu.strip():
            sb.table("project_links").insert(
                {"project_id": p["id"], "title": lt.strip(), "url": lu.strip()}
            ).execute()
            st.rerun()
        else:
            st.warning("标题和链接都要填写")

# ============================================================
# 模块二：实验管理（树形文件夹，无限层级）
# ============================================================
EXP_STATUS = ["计划中", "进行中", "已完成"]

def page_experiments():
    st.header("🧪 实验管理")

    if "exp_folder" not in st.session_state:
        st.session_state.exp_folder = None   # 当前所在文件夹 id，None = 根目录

    cur = st.session_state.exp_folder

    # ---------- 面包屑导航 ----------
    crumbs = []
    fid = cur
    guard = 0
    while fid and guard < 50:                       # 逐级向上找父文件夹
        rows = sb.table("experiment_folders").select("*").eq("id", fid).execute().data
        if not rows:
            break
        crumbs.append(rows[0])
        fid = rows[0]["parent_id"]
        guard += 1
    crumbs.reverse()

    nav = st.columns([1] + [2] * (len(crumbs) + 1))
    if nav[0].button("🏠 根目录"):
        st.session_state.exp_folder = None
        st.rerun()
    for i, c in enumerate(crumbs):
        if nav[i + 1].button(f"📂 {c['name']}", key=f"crumb_{c['id']}"):
            st.session_state.exp_folder = c["id"]
            st.rerun()
    st.caption("当前位置：" + " / ".join(["根目录"] + [c["name"] for c in crumbs]))

    # ---------- 新建文件夹 ----------
    with st.expander("📁 在此位置新建文件夹"):
        with st.form("new_folder"):
            fname = st.text_input("文件夹名称（如：力学性能测试）")
            ok = st.form_submit_button("创建")
        if ok and fname.strip():
            sb.table("experiment_folders").insert({
                "user_id": uid(), "parent_id": cur, "name": fname.strip()
            }).execute()
            st.rerun()

    st.divider()

    # ---------- 当前层的子文件夹 ----------
    q = sb.table("experiment_folders").select("*").eq("user_id", uid())
    q = q.is_("parent_id", "null") if cur is None else q.eq("parent_id", cur)
    subfolders = q.order("created_at").execute().data

    if subfolders:
        st.markdown("**📂 子文件夹**")
        cols = st.columns(4)
        for i, f in enumerate(subfolders):
            with cols[i % 4]:
                if st.button(f"📁 {f['name']}", key=f"open_{f['id']}",
                             use_container_width=True):
                    st.session_state.exp_folder = f["id"]
                    st.rerun()
                if st.button("🗑️", key=f"del_folder_{f['id']}",
                             help="删除该文件夹（其中实验会移到上层）"):
                    # 把该文件夹里的实验和子文件夹移到当前层，再删除文件夹本身
                    sb.table("experiments").update({"folder_id": cur}).eq("folder_id", f["id"]).execute()
                    sb.table("experiment_folders").update({"parent_id": cur}).eq("parent_id", f["id"]).execute()
                    sb.table("experiment_folders").delete().eq("id", f["id"]).execute()
                    st.rerun()

    st.divider()

    # ---------- 当前层的实验记录 ----------
    st.markdown("**🔬 实验记录**")
    projects = fetch_projects()
    proj_map = {p["id"]: p["name"] for p in projects}

    eq = sb.table("experiments").select("*").eq("user_id", uid())
    eq = eq.is_("folder_id", "null") if cur is None else eq.eq("folder_id", cur)
    exps = eq.order("exp_date", desc=True).execute().data

    for e in exps:
        star = {"计划中": "🗓️", "进行中": "🔧", "已完成": "✅"}.get(e["status"], "🔬")
        with st.expander(f"{star} {e['name']} ｜ {e.get('exp_date') or '未定日期'} ｜ {e['status']}"):
            c1, c2 = st.columns(2)
            c1.write(f"**所属项目：** {proj_map.get(e.get('project_id'), '不关联')}")
            c1.write(f"**设备/仪器：** {e.get('equipment') or '—'}")
            c1.write(f"**样品编号：** {e.get('sample_no') or '—'}")
            c2.write(f"**实验日期：** {e.get('exp_date') or '—'}")
            if e.get("data_link"):
                c2.markdown(f"**原始数据：** [打开链接]({e['data_link']})")
            if e.get("conclusion"):
                st.info(f"**结果与结论：** {e['conclusion']}")
            if e.get("image_url"):
                st.image(e["image_url"], caption="实验附件", width=400)
            if st.button("🗑️ 删除此实验", key=f"del_exp_{e['id']}"):
                sb.table("experiments").delete().eq("id", e["id"]).execute()
                st.rerun()

    # ---------- 新建实验 ----------
    with st.expander("➕ 在此位置新建实验记录"):
        with st.form("new_exp", clear_on_submit=True):
            name = st.text_input("实验名称 *")
            proj_opts = ["（不关联）"] + [p["name"] for p in projects]
            proj_sel = st.selectbox("所属项目", proj_opts)
            c1, c2 = st.columns(2)
            equipment = c1.text_input("实验设备/仪器（如：万能试验机、SEM）")
            sample_no = c2.text_input("样品/试件编号")
            c3, c4 = st.columns(2)
            exp_date = c3.date_input("实验日期", value=dt.date.today())
            status = c4.selectbox("实验状态", EXP_STATUS)
            data_link = st.text_input("原始数据链接（百度网盘/共享文件夹）")
            conclusion = st.text_area("实验结果与结论")
            img = st.file_uploader("实验附件图片（可选）",
                                   type=["png", "jpg", "jpeg", "webp"])
            ok = st.form_submit_button("保存实验")
        if ok:
            if not name.strip():
                st.warning("实验名称不能为空")
            else:
                img_url = upload_image(img, "experiments")
                pid = None
                if proj_sel != "（不关联）":
                    pid = next(p["id"] for p in projects if p["name"] == proj_sel)
                sb.table("experiments").insert({
                    "user_id": uid(), "folder_id": cur, "project_id": pid,
                    "name": name.strip(), "equipment": equipment.strip(),
                    "sample_no": sample_no.strip(), "exp_date": str(exp_date),
                    "status": status, "data_link": data_link.strip(),
                    "conclusion": conclusion.strip(), "image_url": img_url,
                }).execute()
                st.success("实验已保存！")
                st.rerun()

# ============================================================
# 模块三：论文管理
# ============================================================
READ_STATUS = ["未读", "在读", "已读"]

def page_papers():
    st.header("📚 论文管理")

    # ---------- 添加论文 ----------
    with st.expander("➕ 添加论文", expanded=False):
        with st.form("new_paper", clear_on_submit=True):
            title = st.text_input("论文标题 *")
            c1, c2 = st.columns(2)
            first_author = c1.text_input("第一作者")
            corresp_author = c2.text_input("通讯作者")
            c3, c4 = st.columns(2)
            journal = c3.text_input("期刊/会议名称")
            year = c4.number_input("发表年份", min_value=1900, max_value=2100,
                                   value=dt.date.today().year)
            doi = st.text_input("DOI 或链接（知网/网盘 PDF 链接等）")
            c5, c6 = st.columns(2)
            read_status = c5.selectbox("阅读状态", READ_STATUS)
            starred = c6.checkbox("⭐ 标记为重要文章")
            tags = st.text_input("关键词/标签（用逗号分隔，如：有限元, 摩擦学）")
            notes = st.text_area("读书笔记/备注")
            img = st.file_uploader("关键图片（可选，上传一张）",
                                   type=["png", "jpg", "jpeg", "webp"])
            ok = st.form_submit_button("保存论文")
        if ok:
            if not title.strip():
                st.warning("论文标题不能为空")
            else:
                img_url = upload_image(img, "papers")
                sb.table("papers").insert({
                    "user_id": uid(), "title": title.strip(),
                    "first_author": first_author.strip(),
                    "corresp_author": corresp_author.strip(),
                    "journal": journal.strip(), "year": int(year),
                    "doi_link": doi.strip(), "read_status": read_status,
                    "starred": starred, "tags": tags.strip(),
                    "notes": notes.strip(), "image_url": img_url,
                }).execute()
                st.success("论文已保存！")
                st.rerun()

    papers = (sb.table("papers").select("*")
              .eq("user_id", uid())
              .order("created_at", desc=True).execute().data)
    if not papers:
        st.info("还没有论文记录，点击上方「添加论文」开始吧！")
        return

    # ---------- 筛选与搜索 ----------
    st.markdown("#### 🔍 筛选 / 搜索")
    f1, f2, f3, f4 = st.columns(4)
    kw = f1.text_input("搜索（标题/作者/期刊）")
    rs = f2.selectbox("阅读状态", ["全部"] + READ_STATUS)
    only_star = f3.checkbox("只看星标 ⭐")
    year_sort = f4.selectbox("排序", ["最新添加", "年份从新到旧", "年份从旧到新"])

    # 收集所有标签供筛选
    all_tags = sorted({t.strip() for p in papers for t in (p.get("tags") or "").split(",") if t.strip()})
    tag_filter = st.multiselect("按标签筛选（命中任一即显示）", all_tags)

    # 依次应用筛选条件
    shown = papers
    if kw.strip():
        k = kw.strip().lower()
        shown = [p for p in shown if k in (p.get("title") or "").lower()
                 or k in (p.get("first_author") or "").lower()
                 or k in (p.get("corresp_author") or "").lower()
                 or k in (p.get("journal") or "").lower()]
    if rs != "全部":
        shown = [p for p in shown if p["read_status"] == rs]
    if only_star:
        shown = [p for p in shown if p.get("starred")]
    if tag_filter:
        shown = [p for p in shown
                 if any(t in (p.get("tags") or "") for t in tag_filter)]
    if year_sort == "年份从新到旧":
        shown = sorted(shown, key=lambda p: p.get("year") or 0, reverse=True)
    elif year_sort == "年份从旧到新":
        shown = sorted(shown, key=lambda p: p.get("year") or 0)

    st.caption(f"共 {len(shown)} 篇")
    st.divider()

    # ---------- 论文列表 ----------
    for p in shown:
        star = "⭐" if p.get("starred") else "📄"
        head = f"{star} {p['title']}（{p.get('year') or '—'}）— {p.get('journal') or '—'}"
        with st.expander(head):
            c1, c2 = st.columns(2)
            c1.write(f"**第一作者：** {p.get('first_author') or '—'}")
            c1.write(f"**通讯作者：** {p.get('corresp_author') or '—'}")
            c2.write(f"**期刊/会议：** {p.get('journal') or '—'}")
            c2.write(f"**阅读状态：** {p['read_status']}")
            if p.get("doi_link"):
                st.markdown(f"**DOI/链接：** [打开]({p['doi_link']})")
            if p.get("tags"):
                st.write(f"**标签：** {p['tags']}")
            if p.get("notes"):
                st.info(f"**读书笔记：** {p['notes']}")
            if p.get("image_url"):
                st.image(p["image_url"], caption="关键图片", width=450)

            # 快捷操作：标星 / 阅读状态 / 删除
            b1, b2, b3 = st.columns(3)
            if b1.button("取消星标" if p.get("starred") else "⭐ 标星",
                         key=f"star_{p['id']}"):
                sb.table("papers").update(
                    {"starred": not p.get("starred")}).eq("id", p["id"]).execute()
                st.rerun()
            nxt = {"未读": "在读", "在读": "已读", "已读": "未读"}[p["read_status"]]
            if b2.button(f"标记为「{nxt}」", key=f"rs_{p['id']}"):
                sb.table("papers").update(
                    {"read_status": nxt}).eq("id", p["id"]).execute()
                st.rerun()
            if b3.button("🗑️ 删除", key=f"del_paper_{p['id']}"):
                sb.table("papers").delete().eq("id", p["id"]).execute()
                st.rerun()

# ============================================================
# 主程序入口
# ============================================================
def main():
    # 未登录 → 显示登录/注册页
    if st.session_state.user is None:
        auth_page()
        return

    restore_session()  # 恢复 Supabase 会话，保证 RLS 生效

    # ----- 左侧边栏：模块导航 + 主题切换 + 退出登录 -----
    with st.sidebar:
        st.title("⏱️ 嘀嘀嗒嘀嗒")
        st.caption(f"👤 {st.session_state.user.email}")
        st.divider()
        page = st.radio("功能模块",
                        ["📁 项目管理", "🧪 实验管理", "📚 论文管理"],
                        label_visibility="collapsed")
        st.divider()
        dark = st.toggle("🌙 深色模式", value=(st.session_state.theme == "dark"))
        new_theme = "dark" if dark else "light"
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()
        st.divider()
        if st.button("🚪 退出登录", use_container_width=True):
            try:
                sb.auth.sign_out()
            except Exception:
                pass
            st.session_state.clear()
            st.rerun()

    # ----- 按导航显示对应模块 -----
    if page == "📁 项目管理":
        page_projects()
    elif page == "🧪 实验管理":
        page_experiments()
    else:
        page_papers()

main()
