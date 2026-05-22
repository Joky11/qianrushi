/* OpenMP 并行版本 C 扩展
 * 对应原 PythonSpeedTest 项目里的 ctypes DLL VC OpenMP 方案 */
#include <math.h>
#include <omp.h>

void calc_omp(const int *input, double *output, int n)
{
    #pragma omp parallel for schedule(static)
    for (int k = 0; k < n; k++) {
        double v = (double)input[k];
        output[k] = sqrt(v) + v * v;
    }
}
