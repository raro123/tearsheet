Few adjustments in category deepdive. The order of charts:
 - Key KPIs
 - Equity curve
 - Detailed metric table (collapsible)
 - Rolling metrics chart
 - Annual return table (collapsible)
 - correlation metric (collapsible)
 - metric bubble and performance metric grid (collapsible)

 

Updates in fund deepdive:
 - Performance metrics - move it from a column to a row (place it below the drawdown chart). Separate return metrics, risk metrics & ration metrics as divs in a single row.Benchmark relative - remove for now, we will use it later
- 
 - ability to add another fund in the comparison (in addition to benchmark). By default no other fund, but we can expand the selection to add another fund to the comparison. This additional fund should appear in all the visuals and in the metric tables

 - the optional selector should also have scheme type and scheme category filters as well similar to fund selector. So have 3 sections Fund Selection, Benchmark Selection, Add Fund to Comparison (optional) and other remaining selections.

 I am debating weather to add apply selections button to the filter pane for fund deepdive tab. This would enable the user to make all selections and then press the button. so that app doesn't refresh too often. What are your thoughts ?

 on fund deepdive
  - add a scatter plot which plots the monthjly benchmark return on x axis and monthly fund return on y axis. If comp fund is selected add that as well in scatter plot at Y axis. Add trendline Fund vs BM , Comp Vs BM a . Also add the compariosn metrics in a table next to the plot (r2, corr, Beta etc.). Add it before the monthly return tables.
  - monthly return table
    - make it collapsible
     - remove formatting on all cells, instead just higlight cells which are outliers(2sdev away)
 -
