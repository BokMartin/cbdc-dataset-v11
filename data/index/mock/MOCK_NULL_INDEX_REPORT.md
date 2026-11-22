# MOCK: privacy index dry run

> **MOCK DATA. Invented inputs; nothing here is a result.**

Projects: 44. Separated pairs (diagnostic, spec §6): stated view 0.0359, admissible view 0.0.

## Coding reliability (Krippendorff's alpha, nominal)

| Cell | n | agreement | alpha (3 categories) | n both valued | alpha (valued) |
|---|---|---|---|---|---|
| F1 | 44 | 0.955 | 0.926 | 36 | 0.942 |
| F2 | 44 | 0.909 | 0.861 | 22 | 1.0 |
| F3 | 44 | 0.818 | 0.765 | 30 | 0.719 |
| F4 | 44 | 0.886 | 0.824 | 23 | 0.909 |
| F7 | 44 | 0.955 | 0.931 | 25 | 0.843 |
| F8 | 44 | 0.864 | 0.792 | 22 | 0.911 |
| F9 | 44 | 0.977 | 0.965 | 24 | 1.0 |
| F10 | 44 | 0.955 | 0.931 | 24 | 1.0 |

## Coverage after merge and expected separation

| Cell | share with a value |
|---|---|
| F1 | 0.795 |
| F2 | 0.5 |
| F3 | 0.409 |
| F4 | 0.5 |
| F7 | 0.523 |
| F8 | 0.477 |
| F9 | 0.545 |
| F10 | 0.545 |

Simulated share of separated pairs at this coverage: 0.0236 (0.0 to 0.055).

## Uncertainty and sensitivity (share of baseline separated pairs kept)

| Variant | all projects | T1 and T2 |
|---|---|---|
| baseline_separated_pairs | 34 | 8 |
| baseline_share | 0.0359 | 0.0667 |
| weights_kept_in_all_draws | 0.0882 | 0.125 |
| weights_mean_kept | 0.7621 | 0.8063 |
| rule_lexicographic_kept | 0.9412 | 0.75 |
| rule_cap_kept | 0.8824 | 0.75 |
| drop_F1_kept | 0.5294 | 0.75 |
| drop_F2_kept | 0.7059 | 0.75 |
| drop_F3_kept | 0.8235 | 0.875 |
| drop_F4_kept | 0.7941 | 0.875 |
| drop_F7_kept | 0.6471 | 0.375 |
| drop_F8_kept | 0.7647 | 0.875 |
| drop_F9_kept | 0.7941 | 0.75 |
| drop_F10_kept | 0.9118 | 0.75 |
| admissible_view_kept | 0.0 | 0.0 |
| without_F3_F9_kept | 0.8824 | 0.875 |
| core4_only_kept | 0.7647 | 0.75 |
| no_route_D_kept | 1.0 | 1.0 |
| with_leaning_kept | 1.0 | 1.0 |
| no_inferred_kept | 1.0 | 1.0 |

## Known cases

| Case | Project | Cell | expected | observed | status |
|---|---|---|---|---|---|
| MK01 | MOCK32 | F9 | yes | yes | hit |
| MK02 | MOCK28 | F7 | yes | yes | hit |
| MK03 | MOCK12 | F10 | no | no | hit |
| MK04 | MOCK35 | F8 | yes | yes | hit |
| MK05 | MOCK21 | F2 | yes | yes | hit |
| MK06 | MOCK38 | F1 | no | yes | miss |

## External measures (validity, not an association claim)

| Measure | role | expected sign | n | rho | 95 % interval |
|---|---|---|---|---|---|
| mock_convergent | convergent | + | 4 | 0.0 | [-1.0, 1.0] |
| mock_discriminant | discriminant | 0 | 4 | -0.4 | [-1.0, 1.0] |

## Privacy talk against commitments (six aspects with a matching F-cell)

| (project, aspect) pairs | count |
|---|---|
| talk_and_committed | 49 |
| talk_stated_not_decided | 100 |
| talk_no_commitment | 0 |
| talk_uncertain | 11 |
| silent_committed | 3 |
| silent_stated | 10 |
| silent_none | 77 |
| silent_uncertain | 14 |

H_TC1_admissible, lower bound: projects with talk share above commitment share 36, below 2, equal 6; one-sided sign test p = 0.0; mean difference 0.3144 (95 % [0.2386, 0.3901]).

H_TC1_admissible, upper bound: projects with talk share above commitment share 40, below 1, equal 3; one-sided sign test p = 0.0; mean difference 0.4091 (95 % [0.3371, 0.4773]).

H_TC2_stated, lower bound: projects with talk share above commitment share 0, below 20, equal 24; one-sided sign test p = 1.0; mean difference -0.1023 (95 % [-0.1439, -0.0606]).

H_TC2_stated, upper bound: projects with talk share above commitment share 6, below 9, equal 29; one-sided sign test p = 0.849121; mean difference -0.0076 (95 % [-0.0492, 0.0341]).

## Index per project

| Project | Tier | F1 | stated | admissible | rungs F1-F2-F3-F4-F7-F8-F9-F10 | decided of 8 |
|---|---|---|---|---|---|---|
| MOCK01 | T2 | undetermined | [0.375, 1.0] | [0.125, 1.0] | 0-2-0-1-0-0-0-3 | 1 |
| MOCK02 | T3 | protective | [0.25, 0.625] | [0.0, 1.0] | 2-0-1-0-1-0-1-1 | 0 |
| MOCK03 | T3 | protective | [0.25, 0.875] | [0.0, 1.0] | 2-0-0-2-0-0-0-1 | 0 |
| MOCK04 | T1 | undetermined | [0.5, 1.0] | [0.25, 1.0] | 0-0-0-0-1-1-3-4 | 2 |
| MOCK05 | T3 | protective | [0.375, 0.875] | [0.375, 1.0] | 3-0-0-3-1-0-4-0 | 3 |
| MOCK06 | T1 | not_protective | [0.625, 0.75] | [0.0, 0.875] | 1-2-1-1-2-0-1-3 | 1 |
| MOCK07 | T3 | protective | [0.25, 0.625] | [0.125, 0.75] | 3-0-4-1-0-2-3-0 | 3 |
| MOCK08 | T3 | protective | [0.375, 0.75] | [0.125, 1.0] | 3-0-1-1-1-0-2-0 | 1 |
| MOCK09 | T1 | undetermined | [0.25, 0.875] | [0.0, 1.0] | 0-0-1-0-0-0-1-1 | 0 |
| MOCK10 | T2 | protective | [0.125, 0.5] | [0.125, 1.0] | 3-1-0-1-0-1-0-1 | 1 |
| MOCK11 | T3 | not_protective | [0.25, 0.5] | [0.125, 0.75] | 2-3-0-2-3-0-3-2 | 3 |
| MOCK12 | T3 | protective | [0.25, 0.75] | [0.0, 1.0] | 1-2-0-0-0-0-1-2 | 0 |
| MOCK13 | T2 | protective | [0.5, 1.0] | [0.0, 1.0] | 1-0-0-0-1-0-1-2 | 0 |
| MOCK14 | T3 | not_protective | [0.375, 0.75] | [0.375, 1.0] | 1-0-3-0-0-1-3-4 | 3 |
| MOCK15 | T3 | not_protective | [0.0, 0.5] | [0.0, 0.875] | 1-0-0-1-2-0-0-4 | 1 |
| MOCK16 | T3 | not_protective | [0.5, 0.875] | [0.0, 1.0] | 1-0-0-1-2-1-1-0 | 0 |
| MOCK17 | T2 | protective | [0.125, 0.875] | [0.0, 0.875] | 1-0-0-0-0-4-0-0 | 1 |
| MOCK18 | T3 | protective | [0.5, 0.875] | [0.125, 1.0] | 1-3-1-0-0-1-0-1 | 1 |
| MOCK19 | T3 | protective | [0.5, 0.875] | [0.125, 1.0] | 2-0-1-3-0-1-1-0 | 1 |
| MOCK20 | T1 | undetermined | [0.375, 0.875] | [0.125, 1.0] | 0-3-0-0-1-1-0-1 | 1 |
| MOCK21 | T3 | protective | [0.375, 0.75] | [0.0, 1.0] | 1-1-1-0-0-2-1-0 | 0 |
| MOCK22 | T3 | protective | [0.5, 0.875] | [0.0, 0.875] | 1-3-1-0-0-1-1-0 | 1 |
| MOCK23 | T3 | not_protective | [0.25, 0.625] | [0.0, 0.625] | 3-1-3-0-3-0-1-0 | 3 |
| MOCK24 | T3 | protective | [0.375, 1.0] | [0.125, 1.0] | 2-0-3-0-0-0-0-1 | 1 |
| MOCK25 | T3 | undetermined | [0.0, 0.75] | [0.0, 0.75] | 0-0-0-0-3-0-4-0 | 2 |
| MOCK26 | T3 | undetermined | [0.0, 0.625] | [0.0, 1.0] | 0-1-0-1-0-0-0-1 | 0 |
| MOCK27 | T2 | not_protective | [0.125, 0.875] | [0.0, 1.0] | 1-0-0-0-2-0-0-0 | 0 |
| MOCK28 | T3 | protective | [0.375, 0.75] | [0.0, 0.75] | 1-1-0-3-1-0-0-3 | 2 |
| MOCK29 | T1 | undetermined | [0.125, 0.875] | [0.125, 1.0] | 0-0-3-0-0-2-0-0 | 1 |
| MOCK30 | T3 | protective | [0.5, 0.875] | [0.25, 1.0] | 4-0-0-2-0-3-1-1 | 2 |
| MOCK31 | T3 | not_protective | [0.25, 0.875] | [0.0, 1.0] | 2-1-0-0-0-1-0-0 | 0 |
| MOCK32 | T1 | not_protective | [0.25, 0.625] | [0.0, 0.625] | 4-0-0-0-1-4-4-1 | 3 |
| MOCK33 | T3 | not_protective | [0.125, 0.875] | [0.125, 0.875] | 3-0-0-0-0-4-0-0 | 2 |
| MOCK34 | T3 | protective | [0.5, 0.75] | [0.25, 1.0] | 4-0-0-2-1-1-4-2 | 2 |
| MOCK35 | T3 | protective | [0.25, 0.75] | [0.125, 1.0] | 4-1-0-1-0-2-0-0 | 1 |
| MOCK36 | T3 | undetermined | [0.125, 0.625] | [0.0, 0.875] | 0-1-0-1-3-0-1-0 | 1 |
| MOCK37 | T2 | protective | [0.125, 0.5] | [0.125, 0.75] | 3-3-1-0-1-0-0-4 | 3 |
| MOCK38 | T1 | not_protective | [0.375, 0.75] | [0.0, 0.875] | 1-0-0-1-4-1-0-1 | 1 |
| MOCK39 | T3 | protective | [0.625, 1.0] | [0.125, 1.0] | 1-2-4-1-1-0-0-0 | 1 |
| MOCK40 | T3 | protective | [0.625, 1.0] | [0.375, 1.0] | 4-3-1-0-1-3-0-0 | 3 |
| MOCK41 | T2 | not_protective | [0.25, 0.375] | [0.125, 0.75] | 2-1-0-4-2-3-2-4 | 3 |
| MOCK42 | T1 | not_protective | [0.0, 0.375] | [0.0, 0.75] | 1-4-1-3-1-0-0-0 | 2 |
| MOCK43 | T2 | protective | [0.125, 0.75] | [0.0, 1.0] | 1-1-0-0-0-0-1-0 | 0 |
| MOCK44 | T3 | undetermined | [0.375, 0.75] | [0.0, 1.0] | 0-2-2-1-0-0-1-1 | 0 |
