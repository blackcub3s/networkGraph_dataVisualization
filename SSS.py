

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import networkx as nx
import time

# Load the Excel file
InvestorsData = pd.read_excel("2. fitxerInversions_parsejatFinal.xlsx")

# -----------------------------------------------------------------------------------------------------



def creaGraf():

    # Create an empty Graph object
    G = nx.Graph()

    #Crea la llista que farem servir al proper document (essencial per poder ajustar l'argument de paritat del proper document)
    ll_investmentInvestor = []
    # Add nodes to the graph
    for index, row in InvestorsData.iterrows():       
        G.add_node(row["Investment"])               #Forecast_Sell_Date=row["Forecast_Sell_Date"])        
        G.add_node(row["Investor_Parsejat"])        
        ll_investmentInvestor += [row["Investment"]]
        ll_investmentInvestor += [row["Investor_Parsejat"]]

    # Add edges to the graph
    for index, row in InvestorsData.iterrows():
        G.add_edge(row["Investment"], row["Investor_Parsejat"],Forecast_Sell_Date=row["Forecast_Sell_Date"], Buy_Date=row["Buy_Date"], Time_Difference=row["Time_Difference"]) #, Forecast_Sell_Date=row["Forecast_Sell_Date"], Time_Difference=row["Time_Difference"], sentence=row["Sentence"])

    # Print some information about the graph
    print("###########################################")
    print(f"Number of nodes: {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")
    print("###########################################")

    # -----------------------------------------------------------------------------------------------------

    minMax_Forecast_Sell_Date = (InvestorsData["Forecast_Sell_Date"].min(), InvestorsData["Forecast_Sell_Date"].max())

    # Get the node positions
    dic_nodePosicio = nx.spring_layout(G) #ES UN DICCIONARI "NODE" : "array([-0.13076184,  0.43108399]". Cal desempaquetar-ho"
    return G, dic_nodePosicio, ll_investmentInvestor, InvestorsData["Investor_Parsejat"], InvestorsData["Time_Difference"], minMax_Forecast_Sell_Date