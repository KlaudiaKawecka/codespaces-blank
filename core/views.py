from django.shortcuts import render
from .models import Zdarzenie, Drug
from django.db.models import F, Count, Case, When, IntegerField

def home(request):
    # Pobieramy wszystkie zgłoszenia
    wszystkie_zgloszenia = Zdarzenie.objects.all().order_by('-data', '-id')
    
    # --- 1. STATYSTYKI OGÓLNE (Kafelki) ---
    liczba_zgloszen = wszystkie_zgloszenia.count()
    liczba_pacjentow = wszystkie_zgloszenia.values('patient').distinct().count()
    liczba_lekow = Drug.objects.count()

    # --- 2. SKUTECZNOŚĆ (Wykres Kołowy) ---
    pomoglo = wszystkie_zgloszenia.filter(nasilenie_przed__gt=F('nasilenie_po')).count()
    zaszkodzilo = wszystkie_zgloszenia.filter(nasilenie_przed__lt=F('nasilenie_po')).count()
    bez_zmian = wszystkie_zgloszenia.filter(nasilenie_przed=F('nasilenie_po')).count()

    # --- 3. PŁEĆ A SKUTECZNOŚĆ (Wykres Słupkowy) ---
    # Ile razy pomogło Kobietom (K) a ile Mężczyznom (M)
    kobiety_pomoglo = wszystkie_zgloszenia.filter(patient__gender='K', nasilenie_przed__gt=F('nasilenie_po')).count()
    mezczyzni_pomoglo = wszystkie_zgloszenia.filter(patient__gender='M', nasilenie_przed__gt=F('nasilenie_po')).count()
    
    # --- 4. WIEK A SKUTECZNOŚĆ (Wykres Liniowy - Grupy wiekowe) ---
    # Dzielimy na 3 grupy: Młodzi (<35), Średni (35-65), Starsi (>65)
    grupa_mlodzi = wszystkie_zgloszenia.filter(patient__age__lt=35, nasilenie_przed__gt=F('nasilenie_po')).count()
    grupa_sredni = wszystkie_zgloszenia.filter(patient__age__gte=35, patient__age__lte=65, nasilenie_przed__gt=F('nasilenie_po')).count()
    grupa_starsi = wszystkie_zgloszenia.filter(patient__age__gt=65, nasilenie_przed__gt=F('nasilenie_po')).count()

    # --- 5. TOP 5 SUBSTANCJI (Ranking) ---
    # To trudniejsze zapytanie: Grupujemy po substancji i liczymy sukcesy
    ranking_substancji = (
        Zdarzenie.objects
        .filter(nasilenie_przed__gt=F('nasilenie_po'))  # Tylko te co pomogły
        .values('drug__active_substance')               # Grupuj po substancji
        .annotate(sukcesy=Count('id'))                  # Policz ile razy pomogły
        .order_by('-sukcesy')[:5]                       # Weź 5 najlepszych
    )
    
    # Przygotowanie list dla Chart.js
    top_substancje_nazwy = [item['drug__active_substance'] for item in ranking_substancji]
    top_substancje_wyniki = [item['sukcesy'] for item in ranking_substancji]

    context = {
        'zgloszenia': wszystkie_zgloszenia,
        'liczba_zgloszen': liczba_zgloszen,
        'liczba_pacjentow': liczba_pacjentow,
        'liczba_lekow': liczba_lekow,
        
        # Dane do wykresów
        'stat_pomoglo': pomoglo,
        'stat_zaszkodzilo': zaszkodzilo,
        'stat_bez_zmian': bez_zmian,
        
        'plec_kobiety': kobiety_pomoglo,
        'plec_mezczyzni': mezczyzni_pomoglo,
        
        'wiek_mlodzi': grupa_mlodzi,
        'wiek_sredni': grupa_sredni,
        'wiek_starsi': grupa_starsi,
        
        'ranking_labels': top_substancje_nazwy,
        'ranking_data': top_substancje_wyniki,
    }

    return render(request, 'core/home.html', context)