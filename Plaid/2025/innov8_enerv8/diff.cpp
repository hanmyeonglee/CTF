static inline double ToDouble(uint64_t state0) {
    // Get a random [0,2**53) integer value (up to MAX_SAFE_INTEGER) by dropping
    // 11 bits of the state.
    double random_0_to_2_53 = static_cast<double>(state0 >> 11);
    // Map this to [0,1) by division with 2**53.
    constexpr double k2_53{static_cast<uint64_t>(1) << 53};
    return random_0_to_2_53 / k2_53;
}

static inline double ToDouble(uint64_t state0) {
    // Exponent for double values for [1.0 .. 2.0)
    static const uint64_t kExponentBits = uint64_t{0x3FF0000000000000};
    uint64_t random = (state0 >> 12) | kExponentBits;
    return base::bit_cast<double>(random) - 1;
}