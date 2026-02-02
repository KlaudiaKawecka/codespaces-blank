from django.db import models

# Create your models here.
from django.db import models

class Manufacturer(models.Model):
    producent = models.CharField(max_length=200, unique=True, verbose_name='Producent')

    class Meta:
        verbose_name = 'Producent'
        verbose_name_plural = 'Producenci'
        ordering = ['producent']

    def __str__(self):
        return self.producent

class Drug(models.Model):
    lek = models.CharField(max_length=255, verbose_name='Lek')
    active_substance = models.CharField(max_length=255, verbose_name='Substancja czynna')
    # TO JEST KLUCZOWE - Relacja do producenta:
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, verbose_name='Producent')

    class Meta:
        verbose_name = 'Lek'
        verbose_name_plural = 'Leki'
        ordering = ['lek']

    def __str__(self):
        return self.lek

class Patient(models.Model):
    GENDER_CHOICES = [('M', 'Mężczyzna'), ('K', 'Kobieta')]
    age = models.IntegerField(verbose_name='Wiek')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Płeć')

    class Meta:
        verbose_name = 'Pacjent'
        verbose_name_plural = 'Pacjenci'
        ordering = ['id']

    def __str__(self):
        return f"Pacjent #{self.id} ({self.age} lat)"

class Objaw(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Nazwa objawu')

    class Meta:
        verbose_name = 'Objaw'
        verbose_name_plural = 'Objawy'
        ordering = ['name']

    def __str__(self):
        return self.name

class Zdarzenie(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name='Pacjent')
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, verbose_name='Lek')
    objawy = models.ManyToManyField(Objaw, verbose_name='Objawy')
    
    # NOWE POLA - NASILENIE
    nasilenie_przed = models.IntegerField(verbose_name="Nasilenie objawów PRZED lekiem (1-10)", default=5)
    nasilenie_po = models.IntegerField(verbose_name="Nasilenie objawów PO leku (1-10)", default=5)
    
    opis = models.TextField(blank=True, verbose_name='Opis zdarzenia')
    data = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Zdarzenie'
        verbose_name_plural = 'Zdarzenia'
        ordering = ['id']

    def __str__(self):
        return f"Zdarzenie: {self.patient}"

    # To jest funkcja, która sama obliczy wynik w HTML
    def efekt_leczenia(self):
        if self.nasilenie_przed > self.nasilenie_po:
            return "✅ Pomógł"
        elif self.nasilenie_przed < self.nasilenie_po:
            return "❌ Zmiana na gorsze"
        else:
            return "➖ Bez zmian"
