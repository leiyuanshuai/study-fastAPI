 for (const row of rows) {
      // 处理日期格式 maturity_dt到期时间
      if (row.maturity_dt) {
        row.maturity_dt = dayjs(row.maturity_dt).format('YYYY-MM-DD');
        // 过滤掉已到期的可转债 三板的 eb可交债
        if (row.maturity_dt < today || row.market_cd === 'sb' || row.btype === 'E') {
          continue;
        }
      }

      // 确保is_analyzed为数字类型，并设置默认值
      row.is_analyzed = row.is_analyzed ? 1 : 0;

      // 确保target_price和level有默认值
      row.target_price = row.target_price || null;
      row.level = row.level || '';

      // 处理下修记录
      if (row.adj_logs) {
        // 解析下修记录
        row.adj_records = parseAdjustData(row.adj_logs, row.bond_id);
      } else {
        row.adj_records = [];
      }

      // 处理现金流数据
      if (row.cash_flow_data) {
        const profitData = parseCashFlowData(row.cash_flow_data, row.bond_id);
        if (profitData) {
          //  net_profits 最近3年的净利润数组
          row.net_profits = profitData.profits;
          //  net_profits 最近3年的净利润总和
          row.total_profit = profitData.total;
          //  profit_bond_gap 剩余规模- 最近3年净利润总和的值 curr_iss_amt 剩余规模
          row.profit_bond_gap = Number((row.curr_iss_amt - profitData.total).toFixed(2));
        }
      }

      delete row.adj_logs;
      delete row.cash_flow_data;

      // 将有效的数据添加到结果数组
      validRows.push(row);
    }
