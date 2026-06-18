type SubjectStatItem = {
  subject?: string | null;
  count?: number | string | null;
  avg_mastery?: number | string | null;
};

interface SubjectMasteryPanelProps {
  subjectStats: SubjectStatItem[];
}

const toSafeNumber = (value: number | string | null | undefined) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

const toPercent = (value: number | string | null | undefined) => {
  const raw = toSafeNumber(value);
  const percent = raw <= 1 ? raw * 100 : raw;

  return Math.max(0, Math.min(Math.round(percent), 100));
};

export default function SubjectMasteryPanel({
  subjectStats,
}: SubjectMasteryPanelProps) {
  return (
    <section className="subject-mastery-card">
      <div className="subject-mastery-card__header">
        <div>
          <h2>学科掌握度</h2>
          <p>按学科聚合知识点平均掌握情况</p>
        </div>
        <span>Subjects</span>
      </div>

      <div className="subject-mastery-card__list">
        {subjectStats.map((item, index) => {
          const percent = toPercent(item.avg_mastery);
          const subjectName = item.subject || "未分类";
          const count = Math.max(0, Math.round(toSafeNumber(item.count)));

          return (
            <article
              className="subject-mastery-card__row"
              key={`${subjectName}-${index}`}
            >
              <div className="subject-mastery-card__name">
                <strong>{subjectName}</strong>
                <em>{count} 个知识点</em>
              </div>

              <div className="subject-mastery-card__bar">
                <span>
                  <i style={{ width: `${percent}%` }} />
                </span>
              </div>

              <b>{percent}%</b>
            </article>
          );
        })}

        {!subjectStats.length && (
          <p className="subject-mastery-card__empty">
            暂无学科掌握度数据
          </p>
        )}
      </div>
    </section>
  );
}