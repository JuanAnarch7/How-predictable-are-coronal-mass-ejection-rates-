# Manuscript

LaTeX source of the paper (to be written in stage F4).

Rule: no result is typed by hand. Every number quoted in the text is a macro defined in
`generated/numbers.tex`, which `scripts/build_dataset.py` (and later the analysis scripts)
generate from `results/numbers.json`. Include it in the preamble:

```latex
\input{generated/numbers.tex}
...
The catalog contains \NEventsTotal{} CMEs between \FirstEventDate{} and \LastEventDate{}.
```

Do not edit `generated/` by hand; rebuild instead.
