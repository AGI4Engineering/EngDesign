#define M_SIZE 64
#define N_SIZE 64
#define K_SIZE 64

void gemm(float A[M_SIZE][K_SIZE], float B[K_SIZE][N_SIZE], float C[M_SIZE][N_SIZE]) {
    #pragma HLS INTERFACE m_axi port=A offset=slave bundle=A_BUS
    #pragma HLS INTERFACE m_axi port=B offset=slave bundle=B_BUS
    #pragma HLS INTERFACE m_axi port=C offset=slave bundle=C_BUS
    #pragma HLS INTERFACE s_axilite port=return bundle=CTRL_BUS

    // Perform matrix multiplication
    for (int i = 0; i < M_SIZE; ++i) {
        for (int j = 0; j < N_SIZE; ++j) {
            #pragma HLS PIPELINE II=1
            float sum = 0;
            for (int k = 0; k < K_SIZE; ++k) {
                sum += A[i][k] * B[k][j];
            }
            C[i][j] = sum;
        }
    }
}