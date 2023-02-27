import os
from __main__grafGuay import crea_grafic
import time

def perAnysForecast_Sell_Date(ll_punts_seleccionats_filtre, d_noms_nodes, edge, informacioFiltre):
    """ 
    ARGUMENTS: - ll_punts_seleccionats_filtre: Una llista que es o be buida o bé conte punts que es van afegints al filtre en funcio de les propietats demanades.
               - d_noms_nodes: fem un diccionari clau valor amb nom del node a l'index que ocupa dins de G.nodes() {"Elon Musk": 1, "Bitcoin": 2} ...
               - edge: una tupla que, desempaquetada, dona lloc a  ---> node1, node2, d_propNode = edge <---: es a dir els noms dels dos nodes units per la 
                    edge i un diccionari amb les pripietats que hi ha definides per a aquesta edge. 
                    Una d'aquestes propietats, "Forecast_Sell_Date", conté el moment per al qual es fa la predicció (sigui emesa per l'Investor, o rebuda 
                    per la tech)
               - informacioFiltre: una llista amb dos enters que contenen els anys entre els quals vols fer el filtre. Si son iguals nomes filtra l'any concret.
    
    RETURNS:    - ll: afegim un o dos enters a la llista ll, que són (i la llista conté) indexos dels nodes que després voldrem filtrar per any.

    """
    node1, node2, d_propNode = edge
    anyInicial, anyFinal = informacioFiltre
    ll = []
    #APLIQUEM EL FILTRE AL NODE CONCRET:
    if anyInicial <= d_propNode["Forecast_Sell_Date"] <= anyFinal:
        #EVALUEM SI ELS NODES JA SON A LA LLISTA FILTRADA (NO CAL REPETIR-LOS)
        if not d_noms_nodes[node1] in ll_punts_seleccionats_filtre:
            ll += [d_noms_nodes[node1]]
        if not d_noms_nodes[node2] in ll_punts_seleccionats_filtre:
            ll += [d_noms_nodes[node2]]
    return ll


def perInvestor(ll_punts_seleccionats_filtre, d_noms_nodes, edge, ll_Investor):
    """ 
    ARGUMENTS: - ll_punts_seleccionats_filtre: Una llista que es o be buida o bé conte punts que es van afegints al filtre en funcio de les propietats demanades.
               - d_noms_nodes: fem un diccionari clau valor amb nom del node a l'index que ocupa dins de G.nodes() {"IBM": 1, Top 3 QC /QIS trends: 2} ...
               - edge: una tupla que, desempaquetada, dona lloc a  ---> node1, node2, d_propNode = edge <---: es a dir els noms dels dos nodes units per la 
                    edge i un diccionari amb les pripietats que hi ha definides per a aquesta edge. 
                    Una d'aquestes propietats, "Forecast_Sell_Date", conté el moment per al qual es fa la predicció (sigui emesa per l'Investor, o rebuda 
                    per la tech)
               - ll_Investor: Una llista amb elements string de l'Investor o Investors que volem filtrar (coincidencia exacta).
    RETURNS:   - ll: afegim un o dos enters a la llista ll, que conté els indexos dels nodes que després voldrem filtrar. En aquest cas
                    Filtrem per Investor pero també filtrem per les technologies incidents a aquest Investor.

    """
    node1, node2, d_propNode = edge
    ll = []
    for str_Investor in ll_Investor:
        #APLIQUEM EL FILTRE AL NODE CONCRET:
        if node1 == str_Investor or node2 == str_Investor:
            #EVALUEM SI ELS NODES JA SON A LA LLISTA FILTRADA (NO CAL REPETIR-LOS)
            if not d_noms_nodes[node1] in ll_punts_seleccionats_filtre:
                ll += [d_noms_nodes[node1]]
            if not d_noms_nodes[node2] in ll_punts_seleccionats_filtre:
                ll += [d_noms_nodes[node2]]
    return ll


def perTime_Difference(ll_punts_seleccionats_filtre, d_noms_nodes, edge, informacioFiltre):
    """ 
    

    """
    node1, node2, d_propNode = edge
    anyInicial, anyFinal = informacioFiltre
    ll = []
    #APLIQUEM EL FILTRE AL NODE CONCRET:
    if anyInicial <= d_propNode["Time_Difference"] <= anyFinal:
        #EVALUEM SI ELS NODES JA SON A LA LLISTA FILTRADA (NO CAL REPETIR-LOS)
        if not d_noms_nodes[node1] in ll_punts_seleccionats_filtre:
            ll += [d_noms_nodes[node1]]
        if not d_noms_nodes[node2] in ll_punts_seleccionats_filtre:
            ll += [d_noms_nodes[node2]]
    return ll



def timelapse_Time_Difference(li,ls):
    """
       NOTA:AQUEST ÉS UN TIPUS DE FILTRE ESPECIAL, PERQUÈ GENERA MÚTLTIPLES FILTRES PER INTERVALS DE Forecast_Sell_Date!
       
       PRE: li, ls son el limit inferior i limit superior d'anys entre els quals vols fer el timelapse.
       POST: produira una imatge per cada any en l'interval tancat [li,ls]. També esborra els json i imatges de timelapses previs.
    """
    #ESBORRO JSONS PREVIS
    if "dic_nodePosicio_guardat.json" in os.listdir():
        os.remove("dic_nodePosicio_guardat.json")
        print("NOTA: eliminem el fitxer json i en crearem un de nou per a tot el timelapse")

    os.chdir("./timelapse_Time_Difference")

    ll_imgs_grafs = os.listdir()
    #ESBORRO IMATGES PREVIES
    if len(ll_imgs_grafs) != 0:
        print("borrem imatges antigues del timelapse previ!")
        time.sleep(3)
        for nomImatge in ll_imgs_grafs:
            os.remove(nomImatge)

    os.chdir("../")

    #GENERO L'ITERADOR PER A FER ELS TIMELAPSES
    i = li
    while i <= ls:
        crea_grafic(fesFiltre = True, tipusFiltre="timelapse_Time_Difference", informacioFiltre=[li,i])
        i = i + 1