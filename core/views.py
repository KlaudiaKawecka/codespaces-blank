from django.shortcuts import render
from .models import Zdarzenie, Drug
from django.db.models import F, Count

def home(request):
    wszystkie_zgloszenia = Zdarzenie.objects.all().order_by('-id')
    
    # --- 1. KAFELKI ---
    liczba_zgloszen = wszystkie_zgloszenia.count()
    liczba_pacjentow = wszystkie_zgloszenia.values('patient').distinct().count()
    liczba_lekow = Drug.objects.count()

    # --- 2. WYKRES KOŁOWY ---
    pomoglo = wszystkie_zgloszenia.filter(nasilenie_przed__gt=F('nasilenie_po')).count()
    zaszkodzilo = wszystkie_zgloszenia.filter(nasilenie_przed__lt=F('nasilenie_po')).count()
    bez_zmian = wszystkie_zgloszenia.filter(nasilenie_przed=F('nasilenie_po')).count()

    # --- 3. PŁEĆ (Słupkowy) ---
    kobiety_pomoglo = wszystkie_zgloszenia.filter(patient__gender='K', nasilenie_przed__gt=F('nasilenie_po')).count()
    mezczyzni_pomoglo = wszystkie_zgloszenia.filter(patient__gender='M', nasilenie_przed__gt=F('nasilenie_po')).count()
    
    # --- 4. WIEK (Liniowy) ---
    grupa_mlodzi = wszystkie_zgloszenia.filter(patient__age__lt=35, nasilenie_przed__gt=F('nasilenie_po')).count()
    grupa_sredni = wszystkie_zgloszenia.filter(patient__age__gte=35, patient__age__lte=65, nasilenie_przed__gt=F('nasilenie_po')).count()
    grupa_starsi = wszystkie_zgloszenia.filter(patient__age__gt=65, nasilenie_przed__gt=F('nasilenie_po')).count()

    # --- 5. TOP 5 SUBSTANCJI (Ranking) ---
    ranking_substancji = (
        Zdarzenie.objects
        .filter(nasilenie_przed__gt=F('nasilenie_po'))
        .values('drug__active_substance')
        .annotate(sukcesy=Count('id'))
        .order_by('-sukcesy')[:5]
    )
    top_substancje_nazwy = [item['drug__active_substance'] for item in ranking_substancji]
    top_substancje_wyniki = [item['sukcesy'] for item in ranking_substancji]

    # --- 6. HEATMAPA (Lek x Wiek) ---
    # Wybieramy 5 najpopularniejszych substancji do analizy
    top_substancje_lista = [item['drug__active_substance'] for item in ranking_substancji]
    
    heatmap_data = []
    for substancja in top_substancje_lista:
        wiersz = {'nazwa': substancja, 'wyniki': []}
        grupy_wiekowe = [
            ('Młodzi (18-35)', 18, 35),
            ('Dorośli (36-65)', 36, 65),
            ('Seniorzy (65+)', 66, 120)
        ]
        
        for opis, min_w, max_w in grupy_wiekowe:
            total_w_grupie = Zdarzenie.objects.filter(
                drug__active_substance=substancja,
                patient__age__gte=min_w, patient__age__lte=max_w
            ).count()
            
            sukcesy_w_grupie = Zdarzenie.objects.filter(
                drug__active_substance=substancja,
                patient__age__gte=min_w, patient__age__lte=max_w,
                nasilenie_przed__gt=F('nasilenie_po')
            ).count()
            
            if total_w_grupie > 0:
                procent = round((sukcesy_w_grupie / total_w_grupie) * 100)
            else:
                procent = 0
            
            # Dobieramy kolor zależnie od procentu
            klasa_koloru = "bg-light text-muted"
            if procent > 0: klasa_koloru = "bg-danger text-white opacity-75" # Słabo
            if procent > 40: klasa_koloru = "bg-warning text-dark opacity-75" # Średnio
            if procent > 70: klasa_koloru = "bg-success text-white opacity-75" # Dobrze
            
            wiersz['wyniki'].append({'procent': procent, 'kolor': klasa_koloru})
        
        heatmap_data.append(wiersz)

    context = {
        'zgloszenia': wszystkie_zgloszenia,
        'liczba_zgloszen': liczba_zgloszen,
        'liczba_pacjentow': liczba_pacjentow,
        'liczba_lekow': liczba_lekow,
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
        'heatmap_data': heatmap_data # Przekazujemy dane do heatmapy
    }

    return render(request, 'core/home.html', context)
