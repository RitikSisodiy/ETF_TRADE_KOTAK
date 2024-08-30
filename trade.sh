#!/bin/bash

#turmux install cmake ninja patchelf
current_time=$(date "+%Y%m%d_%H%M%S")
echo $current_time
cd "$(dirname "$0")"
echo "$(dirname "$0")"
python buy_etf_v4.py >> logs/ETF_daily_$current_time.log 2>&1