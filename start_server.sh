#!/bin/bash

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "检测到未在虚拟环境中运行"
    # 如果你有虚拟环境，可以取消下面的注释并修改路径
    conda activate py_3_11
    # source /path/to/your/venv/bin/activate
fi

# 检查是否提供了环境参数
ENV_FILE=".env"
if [ "$1" = "prod" ]; then
    ENV_FILE=".env.production"
    echo "使用生产环境配置: $ENV_FILE"
elif [ "$1" = "dev" ]; then
    ENV_FILE=".env"
    echo "使用开发环境配置: $ENV_FILE"
fi

# 检查环境文件是否存在
if [ ! -f "$ENV_FILE" ]; then
    echo "错误: 环境文件 $ENV_FILE 不存在"
    exit 1
fi

# 导出环境变量
export ENV_FILE=$ENV_FILE

# 启动 Gunicorn
echo "启动 Gunicorn 服务器..."
gunicorn -c gunicorn.conf.py app.main:app
