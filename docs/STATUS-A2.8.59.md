# Grilling 2.8.59: deterministic eating-curve serialization

Review candidate only. No merge, release or live deployment is implied.

## Confirmed problem
The Windows canonical job for commit 6acd33a77caed8c0ae57ba7bd9aeb4e2ac06f1f2 reported byte differences in java_eating_projection.animation.json. Its bounded diagnostics identify signed zero: committed 0.0 versus generated -0.0, and the converse. Linux regeneration passed. One-ULP math perturbation also exposed unstable initial Euler representatives.

## Change
- Round numeric item/player channels to eight decimals, then serialize either zero sign as 0.0
- Select the first Euler key in [-180,180), resolving values within 1e-8 degrees of the boundary to -180
- Unwrap later keys against the preceding key; never wrap every key independently
- Keep the full byte-for-byte generator check; no tolerance-based acceptance or fixture fallback
- Use a new runtime identity because serialized exported bytes change; frozen 2.8.58 is unchanged

The local diff from 2.8.58 has 1,550 zero-sign changes and 912 angle values shifted by a constant 360 degrees. No other animation values change. Player animation bytes are unchanged. Tests check source-curve offsets, interpolation midpoints, absence of spin discontinuities, exact regeneration, and one-ULP perturbations of sin/cos/asin/atan2. Existing matrix/gameplay tests remain required.

## Acceptance boundaries
This is a reproducibility repair, not additional Java feature completion. The 2.8.58 limited native observations remain historical evidence; they are not an exact-byte client acceptance of this candidate. Windows CI, package/family checks and native regression must be recorded for this identity before claiming readiness. Full Java parity, offhand food activation, helper-arm profiles, saved-world migration and production readiness remain open.
