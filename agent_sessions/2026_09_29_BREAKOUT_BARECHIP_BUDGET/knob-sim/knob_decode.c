/* knob_decode.c — portable knob-typing lexicon decoder (MCU-ready core + host test harness).
 *
 * Lexicon blob (built by export_lex.py), all little-endian:
 *   u32 n_words | u8 max_units | then per word (sorted by unit sequence):
 *   u8 hdr = (lcp << 4) | suffix_len   (units shared with previous word / new units, each <= 15)
 *   u8 cost                            (-log P(word) quantised: cost*COST_Q nats)
 *   6-bit symbols * suffix_len, packed MSB-first, padded to a byte   (symbol = letter*2 + double_flag)
 *
 * Decode = Viterbi edit-distance DP of T observed pause positions vs each word's units,
 * sharing DP rows across common prefixes (sorted lexicon => only lcp..L rows recomputed).
 * RAM: DP rows 16*25 floats (1.6 KB) + emission table 52*24 floats (5.0 KB) + top-K  => ~6.7 KB stack (half with int16).
 * The core (kd_decode) touches no heap and no libc except expf-free float math.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define MAXU 15
#define MAXT 24
#define TOPK 3
#define COST_Q 0.1f
#define NEG (-1e30f)

typedef struct { float mu[26], sd[26]; float lp_del, lp_ins, lp_match; float lf[2][2]; /* lf[flag][dbl] */ float lam; int gap; } kd_params;
typedef struct { uint32_t offset[TOPK]; float score[TOPK]; } kd_result;

static uint64_t g_cells; /* op counter: DP cell updates */

static inline float max3(float a, float b, float c) { float m = a > b ? a : b; return m > c ? m : c; }

/* returns number of words scored */
static uint32_t kd_decode(const uint8_t *blob, const kd_params *P, const float *obs, const uint8_t *flag, int T, kd_result *R) {
    float E[52][MAXT];                 /* emission incl. flag term, per symbol */
    float D[MAXU + 1][MAXT + 1];       /* D[j][t]: j units consumed, t obs consumed */
    float ins[MAXT];
    for (int s = 0; s < 52; s++) {
        int c = s >> 1, dbl = s & 1;
        float inv = 1.0f / P->sd[c], lsd = logf(P->sd[c]) + 0.9189385f;
        for (int t = 0; t < T; t++) {
            float z = (obs[t] - P->mu[c]) * inv;
            float e = -0.5f * z * z - lsd; if (e < -30.f) e = -30.f;
            E[s][t] = e + P->lf[flag[t]][dbl] + P->lp_match;
        }
    }
    for (int t = 0; t < T; t++) ins[t] = P->lp_ins + P->lf[flag[t]][0];
    D[0][0] = 0.f;
    for (int t = 1; t <= T; t++) D[0][t] = D[0][t - 1] + ins[t - 1];
    for (int k = 0; k < TOPK; k++) { R->score[k] = NEG; R->offset[k] = 0; }

    uint32_t n = blob[0] | blob[1] << 8 | blob[2] << 16 | (uint32_t)blob[3] << 24, scored = 0;
    const uint8_t *p = blob + 5;
    uint8_t units[MAXU];
    for (uint32_t w = 0; w < n; w++) {
        uint32_t off = (uint32_t)(p - blob);
        int lcp = p[0] >> 4, sl = p[0] & 15; float cost = p[1] * COST_Q; p += 2;
        uint32_t bits = 0; int nb = 0;
        for (int i = 0; i < sl; i++) {                  /* unpack 6-bit symbols */
            while (nb < 6) { bits = bits << 8 | *p++; nb += 8; }
            units[lcp + i] = (bits >> (nb - 6)) & 63; nb -= 6;
        }
        int L = lcp + sl;
        int gap = L - T; if (gap < 0) gap = -gap;
        /* rows lcp+1..L; rows <= lcp are still valid from the previous word */
        if (gap > P->gap) {
            /* still must refresh rows so later words sharing this prefix are correct */
        }
        for (int j = lcp + 1; j <= L; j++) {
            const float *e = E[units[j - 1]];
            float *prev = D[j - 1], *cur = D[j];
            cur[0] = prev[0] + P->lp_del;
            for (int t = 1; t <= T; t++)
                cur[t] = max3(prev[t - 1] + e[t - 1], prev[t] + P->lp_del, cur[t - 1] + ins[t - 1]);
            g_cells += T;
        }
        if (gap > P->gap) continue;
        scored++;
        float sc = D[L][T] - P->lam * cost;
        if (sc > R->score[TOPK - 1]) {
            int k = TOPK - 1;
            while (k > 0 && R->score[k - 1] < sc) { R->score[k] = R->score[k - 1]; R->offset[k] = R->offset[k - 1]; k--; }
            R->score[k] = sc; R->offset[k] = off;
        }
    }
    return scored;
}

#ifndef KD_CORE_ONLY
/* ------------------------------------------------------------------ host harness */
static uint8_t *slurp(const char *fn, long *len) {
    FILE *f = fopen(fn, "rb"); if (!f) { perror(fn); exit(1); }
    fseek(f, 0, SEEK_END); *len = ftell(f); rewind(f);
    uint8_t *b = malloc(*len); if (fread(b, 1, *len, f) != (size_t)*len) exit(2); fclose(f); return b;
}

/* reconstruct the word at a blob offset by walking from the start (host only) */
static void word_at(const uint8_t *blob, uint32_t target, char *out) {
    uint32_t n = blob[0] | blob[1] << 8 | blob[2] << 16 | (uint32_t)blob[3] << 24;
    const uint8_t *p = blob + 5; uint8_t units[MAXU];
    for (uint32_t w = 0; w < n; w++) {
        uint32_t off = (uint32_t)(p - blob);
        int lcp = p[0] >> 4, sl = p[0] & 15; p += 2;
        uint32_t bits = 0; int nb = 0;
        for (int i = 0; i < sl; i++) { while (nb < 6) { bits = bits << 8 | *p++; nb += 8; } units[lcp + i] = (bits >> (nb - 6)) & 63; nb -= 6; }
        if (off == target) {
            int k = 0;
            for (int j = 0; j < lcp + sl; j++) { out[k++] = 'a' + (units[j] >> 1); if (units[j] & 1) out[k++] = 'a' + (units[j] >> 1); }
            out[k] = 0; return;
        }
    }
    out[0] = 0;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s lex.bin cases.txt\n", argv[0]); return 1; }
    long blen; uint8_t *blob = slurp(argv[1], &blen);
    FILE *cf = fopen(argv[2], "r"); if (!cf) { perror(argv[2]); return 1; }
    kd_params P;
    for (int i = 0; i < 26; i++) if (fscanf(cf, "%f", &P.mu[i]) != 1) return 3;
    for (int i = 0; i < 26; i++) if (fscanf(cf, "%f", &P.sd[i]) != 1) return 3;
    if (fscanf(cf, "%f %f %f %f %f %f %f %f %d", &P.lp_del, &P.lp_ins, &P.lp_match,
               &P.lf[1][1], &P.lf[0][1], &P.lf[1][0], &P.lf[0][0], &P.lam, &P.gap) != 9) return 3;
    int ncase = 0, ok = 0, agree = 0; double secs = 0; uint64_t cells0; uint32_t scored = 0;
    char truth[64], pytop[64], ctop[64];
    int T;
    g_cells = 0; cells0 = 0;
    while (fscanf(cf, "%63s %63s %d", truth, pytop, &T) == 3) {
        float obs[MAXT]; uint8_t fl[MAXT]; int fi;
        for (int t = 0; t < T; t++) { if (fscanf(cf, "%f %d", &obs[t], &fi) != 2) return 4; fl[t] = (uint8_t)fi; }
        if (T > MAXT) continue;
        kd_result R;
        struct timespec a, b; clock_gettime(CLOCK_MONOTONIC, &a);
        for (int rep = 0; rep < 20; rep++) scored = kd_decode(blob, &P, obs, fl, T, &R);
        clock_gettime(CLOCK_MONOTONIC, &b);
        secs += ((b.tv_sec - a.tv_sec) + (b.tv_nsec - a.tv_nsec) * 1e-9) / 20;
        word_at(blob, R.offset[0], ctop);
        ncase++; ok += !strcmp(ctop, truth); agree += !strcmp(ctop, pytop);
    }
    printf("lexicon_bytes=%ld cases=%d top1=%.3f agree_with_python=%.3f mean_us_per_word=%.1f mean_dp_cells_per_word=%.0f words_scored_last=%u\n",
           blen, ncase, (double)ok / ncase, (double)agree / ncase, secs / ncase * 1e6, (double)g_cells / ncase / 20, scored);
    (void)cells0;
    return 0;
}
#else
uint32_t kd_decode_entry(const uint8_t *b, const kd_params *P, const float *o, const uint8_t *f, int T, kd_result *R) { return kd_decode(b, P, o, f, T, R); }
#endif
