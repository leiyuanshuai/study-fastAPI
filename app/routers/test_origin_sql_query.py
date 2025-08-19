from fastapi import FastAPI
from sqlalchemy.sql.expression import text

from app.utils.db_utils import AsyncSessionDep

from fastapi import APIRouter, FastAPI


def add_origin_sql_query_route(app: FastAPI, prefix: str = "/test_origin_sql_query"):
  router = APIRouter(prefix=prefix, tags=["测试原生SQL查询模块"])
  @router.get("/list", )
  async def get_summary_list(session: AsyncSessionDep):
    #
    # result = await session.exec(text("select * from llm_user where username = :username"), {"username": username})
    # 第二种查询方式
    # statement = select(Hero)
    # results = session.exec(statement)
    # heroes = results.all()
    # print(heroes)
    rows = await session.exec(text("""
    SELECT
        s.*,
        bs.target_price,
        bs.target_heavy_price,
        bs.is_state_owned,
        bs.profit_strategy,
        bs.finance_data,
        bs.is_blacklisted,
        bs.sell_price,
        bs.level,
        IFNULL(bs.is_analyzed, 0) as is_analyzed,
        IFNULL(bs.is_favorite, 0) as is_favorite,
        bc.adj_logs,
        bc.update_time,
        bc.cash_flow_data,
        bc.lt_bps
      FROM summary s
      LEFT JOIN bond_strategies bs ON s.bond_id = bs.bond_id
      LEFT JOIN bond_cells bc ON s.bond_id = bc.bond_id
      LIMIT 1000
    """))
    res = []
    for item in rows:
      row = dict(item._mapping)

      res.append(dict(row._mapping))
    return res

  app.include_router(router)

