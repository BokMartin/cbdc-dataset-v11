# MOCK: privacy index dry run

> **MOCK DATA. Invented inputs; nothing here is a result.**

Projects: 44. Separated pairs (diagnostic, spec §6): stated view 0.0243, admissible view 0.0.

## Coding reliability (Krippendorff's alpha, nominal)

| Cell | n | agreement | alpha (3 categories) | n both valued | alpha (valued) |
|---|---|---|---|---|---|
| F1 | 44 | 0.955 | 0.926 | 38 | 0.896 |
| F2 | 44 | 0.886 | 0.829 | 24 | 0.917 |
| F4 | 44 | 0.886 | 0.822 | 20 | 1.0 |
| F7 | 44 | 0.932 | 0.886 | 18 | 1.0 |
| F8 | 44 | 0.955 | 0.931 | 25 | 1.0 |
| F9 | 44 | 0.955 | 0.921 | 18 | 1.0 |
| F10 | 44 | 0.977 | 0.966 | 26 | 1.0 |

## Coverage after merge and expected separation

| Cell | share with a value |
|---|---|
| F1 | 0.818 |
| F2 | 0.523 |
| F4 | 0.455 |
| F7 | 0.409 |
| F8 | 0.568 |
| F9 | 0.409 |
| F10 | 0.591 |

Simulated share of separated pairs at this coverage: 0.0314 (0.0032 to 0.0698).

## Uncertainty and sensitivity (share of baseline separated pairs kept)

| Variant | all projects | T1 and T2 |
|---|---|---|
| baseline_separated_pairs | 23 | 2 |
| baseline_share | 0.0243 | 0.0167 |
| weights_kept_in_all_draws | 0.087 | 0.0 |
| weights_mean_kept | 0.7688 | 0.698 |
| rule_lexicographic_kept | 1.0 | 1.0 |
| rule_cap_kept | 1.0 | 1.0 |
| drop_F1_kept | 0.4348 | 0.0 |
| drop_F2_kept | 0.9565 | 0.5 |
| drop_F4_kept | 0.913 | 1.0 |
| drop_F7_kept | 0.8696 | 1.0 |
| drop_F8_kept | 0.3913 | 0.0 |
| drop_F9_kept | 0.7826 | 1.0 |
| drop_F10_kept | 0.6957 | 1.0 |
| admissible_view_kept | 0.0 | 0.0 |
| core4_only_kept | 0.2609 | 0.5 |
| no_route_D_kept | 1.0 | 1.0 |
| with_leaning_kept | 1.0 | 1.0 |
| no_inferred_kept | 1.0 | 1.0 |

## Known cases

| Case | Project | Cell | expected | observed | status |
|---|---|---|---|---|---|
| MK01 | MOCK34 | F1 | yes | yes | hit |
| MK02 | MOCK30 | F7 | no | no | hit |
| MK03 | MOCK14 | F2 | yes | yes | hit |
| MK04 | MOCK37 | F3 | via_psp | undetermined | undetermined |
| MK05 | MOCK22 | F1 | yes | undetermined | undetermined |
| MK06 | MOCK39 | F4 | no | yes | miss |

## External measures (validity, not an association claim)

| Measure | role | expected sign | n | rho | 95 % interval |
|---|---|---|---|---|---|
| mock_convergent | convergent | + | 2 | None | None |
| mock_discriminant | discriminant | 0 | 2 | None | None |

## Privacy talk against commitments (six aspects with a matching F-cell)

| (project, aspect) pairs | count |
|---|---|
| talk_and_committed | 36 |
| talk_stated_not_decided | 82 |
| talk_no_commitment | 69 |
| talk_uncertain | 19 |
| silent_committed | 12 |
| silent_stated | 24 |
| silent_none | 16 |
| silent_uncertain | 6 |

H_TC1_admissible, lower bound: projects with talk share above commitment share 42, below 0, equal 2; one-sided sign test p = 0.0; mean difference 0.5038 (95 % [0.4356, 0.5682]).

H_TC1_admissible, upper bound: projects with talk share above commitment share 44, below 0, equal 0; one-sided sign test p = 0.0; mean difference 0.5985 (95 % [0.5341, 0.6667]).

H_TC2_stated, lower bound: projects with talk share above commitment share 22, below 9, equal 13; one-sided sign test p = 0.014725; mean difference 0.1023 (95 % [0.0341, 0.1742]).

H_TC2_stated, upper bound: projects with talk share above commitment share 29, below 4, equal 11; one-sided sign test p = 5e-06; mean difference 0.197 (95 % [0.125, 0.2727]).

## Index per project

| Project | Tier | F1 | stated (7 cells) | admissible | four cells | F3 (category) | rungs F1-F2-F4-F7-F8-F9-F10 | decided of 7 |
|---|---|---|---|---|---|---|---|---|
| MOCK01 | T3 | undetermined | [0.4286, 1.0] | [0.1429, 1.0] | [0.5, 1.0] | undetermined | 0-2-1-0-0-0-3 | 1 |
| MOCK02 | T3 | protective | [0.1429, 0.5714] | [0.0, 1.0] | [0.25, 0.75] | via_cb | 2-0-0-1-0-1-1 | 0 |
| MOCK03 | T3 | protective | [0.2857, 0.8571] | [0.0, 1.0] | [0.5, 1.0] | none_stated | 2-0-2-0-0-0-1 | 0 |
| MOCK04 | T3 | undetermined | [0.2857, 0.8571] | [0.1429, 1.0] | [0.25, 1.0] | undetermined | 0-0-0-1-0-1-4 | 1 |
| MOCK05 | T3 | undetermined | [0.1429, 0.7143] | [0.1429, 1.0] | [0.0, 0.75] | via_psp | 0-0-1-0-1-0-4 | 1 |
| MOCK06 | T2 | protective | [0.5714, 0.8571] | [0.0, 1.0] | [0.5, 0.75] | undetermined | 2-0-1-1-2-0-1 | 0 |
| MOCK07 | T3 | protective | [0.1429, 0.5714] | [0.0, 0.7143] | [0.25, 0.75] | undetermined | 1-3-0-0-0-3-2 | 2 |
| MOCK08 | T3 | not_protective | [0.1429, 0.5714] | [0.0, 0.8571] | [0.0, 0.5] | undetermined | 3-1-0-0-1-0-1 | 1 |
| MOCK09 | T1 | not_protective | [0.0, 0.7143] | [0.0, 1.0] | [0.0, 0.5] | undetermined | 2-0-0-1-0-0-0 | 0 |
| MOCK10 | T3 | not_protective | [0.2857, 0.5714] | [0.0, 1.0] | [0.0, 0.25] | undetermined | 1-1-1-0-2-0-1 | 0 |
| MOCK11 | T2 | not_protective | [0.4286, 0.7143] | [0.1429, 0.8571] | [0.5, 0.75] | undetermined | 3-1-3-0-2-0-2 | 2 |
| MOCK12 | T3 | protective | [0.4286, 0.7143] | [0.2857, 0.8571] | [0.25, 0.75] | via_both | 4-3-0-0-1-3-1 | 3 |
| MOCK13 | T2 | protective | [0.1429, 0.5714] | [0.1429, 1.0] | [0.25, 0.75] | undetermined | 3-1-0-0-1-1-0 | 1 |
| MOCK14 | T3 | protective | [0.4286, 0.7143] | [0.0, 1.0] | [0.5, 0.75] | undetermined | 1-1-2-0-0-1-2 | 0 |
| MOCK15 | T3 | not_protective | [0.1429, 0.4286] | [0.1429, 0.8571] | [0.25, 0.5] | undetermined | 1-4-3-0-1-2-0 | 2 |
| MOCK16 | T3 | undetermined | [0.2857, 0.8571] | [0.0, 1.0] | [0.0, 0.75] | undetermined | 0-0-1-0-0-1-2 | 0 |
| MOCK17 | T2 | protective | [0.1429, 0.5714] | [0.0, 0.8571] | [0.25, 0.75] | undetermined | 1-2-0-0-0-4-2 | 1 |
| MOCK18 | T3 | not_protective | [0.0, 0.5714] | [0.0, 0.8571] | [0.0, 0.5] | undetermined | 4-0-0-1-0-1-0 | 1 |
| MOCK19 | T3 | protective | [0.5714, 0.8571] | [0.1429, 1.0] | [0.75, 1.0] | via_cb | 2-0-1-3-0-1-1 | 1 |
| MOCK20 | T3 | not_protective | [0.4286, 0.7143] | [0.1429, 1.0] | [0.25, 0.5] | undetermined | 1-1-1-0-3-0-1 | 1 |
| MOCK21 | T3 | not_protective | [0.1429, 0.7143] | [0.1429, 1.0] | [0.25, 0.5] | none_stated | 2-0-1-3-0-0-0 | 1 |
| MOCK22 | T3 | undetermined | [0.1429, 1.0] | [0.0, 1.0] | [0.0, 1.0] | via_both | 0-0-0-0-0-0-1 | 0 |
| MOCK23 | T3 | not_protective | [0.4286, 0.8571] | [0.1429, 0.8571] | [0.5, 0.75] | via_psp | 4-1-0-4-1-0-0 | 2 |
| MOCK24 | T2 | undetermined | [0.1429, 1.0] | [0.0, 1.0] | [0.0, 1.0] | undetermined | 0-0-0-0-2-0-0 | 0 |
| MOCK25 | T2 | not_protective | [0.4286, 0.7143] | [0.1429, 0.8571] | [0.5, 0.75] | undetermined | 4-3-0-1-2-0-2 | 2 |
| MOCK26 | T1 | not_protective | [0.1429, 0.8571] | [0.0, 0.8571] | [0.0, 0.75] | via_both | 3-0-0-0-0-2-0 | 1 |
| MOCK27 | T3 | not_protective | [0.2857, 0.8571] | [0.2857, 1.0] | [0.25, 0.75] | none_stated | 1-3-0-0-0-0-3 | 2 |
| MOCK28 | T3 | protective | [0.4286, 1.0] | [0.0, 1.0] | [0.25, 1.0] | none_stated | 1-0-0-0-1-0-1 | 0 |
| MOCK29 | T3 | protective | [0.1429, 0.7143] | [0.0, 0.8571] | [0.25, 0.75] | none_stated | 2-0-1-0-0-3-0 | 1 |
| MOCK30 | T1 | undetermined | [0.0, 0.7143] | [0.0, 1.0] | [0.0, 0.5] | undetermined | 0-1-0-2-0-0-0 | 0 |
| MOCK31 | T3 | protective | [0.1429, 0.8571] | [0.0, 0.8571] | [0.25, 1.0] | via_both | 2-0-0-0-3-0-0 | 1 |
| MOCK32 | T1 | not_protective | [0.1429, 0.4286] | [0.0, 1.0] | [0.25, 0.5] | none_stated | 1-1-1-0-1-1-0 | 0 |
| MOCK33 | T2 | protective | [0.4286, 0.7143] | [0.1429, 0.7143] | [0.5, 1.0] | undetermined | 3-0-0-1-4-4-1 | 3 |
| MOCK34 | T3 | not_protective | [0.1429, 0.8571] | [0.1429, 0.8571] | [0.0, 0.75] | none_stated | 3-0-0-0-4-0-0 | 2 |
| MOCK35 | T3 | protective | [0.5714, 0.7143] | [0.2857, 1.0] | [0.5, 0.75] | none_stated | 4-0-2-1-1-4-2 | 2 |
| MOCK36 | T3 | protective | [0.2857, 0.7143] | [0.1429, 1.0] | [0.5, 0.75] | undetermined | 4-1-1-0-2-0-0 | 1 |
| MOCK37 | T1 | undetermined | [0.1429, 0.5714] | [0.0, 0.8571] | [0.25, 0.5] | undetermined | 0-1-1-3-0-1-0 | 1 |
| MOCK38 | T3 | protective | [0.1429, 0.5714] | [0.1429, 0.7143] | [0.25, 0.5] | via_cb | 3-3-0-1-0-0-4 | 3 |
| MOCK39 | T2 | not_protective | [0.4286, 0.7143] | [0.0, 0.8571] | [0.25, 0.5] | none_stated | 1-0-1-4-1-0-1 | 1 |
| MOCK40 | T1 | protective | [0.5714, 1.0] | [0.0, 1.0] | [0.75, 1.0] | via_both | 1-2-0-1-1-0-0 | 0 |
| MOCK41 | T1 | not_protective | [0.1429, 0.7143] | [0.1429, 1.0] | [0.0, 0.5] | via_cb | 1-0-0-1-3-0-0 | 1 |
| MOCK42 | T3 | not_protective | [0.2857, 0.2857] | [0.1429, 0.7143] | [0.5, 0.5] | undetermined | 2-1-4-2-3-2-4 | 3 |
| MOCK43 | T1 | not_protective | [0.1429, 0.5714] | [0.1429, 0.8571] | [0.25, 0.5] | via_both | 1-4-4-0-1-0-0 | 2 |
| MOCK44 | T3 | protective | [0.4286, 0.8571] | [0.0, 1.0] | [0.25, 0.75] | via_both | 1-1-0-0-1-0-1 | 0 |
