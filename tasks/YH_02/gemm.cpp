#include <hls_stream.h>
#include <ap_int.h>
#include <ap_axi_sdata.h>
#include <stdexcept>

#define M_SIZE 1024
#define N_SIZE 1024
#define K_SIZE 1024
#define TM 64
#define TN 64
#define TK 64

void gemm(float *A, float *B, float *C)
{
    if (!A || !B || !C)
    {
#ifndef __SYNTHESIS__
        throw std::runtime_error("Null pointer passed to gemm");
#endif
        return;
    }

#pragma HLS INTERFACE m_axi port = A bundle = gmem0 offset = slave depth = 1048576
#pragma HLS INTERFACE m_axi port = B bundle = gmem1 offset = slave depth = 1048576
#pragma HLS INTERFACE m_axi port = C bundle = gmem2 offset = slave depth = 1048576
#pragma HLS INTERFACE s_axilite port = A
#pragma HLS INTERFACE s_axilite port = B
#pragma HLS INTERFACE s_axilite port = C
#pragma HLS INTERFACE s_axilite port = return

    float localA[TM][TK];
#pragma HLS ARRAY_PARTITION variable = localA dim = 2 complete

    float localB[TK][TN];
#pragma HLS ARRAY_PARTITION variable = localB dim = 1 complete

    float localC[TM][TN];
#pragma HLS ARRAY_PARTITION variable = localC dim = 1 complete
#pragma HLS ARRAY_PARTITION variable = localC dim = 2 complete

#pragma HLS DATAFLOW
    // Tiled matrix multiplication
    for (int i = 0; i < M_SIZE; i += TM)
    {
        for (int j = 0; j < N_SIZE; j += TN)
        {
            // Initialize localC tile
            for (int ti = 0; ti < TM; ti++)
            {
                for (int tj = 0; tj < TN; tj++)
                {
#pragma HLS PIPELINE II = 1
                    localC[ti][tj] = 0;
                }
            }

            // Compute tile
            for (int k = 0; k < K_SIZE; k += TK)
            {
                // Load tile from A
                for (int ti = 0; ti < TM; ti++)
                {
                    for (int tk = 0; tk < TK; tk++)
                    {
#pragma HLS PIPELINE II = 1
                        int idx_a = (i + ti) * K_SIZE + (k + tk);
                        if (idx_a < M_SIZE * K_SIZE)
                        {
                            localA[ti][tk] = A[idx_a];
                        }
                    }
                }

                // Load tile from B
                for (int tk = 0; tk < TK; tk++)
                {
                    for (int tj = 0; tj < TN; tj++)
                    {
#pragma HLS PIPELINE II = 1
                        int idx_b = (k + tk) * N_SIZE + (j + tj);
                        if (idx_b < K_SIZE * N_SIZE)
                        {
                            localB[tk][tj] = B[idx_b];
                        }
                    }
                }

                // Compute tile
                for (int ti = 0; ti < TM; ti++)
                {
                    for (int tj = 0; tj < TN; tj++)
                    {
#pragma HLS PIPELINE II = 1
                        float sum = localC[ti][tj];
                        for (int tk = 0; tk < TK; tk++)
                        {
                            sum += localA[ti][tk] * localB[tk][tj];
                        }
                        localC[ti][tj] = sum;
                    }
                }
            }

            // Store result tile to C
            for (int ti = 0; ti < TM; ti++)
            {
                for (int tj = 0; tj < TN; tj++)
                {
#pragma HLS PIPELINE II = 1
                    int idx_c = (i + ti) * N_SIZE + (j + tj);
                    if (idx_c < M_SIZE * N_SIZE)
                    {
                        C[idx_c] = localC[ti][tj];
                    }
                }
            }
        }
    }
}