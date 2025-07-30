## v3.12.1 (2025-07-04)

### 🐞 Bug Fixes

- **io.plugins.merlin:** take energy step from data attributes ([84bc6b9](https://github.com/kmnhan/erlabpy/commit/84bc6b9e133c841597f6f74e727a13fe3c6a0147))

  Fixed and swept mode scans have random numerical errors in the start & step of the energy axis. The error of the step accumulates over the scan, effectively resulting in a tiny renormalization of the energy axis. We choose to ignore the energy axis information contained in the wave, and take the step from the attributes instead.

### ♻️ Code Refactor

- **io.plugins.merlin:** do not subtract BL Energy from eV for Live XY and Live Polar scans ([379fc8d](https://github.com/kmnhan/erlabpy/commit/379fc8dd9635589bbcdcd4af1f61e38d3f4a0959))

  The BL Energy attribute is not reliable for Live XY and Live Polar scans, so we just take the raw energy values like Igor Pro does.

[main 79f79a2] bump: version 3.12.0 → 3.12.1
 3 files changed, 16 insertions(+), 2 deletions(-)

