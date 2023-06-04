import pandas
import streamlit as st
import altair as alt
import numpy as np
import main

# remove sidebar
st.set_page_config(initial_sidebar_state="collapsed",
                   layout="wide")

# get data
source = pandas.read_csv("Zappi_output.csv")
source2 = pandas.read_csv("PV-Anlage.csv")
source2 = source2.replace("--", "0")
source2["Ertrag in kWh"] = source2["Ertrag in kWh"].astype(float)
source2["Ertrag in kWh"] = source2["Ertrag in kWh"] / 4000

for num, row in source2.iterrows():
    y = num * 15
    if y < len(source) - 15:
        for x in range(0, 15):
            source.loc[y + x, "Ertrag in kWh"] = row["Ertrag in kWh"] / 15

source.index = source["Datum"]

with st.sidebar:
    st.header("Energiebilanzierung Becker")
    date = st.date_input("Betrachtungstag")
    st.write(date)
    st.button("Lade neue Daten", on_click=main.create_new_zappi_data(date))

source3 = source.copy()
source3 = source3.drop(columns="Datum")
for i in source3.columns:
    source3[i] = source3[i].astype(float)
    
table = source3.sum(axis=0)
for column in ["Netzfrequenz in Hz", "Spannung Phase 1 in V"]:
    table[column] /= len(source3[column])

# Create list with headers
summary_headers = list(table.keys())
# add the energy system costs
cost1, cost2, cost3, cost4 = st.columns(4)
cost1.metric(label=summary_headers[5], value="{:,.2f}".format(float(round(
    table[summary_headers[5]], 2))))
cost2.metric(label=summary_headers[4], value="{:,.2f}".format(float(round(
    table[summary_headers[4]], 2))))
cost3.metric(label=summary_headers[11], value="{:,.4f}".format(float(round(
    table[summary_headers[11]], 4))))
cost4.metric(label=summary_headers[10], value="{:,.4f}".format(float(round(
    table[summary_headers[10]], 4))))


chart1, chart2, chart3, chart4 = st.columns(4)
with chart1:
    # plot net frequency
    st.altair_chart(alt.Chart(source).mark_line().encode(
        x=alt.X('Datum', axis=alt.Axis()),
        y=alt.Y('Netzfrequenz in Hz',
                scale=alt.Scale(domain=[np.min(source["Netzfrequenz in Hz"]),
                                        np.max(source["Netzfrequenz in Hz"])]))
    ), use_container_width=True)

with chart2:
    st.altair_chart(alt.Chart(source).mark_line().encode(
        x=alt.X('Datum', axis=alt.Axis()),
        y=alt.Y('Spannung Phase 1 in V',
                scale=alt.Scale(domain=[np.min(source["Spannung Phase 1 in V"]),
                                        np.max(source["Spannung Phase 1 in V"])]
                                ))), use_container_width=True)
with chart3:
    st.altair_chart(alt.Chart(source).mark_line().encode(
            x=alt.X('Datum', axis=alt.Axis()),
            y=alt.Y('Import in kWh',
                    scale=alt.Scale(domain=[np.min(source["Import in kWh"]),
                                            np.max(source["Import in kWh"])]
                                    ))), use_container_width=True)
    
with chart4:
    base = alt.Chart(source).transform_fold(["Export in kWh",
                                             "Ertrag in kWh"],
                                            as_=['Plot', 'Energie']
                                            ).mark_line().encode(
            x='Datum',
            y='Energie:Q',
            color='Plot:N'
    )
    st.altair_chart(base, use_container_width=True)
    
for column in ["Netzfrequenz in Hz", "Spannung Phase 1 in V"]:
    table[column] /= len(source3[column])

# add the energy system costs
cost5, cost6, cost7, cost8 = st.columns(4)
cost5.metric(label=summary_headers[1], value="{:,.4f}".format(float(round(
    table[summary_headers[1]], 4))))
cost6.metric(label=summary_headers[2], value="{:,.4f}".format(float(round(
    table[summary_headers[2]], 4))))
cost7.metric(label=summary_headers[3], value="{:,.4f}".format(float(round(
    table[summary_headers[3]], 4))))
cost8.metric(label=summary_headers[11], value="{:,.4f}".format(float(round(
    table[summary_headers[11]], 4))))


chart5, chart6, chart7, chart8 = st.columns(4)
with chart5:
    # plot net frequency
    st.altair_chart(alt.Chart(source).mark_line().encode(
            x=alt.X('Datum', axis=alt.Axis()),
            y=alt.Y('bezogene Energie Phase 1 in kWh',
                    scale=alt.Scale(
                        domain=[np.min(source["Import in kWh"]),
                                np.max(source["Import in kWh"])]))
    ), use_container_width=True)

with chart6:
    st.altair_chart(alt.Chart(source).mark_line().encode(
            x=alt.X('Datum', axis=alt.Axis()),
            y=alt.Y('bezogene Energie Phase 2 in kWh',
                    scale=alt.Scale(
                        domain=[np.min(source["Import in kWh"]),
                                np.max(source["Import in kWh"])]
                        ))), use_container_width=True)
    
with chart7:
    st.altair_chart(alt.Chart(source).mark_line().encode(
            x=alt.X('Datum', axis=alt.Axis()),
            y=alt.Y('bezogene Energie Phase 3 in kWh',
                    scale=alt.Scale(domain=[np.min(source["Import in kWh"]),
                                            np.max(source["Import in kWh"])]
                                    ))), use_container_width=True)

with chart8:
    st.altair_chart(alt.Chart(source).mark_line().encode(
            x=alt.X('Datum', axis=alt.Axis()),
            y=alt.Y('Import in kWh',
                    scale=alt.Scale(
                        domain=[np.min(source["Import in kWh"]),
                                np.max(source["Import in kWh"])]
                        ))), use_container_width=True)

