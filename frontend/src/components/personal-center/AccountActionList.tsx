interface AccountActionListProps {
  isStudent?: boolean;
  onEditProfile: () => void;
  onChangePassword: () => void;
  onEditStudent?: () => void;
}

type AccountActionItem = {
  key: string;
  title: string;
  description: string;
  actionText: string;
  visible: boolean;
  onClick?: () => void;
};

export default function AccountActionList({
  isStudent = false,
  onEditProfile,
  onChangePassword,
  onEditStudent,
}: AccountActionListProps) {
  const actions: AccountActionItem[] = [
    {
      key: "edit-profile",
      title: "修改个人资料",
      description: "修改用户名、邮箱等基础信息",
      actionText: "去修改 →",
      visible: true,
      onClick: onEditProfile,
    },
    {
      key: "change-password",
      title: "修改密码",
      description: "修改当前账号的登录密码",
      actionText: "去修改 →",
      visible: true,
      onClick: onChangePassword,
    },
    {
      key: "edit-student",
      title: "学生资料",
      description: "维护学号、专业、年级、班级等信息",
      actionText: "去编辑 →",
      visible: isStudent,
      onClick: onEditStudent,
    },
  ];

  return (
    <section className="personal-action-list" aria-label="账号操作">
      <div className="personal-action-list__header">
        <h2>账号操作</h2>
        <span>Account</span>
      </div>

      <div className="personal-action-list__body">
        {actions
          .filter((item) => item.visible)
          .map((item) => (
            <button
              key={item.key}
              type="button"
              className="personal-action-list__item"
              onClick={item.onClick}
              disabled={!item.onClick}
            >
              <span className="personal-action-list__text">
                <strong>{item.title}</strong>
                <em>{item.description}</em>
              </span>

              <span className="personal-action-list__link">
                {item.actionText}
              </span>
            </button>
          ))}
      </div>
    </section>
  );
}