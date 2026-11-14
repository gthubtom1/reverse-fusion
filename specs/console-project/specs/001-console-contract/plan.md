# Implementation plan

1. Freeze the source reference and Evidence pointer in the original case.
2. Implement the candidate through the bounded builder contract.
3. Run the independent evaluator against normal and error variants.
4. Append the result and cleanup status to the case handoff.

The plan keeps specification compliance, behavior comparison and independent
runtime acceptance as separate checks.
