The first runner stopped while serializing a NumPy boolean after the initial
mirror K=1 reference. No method selection or numerical algorithm failed.
The input plan is unchanged. The corrected runner explicitly converts NumPy
scalars to native JSON types and writes a new `dictionary_comparison_v2`
directory; this failed attempt and its source snapshot remain preserved.
