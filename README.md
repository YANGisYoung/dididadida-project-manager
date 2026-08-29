# ⏱️ “嘀嘀嗒嘀嗒”项目管理系统 —— 保姆级使用说明书

> 这份说明书专为**完全没有编程和网页开发经验**的你而写。
> 请像跟着菜谱做菜一样，**从头到尾按顺序操作**，每一步都写得很细。
> 全程预计 40~60 分钟，只需要一台能上网的电脑。

---

## 📦 你将得到什么

一个属于你自己的网页系统，网址形如 `https://你的应用名.streamlit.app`：

- 📁 **项目管理**：项目看板、BOM 物料清单、阶段甘特图、图纸/网盘链接
- 🧪 **实验管理**：文件夹可以套文件夹（无限层级），实验记录带图片
- 📚 **论文管理**：阅读状态、星标、标签筛选、笔记、关键图片
- 🌙 深色/浅色主题一键切换，手机、平板、电脑浏览器都能访问
- 🔒 数据存在云端数据库，只有登录后的你自己能看到

**全程免费**（Supabase 和 Streamlit Cloud 的免费额度对个人完全够用）。

---

## 🗂️ 这个文件夹里的文件都是干什么的？

| 文件 | 作用 | 你需要动它吗 |
|---|---|---|
| `app.py` | 系统全部源代码 | ❌ 不用动 |
| `requirements.txt` | 告诉电脑需要安装哪些软件包 | ❌ 不用动 |
| `supabase_setup.sql` | 建数据库用的脚本，**只需复制粘贴运行一次** | ✅ 第 3 步要用 |
| `.env.example` | 密钥配置的模板 | ✅ 第 4 步要用 |
| `README.md` | 就是本说明书 | 📖 现在正读着 |

---

# 第一步：注册 Supabase（云端数据库）🐘

Supabase 就是你的数据仓库，你的项目、实验、论文数据都存在这里。

1. 打开浏览器，访问 👉 **https://supabase.com**
2. 点右上角 **Start your project**
3. 用 **GitHub 账号** 或 **邮箱** 注册（建议用邮箱，直接填邮箱+密码即可）
4. 登录后点 **New project**（新建项目），按下面填写：
   - **Name（项目名）**：随便起，比如 `didi-project`
   - **Database Password（数据库密码）**：点 **Generate a password** 自动生成，**然后把它复制下来存到记事本里**（以后基本用不到，但存一份保险）
   - **Region（地区）**：选 **Singapore**（新加坡，国内访问较快）
   - 套餐保持 **Free**（免费）
5. 点 **Create new project**，等待 1~2 分钟，项目就建好了（页面转圈是正常现象）。

---

# 第二步：创建数据库表 📊

项目建好后，我们要在数据库里建 7 张表和 1 个图片仓库。不用懂原理，复制粘贴即可：

1. 在 Supabase 后台**左侧菜单**找到 **SQL Editor**（图标像 `>_`），点进去
2. 点 **New query**（新建查询）
3. 用记事本打开本文件夹里的 **`supabase_setup.sql`**，**全选（Ctrl+A）→ 复制（Ctrl+C）**
4. 粘贴（Ctrl+V）到 Supabase 的 SQL 编辑框里
5. 点右下角绿色按钮 **Run**（或按 Ctrl+Enter）
6. 看到下方显示 **Success** ✅ 就大功告成

> 💡 **验证一下**：点左侧菜单 **Table Editor**（表格图标），应该能看到
> `projects`、`bom_items`、`timeline`、`project_links`、`experiment_folders`、`experiments`、`papers` 这 7 张表。

---

# 第三步：拿到你的两把"钥匙" 🔑

1. 在 Supabase 后台，点左下角 **⚙️ Project Settings**（齿轮图标）
2. 点 **API**（或左侧 Data API）
3. 你会看到两个重要信息：
   - **Project URL**：形如 `https://abcdefgh.supabase.co`
   - **anon public** 密钥：一长串以 `eyJ` 开头的字符（在 "API Keys" 区域，点 Reveal/复制按钮）
4. 把这两个值**复制到记事本里备用**，马上要用。

> ⚠️ 注意：页面上还有一个 `service_role` 密钥，**千万不要用它**，也不要泄露给任何人。我们只用 `anon public` 这个。

---

# 第四步：在你自己的电脑上运行 💻

## 4.1 安装 Python（系统的"发动机"）

1. 打开 👉 **https://www.python.org/downloads/**
2. 点黄色大按钮 **Download Python 3.x.x** 下载
3. 双击下载好的安装包，**⚠️ 最关键的一步：安装界面最下方有个 `Add python.exe to PATH` 的勾，一定要打上！** 然后点 **Install Now**
4. 安装完点 Close

> 💡 验证：按键盘 `Win + R`，输入 `cmd` 回车，在黑色窗口里输入 `python --version` 回车，
> 显示 `Python 3.1x.x` 就说明成功了。如果提示"不是内部或外部命令"，就是上一步的勾没打，重新安装一遍。

## 4.2 配置密钥文件

1. 在本文件夹里找到 **`.env.example`**，**复制一份**（Ctrl+C、Ctrl+V）
2. 把复制出来的那份**重命名为 `.env`**（注意：名字就是一个点加 env，没有别的字）
   > Windows 如果看不到文件名后缀：随便打开一个文件夹 → 上方"查看" → 勾选"文件扩展名"
3. 用记事本打开 `.env`，把第三步拿到的两把钥匙填进去，改成这样：

```
SUPABASE_URL=https://abcdefgh.supabase.co
SUPABASE_KEY=eyJhbGciOi......（你那一大串密钥）
```

4. 保存关闭。

## 4.3 安装依赖并启动

1. 在文件夹空白处 **按住 Shift 键 + 鼠标右键** → 选 **"在此处打开 PowerShell 窗口"** 或 **"在终端中打开"**
2. 在弹出的窗口里输入下面这行命令，回车（这是在安装系统需要的软件包，约 1~3 分钟）：

```
pip install -r requirements.txt
```

3. 装完后，输入下面这行命令，回车：

```
streamlit run app.py
```

4. 稍等几秒，浏览器会**自动打开** `http://localhost:8501`，你就能看到系统界面了！🎉

> 💡 以后每次想用，重复第 4.3 步的 1 和 3 即可（不用重装）。
> 想关闭系统：在黑色窗口里按 `Ctrl + C`。

---

# 第五步：注册你自己的账号并锁门 🔒

1. 在打开的网页里，点 **📝 注册** 标签，用你的邮箱注册一个账号
2. 注册成功后会自动登录进系统
3. **然后立刻去"锁门"**（防止别人也注册你的系统）：
   - 回到 Supabase 后台 → 左侧 **Authentication**（人像图标）→ **Sign In / Providers**
   - 找到 **Email** 那一项点进去
   - 把 **"Confirm email"（验证邮箱）** 关掉 → Save（这样注册不用收邮件）
   - 把 **"Allow new users to sign up"（允许新用户注册）** 关掉 → Save

> 这样，全世界只有你注册好的这一个账号能登录。即使别人拿到网址，没有你的密码也进不去。

---

# 第六步：部署到云端（手机/平板/其他电脑都能访问）☁️

本地运行只能在这台电脑上用。想随时随地任何设备访问，就把它免费部署到 Streamlit Cloud。

## 6.1 注册 GitHub（代码托管网站，相当于代码的网盘）

1. 打开 👉 **https://github.com** ，点 **Sign up** 注册（用邮箱即可，全免费）
2. 注册并登录后，点右上角头像旁的 **+** → **New repository**
3. **Repository name** 填：`didi-project-manager`（或任意英文名）
4. 选择 **Private**（私有，重要！）→ 点 **Create repository**

## 6.2 上传代码文件

1. 在刚创建的仓库页面，点 **uploading an existing file** 链接
2. 把本文件夹里的这 **4 个文件**拖进网页：
   - `app.py`
   - `requirements.txt`
   - `supabase_setup.sql`（可传可不传）
   - `README.md`（可传可不传）
3. **⚠️ 千万不要上传 `.env` 文件！**（密钥会泄露）
4. 点页面下方绿色 **Commit changes** 按钮

## 6.3 部署到 Streamlit Cloud

1. 打开 👉 **https://share.streamlit.io**
2. 点 **Sign in with GitHub**，授权登录
3. 点 **Create app**（或 New app）→ **Deploy a public app from GitHub**
4. 在 **Repository** 下拉框选你刚建的 `didi-project-manager`
5. **Main file path** 确认是 `app.py`
6. 点 **Advanced settings**（高级设置）⚠️ 关键一步：
   在 **Secrets** 大文本框里粘贴下面内容（换成你自己的两把钥匙）：

```toml
SUPABASE_URL = "https://abcdefgh.supabase.co"
SUPABASE_KEY = "eyJhbGciOi......你那一大串密钥"
```

7. 点 **Deploy!**，等 2~3 分钟
8. 部署完成后，你会得到一个网址，形如 `https://didi-project-manager-xxxx.streamlit.app`

## 6.4 完成！🎉

把这个网址收藏到浏览器书签里。以后**手机、平板、任何电脑**打开这个网址，用你的账号登录就能用，所有设备数据实时同步（因为数据都在 Supabase 云端）。

---

# 📖 日常使用小指南

| 你想做什么 | 怎么做 |
|---|---|
| 切换深色/浅色 | 左侧边栏底部的 **🌙 深色模式** 开关 |
| 新建项目 | 项目管理 → ➕ 新建项目（会自动生成甘特图时间线，可改） |
| 改 BOM / 时间线 | 在表格里直接改（可以增删行），改完点对应的 **💾 保存** 按钮 |
| 实验分类 | 实验管理 → 📁 新建文件夹，点文件夹进入，里面还能再建文件夹 |
| 给论文标星 | 论文管理 → 展开论文 → ⭐ 标星 |
| 找论文 | 用筛选区的搜索框 / 状态 / 星标 / 标签 / 年份排序 |
| 退出登录 | 左侧边栏底部 🚪 退出登录 |

---

# ❓ 常见问题（出问题先看这里）

**Q1：网页提示"没有找到 Supabase 密钥"？**
→ 本地运行：检查 `.env` 文件名是否正确（不是 `.env.txt`！）、内容是否填对。
→ 云端：检查第 6.3 步的 Secrets 是否粘贴正确（注意每行都有英文引号）。

**Q2：注册/登录失败，提示邮箱要验证？**
→ 回到第五步第 3 条，去 Supabase 把 "Confirm email" 关掉。

**Q3：图片上传失败或打不开？**
→ 检查第二步的 SQL 是否完整执行成功（Storage 部分在最后）。可重新完整运行一次 `supabase_setup.sql`（重复运行不会出错）。

**Q4：打开网页是空白/一直转圈？**
→ 云端部署的应用长时间没人访问会"休眠"，等 30 秒左右它会自己醒来，属正常现象。

**Q5：忘记密码怎么办？**
→ 去 Supabase 后台 → Authentication → Users，找到你的账号，可以重置或删除后重新注册（删除账号会同时删掉所有数据，慎用）。

**Q6：想改系统功能/界面？**
→ 把 `app.py` 发给 AI 助手（比如 Claude），说"帮我修改这个文件，我想要……"即可。改完后本地直接生效；云端需要重新上传 `app.py` 到 GitHub（在仓库页面点 Add file → Upload files，同名覆盖即可，会自动重新部署）。

---

祝你科研顺利，项目都能按时结项！⏱️
