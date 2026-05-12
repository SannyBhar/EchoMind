# Final Report LaTeX Snippets

These snippets assume the paper is built from the repository root and that
`artifacts/report/` is available alongside the manuscript sources.

## Figure 1

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{artifacts/report/final_figures/figure_1_pipeline_overview.png}
  \caption{EchoMind frozen publication pipeline. Cue variants are planned deterministically, rendered into local artifacts, passed through a text-first TRIBE smoke path, scored with decomposed submetrics, and aggregated into grouped comparison outputs. Only \texttt{TEXT\_ONLY} cues currently traverse the TRIBE stub.}
  \label{fig:pipeline-overview}
\end{figure}
```

## Figure 2

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{artifacts/report/final_figures/figure_2_grouped_composite_scores.png}
  \caption{Grouped average composite scores across the three comparison dimensions in the frozen 12-memory run. Confidence labels distinguish the cleaner framing contrast from dimensions more constrained by the current simulation path. Delivery-mode values remain limited because only \texttt{TEXT\_ONLY} reaches the stub.}
  \label{fig:grouped-composite}
\end{figure}
```

## Figure 3

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{artifacts/report/final_figures/figure_3_personalized_vs_generic.png}
  \caption{Per-memory comparison of generic and personalized cue groups across the 12 synthetic memories. The apparent generic advantage in this frozen run reflects deterministic stub-text variance and should be interpreted as an input contrast rather than a recall-quality claim.}
  \label{fig:personalized-vs-generic}
\end{figure}
```

## Figure 4

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=0.82\linewidth]{artifacts/report/final_figures/figure_4_warm_vs_neutral.png}
  \caption{Warm versus neutral framing in the frozen 12-memory run. Bars show mean per-memory composite score; error bars show $\pm 1$ SD across memories. This is the cleanest current contrast, but it remains simulation-only.}
  \label{fig:warm-vs-neutral}
\end{figure}
```

## Figure 5

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=0.88\linewidth]{artifacts/report/final_figures/figure_5_delivery_mode_limited.png}
  \caption{Delivery-mode comparison under the current text-first smoke path. \texttt{TEXT\_ONLY} traverses the TRIBE stub, while narration and slideshow values are heuristic-only constants. This figure is included for completeness and should not be interpreted as a modality preference result.}
  \label{fig:delivery-mode-limited}
\end{figure}
```

## Table 1

```latex
\begin{table}[t]
  \centering
  \caption{Representative ranked cue breakdown for \texttt{demo-university-001}.}
  \label{tab:representative-ranked-cues}
  % Source: artifacts/report/final_tables/table_1_representative_ranked_cues.csv
\end{table}
```

## Table 2

```latex
\begin{table}[t]
  \centering
  \caption{Compact summary of the three comparison dimensions, including interpretation labels, confidence, and required limitation notes.}
  \label{tab:summary-findings}
  % Source: artifacts/report/final_tables/table_2_summary_findings.csv
\end{table}
```
