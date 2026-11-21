# MOCK: privacy index dry run

> **MOCK DATA. Invented inputs; nothing here is a result.**

Projects: 44. Separated pairs (diagnostic, spec §6): stated view 0.2495, admissible view 0.0148.

## Coding reliability (Krippendorff's alpha, nominal)

| Cell | n | agreement | alpha (3 categories) | n both valued | alpha (valued) |
|---|---|---|---|---|---|
| F1 | 44 | 0.955 | 0.93 | 31 | 1.0 |
| F2 | 44 | 0.909 | 0.846 | 18 | 0.784 |
| F4 | 44 | 0.977 | 0.964 | 22 | 1.0 |
| F7 | 44 | 0.886 | 0.819 | 20 | 0.805 |

## Coverage after merge and expected separation

| Cell | share with a value |
|---|---|
| F1 | 0.705 |
| F2 | 0.364 |
| F4 | 0.5 |
| F7 | 0.409 |

Simulated share of separated pairs at this coverage: 0.268 (0.1839 to 0.352).

## Uncertainty and sensitivity (share of baseline separated pairs kept)

| Variant | all projects | T1 and T2 |
|---|---|---|
| baseline_separated_pairs | 236 | 29 |
| baseline_share | 0.2495 | 0.2417 |
| weights_kept_in_all_draws | 1.0 | 1.0 |
| weights_mean_kept | 1.0 | 1.0 |
| rule_mean_kept | 0.1229 | 0.3793 |
| rule_cap_kept | 0.1229 | 0.3793 |
| drop_F1_kept | 0.0678 | 0.069 |
| drop_F2_kept | 0.9958 | 1.0 |
| drop_F4_kept | 0.9576 | 0.9655 |
| drop_F7_kept | 0.9873 | 1.0 |
| admissible_view_kept | 0.0593 | 0.1379 |
| with_F8_F10_kept | 0.9322 | 0.931 |
| no_route_D_kept | 1.0 | 1.0 |
| no_inferred_kept | 1.0 | 1.0 |

## Known cases

| Case | Project | Cell | expected | observed | status |
|---|---|---|---|---|---|
| MK01 | MOCK34 | F4 | no | no | hit |
| MK02 | MOCK31 | F2 | yes | yes | hit |
| MK03 | MOCK16 | F7 | no | no | hit |
| MK04 | MOCK38 | F1 | no | no | hit |
| MK05 | MOCK24 | F4 | yes | yes | hit |
| MK06 | MOCK41 | F1 | yes | no | miss |

## External measures (validity, not an association claim)

| Measure | role | expected sign | n | rho | 95 % interval |
|---|---|---|---|---|---|
| mock_convergent | convergent | + | 12 | 0.786 | [0.376, 0.906] |
| mock_discriminant | discriminant | 0 | 12 | 0.491 | [0.0, 0.776] |

## Index per project

| Project | Tier | F1 | stated | admissible | rungs F1-F2-F4-F7 | decided of 4 |
|---|---|---|---|---|---|---|
| MOCK01 | T1 | protective | [0.6667, 0.8333] | [0.0, 1.0] | 2-1-0-1 | 0 |
| MOCK02 | T3 | protective | [0.6667, 1.0] | [0.0, 1.0] | 2-0-0-2 | 0 |
| MOCK03 | T3 | undetermined | [0.5, 1.0] | [0.0, 1.0] | 0-2-1-2 | 0 |
| MOCK04 | T3 | undetermined | [0.0, 1.0] | [0.0, 1.0] | 0-0-0-0 | 0 |
| MOCK05 | T1 | protective | [0.6667, 0.8333] | [0.1667, 1.0] | 1-4-2-0 | 1 |
| MOCK06 | T3 | not_protective | [0.3333, 0.5] | [0.1667, 1.0] | 1-3-2-0 | 1 |
| MOCK07 | T3 | undetermined | [0.0, 1.0] | [0.0, 1.0] | 0-0-0-0 | 0 |
| MOCK08 | T3 | undetermined | [0.0, 1.0] | [0.0, 1.0] | 0-0-0-0 | 0 |
| MOCK09 | T3 | not_protective | [0.0, 0.3333] | [0.0, 1.0] | 1-0-1-0 | 0 |
| MOCK10 | T3 | protective | [0.6667, 1.0] | [0.0, 1.0] | 2-0-2-0 | 0 |
| MOCK11 | T2 | undetermined | [0.0, 1.0] | [0.0, 1.0] | 0-0-0-0 | 0 |
| MOCK12 | T1 | protective | [0.6667, 0.6667] | [0.5, 1.0] | 3-2-1-2 | 1 |
| MOCK13 | T3 | undetermined | [0.3333, 0.8333] | [0.1667, 1.0] | 0-2-4-1 | 1 |
| MOCK14 | T3 | undetermined | [0.0, 1.0] | [0.0, 1.0] | 0-0-0-0 | 0 |
| MOCK15 | T1 | protective | [0.6667, 1.0] | [0.6667, 1.0] | 3-0-3-0 | 2 |
| MOCK16 | T1 | not_protective | [0.0, 0.1667] | [0.0, 0.5] | 3-1-0-1 | 1 |
| MOCK17 | T3 | protective | [0.5, 0.8333] | [0.0, 1.0] | 2-0-2-0 | 0 |
| MOCK18 | T3 | undetermined | [0.0, 1.0] | [0.0, 1.0] | 0-0-0-0 | 0 |
| MOCK19 | T2 | undetermined | [0.5, 1.0] | [0.1667, 1.0] | 0-4-1-2 | 1 |
| MOCK20 | T2 | undetermined | [0.0, 0.6667] | [0.0, 1.0] | 0-0-1-2 | 0 |
| MOCK21 | T3 | not_protective | [0.1667, 0.5] | [0.0, 1.0] | 1-0-1-0 | 0 |
| MOCK22 | T3 | not_protective | [0.1667, 0.3333] | [0.1667, 0.8333] | 1-0-4-4 | 2 |
| MOCK23 | T3 | not_protective | [0.1667, 0.5] | [0.1667, 1.0] | 1-3-0-0 | 1 |
| MOCK24 | T3 | not_protective | [0.1667, 0.3333] | [0.1667, 1.0] | 1-0-3-1 | 1 |
| MOCK25 | T2 | protective | [0.6667, 1.0] | [0.0, 1.0] | 1-0-1-0 | 0 |
| MOCK26 | T2 | not_protective | [0.0, 0.3333] | [0.0, 0.8333] | 1-0-3-0 | 1 |
| MOCK27 | T3 | protective | [0.5, 0.8333] | [0.0, 1.0] | 2-0-0-1 | 0 |
| MOCK28 | T3 | undetermined | [0.1667, 0.8333] | [0.1667, 0.8333] | 0-3-0-3 | 2 |
| MOCK29 | T1 | protective | [0.6667, 1.0] | [0.1667, 1.0] | 2-4-0-0 | 1 |
| MOCK30 | T2 | not_protective | [0.0, 0.5] | [0.0, 1.0] | 1-0-0-0 | 0 |
| MOCK31 | T2 | protective | [0.6667, 0.8333] | [0.1667, 1.0] | 1-1-0-3 | 1 |
| MOCK32 | T3 | protective | [0.5, 0.8333] | [0.5, 0.8333] | 3-0-3-0 | 2 |
| MOCK33 | T1 | protective | [0.6667, 0.8333] | [0.5, 1.0] | 4-1-1-0 | 1 |
| MOCK34 | T3 | not_protective | [0.0, 0.3333] | [0.0, 0.8333] | 1-0-3-0 | 1 |
| MOCK35 | T2 | protective | [0.6667, 1.0] | [0.5, 1.0] | 3-0-1-0 | 1 |
| MOCK36 | T3 | protective | [0.5, 0.6667] | [0.5, 0.8333] | 3-2-0-3 | 2 |
| MOCK37 | T1 | undetermined | [0.0, 0.8333] | [0.0, 0.8333] | 0-0-0-3 | 1 |
| MOCK38 | T3 | protective | [0.5, 0.8333] | [0.0, 1.0] | 1-1-0-0 | 0 |
| MOCK39 | T3 | not_protective | [0.0, 0.3333] | [0.0, 0.3333] | 3-0-3-0 | 2 |
| MOCK40 | T3 | protective | [0.5, 1.0] | [0.5, 1.0] | 4-0-0-0 | 1 |
| MOCK41 | T3 | protective | [0.6667, 0.8333] | [0.0, 0.8333] | 1-0-3-1 | 1 |
| MOCK42 | T3 | protective | [0.5, 0.6667] | [0.0, 1.0] | 1-1-0-1 | 0 |
| MOCK43 | T3 | protective | [0.6667, 1.0] | [0.0, 1.0] | 1-0-0-1 | 0 |
| MOCK44 | T3 | undetermined | [0.0, 1.0] | [0.0, 1.0] | 0-0-0-0 | 0 |
