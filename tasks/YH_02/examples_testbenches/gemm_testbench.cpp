#include <stdio.h>
        #include <stdlib.h>
        #include <math.h>

        #define M_SIZE 1024
        #define N_SIZE 1024
        #define K_SIZE 1024

        void gemm(float A[M_SIZE][K_SIZE], float B[K_SIZE][N_SIZE], float C[M_SIZE][N_SIZE]);

        int main() {
            float A[M_SIZE][K_SIZE];
            float B[K_SIZE][N_SIZE];
            float C[M_SIZE][N_SIZE];
            float C_ref[M_SIZE][N_SIZE];

            // Initialize input matrices
            for (int i = 0; i < M_SIZE; i++) {
                for (int j = 0; j < K_SIZE; j++) {
                    A[i][j] = (float)rand() / RAND_MAX;
                }
            }
            
            for (int i = 0; i < K_SIZE; i++) {
                for (int j = 0; j < N_SIZE; j++) {
                    B[i][j] = (i - j) % 7 * 0.25f;
                }
            }

            // Reference software GEMM
            for (int i = 0; i < M_SIZE; i++) {
                for (int j = 0; j < N_SIZE; j++) {
                    float sum = 0.0f;
                    for (int k = 0; k < K_SIZE; k++) {
                        sum += A[i][k] * B[k][j];
                    }
                    C_ref[i][j] = sum;
                }
            }

            // Call DUT (Device Under Test)
            gemm(A, B, C);

            // Verify the results
            int errors = 0;
            for (int i = 0; i < M_SIZE; i++) {
                for (int j = 0; j < N_SIZE; j++) {
                    if (fabs(C_ref[i][j] - C[i][j]) > 1e-3) {
                        errors++;
                        if (errors < 10) { // Only print first few errors
                            printf("Mismatch at (%d,%d): expected %f, got %f\n", i, j, C_ref[i][j], C[i][j]);
                        }
                    }
                }
            }

            if (errors == 0) {
                printf("TESTBENCH~PASSED\n");
                return 0;
            } else {
                printf("TESTBENCH~FAILED");
                return -1;
            }
        }
        