/* C 扩展：对每个 i 计算 sqrt(i) + i*i，写入输出数组
 * 对应原 PythonSpeedTest 项目里的 ctypes DLL 方案 */
#include <math.h>
#include <stddef.h>

void calc_c(const int *input, double *output, int n)
{
    for (int k = 0; k < n; k++) {
        double v = (double)input[k];
        output[k] = sqrt(v) + v * v;
    }
}
