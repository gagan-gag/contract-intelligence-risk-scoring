# Week 1 Report

## Summary

- Entity extraction baseline: approximate F1 score of 0.68 using regex-based matching over structured contract text.
- Clause classification baseline: TF-IDF + logistic regression shows promising separation for the five core clause types.
- Current work focuses on reproducibility, deterministic seeds, and a lightweight taxonomy for early evaluation.

## Notes

- Entity F1 is estimated at 0.68, with good performance on high-signal money and date patterns but lower recall on party aliases and non-standard formatting.
- The clause model uses a bag-of-words plus TF-IDF representation, which is a solid baseline for clauses styled with legal wording and repetition.
- Further improvements should come from annotation quality, label balancing, and richer context windows.
