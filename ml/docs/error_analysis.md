# Error Analysis

This document is intentionally a placeholder for the first evaluation pass.

## False Positives

- Review model predictions that trigger on generic legal language without matching the target clause scope.
- Look for ambiguous phrases such as "subject to" and "as applicable" that can inflate confidence without true clause alignment.

## False Negatives

- Catch clauses with unusual wording, legacy legal phrasing, or partially omitted language.
- Review edge cases where clause spans are split across page breaks or sentences.

## Next Steps

- Document common failure patterns from a labeled validation set.
- Compare predicted labels against manual adjudication.
- Add targeted examples for borderline legal wording before the next sprint.
