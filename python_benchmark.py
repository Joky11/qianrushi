# -*- coding: utf-8 -*-
"""
Python 版本基准测试程序
功能：循环 100000 次计算 sqrt(i) + pow(i, 2)，并测量总耗时
对应作业要求 1.1：Python 实现
"""

import datetime
import math


def calculate():
    """执行 10 万次 sqrt + pow 运算"""
    # 记录计算开始前的时间戳
    before_cal = datetime.datetime.now()

    # 循环 100000 次，计算 sqrt(number) + pow(number, 2)
    for number in range(100000):
        result = math.sqrt(number) + math.pow(number, 2)

    # 记录计算结束后的时间戳
    after_cal = datetime.datetime.now()

    # 计算耗时（timedelta 对象）
    cal_cost = after_cal - before_cal
    return cal_cost


def main():
    # 为减小单次测量的偶然误差，运行多次取平均值
    runs = 10
    total_microseconds = 0
    print("=== Python 基准测试（100000 次 sqrt + pow 运算）===")
    for i in range(runs):
        cost = calculate()
        # 将 timedelta 统一转换为微秒进行累加
        microseconds = cost.total_seconds() * 1_000_000
        total_microseconds += microseconds
        print(f"第 {i + 1:>2} 次运行耗时：{cost}  （约 {microseconds:.0f} 微秒）")

    avg_ms = (total_microseconds / runs) / 1000.0
    print(f"\n平均耗时：{avg_ms:.3f} 毫秒 / {total_microseconds / runs:.0f} 微秒")


if __name__ == "__main__":
    main()
