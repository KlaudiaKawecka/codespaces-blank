import random
from core.models import Manufacturer, Drug, Patient, Objaw, Zdarzenie

print("--- ROZPOCZYNAM ŁADOWANIE DANYCH (ULEPSZONE) ---")

# 1. CZYSZCZENIE STAREJ BAZY
print("Usuwanie starych danych...")
Zdarzenie.objects.all().delete()
Patient.objects.all().delete()
Drug.objects.all().delete()
Manufacturer.objects.all().delete()
Objaw.objects.all().delete()

# 2. TWORZENIE PRODUCENTÓW (TWOJA LISTA)
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

# 3. TWORZENIE LEKÓW (TWOJA LISTA + AUTOMATYCZNE ROZPOZNAWANIE SUBSTANCJI)
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

def rozpoznaj_substancje(nazwa_leku):
    n = nazwa_leku.lower()
    if "meloksikam" in n or "movalis" in n or "aspicam" in n: return "Meloksikam"
    if "indometacyna" in n or "indocid" in n: return "Indometacyna"
    if "diklofenak" in n or "voltaren" in n or "diclo" in n: return "Diklofenak"
    if "pyralgina" in n or "pyreox" in n or "gardan" in n: return "Metamizol"
    if "paracetamol" in n or "calpol" in n: return "Paracetamol"
    if "aspirin" in n or "polopiryna" in n or "acard" in n or "polocard" in n: return "Kwas acetylosalicylowy"
    if "piroksikam" in n or "feldene" in n: return "Piroksikam"
    if "ketonal" in n or "ketoprofen" in n or "ketolek" in n or "febrofen" in n: return "Ketoprofen"
    if "naproxen" in n or "nalgesin" in n or "apo-napro" in n or "vemonis" in n: return "Naproksen"
    if "ibuprofen" in n or "ibum" in n or "ibufen" in n: return "Ibuprofen"
    return "Inna substancja"

leki_db = []
for nazwa in lista_lekow_nazwy:
    wylosowany_producent = random.choice(producenci_db)
    substancja = rozpoznaj_substancje(nazwa) # <--- TO NAPRAWIA WYKRES
    lek = Drug.objects.create(lek=nazwa, active_substance=substancja, manufacturer=wylosowany_producent)
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

# 6. TWORZENIE ZDARZEŃ (Twoja logika)
print("Generowanie raportów...")

for pacjent in pacjenci_db:
    los = random.random()
    lek = random.choice(leki_db)
    
    # Mały dodatek logiczny dla Heatmapy:
    # Zróbmy tak, że Ketoprofen działa lepiej na dorosłych, a Paracetamol słabiej na seniorów
    # (To tylko symulacja, żeby heatmapa była kolorowa)
    szansa = 0.70
    if lek.active_substance == "Paracetamol" and pacjent.age > 65: szansa = 0.40
    if lek.active_substance == "Ketoprofen" and 35 <= pacjent.age <= 65: szansa = 0.95

    if los < szansa: 
        przed = random.randint(7, 10)
        po = random.randint(1, 4)
        opis = "Widoczna poprawa kliniczna."
    elif los < szansa + 0.20:
        wartosc = random.randint(3, 8)
        przed = wartosc
        po = wartosc
        opis = "Brak istotnej zmiany."
    else:
        przed = random.randint(1, 4)
        po = random.randint(6, 9)
        opis = "Działania niepożądane."

    zdarzenie = Zdarzenie.objects.create(
        patient=pacjent,
        drug=lek,
        nasilenie_przed=przed,
        nasilenie_po=po,
        opis=opis
    )
    zdarzenie.objawy.add(random.choice(objawy_db))

print("--- DANE ZAŁADOWANE POMYŚLNIE ---")