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

with st.sidebar:
    st.header("Energiebilanzierung Becker")
    date = st.date_input("Betrachtungstag")
    st.write(date)
    st.button("Lade neue Daten", on_click=main.create_new_zappi_data(date))

source3 = source.drop("Datum")
for i in source3.columns():
    source3[i] = source3[i].astype(float)
table = source.sum(axis=1)
st.table(data=table)

# plot net frequency
frequency_chart = alt.Chart(source).mark_line().encode(
    x=alt.X('Datum', axis=alt.Axis(labelAngle=-20)),
    y=alt.Y('Netzfrequenz in Hz',
            scale=alt.Scale(domain=[np.min(source["Netzfrequenz in Hz"]),
                                    np.max(source["Netzfrequenz in Hz"])]))
).properties(width=500)

voltage_chart = alt.Chart(source).mark_line().encode(
    x=alt.X('Datum', axis=alt.Axis(labelAngle=-20)),
    y=alt.Y('Spannung Phase 1 in V',
            scale=alt.Scale(domain=[np.min(source["Spannung Phase 1 in V"]),
                                    np.max(source["Spannung Phase 1 in V"])]
                            ))).properties(width=500)
    
st.altair_chart(frequency_chart | voltage_chart, use_container_width=True)

st.altair_chart(
    alt.Chart(source).mark_line().encode(
        x=alt.X('Datum', axis=alt.Axis(labelAngle=-20)),
        y=alt.Y('Import',
                scale=alt.Scale(domain=[np.min(source["Import"]),
                                        np.max(source["Import"])]
                                ))
    ).properties(width="container"),
    use_container_width=True)
    

st.altair_chart(
        alt.Chart(source2).mark_line().encode(
                x=alt.X('Datum', axis=alt.Axis(labelAngle=-20)),
                y=alt.Y('Ertrag in kWh',
                        scale=alt.Scale(
                            domain=[np.min(source2["Ertrag in kWh"]),
                                    np.max(source2["Ertrag in kWh"])]
                            ))
        ).properties(width="container"),
        use_container_width=True)


plt1 = alt.Chart(source).mark_line().encode(
        x=alt.X('Datum', axis=alt.Axis(labelAngle=-20)),
        y=alt.Y('Diff_Import',
                scale=alt.Scale(domain=[np.min(source["Diff_Import"]),
                                        np.max(source["Diff_Import"])]
                                ))
    )
plt2 = alt.Chart(source).mark_line().encode(
            x=alt.X('Datum', axis=alt.Axis(labelAngle=-20)),
            y=alt.Y('Diff_Export',
                    scale=alt.Scale(domain=[np.min(source["Diff_Export"]),
                                            np.max(source["Diff_Export"])]
                                    ))
    )

st.altair_chart(plt1 + plt2, use_container_width=True)

bar = alt.Chart(source).mark_area(opacity=0.7, interpolate='cardinal').encode(
        x=alt.X('Datum', axis=alt.Axis(title='Datum')),
        y=alt.Y('pos. Leistung Phase 2 in kW'),
        tooltip=['Datum', alt.Tooltip('pos. Leistung Phase 2 in kW')],
        fill=alt.Fill(field='Type', title='Courbe : '))

bar_original = alt.Chart(source).mark_line(color='red',
                                           interpolate='cardinal',
                                           opacity=0.7).encode(
        x=alt.X('Datum', axis=alt.Axis(title='Datum')),
        y=alt.Y('Energieimport in kWh'),
        tooltip=['Datum', alt.Tooltip('Energieimport in kWh')],
        opacity=alt.Opacity(field='Type', title=None))

st.altair_chart(bar + bar_original, use_container_width=True)

#st.area_chart(data=source,
#              x="Datum",
#              y=["Leistung Phase 1 in kW",
#                 "Leistung Phase 2 in kW",
#                 "Leistung Phase 3 in kW"],
#              )
