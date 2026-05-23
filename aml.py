#!/bin/python3

import numpy as np
import pandas as pd
import random

# ===========================================================================
# Przygotowanie danych do analizy i zapisanie do pliku transakcje_bankowe.csv
# ===========================================================================

# inicjujemy generator liczb losowych
np.random.seed(42)
n_transakcji = 10000
print(n_transakcji)

id_klientow =[f"ACC_{i:04d}" for i in range(1, 201)]# tworzymy 200 klientow, :04d to zeby pokazac wiodace zera np 0001

dane = {
    "transakcja_id": [f"TX_{i:06d}"for i in range(1, n_transakcji+1)],
    "klient_id": [random.choice(id_klientow) for _ in range(n_transakcji)],
    "kwota": np.round(np.random.exponential(scale=3000, size=n_transakcji)+10, 2),#srednia kwota to 3000 ale przedzial 0 do nieskonczonosci
    "typ_operacji": [random.choice(["WPLATA", "WYPLATA", "PRZELEW_KRAJ", "PRZELEW_ZAGR"]) for _ in range(n_transakcji)],
    "data_godzina": pd.date_range("2026-05-01", periods=n_transakcji, freq="min")
}
df = pd.DataFrame(dane)
print(df.head(5))

# podejrzane transakcje

# tuż pod progiem 15 000
for i in range(10):
  df.loc[random.randint(0, n_transakcji-1), "kwota"] = 14900.00 #df.loc[wiersz, kolumna]

# bardzo wysokie kwoty, pranie pieniedzy
for i in range(5):
  df.loc[random.randint(0, n_transakcji-1), "kwota"] = random.randint(120000, 250000)

df.to_csv("transakcje_bankowe.csv", index=False)
print("Plik transakcje_bankowe.csv zostal wygenerowany!")

# ==================================================================================
# Analiza danych znalezienie podejrzanych transakcji i zapis do pliku aml_alerts.csv
# ==================================================================================

df = pd.read_csv("transakcje_bankowe.csv")


print("----OGÓLNE INFORMACJE O BAZIE TRANSAKCJI----\n")
print(f"Liczba wszystkich transakcji: {len(df)}")
print("\nPodgląd transakcji:\n")
print(df.head(5))

print("\nALERT 1: Transakcje blisko progu raportowania 15k")

podejrzani = df[(df['kwota'] >= 14100) & (df['kwota'] < 15000)]
print(podejrzani['klient_id'].value_counts())

# ==============================================================
# ==============================================================
print("ALERT 2: Gigantyczne transfery zagraniczne, pranie pięniedzy")
pranie = df[(df['typ_operacji'] == 'PRZELEW_ZAGR') & (df['kwota'] > 99000)]
print(pranie[["klient_id", "kwota", "data_godzina"]])

from csv import writer
# RAPORT KOŃCOWY
print("\nRAPORT KOŃCOWY")
zgrupowane = df.groupby('typ_operacji', as_index=False).agg(
      suma = ('kwota', 'sum'),
      srednia = ('kwota', 'mean')
    ).round(2)
print(zgrupowane)


with pd.ExcelWriter('output.xlsx') as writer:
  pranie.to_excel(writer, sheet_name="Gig_trans_zag", index=False)
  zgrupowane.to_excel(writer, sheet_name="Rap_kwot", index=False)
