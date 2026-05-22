// C# 版本基准测试程序
// 功能：循环 100000 次计算 Sqrt(i) + Pow(i, 2)，并测量总耗时
// 对应作业要求 1.1：C# 实现

using System;
using System.Diagnostics;

namespace CSharpBenchmark
{
    class Program
    {
        /// <summary>
        /// 执行 10 万次 sqrt + pow 运算（与题目给出的代码片段完全对应）
        /// </summary>
        public static void CalCulate()
        {
            // 获取 for(int 100000) 计算
            for (int i = 0; i < 100000; i++)
            {
                double result = Math.Sqrt(i) + Math.Pow(i, 2);
            }
        }

        static void Main(string[] args)
        {
            const int runs = 10;                 // 运行次数，用于取平均值
            double totalMicroseconds = 0;        // 总耗时（微秒）

            Console.WriteLine("=== C# 基准测试（100000 次 Sqrt + Pow 运算）===");

            for (int r = 0; r < runs; r++)
            {
                // Stopwatch 是 .NET 中用于高精度计时的类
                Stopwatch sw = Stopwatch.StartNew();
                CalCulate();
                sw.Stop();

                // Elapsed 是 TimeSpan 类型，与 Python 的 timedelta 对应
                double microseconds = sw.Elapsed.TotalMilliseconds * 1000.0;
                totalMicroseconds += microseconds;

                Console.WriteLine(
                    $"第 {r + 1,2} 次运行耗时：{sw.Elapsed}  （约 {microseconds:F0} 微秒）");
            }

            double avgUs = totalMicroseconds / runs;
            Console.WriteLine();
            Console.WriteLine($"平均耗时：{avgUs / 1000.0:F3} 毫秒 / {avgUs:F0} 微秒");
        }
    }
}
