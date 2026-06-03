import asyncio
import pandas as pd

from app.db.database import AsyncSessionLocal
from app.db.models.question import Question


CSV_PATH = "/Users/admin/Desktop/26大二下春季课程资料/26何婧数据库概论/题库资源/《马克思主义基本原理》单选题_副本.csv"


async def main():
    df = pd.read_csv(CSV_PATH)

    # 去掉空表头列
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    async with AsyncSessionLocal() as db:
        for _, row in df.iterrows():
            q = Question(
                knowledge_id=int(row["zsd"]),
                question_type=row["题目类型"],
                stem=row["题干"],
                option_a=row["A"],
                option_b=row["B"],
                option_c=row["C"],
                option_d=row["D"],
                answer=row["答案"],
                difficulty=int(row["难度"]),
            )
            db.add(q)

        await db.commit()


asyncio.run(main())