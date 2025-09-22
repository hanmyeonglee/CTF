(() => {
    "use strict";

    const _POOL = [
        "QUJD",
        "fUp8",
        "AAAA",
        "S3Zr",
        "J15S",
        "T0If",
        "Onp9",
        "////",
        "H1IV",
        "dWx4",
        "EFQe",
        "Okwn",
        "RCxY",
        "Zg==",
        "DSU=",
        "Fyo="
    ];

    const _IDX_C = [1, 3, 4, 5, 6, 8, 9, 10, 11, 12];
    const _IDX_S = [14, 15];

    const _a2b = (b64) => {
        const bin = atob(b64);
        const out = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
        return out;
    };

    const _joinChunks = (idxs) => {
        let totalLen = 0, parts = [];
        for (const idx of idxs) {
            const part = _a2b(_POOL[idx]);
            parts.push(part); totalLen += part.length;
        }
        const out = new Uint8Array(totalLen);
        let off = 0;
        for (const p of parts) { out.set(p, off); off += p.length; }
        return out;
    };

    const _C = _joinChunks(_IDX_C);
    const _S = _joinChunks(_IDX_S);

    function _deriveKey(s) { let a = 0, b = 1; for (let i = 0; i < s.length; i++) { const ch = s.charCodeAt(i) & 255; a = (a + ch) & 255; b = (b * 131 + ch) & 255; } return new Uint8Array([a, b, a ^ b, (a * 3 + b * 5) & 255]); }
    const F_SALT = new Uint8Array([0, 0, 0, 0]);

    function _check(inp) {
        const out = new Uint8Array(_C.length);
        for (let i = 0; i < _C.length; i++) out[i] = _C[i] ^ _S[i % _S.length];
        const flag = new TextDecoder().decode(out);
        return inp === flag;
    }

    document.getElementById("b").addEventListener("click", () => {
        const v = document.getElementById("f").value;
        document.getElementById("o").innerText = _check(v) ? "Correct" : "Wrong";
    });

})();
