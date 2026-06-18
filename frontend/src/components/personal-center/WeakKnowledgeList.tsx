type WeakPointItem = {
  knowledge_id?: number | string | null;
  name?: string | null;
  subject?: string | null;
  mastery_percent?: number | string | null;
};

interface WeakKnowledgeListProps {
  weakPoints: WeakPointItem[];
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

export default function WeakKnowledgeList({
  weakPoints,
}: WeakKnowledgeListProps) {
  const items = weakPoints.slice(0, 5);

  return (
    <section className="weak-knowledge-card">
      <div className="weak-knowledge-card__header">
        <div>
          <h2>薄弱知识点 TOP5</h2>
          <p>优先处理掌握度较低的知识点</p>
        </div>
        <span>Weakness</span>
      </div>

      <div className="weak-knowledge-card__list">
        {items.map((item, index) => {
          const percent = toPercent(item.mastery_percent);

          return (
            <article
              className="weak-knowledge-card__row"
              key={item.knowledge_id ?? `${item.name ?? "unknown"}-${index}`}
            >
              <span className="weak-knowledge-card__index">
                {index + 1}
              </span>

              <div className="weak-knowledge-card__main">
                <strong>{item.name || "未命名知识点"}</strong>
                <em>{item.subject || "未分类"}</em>
              </div>

              <div className="weak-knowledge-card__progress">
                <span>
                  <i style={{ width: `${percent}%` }} />
                </span>
                <b>{percent}%</b>
              </div>
            </article>
          );
        })}

        {!items.length && (
          <p className="weak-knowledge-card__empty">
            暂无薄弱知识点
          </p>
        )}
      </div>
    </section>
  );
}