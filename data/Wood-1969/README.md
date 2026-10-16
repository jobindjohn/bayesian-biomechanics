# Wood (1969): tensile tests on human cranial bone

## Source

Tensile tests on human cranial bone from Jack Leslie Wood's doctoral thesis:

* Wood, J. L. (1969). *Mechanical properties of human cranial bone in tension* [Doctoral
  dissertation, University of Michigan].
* Published as Wood, J. L. (1971). Dynamic response of human cranial bone. *Journal of
  Biomechanics, 4*(1), 1–12. <https://doi.org/10.1016/0021-9290(71)90010-8>

The test table (sheet `Blad1` of `Wood-1969.xlsx`, not included here) was typed in by hand from the
source, and its correlation matrix matches the published one. The two VA63 stress–strain curves
(`va_63_data_new.csv`, not included) were digitised from a figure. These processed tables were made
from those two files on 2026-10-16, in a separate analysis project.

## Files

Each table is stored twice, with the same rows and columns: as Parquet (`*.parquet`, with column
types) and as CSV (`*.csv`). Lessons that run in the browser read the CSV, because Pyodide's polars
cannot read Parquet without pyarrow. In the CSV, the `category` columns are plain text. The CSV
files are written from the Parquet files, so regenerate them whenever the Parquet files change.

## Licence

These tables are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Please
cite Wood (1969) when you use them.

## Cleaning steps

1. Read sheet `Blad1` of `Wood-1969.xlsx`; rename columns to snake_case.
2. Convert to SI: ksi → MPa and 10⁶ psi → GPa (× 6.894757), % → engineering strain (/ 100),
   in·lbf/in³ → MPa (× 0.006894757). Add `failure_strain_true = log1p(failure_strain)` and
   `log10_strain_rate`.
3. `donor_id` from the specimen ID; `part` split into `region` and `side`; layer codes spelled out
   (`OT` outer table, `IT` inner table, `D` diploë; two tests without a code are `unknown`).
4. Rows without a breaking stress are low-rate modulus-only tests (`test_type = modulus_only`); the
   same coupons appear again as failure tests. `test_id` = specimen + layer (+ `-E`) is unique.
5. Curves: the two-row header of the CSV parsed into `curve_id`, the padding dropped, the points
   sorted by strain and converted to SI. The curves start just above the origin (no (0, 0) point).
6. Validated in the notebook: IDs and codes well formed; one sex, age and cause of death per donor;
   for all 120 complete tests failure strain ≥ σ/E and ½σε ≤ SED ≤ σε (confirms the units); each
   VA63 curve ends within 2.2 % of the mean failure point of the three VA63 outer-table tests at that
   rate and its area is within 1.9 % of their mean fracture energy, so the curves are the average
   curves of those tests.

## Known quirks

* 17 failure tests miss at least one property (no strain or modulus result, or no strain rate):
  the UM29 outer-table tests, VA25-4, VA27-1/-2, all eight diploë tests (no strain rate or fracture
  energy), and the VA65 coupons with very low breaking stress (VA65-2 outer and inner table, VA65-6,
  VA65-7; probably damaged).
* VA65-6 and VA65-7 have no layer recorded.
* Only 4 of 29 donors are female; most tests are parietal outer table.
* Strain rate spans six decades (0.0003–130 /s) in four loose groups (≈0.0003–0.02, ≈0.07–0.4,
  ≈1.6–5 and ≈27–130 /s); the lowest rates (≤ 0.0015 /s) are mostly modulus-only tests.

## Tables

### `skull_tension_tests.parquet`

One row per test, all strain rates, layers and test types. 142 rows.

| Column | dtype | Unit | Description |
|---|---|---|---|
| `test_id` | str |  | Unique test ID: specimen, layer code (`OT`, `IT`, `D`, or `X` if not recorded), and `-E` for modulus-only tests |
| `donor_id` | str |  | Donor: the specimen ID up to the dash (`UM` / `VA` + number) |
| `specimen` | str |  | Specimen ID as in the source (`Speciment`); reused across layers and for repeat loading |
| `sheet_row` | int64 |  | Row in `Wood-1969.xlsx` (sheet `Blad1`), for tracing back |
| `sex` | str |  | `F` or `M` |
| `age_yr` | int64 | yr | Age at death |
| `cause_of_death` | str |  | As in the source; `Canser` corrected to `Cancer` |
| `part` | str |  | Skull part code from the source: F/P/T (frontal, parietal, temporal) + L/R |
| `region` | category |  | `frontal`, `parietal` or `temporal` |
| `side` | str |  | `L` or `R` |
| `layer` | category |  | `outer table`, `inner table`, `diploe`, or `unknown` (not recorded) |
| `test_type` | str |  | `failure`, or `modulus_only` (low-rate, non-destructive modulus test; same coupon later tested to failure) |
| `strain_rate_per_s` | float64 | 1/s | Strain rate, as tabulated |
| `log10_strain_rate` | float64 |  | log10 of `strain_rate_per_s` |
| `modulus_gpa` | float64 | GPa | Young's modulus (source: 10⁶ psi × 6.894757) |
| `failure_stress_mpa` | float64 | MPa | Breaking stress (source: ksi × 6.894757) |
| `failure_strain` | float64 | - | Breaking strain, engineering (source: % / 100) |
| `sed_total_mpa` | float64 | MPa = MJ/m³ | Fracture energy, area under the stress–strain curve (source: in·lbf/in³ × 0.006894757) |
| `failure_strain_true` | float64 | - | True failure strain, log1p(failure_strain) |
| `complete` | bool |  | All four properties (modulus, stress, strain, SED) present |

### `skull_tension_donors.parquet`

One row per donor. 29 rows.

| Column | dtype | Unit | Description |
|---|---|---|---|
| `donor_id` | str |  | Donor: the specimen ID up to the dash (`UM` / `VA` + number) |
| `sex` | str |  | `F` or `M` |
| `age_yr` | int64 | yr | Age at death |
| `cause_of_death` | str |  | As in the source; `Canser` corrected to `Cancer` |
| `parts` | str |  | Skull parts tested, joined by `;` |
| `n_tests` | int64 |  | Number of tests of the donor (all types) |
| `n_complete` | int64 |  | Number of complete tests of the donor |

### `skull_tension_curves.parquet`

The two digitised VA63 stress–strain curves, long format, sorted by strain. 78 rows.

| Column | dtype | Unit | Description |
|---|---|---|---|
| `curve_id` | str |  | `VA63-` + the curve name in the CSV |
| `donor_id` | str |  | Donor: the specimen ID up to the dash (`UM` / `VA` + number) |
| `nominal_rate_per_s` | float64 | 1/s | Strain rate read from the curve name (`sec0007` → 0.007, `sec110` → 110) |
| `digitised_order` | int64 |  | Row of the point in the CSV (0-based); the points were not digitised in order |
| `strain` | float64 | - | Engineering strain (source: % / 100) |
| `stress_mpa` | float64 | MPa | Engineering stress (source: ksi × 6.894757) |
