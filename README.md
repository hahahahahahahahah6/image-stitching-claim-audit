# Documentation claim auditor

Version 0.1.0. Offline, deterministic, standard-library-only Python 3.9+ CLI
comparing documentation about joining overlapping pictures into one wide picture
with static source patterns. No LLM, network, telemetry, or filesystem writes.
MIT licensed.

## Install and run

```sh
python3 -m pip install .
image-stitching-claim-audit --version
image-stitching-claim-audit audit . --json
python3 -m image_stitching_claim_audit audit . --verbose
image-stitching-claim-audit audit --ignore docs/archive/ . --fail-on medium
python3 -m unittest discover
python3 -m build
```

The repository defaults to the current directory. Repeat the single-value ignore
option to skip multiple path prefixes. Verbose scope and decisions go to stderr.
JSON includes verdict and message fields on every finding. Exit codes are 0 for
PASS, 2 for findings at the selected threshold, and 1 for usage or IO errors.
The default threshold is high; medium also fails test-only claims. Each rule
family produces at most one finding.

```text
documented-image-stitching-claim-false (high; test-only: medium)
documented-no-image-stitching-claim-false (high)
```

## Scope and evidence

Scans root README.md and docs/**/*.md. Triple-backtick fenced blocks are excluded;
inline code counts as prose. Matching uses case-insensitive exact substrings,
without stemming or hyphen normalization. Denial spans are removed first.
Longest-first matching with span blanking makes each occurrence match once under
its longest phrase. No claims is a pass. A denial without contrary code is a pass.
Fixtures under tests/ can yield a medium finding.

Every Python source is checked independently, excluding Git metadata, bytecode
caches, and virtual environments. Each complete route must occur in one module.
Imports and aliases are resolved; local function and class definitions shadow
route names. Assigned and chained constructions are recognized.

```text
OpenCV: Stitcher_create / createStitcher / Stitcher.create + instance .stitch()
stitching package: imported Stitcher + instance .stitch() or .stitch_verbose()
Manual: SIFT_create / ORB_create / AKAZE_create / BRISK_create
  + BFMatcher / FlannBasedMatcher + findHomography + warpPerspective
Generic: 24 explicit method names, e.g. x.stitch_images() or imported stitch_images()
```

Imports, lone constructions, incomplete manual pipelines, single-picture warps,
blending, viewing, stabilization, capture, metadata, classification, captioning,
generation, enlargement, filling, colorization, cutouts, and detection alone do
not provide evidence. Strings, comments, docstrings, unbound references and
subprocess commands do not provide evidence.

## Differentiation

The checked capability joins overlapping pictures into one wide picture.
The neighboring tools below check separate operations, in order: assigning one
label to a whole picture; cutting a subject out of a picture; upscaling one
picture; filling a hole in one picture; adding color to a grey picture; finding
and boxing things in one picture.

```text
image-classification-claim-audit
image-background-removal-claim-audit
super-resolution-claim-audit
image-inpainting-claim-audit
image-colorization-claim-audit
image-object-detection-claim-audit
```

## Limitations

Static pattern matching is not semantic judgement or proof of working behavior.
Exact phrases miss restatements. The first phrase below can also describe
stitching by hand in a photo editor. The second can also describe taking a
panorama photo with a phone camera. Both still match, by design.

```text
stitch images together
create a panorama
```

The manual feature-match pipeline also matches plain image registration /
alignment work that never produces a panorama. A generic call below on an
unrelated object counts as evidence because the method name is shared.

```python
x.create_panorama()
```

For a README-only self-audit, copy this file to an otherwise empty directory and
audit it. The full checkout yields an expected medium finding from the fixed
phrase-oracle literals in tests/.
