import random
from core.models import Manufacturer, Drug, Patient, Objaw, Zdarzenie

print("--- ROZPOCZYNAM ŁADOWANIE DANYCH (WERSJA OPTYMISTYCZNA) ---")

# 1. CZYSZCZENIE STAREJ BAZY
print("Usuwanie starych danych...")
Zdarzenie.objects.all().delete()
Patient.objects.all().delete()
Drug.objects.all().delete()
Manufacturer.objects.all().delete()
Objaw.objects.all().delete()

# 2. TWORZENIE PRODUCENTÓW (Sortowanie A-Z)
surowa_lista_producentow = [
    "Polpharma", "Zentiva", "Sandoz", "KRKA", "Hasco-Lek", "Teva Pharmaceuticals",
    "Perrigo", "Boehringer Ingelheim", "MSD (Merck Sharp & Dohme)", "Novartis",
    "Aflofarm", "GlaxoSmithKline (GSK)", "Polfa Łódź", "Stada", "Bayer", "Pfizer", "Apotex"
]
surowa_lista_producentow.sort() 

producenci_db = []
for nazwa in surowa_lista_producentow:
    p = Manufacturer.objects.create(producent=nazwa)
    producenci_db.append(p)
print(f"--> Dodano {len(producenci_db)} producentów.")

# 3. TWORZENIE LEKÓW
lista_lekow_nazwy = [
    "Movalis", "Meloksikam Polpharma", "Meloksikam Zentiva", "Aspicam", "Meloksikam Sandoz",
    "Indometacyna Polpharma", "Indometacyna Hasco", "Indocid", "Indometacyna Zentiva",
    "Indometacyna Teva", "Voltaren (tabletki klasyczne)", "Diclomax", "Dicloratio",
    "Diklofenak Polpharma", "Diklofenak Perrigo", "Pyralgina", "Pyralgina Max", "Pyreox",
    "Gardan", "Vemonis", "Paracetamol Zentiva", "Paracetamol Polfa-Łódź", "Calpol",
    "Paracetamol Stada", "Paracetamol Teva", "Aspirin (klasyczna)", "Aspirin Cardio",
    "Polopiryna S", "Polocard", "Acard", "Feldene", "Piroksikam Hasco", "Piroksikam Polpharma",
    "Piroksikam Zentiva", "Piroksikam Teva", "Ketonal", "Ketonal Forte", "Ketolek", "Febrofen",
    "Ketoprofen Hasco", "Naproxen Aflofarm", "Nalgesin", "Nalgesin Mini", "Apo-Napro",
    "Naproksen Teva", "Ibum", "Ibufen", "Ibuprofen Zentiva", "Ibuprofen Teva", "Ibuprofen Stada"
]

leki_db = []
for nazwa in lista_lekow_nazwy:
    wylosowany_producent = random.choice(producenci_db)
    lek = Drug.objects.create(lek=nazwa, active_substance="Substancja czynna", manufacturer=wylosowany_producent)
    leki_db.append(lek)
print(f"--> Dodano {len(leki_db)} leków.")

# 4. TWORZENIE OBJAWÓW
lista_objawow = ["Ból głowy", "Ból stawów", "Gorączka", "Ból mięśni", "Migrena"]
objawy_db = []
for nazwa in lista_objawow:
    o = Objaw.objects.create(name=nazwa)
    objawy_db.append(o)
print(f"--> Dodano {len(objawy_db)} objawy.")

# 5. TWORZENIE PACJENTÓW
plec_opcje = ['K', 'M']
pacjenci_db = []
for i in range(250):
    p = Patient.objects.create(age=random.randint(18, 95), gender=random.choice(plec_opcje))
    pacjenci_db.append(p)
print(f"--> Dodano {len(pacjenci_db)} pacjentów.")

# 6. TWORZENIE ZDARZEŃ (WERSJA OPTYMISTYCZNA)
print("Generowanie raportów (Ustawianie, aby leki częściej pomagały)...")

for pacjent in pacjenci_db:
    los = random.random() # Losuje liczbę od 0.0 do 1.0
    
    if los < 0.70: 
        # 70% SZANS: LEK POMAGA (Duży ból przed -> Mały ból po)
        przed = random.randint(7, 10)
        po = random.randint(1, 4)
        opis = "Widoczna poprawa kliniczna."
        
    elif los < 0.90:
        # 20% SZANS: BEZ ZMIAN (Np. 5 -> 5)
        wartosc = random.randint(3, 8)
        przed = wartosc
        po = wartosc
        opis = "Brak istotnej zmiany w samopoczuciu."
        
    else:
        # 10% SZANS: ZASZKODZIŁ (Mały ból przed -> Duży po)
        przed = random.randint(1, 4)
        po = random.randint(6, 9)
        opis = "Wystąpienie działań niepożądanych."

    zdarzenie = Zdarzenie.objects.create(
        patient=pacjent,
        drug=random.choice(leki_db),
        nasilenie_przed=przed,
        nasilenie_po=po,
        opis=opis
    )
    zdarzenie.objawy.add(random.choice(objawy_db))

print("--- SUKCES! DANE ZAKTUALIZOWANE (TERAZ LEKI DZIAŁAJĄ LEPIEJ) ---")