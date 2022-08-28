#include <complex.h>
#include <math.h>
#include <pulse/error.h>
#include <pulse/simple.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define SAMPLE_RATE 16000

#define FRAME 128
#define MAPLEWAVE_MAGIC "MPLEWAVE"

const char *usage_msg = "usage: wave [options] <out.maplewave>\n"
                        "Record audio.\n\n"
                        "Interrupt with ctrl-c when done.\n\n"
                        "  -c level  set compression level (0-2, default 0)\n";

void usage_and_exit(void);
void record_loop(const char *path, int codec);

typedef struct maplewave {
    FILE *file;
    char codec;
    int frames;
    int bytes;

    unsigned long bits_prev;
    int bits_prev_num;

    unsigned char prev;
    signed char dc_prev;

    /* For RLE */
    int prev_emit;
    int prev_count;

} maplewave_t;

maplewave_t maplewave_open(const char *path, int codec);
void maplewave_append(maplewave_t *mpl, const unsigned char *samples);
void maplewave_close(maplewave_t *mpl);

int main(int argc, char **argv) {
    int opt;
    int level = 0;
    while ((opt = getopt(argc, argv, "c:")) != -1) {
        switch (opt) {
        case 'c':
            level = atoi(optarg);
            if (level < 0 || level > 2)
                usage_and_exit();
            break;
        default:
            usage_and_exit();
        }
    }

    if (optind != argc - 1)
        usage_and_exit();

    record_loop(argv[optind], level);
}

void usage_and_exit(void) {
    fputs(usage_msg, stderr);
    exit(1);
}

pa_sample_spec sample_spec = {
    .channels = 1,
    .rate = SAMPLE_RATE,
    .format = PA_SAMPLE_U8,
};

pa_buffer_attr buffer_attr = {
    .maxlength = -1,
    .tlength = -1,
    .prebuf = -1,
    .minreq = -1,
    .fragsize = FRAME,
};

volatile sig_atomic_t cancel = 0;

void handle_sigint(int x) { cancel = 1; }

void record_loop(const char *path, int codec) {
    if (signal(SIGINT, handle_sigint) == SIG_ERR) {
        perror("signal");
        exit(1);
    }

    static unsigned char samples[FRAME];
    pa_simple *stream;
    int err;
    stream = pa_simple_new(NULL, "wave", PA_STREAM_RECORD, NULL, "wave",
                           &sample_spec, NULL, &buffer_attr, &err);
    if (!stream) {
        printf("pa_simple_new: %s", pa_strerror(err));
    }

    maplewave_t mpl = maplewave_open(path, codec);

    int frame;
    int min = 0, s = 0, ds = 0, ms = 0;
    for (frame = 0; !cancel; frame++) {
        if (frame % 8 == 0) {
            char spinner = "-\\|/"[(frame >> 3) & 0x3];
            min = ms / 60000;
            s = (ms / 1000) % 60;
            ds = (ms / 10) % 100;
            fprintf(stderr, "\r[%c] recording to %s: [%d:%02d.%02d] %d kB...",
                    spinner, path, min, s, ds, mpl.bytes / 1024);
        }

        pa_simple_read(stream, samples, sizeof samples, &err);
        maplewave_append(&mpl, samples);
        ms += 1000 * FRAME / SAMPLE_RATE;
    }

    maplewave_close(&mpl);
    pa_simple_free(stream);

    printf("\r\033[2K[*] done! %s\n", path);
    printf("    codec:    %d\n    duration: %d:%02d.%02d\n    size:     %d "
           "kB\n    ratio:    %-3d%%\n",
           mpl.codec, min, s, ds, mpl.bytes / 1024,
           mpl.bytes * 100 / (frame * FRAME));
}

struct maplewave_header {
    char magic[8];
    char codec;
    char unused[3];
    int frames;
};

maplewave_t maplewave_open(const char *path, int codec) {
    FILE *f = fopen(path, "wb");
    if (!f) {
        perror("open");
        exit(1);
    }

    struct maplewave_header header = {
        .magic = MAPLEWAVE_MAGIC,
        .codec = codec,
        .unused = {0},
        .frames = 0,
    };
    fwrite(&header, 1, sizeof header, f);

    return (maplewave_t){
        .file = f,
        .codec = codec,
        .frames = 0,
        .bytes = sizeof header,

        .bits_prev = 0,
        .bits_prev_num = 0,

        .prev = 0,
        .dc_prev = 0,

        .prev_emit = 0,
        .prev_count = 0,
    };
}

void maplewave_a_uncompressed(maplewave_t *mpl, const unsigned char *samples);
void maplewave_a_golomb(maplewave_t *mpl, const unsigned char *samples);
void maplewave_a_dct(maplewave_t *mpl, const unsigned char *samples);

void maplewave_c_uncompressed(maplewave_t *mpl);
void maplewave_c_rle(maplewave_t *mpl);

void (*codecs_a[])(maplewave_t *mpl, const unsigned char *samples) = {
    maplewave_a_uncompressed,
    maplewave_a_golomb,
    maplewave_a_dct,
};

void (*codecs_c[])(maplewave_t *mpl) = {
    maplewave_c_uncompressed,
    maplewave_c_rle,
    maplewave_c_rle,
};

void maplewave_close(maplewave_t *mpl) {
    codecs_c[(int)mpl->codec](mpl);

    struct maplewave_header header = {
        .magic = MAPLEWAVE_MAGIC,
        .codec = mpl->codec,
        .unused = {0},
        .frames = mpl->frames,
    };
    fseek(mpl->file, 0, SEEK_SET);
    fwrite(&header, 1, sizeof header, mpl->file);
    fclose(mpl->file);
}

void maplewave_append(maplewave_t *mpl, const unsigned char *samples) {
    codecs_a[(int)mpl->codec](mpl, samples);
    mpl->frames += 1;
}

void maplewave_a_uncompressed(maplewave_t *mpl, const unsigned char *samples) {
    int bs = fwrite(samples, 1, FRAME, mpl->file);
    if (bs != FRAME) {
        perror("write");
        exit(1);
    }
    mpl->bytes += bs;
}

void maplewave_c_uncompressed(maplewave_t *mpl) {}

static void maplewave_out_bits(maplewave_t *mpl, unsigned bits, int num) {
    if (num == 0)
        return;

    mpl->bits_prev <<= num;
    mpl->bits_prev |= bits & ((1 << num) - 1);
    mpl->bits_prev_num += num;

    while (mpl->bits_prev_num >= 8) {
        mpl->bits_prev_num -= 8;
        fputc((mpl->bits_prev >> mpl->bits_prev_num) & 0xff, mpl->file);
        mpl->bytes += 1;
    }

    mpl->bits_prev_num &= (1 << mpl->bits_prev_num) - 1;
}

static void maplewave_out_finish(maplewave_t *mpl) {
    if (mpl->bits_prev_num > 0) {
        fputc((mpl->bits_prev << (8 - mpl->bits_prev_num)) & 0xff, mpl->file);
        mpl->bytes += 1;
    }

    mpl->bits_prev = 0;
    mpl->bits_prev_num = 0;
}

static inline unsigned char ilog2(unsigned int x) {
    return x == 0 ? 0 : 32 - __builtin_clz(x);
}

static void maplewave_out_golomb_u(maplewave_t *mpl, unsigned int diff) {
    unsigned char exp = ilog2(diff);
    unsigned exp_encoding = ((1 << exp) - 1) << 1;
    int exp_len = exp + 1;
    unsigned mantissa = diff & ((1 << (exp - 1)) - 1);
    int mantissa_len = exp == 0 ? 0 : exp - 1;

    maplewave_out_bits(mpl, exp_encoding, exp_len);
    maplewave_out_bits(mpl, mantissa, mantissa_len);
}

static void maplewave_out_golomb_s(maplewave_t *mpl, int diff) {
    char sign = diff < 0;
    if (sign)
        diff = -diff;

    maplewave_out_bits(mpl, sign, 1);
    maplewave_out_golomb_u(mpl, diff);
}

static void maplewave_emit_rle(maplewave_t *mpl) {
    if (mpl->prev_count > 0) {
        maplewave_out_bits(mpl, 0x2, 2);
        maplewave_out_golomb_u(mpl, mpl->prev_count);
    }
    mpl->prev_count = 0;
    mpl->prev_emit = 0;
}

void maplewave_emit(maplewave_t *mpl, int x) {
    if (x == mpl->prev_emit) {
        mpl->prev_count++;
    } else {
        maplewave_emit_rle(mpl);
        maplewave_out_golomb_s(mpl, x);
        mpl->prev_emit = x;
    }
}

void maplewave_a_golomb(maplewave_t *mpl, const unsigned char *samples) {
    for (int i = 0; i < FRAME; i++) {
        int diff = samples[i] - mpl->prev;
        mpl->prev = samples[i];
        maplewave_emit(mpl, diff);
    }

    maplewave_emit_rle(mpl);
    mpl->prev = 0;
}

void maplewave_c_rle(maplewave_t *mpl) {
    maplewave_emit_rle(mpl);
    maplewave_out_finish(mpl);
}

void dct(float *x);

void maplewave_a_dct(maplewave_t *mpl, const unsigned char *samples) {
    static float samples_f[FRAME];
    for (int i = 0; i < FRAME; i++) {
        samples_f[i] = (samples[i] - 128.0) / 128.0;
    }
    dct(samples_f);

    signed char dc = samples_f[0];
    maplewave_out_golomb_s(mpl, dc - mpl->dc_prev);
    mpl->dc_prev = dc;

    for (int i = 1; i < FRAME; i++) {
        int coef = samples_f[i];
        maplewave_emit(mpl, coef);
    }

    maplewave_emit_rle(mpl);
}

#define MAX_FFT (4 * FRAME)
#define MAX_FFT_BITS 9

/* Bit reversal permutation for 512 elements */
short bit_reverse[4 * FRAME];

__attribute__((constructor)) void init_fft_coefs() {
    for (int i = 0; i < 4 * FRAME; i++) {
        int j = 0;
        for (int k = 0; k < 9; k++)
            j |= ((i >> k) & 1) << (MAX_FFT_BITS - 1 - k);
        bit_reverse[j] = i;
    }
}

void fft(float complex *x) {
    for (int k = 0; k < MAX_FFT; k++) {
        if (bit_reverse[k] < k)
            continue;
        float complex tmp = x[k];
        x[k] = x[bit_reverse[k]];
        x[bit_reverse[k]] = tmp;
    }

    for (int m = 2; m <= MAX_FFT; m *= 2) {
        float complex omega_m = cexpf(-2i * M_PI / m);
        for (int k = 0; k < MAX_FFT; k += m) {
            float complex omega = 1;
            for (int j = 0; j < m / 2; j++) {
                float complex t = omega * x[k + j + m / 2];
                float complex u = x[k + j];
                x[k + j] = u + t;
                x[k + j + m / 2] = u - t;
                omega *= omega_m;
            }
        }
    }
}

void dct(float *x) {
    static float complex y[MAX_FFT];
    for (int i = 0; i < FRAME; i++) {
        y[2 * i] = 0;
        y[1 + 2 * i] = x[i];
        y[MAX_FFT - 1 - 2 * i] = x[i];
        y[MAX_FFT - 2 - 2 * i] = 0;
    }
    fft(y);
    for (int i = 0; i < FRAME; i++) {
        x[i] = crealf(y[i]);
    }
}
