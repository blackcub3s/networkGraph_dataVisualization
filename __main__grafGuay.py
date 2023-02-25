    # Hem adaptat aquest codi. --> https://plotly.com/python/network-graphs/ Al fitxer aquí present.


"""
###########################################################################
NOTA: LLEGIU EL readme.txt                                                #
                                                                          #
PRESTEU MOLTÍSSIMA ATENCIÓ A PAS 2.1 I PAS 2.2 PER TENIR CLAR             #
EL FORMAT QUE HAN DE TENIR LES COLUMNES Investor_Parsejat i Investment   #
###########################################################################
"""

import plotly.graph_objects as go
import networkx as nx
import SSS
import filtres
import time
import plotly.io as pio
import json
import os 
import datetime



def converteixAny_a_AnyMesDia(anyet):
    #pre: anyet es un float o un string de la forma "12.257" (conté un nombre real d'anys)
    #post: string de forma A anys, D mesos i d dies
    anyet = float(anyet)
    anyetPartEntera = int(anyet)
    anyetMantisa = anyet - anyetPartEntera 
    mesos = anyetMantisa * 12
    mesosPartEntera = int(mesos)
    mesosMantisa = mesos - mesosPartEntera
    diesPartEntera = int(mesosMantisa * 30.44)
    return "{} year/s, {} month/s and {} day/s".format(anyetPartEntera, mesosPartEntera, diesPartEntera)


def guarda_o_recupera_coordenades(dic_nodePosicio):
    """
    DESCRIPCIÓ: en aquesta funcio permetem processar el dic_nodePosicio per fer-lo apte de guardar. Si no hi es el guarda
                per recuperar-lo després i el retorna inalterat. Si hi és, el recupera i el retorna. Útil per fer un timelapse de gràfics.
    PRE:        el dic_nodePosicio amb les coordenades
    POST:       el diccionari node posicio amb les coordenades que estaven guardades (o amb les mateixes, segons s'escaigui)"""

    #LLEGEIXO EL DICCIONARI DE COORDENADES SI JA HI ES, I SI NO HI ES EN CREO UN DE NOU
    try:
        #CARREGO EL DICT D'UN JSON GUARDAT
        with open("dic_nodePosicio_guardat.json","r") as f:
            dic_nodePosicio = json.load(f) 
    except:
        #CAL CANVIAR LES COORDENADES NDARRAY A LIST. O SINO DUMP NO VA
        for node in dic_nodePosicio:
            dic_nodePosicio[node] = list(dic_nodePosicio[node])
            print(dic_nodePosicio[node],type(dic_nodePosicio[node]))    
        #GUARDO EL DICT A UN json    
        with open("dic_nodePosicio_guardat.json","w") as f:
            json.dump(dic_nodePosicio,f)

    return dic_nodePosicio


def informaRepetits(ll_investmentInvestor,imprimir):
    """
    DESCRIPCIO_ Ens permet corregir el problema de paritat que es dóna en desapareixer els elements de l'excel un cop passats al graf G. 
    Absolutament essencial perquè les descripcions de Investor i Investment no es mesclin al graf.
    PRE:  ll_investmentInvestor <--      (variable global) : es la llista que conté les columnes "Investment i Investor_Parsejat" de l'excel processades 
        de FORMA ALTERNA i indexades desde zero (i.e [fila1_columnaInvestment, fila1_columnaInvestor, f2_cBT, f2_cBO, f3_cBT, f3_cBO, [...], filaN_columnaInvestment, 
        filaN_columnaInvestor]). A aquesta extracció l'anomerament la col·lecció d'elements excel. Noteu que ll_noms_dels_nodes conté aquesta col·lecció, 
        respectant-ne l'ordre, però amb els noms dels repetits eliminats. El problema d'això és que ens trenca l'argument de paritat, que ens ajuda a 
        decidir si un node és Investor o Investment, per tal de poder fer la llegenda hoverable del gràfic.
        la funció retorna en quins indexos de "ll_noms_dels_nodes" (on nodes) caldrà fer un CANVI de paritat per 
        decidir aixi si es Investor o no.
        imprimir <-- un boolea que, si es true, demana que imprimim el diccionari de ocurrencies multiples i el set de indexos a eliminar
    POST: set_indexos_canvis_paritat --> un conjunt amb els indexos dels nodes en els quals caldrà modeficar la paritat per compensar les eliminacions que produeix fer el graf sense repetir nodes.  
    """
    j = 0
    conjunt_rep = set() #un conjunt amb els elements repetits i com a valors llistes dels indexos on caldra fer el canvi de paritat a ll_noms_dels_nodes
    d_canvis_paritat = {} #diccionari que contindrà com a claus els indexos en els quals, abans de processar el node, caldrà fer un canvi de paritat si el seu valor es IMPARELL (es un diccionari d'ocurrencies multiples que informa quants elements s'eliminen per davant i, per tant, d'aqui podem treure els canvis de paritat)
    for i in range(len(ll_investmentInvestor)):   
        if ll_investmentInvestor[i] in conjunt_rep:
            if j in d_canvis_paritat:
                d_canvis_paritat[j] += 1
            else:
                d_canvis_paritat[j] = 1
            j = j - 1
        else:
            conjunt_rep.add(ll_investmentInvestor[i])
        j = j + 1
    set_indexos_canvis_paritat = set() #el que retornarem
    for clau in d_canvis_paritat:
        if d_canvis_paritat[clau] % 2 != 0: #son els repetits que es repeteixen de forma imparell, i si generen canvis de paritat. Els unics que cal ajustar!
            set_indexos_canvis_paritat.add(clau)
    #RETORNEM només els indexos on cal canviar la paritat  
    if imprimir:
        print("d_canvis_paritat:\n    ",d_canvis_paritat)
        print("set_indexos_canvis_paritat\n    ",set_indexos_canvis_paritat)
    return set_indexos_canvis_paritat








def crea_grafic(fesFiltre, tipusFiltre, informacioFiltre):
    """
    PRE: - fesFiltre: Booleà. Si és True anirà a mirar la resta de paràmetres per definir el filtre. En cas contrari la resta de paràmetres 
                no importaran i podran deixar-se com a string buit (tipusFiltre) i llista buida (informacioFiltre), respectivament.
         - tipusFiltre: Un string que pot prendre quatre valors: "intervalForecast_Sell_Date", "Investor", "Time_Difference" o "timelapse_Time_Difference" (l'últim requereix posar la funció dins un while)
         - informacioFiltre: és diferent en funció del paràmetre que pren tipus Filtre. 
                Si a tipusFiltre poses "Investor" -------------> dins "informacioFiltre" has de ficar una llista d'strings que contingui un o diversos Investors -strings- pels quals vulguis filtrar.
                Si a tipusFiltre poses "intervalForecast_Sell_Date" --> dins "informacioFiltre" has de ficar dos enters: l'any inici i l'any final (limit superior i inferior) del filtre.
                Si a tipusFiltre poses "Time_Difference" ------------> dins "informacioFiltre" has de ficar una llista d'strings que contingui un o diversos Time_Differences -strings- pels quals vulguis filtrar.
                Si a tipusFiltre poses "timelapse_Time_Difference" -> dins "informacioFiltre" has de ficar dos enters: l'any inici i l'any final (limit superior i inferior) del filtre I TAMBÉ has de posar el codi dins un while, tal i com hem fet abaix de tot a l'exemple.
    
    POST: - El gràfic obert al navegador.
          - document txt (out_Investors_orderedByNumberOfInvestments.txt) amb els Investors, ordenats per la quantitat d'inversions que s'associen a cada un.
    """

    #PORTO EL GRAF DE L'ALTRE FITXER I LES POSICIONS (coordenades) ASSIGNADES A CADA NODE
    G, dic_nodePosicio, ll_investmentInvestor, Investor_series, Time_Difference_series, minMax_Forecast_Sell_Date = SSS.creaGraf() #ll_to

    if tipusFiltre == "timelapse_Time_Difference":
        dic_nodePosicio = guarda_o_recupera_coordenades(dic_nodePosicio) #FIXO EL DICCIONARI NODE POSICIÓ

    limInf, limSup = minMax_Forecast_Sell_Date
    #IMPRIMIM LES CONNEXIONS DE CADA Investor, ORDENADES DE MÉS A MENYS CONNEXIONS
    print("\n###########################################")
    #print(Investor_series.value_counts())
    print("Forecast_Sell_Date ------------------> min: {} || max: {}. \n      (Pots fer servir aquesta informació per decidir\n      com filtrar quan filtres per Forecast_Sell_Date)".format(limInf, limSup))
    print("llistat exhaustiu Investors --> out_Investors_orderedByNumberOfInvestments.txt")
    print("###########################################\n")

    
    #TREIEM LA INFORMACIÓ DELS VALUE COUNTS
    Investors_de_mes_a_menys_connexions = list(Investor_series.value_counts().keys())
    nombre_de_connexions = list(Investor_series.value_counts().values)
    Time_Differences_ordPer_ocurrencies = list(Time_Difference_series.value_counts().keys())
    Time_Differences_ocurrencies = list(Time_Difference_series.value_counts().values)

    #GUARDEM EN UN TXT PER PODER CONSULTAR EN FER EL DESPLEGABLE DEL FILTRE DE InvestorS (TÉ MES VALOR SABER ELS QUE TENEN MES INVERSIONS PER FILTRAR-LOS)
    with open("out_Investors_orderedByNumberOfInvestments.txt","w") as f:
        for Investor, connexions, Time_Difference, sorcOcurr in zip(Investors_de_mes_a_menys_connexions, nombre_de_connexions, Time_Differences_ordPer_ocurrencies, Time_Differences_ocurrencies):
            f.write(str(connexions) + "\t" + Investor + "\n")
           
    
    #TREBALLEM AMB ELS NODES
    node_x = []
    node_y = []
    ll_noms_dels_nodes = [] #afegim els noms dels nodes!
    i = 0
    d_noms_nodes = {} #fem un diccionari clau valor amb nom del node a l'index  {"IBM": 1, Top 3 QC /QIS trends: 2} ...
    for node in G.nodes(data=False): #afegeix data = true si vols accedir a atributs dels nodes
        #SI VOLS ACCEDIR A PROPIETATS DELS NODES POSA TRUE A G.nodes i afegeix la seguent linia, i pots usar dic_Atributs
        #node, dic_atributs = tupla_node #node es el nom del node
        #print(node,dic_atributs) # {"Forecast_Sell_Date":2023, "asd":"blah",...} Pots afegir mes claus anant al fitxer SSS
        #time.sleep(2)
        x,y = dic_nodePosicio[node] #x, y = G.nodes[node]['pos'] CODI CANVIAT PER LA LINIA NO COMENTADA

        node_x.append(x)
        node_y.append(y)

        ll_noms_dels_nodes += [node]   #LINIA AFEGIDA
        d_noms_nodes[node] = i #linia afegida. ens permetra trobar els indexos a afegir al grafic en que filtrarem per propietats del mateix
        i = i + 1


    #CREAR ARESTES
    edge_x = []
    edge_y = []
     
    #SI FEM FILTRE CAL TRACTAR LES DADES DE FORMA DIFERENT
    if fesFiltre:
        ll_punts_seleccionats_filtre = [] #LLISTA AMB EL PUNTS DEL FILTRE
    else:
        ll_punts_seleccionats_filtre = "" #LA FEM STRING BUIT PERQUÈ EN PASSAR-HO A selectedpoints DE go.scatter() NO HI HAGI FILTRE

    #NOTEU QUE edge[0] es un node i edge[1] es l'altre node (units per una aresta)
    dic_etiquetes_edges = {}
    for edge in G.edges(data = True): 
        #x0, y0 = G.nodes[edge[0]]['pos'] #AIXO HO HEM ESBORRAT PERQUÈ HEM NECESSITAT ACCEDIR A LES COORDENADES D'UNA ALTRA MANERA QUE AL CODI D'ORIGEN LINQUEJAT A LA CAPÇALERA DEL DOCUMENT
        x0, y0 = (dic_nodePosicio[edge[0]][0], dic_nodePosicio[edge[0]][1]) 
        x1, y1 = (dic_nodePosicio[edge[1]][0], dic_nodePosicio[edge[1]][1])#ABANS ERA: x1, y1 = G.nodes[edge[1]]['pos'] (IDEM A CANVI EN L'OBTENCIÓ de coordenades x0, y0


        #CRIDEM A LA FUNCIO QUE ENS FA EL FILTRE DELS NODES (ACCEDINT A LES PROPIETATS DE LES EDGES, RETORNA ELS INDEXOS DELS NODES ALS QUALS LES EDGES SON INCIDENTS=
        if fesFiltre:
            if tipusFiltre == "intervalForecast_Sell_Date":
                ll_punts_seleccionats_filtre += filtres.perAnysForecast_Sell_Date(ll_punts_seleccionats_filtre, d_noms_nodes, edge, informacioFiltre)#nota que edge permet fer ---> node1, node2, dic_propietats = edge
            elif tipusFiltre == "Investor":
                ll_punts_seleccionats_filtre += filtres.perInvestor(ll_punts_seleccionats_filtre, d_noms_nodes, edge, informacioFiltre)
            elif tipusFiltre == "Time_Difference":
                ll_punts_seleccionats_filtre += filtres.perTime_Difference(ll_punts_seleccionats_filtre, d_noms_nodes, edge, informacioFiltre)
            elif tipusFiltre == "timelapse_Time_Difference":
                ll_punts_seleccionats_filtre += filtres.perTime_Difference(ll_punts_seleccionats_filtre, d_noms_nodes, edge, informacioFiltre)
            else:
                raise ValueError('El nom del filtre aplicat no correspon a cap filtre! Escull entre "Forecast_Sell_Date","technologies","Investor" o "Time_Difference"')

        
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

        #AFEGIM ELS ANYS DE Forecast_Sell_Date A DINS LES EDGES CAL RESPECTAR LES ESTRUCTURES QUE DEMANA nx.draw_networkx_edge_labels
        node1, node2, d_propNode = edge





        dic_etiquetes_edges[(node1, node2)] = "{}::{}::{}".format(d_propNode["Forecast_Sell_Date"], 
                                                                d_propNode["Buy_Date"], 
                                                                d_propNode["Time_Difference"]) #FIQUEM ELS DOS NODES DE L'EDGE COM A CLAUS I COM A VALOR L'ANY DE Forecast_Sell_Date
        
        










    #INFORMACIO COMPLEMENTARIA ALS FILTRES
    if fesFiltre:
        if tipusFiltre == "intervalForecast_Sell_Date":
            anyIni, anyFi = informacioFiltre
            if anyIni == anyFi:
                infoFiltre = " ({})".format(anyIni) #o anyFi
            else:
                infoFiltre = " ({} to {})".format(anyIni,anyFi)
        elif tipusFiltre == "Investor":
            infoFiltre = " (filtered by Investor: {} Investor/s)".format(len(informacioFiltre))
        elif tipusFiltre == "Time_Difference" or tipusFiltre == "timelapse_Time_Difference":
            anyIni, anyFi = informacioFiltre
            #CODI ADAPTAT COPIAT DE FILTRE PER ANYS (intervalForecast_Sell_Date per fer la versió adaptada)
            if anyIni == anyFi:
                infoFiltre = " ({} years needed)".format(anyIni) #o anyFi
            else:
                infoFiltre = " (between {} to {} years needed)".format(anyIni,anyFi)
        else:
            infoFiltre = ""
    else:
        infoFiltre = ""
           

    #FER ELS GRAFICS
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='all', #NO FUNCIONA
        mode='lines',
        showlegend=False) #linia afegida perque no surti la llegenda dela trace


    node_trace = go.Scatter(
        x=node_x, y=node_y,
        showlegend=False, #linia afegida perque no surti la llegenda dela trace
        selectedpoints = ll_punts_seleccionats_filtre, #si ll_punts_seleccionats_filtre canvia a string buit no aplica filtre, aquesta es la estrategia que he pres per no filtrar
        mode='markers',
        hoverinfo='text',
        #text=ll_noms_dels_nodes, #LINIA AFEGIDA!
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='Hot',
            reversescale=True,
            color=[],
            size=6.5,
            colorbar=dict(
                thickness=13,
                title='Number of connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=1))


    #COLOREJAR
    node_adjacencies = []
    node_text = []
    set_indexos_canvis_paritat = informaRepetits(ll_investmentInvestor,False)
    correccio = 0
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        """A continuació, mitjançant argument de paritat aconseguim que només es mostrin les connexions per a l'Investor i que es
        pugui diferenciar a la llegenda si el node es tracta d'Investment o d'Investor. Cal vigilar molt la paritat obtinguda a ll_investmentInvestor.
        Aquest llista ve de l'excel i allà index parell es un Investment i l'index senar es un Investor. Cal prestar atenció a aquest detall perquè la 
        paritat queda destruïda en fer el graf... ja que dins el mateix s'eliminen els nodes repetits. Per tal de poder obtenir de nou la informació que la 
        destrucció d'aquesta paritat genera hem creat la funció informaRepetits, que ens diu en quins indexos de ll_noms_Dels_nodes 
        caldrà fer una correcció abans d'accedir a l'element."
        """
        #CORREGIM LA PARITAT SI S'ESCAU IMPORTANTISSIM
        if node in set_indexos_canvis_paritat:
            correccio += 1
        if (node + correccio) % 2 == 0:
            node_text.append('<i>Investment:</i> <b>{}</b>'.format(ll_noms_dels_nodes[node])) #TROBAR AIXÒ HA COSTAT UN HUEVO
        else:
            node_text.append('<i>Number of investments:</i> {}<br><i>Investor:</i> <b>{}</b>'.format(len(adjacencies[1]), ll_noms_dels_nodes[node])) #TROBAR AIXÒ HA COSTAT UN HUEVO

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text



    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title='Investors and their time to double investment'+infoFiltre,
                    titlefont_size=16,
                    showlegend=True,
                    hovermode="closest",  #https://plotly.com/python/reference/layout/#layout-hovermode NO PERMET AFEGIR MES DADES
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text="Python code: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )



    #BIB:
    #https://stackoverflow.com/questions/47094949/labeling-edges-in-networkx
    #https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_networkx_edge_labels.html
    #nx.draw(G, dic_nodePosicio, edge_color='black', width=1, linewidths=1,node_size=10, node_color='blue', alpha=0.5,labels={node: node for node in G.nodes()})    
    dic_edge_posicionsText = nx.draw_networkx_edge_labels(G, dic_nodePosicio, edge_labels=dic_etiquetes_edges, font_color='red')

    for tupla_edge in dic_edge_posicionsText:

        #HEM DE TREURE L'ANY I LES POSICIONS DE L'ANY, PERQUE ESTA DINS UNA CLASSE MATPLOBLIB. CONSULTANT L'API HEM TROBAT
        #COM EXTREURE-HO       https://matplotlib.org/stable/api/text_api.html#matplotlib.text.Text.get_position
        anyForecast_Sell_Date__anyPrediccio__Time_Difference = dic_edge_posicionsText[tupla_edge].get_text()
        x_txt_edge, y_txt_edge = dic_edge_posicionsText[tupla_edge].get_position()
        
        Forecast_Sell_Date, Buy_Date, Time_Difference = anyForecast_Sell_Date__anyPrediccio__Time_Difference.split("::")

        
        # AFEGIM ELS ANYS DE Forecast_Sell_Date A LES EDGES QUE UNEXIEN L'Investor AMB LA TECH EN CONCRET. NO ES POT FER HOVERABLE, PERÒ MILLOR
        # AIXI QUE NO PAS AFEGIR-HO ALS NODES DE TECH, CAS EN QUE SI DOS InvestorS APUNTEN A UNA SOLA TECH NO ES PODRIA VEURE QUIN ANY
        # DE Forecast_Sell_Date ELS PERTOCA A CADA UN D'ELLS...

        

        anyActual = datetime.datetime.now().year
        
        if anyActual > int(Forecast_Sell_Date):
            etiqueta = "[Investment x2]" #Sell Date a la qual la inversió es va duplicar (cas que va ocórrer)
        else:
            etiqueta = "Forecast [Investment x2]" #Forecast Sell Date ()



        fig.add_annotation(
            text="  ",          #https://plotly.com/python/text-and-annotations/#:~:text=Annotations%20can%20be%20added%20to%20a%20figure%20using,rendering%20the%20information%2C%20and%20will%20override%20textinfo%20.
            hovertext="Buy Date: {}<br>{}: {}<br>Time Difference: {}".format(Buy_Date, etiqueta, Forecast_Sell_Date, converteixAny_a_AnyMesDia(Time_Difference)),
            x=x_txt_edge,
            y=y_txt_edge,
            xref="x",
            yref="y",
            showarrow=False
        )
        

    if tipusFiltre == "timelapse_Time_Difference":
        li, ls = informacioFiltre[0], informacioFiltre[1]
        fig.write_image('timelapse_Time_Difference/{}_to_{}_years.jpeg'.format(li,ls), scale=7)
    else:
        fig.show()


    



if __name__ == "__main__":
    #--------------------------------------------------------------------------------
    #EXEMPLE SENSE FILTRE (els paràmetres després de fesFiltre poden valdre qualsevol valor, no s'usen; però han d'estar inicialitzats a alguna cosa)
    
    crea_grafic(fesFiltre = False, 
                tipusFiltre="",
                informacioFiltre=[])  
    
    

    #--------------------------------------------------------------------------------
    #EXEMPLE AMB FILTRE PER Forecast_Sell_Date (mirar un interval d'anys i veure quins inversors han duplicat el valor de les seves inversions)
    """
    crea_grafic(fesFiltre = True, #si vols filtre posa fesFiltre = True i, aleshores, dona valors als paràmetres restants. En cas contrari, si poses, False, el filtre no filtra res i es indistint el valor que prenguin la resta de parametres.
                tipusFiltre="intervalForecast_Sell_Date", #TRES POSSIBILITATS --> intervalForecast_Sell_Date, Investor, Time_Difference  
                informacioFiltre=[2015,2020])  #la llista que passem a informacioFiltre conté limit inferior i limit superior, respectivament. Si vols trobar inversors que podrien duplicar la seva inversió en un sol, fes que conicideixin els limits.
    """
    


    #--------------------------------------------------------------------------------
    #EXEMPLE AMB FILTRE PER Investor (Permet filtrar les inversors d'un o diversos inversors 
    # especificats a la llista que es passa al paràmetre informacioFiltre)
    """
    crea_grafic(fesFiltre = True, #si vols filtre posa-ho a true i, aleshores, mira els següents paràmetres. En cas contrari false, no filtra res i es indistint el valor que prenguin la resta de parametres.
                tipusFiltre="Investor",#intervalForecast_Sell_Date, Investor, Time_Difference  
                informacioFiltre=["Elon Musk", "John Paulson", "George Soros"])  #Admet múltiples Investors, cada un com a element diferent de la llista. Si tipusFiltre == ["George Soros"], la informacio del Filtre tindrà només les inversions que ell ha fet ell.
    """


    #--------------------------------------------------------------------------------
    #EXEMPLE AMB FILTRE PER Time_Difference (Permet filtrar pel temps que els inversors tarden en duplicar les seves inversions)
    """
    crea_grafic(fesFiltre = True, #si vols filtre posa-ho a true i, aleshores, mira els següents paràmetres. En cas contrari (false), resta de paràmetres indistints (poden ser objecte buit).
                tipusFiltre="Time_Difference",   
                informacioFiltre=[0,3])  #Admet dos arguments: anys d'inici i any de final (poden ser floats pero millor deixa-ho en enters perquè sino titol es veurà lleig)
    """

    #--------------------------------------------------------------------------------
    # LIMIT INFERIOR I EL SUPERIOR ELS ESCOLLIM NOSALTRES, CAL MIRAR L'EXCEL, COLUMNA Time_Difference 
    # PER TROBAR PUNT MÀXIM I MINIM O MIRAR EL PRINT PER PANTALLA QUE T'INDICA
    # Nota: millor definiu li i ls enters. Si trobeu que el màxim any dins Time_Difference és 10,4150 aleshores escolliu a ls = 11 perquè 
    # l'inclogui. Si veieu que el minim any és 0,3148 aleshores podeu posar li = 0 perquè també l'inclogui al timelapse.
    """
    filtres.timelapse_Time_Difference(li = 0, ls = 11)
    """
       
    


"""
Programa fet per @blackcub3s (Santi Sánchez Sans)
https://github.com/blackcub3s
Analista de dades amb python
"""