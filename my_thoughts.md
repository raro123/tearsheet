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

Rolling analysis:
 - lets have a 2*2 subplots:
  - chart contains - rolling return, volatility, Beta against the benchmark and correlation against the benchmark. all except beta also have the comp fund optionality
  - radio button for 6m, 1,3,5 years. rolling option based on simple avg and well as exponential weight (corresponding to 6m,1, 3, 5)

  I need a viz which also shows the progression of Rs 100 invested per month (SIP) in the fund/benchmark/comp fund (if selected). It should show the irr of investment as text in the chart. I am unsure about its placement. May be in subplot as first chart above cumulative return. What are your thoughts

    I need a table which also shows the progression of Rs 100 invested per month (SIP) at start of month in the fund/benchmark/comp fund (if selected). columns will be Year/month, amt invested,amt value in fund, amount value in benchmark and amount value in comp fund, second last row has grand total and last row has irr for invetsments. It should show the irr of investment at bottom.Place it at bottom for now


    Some last touches:
    1. in the main heading fund name vs benchmark vs Comp F. The names should be colored in the color used for each of them in charts
    2. Move Log scale toggle for cumulative return to sidebar
    3. Align the color and linestyle used for benchmark in sip (gray + ---) and cumulative return chart + others
    4. legend appears twice now in performance section once in sip once in cum return chart. keep legend only once
    5. header on sip chart should be similar to charts below it. 



    Now fund invetigator in iddependent.I want to clear up the project directory. Organise it so that fund investigator is the focus. Rest all can be put to work in progress as that will not go to production. 
    We will also need to update the filterpane - to remove the non-live tabs. Remove performance cache metrics as we prepare for release.