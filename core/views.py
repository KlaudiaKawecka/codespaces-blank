from django.shortcuts import render, get_object_or_404
from .models import Zdarzenie, Drug, Objaw, Manufacturer
from django.db.models import F, Count

def home(request):
    wszystkie_zgloszenia = Zdarzenie.objects.all().order_by('-id')
    
    # --- STATYSTYKI OGÓLNE ---
    liczba_zgloszen = wszystkie_zgloszenia.count()
    liczba_pacjentow = wszystkie_zgloszenia.values('patient').distinct().count()
    liczba_lekow = Drug.objects.count()
    liczba_objawow = Objaw.objects.count()
    liczba_producentow = Manufacturer.objects.count()

    # --- WYKRESY (DANE) ---
    pomoglo = wszystkie_zgloszenia.filter(nasilenie_przed__gt=F('nasilenie_po')).count()
    zaszkodzilo = wszystkie_zgloszenia.filter(nasilenie_przed__lt=F('nasilenie_po')).count()
    bez_zmian = wszystkie_zgloszenia.filter(nasilenie_przed=F('nasilenie_po')).count()

    kobiety_pomoglo = wszystkie_zgloszenia.filter(patient__gender='K', nasilenie_przed__gt=F('nasilenie_po')).count()
    mezczyzni_pomoglo = wszystkie_zgloszenia.filter(patient__gender='M', nasilenie_przed__gt=F('nasilenie_po')).count()
    
    grupa_mlodzi = wszystkie_zgloszenia.filter(patient__age__lt=35, nasilenie_przed__gt=F('nasilenie_po')).count()
    grupa_sredni = wszystkie_zgloszenia.filter(patient__age__gte=35, patient__age__lte=65, nasilenie_przed__gt=F('nasilenie_po')).count()
    grupa_starsi = wszystkie_zgloszenia.filter(patient__age__gt=65, nasilenie_przed__gt=F('nasilenie_po')).count()

    # --- RANKING SUBSTANCJI ---
    ranking_substancji = (
        Zdarzenie.objects.filter(nasilenie_przed__gt=F('nasilenie_po'))
        .values('drug__active_substance')
        .annotate(sukcesy=Count('id'))
        .order_by('-sukcesy')[:5]
    )
    top_substancje_nazwy = [item['drug__active_substance'] for item in ranking_substancji]
    top_substancje_wyniki = [item['sukcesy'] for item in ranking_substancji]

    # --- HEATMAPA ---
    wszystkie_substancje_lista = Drug.objects.values_list('active_substance', flat=True).distinct().order_by('active_substance')
    heatmap_data = []
    for substancja in wszystkie_substancje_lista:
        wiersz = {'nazwa': substancja, 'wyniki': []}
        grupy_wiekowe = [('Młodzi', 18, 35), ('Dorośli', 36, 65), ('Seniorzy', 66, 120)]
        for opis, min_w, max_w in grupy_wiekowe:
            total = Zdarzenie.objects.filter(drug__active_substance=substancja, patient__age__gte=min_w, patient__age__lte=max_w).count()
            sukcesy = Zdarzenie.objects.filter(drug__active_substance=substancja, patient__age__gte=min_w, patient__age__lte=max_w, nasilenie_przed__gt=F('nasilenie_po')).count()
            procent = round((sukcesy / total) * 100) if total > 0 else 0
            
            klasa = "bg-light text-muted"
            if total > 0:
                if procent >= 0: klasa = "bg-danger text-white opacity-75"
                if procent > 40: klasa = "bg-warning text-dark opacity-75"
                if procent > 70: klasa = "bg-success text-white opacity-75"
            wiersz['wyniki'].append({'procent': procent, 'kolor': klasa})
        heatmap_data.append(wiersz)

    # --- POPRAWKA: LOGIKA DLA ZAKŁADKI OBJAWY (TOP 3 LEKI) ---
    # Ta część została zmieniona, aby uniknąć błędu ValueError
    objawy_data = []
    wszystkie_objawy_db = Objaw.objects.all()
    
    for objaw in wszystkie_objawy_db:
        # 1. Pobieramy zdarzenia, gdzie wystąpił dany objaw I lek pomógł
        skuteczne_zdarzenia = Zdarzenie.objects.filter(
            objawy=objaw, 
            nasilenie_przed__gt=F('nasilenie_po')
        )
        
        # 2. Grupujemy po leku i liczymy wystąpienia
        ranking_lekow = (
            skuteczne_zdarzenia
            .values('drug')
            .annotate(liczba_wyleczen=Count('drug'))
            .order_by('-liczba_wyleczen')[:3]
        )
        
        # 3. Zamieniamy ID leków na obiekty Drug, aby szablon HTML je zrozumiał
        top_leki_lista = []
        for item in ranking_lekow:
            try:
                lek_obj = Drug.objects.get(id=item['drug'])
                # Doklejamy liczbę wyleczeń "na żywo" do obiektu, żeby wyświetlić w HTML
                lek_obj.liczba_wyleczen = item['liczba_wyleczen']
                top_leki_lista.append(lek_obj)
            except Drug.DoesNotExist:
                continue

        objawy_data.append({
            'objaw': objaw,
            'top_leki': top_leki_lista
        })

    # --- LISTY DO ZAKŁADEK ---
    lista_lekow = Drug.objects.all().order_by('lek')
    lista_producentow = Manufacturer.objects.all().order_by('producent')

    context = {
        'zgloszenia': wszystkie_zgloszenia,
        'liczba_zgloszen': liczba_zgloszen, 'liczba_pacjentow': liczba_pacjentow, 'liczba_lekow': liczba_lekow,
        'liczba_objawow': liczba_objawow, 'liczba_producentow': liczba_producentow,
        'stat_pomoglo': pomoglo, 'stat_zaszkodzilo': zaszkodzilo, 'stat_bez_zmian': bez_zmian,
        'plec_kobiety': kobiety_pomoglo, 'plec_mezczyzni': mezczyzni_pomoglo,
        'wiek_mlodzi': grupa_mlodzi, 'wiek_sredni': grupa_sredni, 'wiek_starsi': grupa_starsi,
        'ranking_labels': top_substancje_nazwy, 'ranking_data': top_substancje_wyniki,
        'heatmap_data': heatmap_data,
        'objawy_data': objawy_data,
        'lista_lekow': lista_lekow,
        'lista_producentow': lista_producentow
    }
    return render(request, 'core/home.html', context)

# --- WIDOKI DLA MINI-STRON ---

def drug_detail(request, id):
    lek = get_object_or_404(Drug, id=id)
    uzycia = Zdarzenie.objects.filter(drug=lek).order_by('-id')
    skuteczne = uzycia.filter(nasilenie_przed__gt=F('nasilenie_po')).count()
    wszystkie = uzycia.count()
    skutecznosc_proc = round((skuteczne/wszystkie)*100) if wszystkie > 0 else 0
    
    context = {'lek': lek, 'uzycia': uzycia, 'skutecznosc': skutecznosc_proc}
    return render(request, 'core/drug_detail.html', context)

def manufacturer_detail(request, id):
    producent = get_object_or_404(Manufacturer, id=id)
    leki_producenta = Drug.objects.filter(manufacturer=producent)
    context = {'producent': producent, 'leki': leki_producenta}
    return render(request, 'core/manufacturer_detail.html', context)