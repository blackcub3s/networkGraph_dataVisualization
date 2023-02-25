import pandas as pd
import time
import os

fitxer_origen_a_parsejar = "1. fitxerInversions_inicial.xlsx" 			#NOM FITXER D'ENTRADA
nomFitxerFinal = "2. fitxerInversions_parsejatFinal.xlsx"			   #NOM QUE TINDRÀ EL FITXER DE SORTIDA
df = pd.read_excel(fitxer_origen_a_parsejar)


def parsejar():
	"""PRE: Document excel amb columna "investor", que conté string amb la ocurrència del caràcter ":"
	   POST: Retorna una llista amb els "investors" parsejats (sense espais i sense :)
	"""

	ll_Investor_Parsejat = []
	for i in range(len(df)):
		Investor_Parsejat = df["Investor"][i].split(":")

		#protegim errors
		if not len(Investor_Parsejat) == 2:
			print("error amb els dos punts, no hi son a la columna\nInvestor, fila {}: --> '{}' <--.\nPosa'ls com a la resta de files!".format(i + 2, df["Investor"][i]))
			return

		#ENS QUEDEM NOMES AMB EL NOM I TREIEM ESPAIS
		Investor_Parsejat = Investor_Parsejat[1].strip()

		#GUARDEM EN LLISTA
		ll_Investor_Parsejat += [Investor_Parsejat]
	return ll_Investor_Parsejat


def afegeix_Col_a_DataFrame(ll_col_parsejada):
	"""AFEGIM LA COLUMNA Investor PARSEJADA AL DATAFRAME"""
	df["Investor_Parsejat"] = ll_Investor_Parsejat



#L'ha fet GPT3 amb els promps de la capçalera
def hiHaRepeticions(series1, series2):
	""" ARGUMENTS: series1 and series2, both are pandas.series with strings.
		PRINTS: a string that tells the values that appear in series1 that also appear in series2. 
		If no values are repeated it'll print "no es comparteixen valors entre Investment i Investor".
		RETURNS: a bollean that tells if therer are shared values between both series or not
	"""	
	# Find values that appear in both series
	repeated_values = set(series1) & set(series2)
	# Check if there are any repeated values
	if len(repeated_values) == 0:
		print("no es comparteixen valors entre Investment i Investor :D. Fantàstic!\nEs un conjunt buit! Les etiquetes Investor i Investment del graf es mostraran correctament")
		return False
	else:
		print("El graf mostrara alguns valors mal etiquetats. Això és perquè el programa\nno admet que els següents valors ESTIGUIN tant a Investment com a Investor_Parsejat.\nEls valors duplicats són: {}.\nCorregeix l'excel i torna a executar aquest script".format(repeated_values))
		return True



def guarda_a_excel(nom_fitxer_nou, df):
	"""Guardem el dataframe (df) a un nou fitxer excel (nom_fitxer_nou)"""
	if nom_fitxer_nou in os.listdir():
		os.system("cls")
		print("###########################################\nFITXER JA EXISTEIX. S'HA DESTRUIT I SE N'HA GENERAT UN DE NOU!")
		
	else:
		print("###########################################\nFITXER FITXER \n-->{}<--\n\n CORRECTAMENT GENERAT!\n###########################################".format(nom_fitxer_nou))
	time.sleep(2)

	df.to_excel(nom_fitxer_nou)

if __name__ == "__main__":
	#PARSEJEM LA COLUMNA Investor (treiem els dospuntsi  els espais). Actes seguit guardem la columna al dataset excel
	ll_Investor_Parsejat = parsejar()
	afegeix_Col_a_DataFrame(ll_Investor_Parsejat)
	guarda_a_excel(nomFitxerFinal, df)

	#COMPROVEM QUE NO EXISTEIXEN NOMES A LA COLUMNA Investor_Parsejat QUE COINCIDEIXIN AMB Investment. SI AIXO PASSA L'ETIQUETATGE Investment i Investor FALLARA
	if not hiHaRepeticions(df["Investor_Parsejat"],df["Investment"]):
		print("#######################################\nTot correcte! Podeu aplicar el __main__grafGuay.py per treure el graf\n#######################################")
		

	


