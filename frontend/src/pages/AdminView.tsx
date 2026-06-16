import { useEffect, useState } from "react";
import { Plus, RefreshCw } from "lucide-react";
import { useAdminStore } from "../stores";
import "../styles/pages/CourseManagementView.css";

/** 后台管理页：统计、角色、菜单、权限的基础管理入口。 */
export default function AdminView() {
  const { stats, roles, menus, permissions, loading, error, loadStats, loadRoles, loadMenus, loadPermissions, createRole, createMenu, createPermission } = useAdminStore();
  const [roleName, setRoleName] = useState("");
  const [menuName, setMenuName] = useState("");
  const [permissionName, setPermissionName] = useState("");
  const [permissionCode, setPermissionCode] = useState("");

  const refresh = async () => { await Promise.all([loadStats(), loadRoles(), loadMenus(), loadPermissions()]); };
  useEffect(() => { void refresh(); }, []);

  return (
    <div className="course-management-view">
      <header className="course-header">
        <div><h1>后台管理</h1><p>管理系统角色、菜单、权限和数据统计。</p></div>
        <div className="course-header-actions"><button className="course-btn ghost" type="button" onClick={() => void refresh()}><RefreshCw size={16} />刷新</button></div>
      </header>
      {loading && <p className="course-empty">加载中…</p>}
      {error && <p className="course-empty">{error}</p>}

      <div className="course-stats">
        <div className="course-stat"><strong>{stats?.total_users ?? 0}</strong><span>用户数</span></div>
        <div className="course-stat"><strong>{stats?.course_count ?? 0}</strong><span>课程数</span></div>
      </div>

      <section className="course-card">
        <h2>角色管理</h2>
        <form className="course-form" onSubmit={async (e) => { e.preventDefault(); if (roleName.trim()) { await createRole(roleName.trim()); setRoleName(""); } }}>
          <label>角色名称<input value={roleName} onChange={(e) => setRoleName(e.target.value)} placeholder="admin / teacher / student" /></label>
          <button className="course-btn primary" type="submit"><Plus size={16} />新增角色</button>
        </form>
        <div className="course-list course-grid-list">{roles.map((item) => <article className="course-item course-mini-card" key={item.role_id}><div><h3>{item.role_name}</h3><p>角色 ID：{item.role_id}</p></div></article>)}</div>
      </section>

      <section className="course-card">
        <h2>菜单管理</h2>
        <form className="course-form" onSubmit={async (e) => { e.preventDefault(); if (menuName.trim()) { await createMenu({ menu_name: menuName.trim() }); setMenuName(""); } }}>
          <label>菜单名称<input value={menuName} onChange={(e) => setMenuName(e.target.value)} /></label>
          <button className="course-btn primary" type="submit"><Plus size={16} />新增菜单</button>
        </form>
        <div className="course-list course-grid-list">{menus.map((item) => <article className="course-item course-mini-card" key={item.menu_id}><div><h3>{item.menu_name}</h3><p>{item.description || "暂无描述"}</p></div></article>)}</div>
      </section>

      <section className="course-card">
        <h2>权限管理</h2>
        <form className="course-form" onSubmit={async (e) => { e.preventDefault(); if (permissionName.trim() && permissionCode.trim()) { await createPermission({ permission_name: permissionName.trim(), permission_code: permissionCode.trim() }); setPermissionName(""); setPermissionCode(""); } }}>
          <label>权限名称<input value={permissionName} onChange={(e) => setPermissionName(e.target.value)} /></label>
          <label>权限编码<input value={permissionCode} onChange={(e) => setPermissionCode(e.target.value)} placeholder="course:manage" /></label>
          <button className="course-btn primary" type="submit"><Plus size={16} />新增权限</button>
        </form>
        <div className="course-list course-grid-list">{permissions.map((item) => <article className="course-item course-mini-card" key={item.permission_id}><div><h3>{item.permission_name}</h3><p>{item.permission_code}</p><span>{item.description || "暂无描述"}</span></div></article>)}</div>
      </section>
    </div>
  );
}
