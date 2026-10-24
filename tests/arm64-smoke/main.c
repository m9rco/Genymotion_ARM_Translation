/* Compile with the Android NDK AArch64 compiler, not the host compiler. */
#include <stdint.h>
#include <stdio.h>

#if !defined(__aarch64__)
#error "This probe must be compiled for AArch64 / arm64-v8a"
#endif

int main(void) {
    volatile uint64_t input = UINT64_C(0x123456789abcdef0);
    uint64_t rotated = (input << 13) | (input >> 51);
    if (sizeof(void *) != 8 || rotated != UINT64_C(0x8acf13579bde0246)) {
        return 1;
    }
    puts("ARM64_TRANSLATION_OK");
    return 0;
}
