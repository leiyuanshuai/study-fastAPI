import datetime
from typing import List, Dict, Any

def parse_adjust_data(adj_logs, bond_id):
    # 这里实现你的下修记录解析逻辑
    return []

def parse_cash_flow_data(cash_flow_data, bond_id):
    # 这里实现你的现金流数据解析逻辑
    # 返回 {'profits': [...], 'total': float}
    return None

def process_rows(rows: List[Dict[str, Any]], today: str) -> List[Dict[str, Any]]:
    valid_rows = []
    today_date = datetime.datetime.strptime(today, '%Y-%m-%d').date()

    for row in rows:
        # 处理日期格式 maturity_dt到期时间
        if row.get('maturity_dt'):
            maturity_dt = datetime.datetime.strptime(row['maturity_dt'], '%Y-%m-%d').date()
            row['maturity_dt'] = maturity_dt.strftime('%Y-%m-%d')
            # 过滤掉已到期的可转债 三板的 eb可交债
            if maturity_dt < today_date or row.get('market_cd') == 'sb' or row.get('btype') == 'E':
                continue

        # 确保is_analyzed为数字类型，并设置默认值
        row['is_analyzed'] = 1 if row.get('is_analyzed') else 0

        # 确保target_price和level有默认值
        row['target_price'] = row.get('target_price', None)
        row['level'] = row.get('level', '')

        # 处理下修记录
        if row.get('adj_logs'):
            row['adj_records'] = parse_adjust_data(row['adj_logs'], row.get('bond_id'))
        else:
            row['adj_records'] = []

        # 处理现金流数据
        if row.get('cash_flow_data'):
            profit_data = parse_cash_flow_data(row['cash_flow_data'], row.get('bond_id'))
            if profit_data:
                row['net_profits'] = profit_data['profits']
                row['total_profit'] = profit_data['total']
                row['profit_bond_gap'] = round(float(row.get('curr_iss_amt', 0)) - profit_data['total'], 2)

        row.pop('adj_logs', None)
        row.pop('cash_flow_data', None)

        # 将有效的数据添加到结果数组
        valid_rows.append(row)

    return valid_rows
