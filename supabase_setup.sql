-- ============================================================
--  “嘀嘀嗒嘀嗒”项目管理系统 —— 数据库初始化脚本
--  使用方法：打开 Supabase 后台 → 左侧 SQL Editor → New query
--           → 把本文件【全部内容】粘贴进去 → 点 Run 运行一次即可
-- ============================================================

-- ------------------------------------------------------------
-- 1. 项目表
-- ------------------------------------------------------------
create table if not exists projects (
    id          uuid primary key default gen_random_uuid(),
    user_id     uuid not null references auth.users(id) on delete cascade,
    name        text not null,
    source      text default '',
    deadline    date,
    stage       text default '方案设计',
    created_at  timestamptz default now()
);

-- ------------------------------------------------------------
-- 2. BOM 物料清单表
-- ------------------------------------------------------------
create table if not exists bom_items (
    id          uuid primary key default gen_random_uuid(),
    project_id  uuid not null references projects(id) on delete cascade,
    part_name   text not null,
    material    text default '',
    qty         integer default 0,
    supplier    text default '',
    status      text default '待采购'
);

-- ------------------------------------------------------------
-- 3. 项目阶段时间线表（甘特图数据）
-- ------------------------------------------------------------
create table if not exists timeline (
    id          uuid primary key default gen_random_uuid(),
    project_id  uuid not null references projects(id) on delete cascade,
    phase_name  text not null,
    start_date  date,
    end_date    date
);

-- ------------------------------------------------------------
-- 4. 项目文件链接表（百度网盘 / CAD 图纸链接，多条记录）
-- ------------------------------------------------------------
create table if not exists project_links (
    id          uuid primary key default gen_random_uuid(),
    project_id  uuid not null references projects(id) on delete cascade,
    title       text not null,
    url         text not null,
    created_at  timestamptz default now()
);

-- ------------------------------------------------------------
-- 5. 实验分类文件夹表（parent_id 指向自己这张表，实现无限层级嵌套）
-- ------------------------------------------------------------
create table if not exists experiment_folders (
    id          uuid primary key default gen_random_uuid(),
    user_id     uuid not null references auth.users(id) on delete cascade,
    parent_id   uuid references experiment_folders(id) on delete set null,
    name        text not null,
    created_at  timestamptz default now()
);

-- ------------------------------------------------------------
-- 6. 实验记录表
-- ------------------------------------------------------------
create table if not exists experiments (
    id          uuid primary key default gen_random_uuid(),
    user_id     uuid not null references auth.users(id) on delete cascade,
    folder_id   uuid references experiment_folders(id) on delete set null,
    project_id  uuid references projects(id) on delete set null,
    name        text not null,
    equipment   text default '',
    sample_no   text default '',
    exp_date    date,
    status      text default '计划中',
    data_link   text default '',
    conclusion  text default '',
    image_url   text,
    created_at  timestamptz default now()
);

-- ------------------------------------------------------------
-- 7. 论文表
-- ------------------------------------------------------------
create table if not exists papers (
    id              uuid primary key default gen_random_uuid(),
    user_id         uuid not null references auth.users(id) on delete cascade,
    title           text not null,
    first_author    text default '',
    corresp_author  text default '',
    journal         text default '',
    year            integer,
    doi_link        text default '',
    read_status     text default '未读',
    starred         boolean default false,
    tags            text default '',
    notes           text default '',
    image_url       text,
    created_at      timestamptz default now()
);

-- ============================================================
-- 8. 行级安全（RLS）：开启后，每个人只能读写自己的数据
--    这一步非常重要，不开启的话任何人拿到网址都可能看到你的数据！
-- ============================================================
alter table projects           enable row level security;
alter table bom_items          enable row level security;
alter table timeline           enable row level security;
alter table project_links      enable row level security;
alter table experiment_folders enable row level security;
alter table experiments        enable row level security;
alter table papers             enable row level security;

-- 直接挂 user_id 的表：本人可增删改查
create policy "own_projects"  on projects
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own_folders"   on experiment_folders
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own_experiments" on experiments
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own_papers"    on papers
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- 挂在项目下的三张表：通过项目归属判断“是不是我的数据”
create policy "own_bom" on bom_items
    for all using (exists (select 1 from projects p
                           where p.id = project_id and p.user_id = auth.uid()))
    with check (exists (select 1 from projects p
                        where p.id = project_id and p.user_id = auth.uid()));
create policy "own_timeline" on timeline
    for all using (exists (select 1 from projects p
                           where p.id = project_id and p.user_id = auth.uid()))
    with check (exists (select 1 from projects p
                        where p.id = project_id and p.user_id = auth.uid()));
create policy "own_links" on project_links
    for all using (exists (select 1 from projects p
                           where p.id = project_id and p.user_id = auth.uid()))
    with check (exists (select 1 from projects p
                        where p.id = project_id and p.user_id = auth.uid()));

-- ============================================================
-- 9. 图片存储桶（存放论文关键图片、实验附件图片）
--    public = true 表示图片可通过链接直接访问（方便网页展示）
--    但【只有登录的你】才能上传/删除
-- ============================================================
insert into storage.buckets (id, name, public)
values ('images', 'images', true)
on conflict (id) do nothing;

-- 任何人可读（因为桶是公开的）；只有登录用户能上传/更新/删除，且只能操作自己文件夹下的
create policy "images_public_read" on storage.objects
    for select using (bucket_id = 'images');
create policy "images_auth_insert" on storage.objects
    for insert to authenticated
    with check (bucket_id = 'images' and (storage.foldername(name))[1] = auth.uid()::text);
create policy "images_auth_update" on storage.objects
    for update to authenticated
    using (bucket_id = 'images' and (storage.foldername(name))[1] = auth.uid()::text);
create policy "images_auth_delete" on storage.objects
    for delete to authenticated
    using (bucket_id = 'images' and (storage.foldername(name))[1] = auth.uid()::text);

-- ============================================================
--  执行完毕后，请回到 README.md 继续下一步
-- ============================================================
