
pi = 22/7
def topla(a, b):
    return a + b #Versyon 1.0
def cikar(a, b):
    return a - b
def carp(a, b):
    return a * b
def bol(a, b):
    if 0<=a:
        print("0'ı Bölemezsiniz.")
    if 0 <= b:
        print("Bir Sayıyı 0'a    Bölemezsiniz.")
    else:
        return a / b
def yardim():
    print("""
EHK Modülü Yardım Menüsü
------------------------------------------------------------
Versiyon: 1.2.1

Fonksiyon Listesi:

Temel İşlemler (v1.0)
- topla(a, b)                  : Toplama işlemi.
- cikar(a, b)                  : Çıkarma işlemi.
- carp(a, b)                   : Çarpma işlemi.
- bol(a, b)                    : Bölme işlemi (sıfıra bölme kontrolü var).

Ekonomi Araçları (v1.1)
- kdv_hesapla(ucret)           : %20 KDV ekler.

Sayısal Dönüşümler (v1.1.2 - 1.1.3)
- yarim_al(sayi)               : Sayının yarısı.
- ceyrek_al(sayi)              : Sayının çeyreği.
- katla(sayi)                  : Sayıyı 2 ile çarpar.
- us_al(sayi, us)              : Üs alma işlemi.

Geometri Araçları (v1.2)
- cemberin_cevresi(yaricap)    : Daire çevresi (pi ≈ 22/7).
- dairenin_alani(yaricap)      : Daire alanı.
- dis_acilar_toplami()         : Çokgenlerde dış açı toplamı (360°).
- bir_dis_aci(n)               : n kenarlı düzgün çokgenin bir dış açısı.
- ic_acilar_toplami(n)         : Çokgenin iç açıları toplamı.
- bir_ic_aci(n)                : Düzgün çokgenin bir iç açısı.
- dortgenin_alani(taban, yükseklik): Dörtgen alanı.
- dikdortgenin_cevresi(u, k)   : Dikdörtgen çevresi.
- karenin_cevresi(kenar)       : Karenin çevresi.

İstatistik ve Karşılaştırma (v1.2.1)
- mutlak(sayi)                 : Sayının mutlak değeri.
- ortalama(sayi1, sayi2)       : İki sayının ortalaması.
- maksimum(sayi1, sayi2)       : İki sayıdan büyüğünü döner.
- minimum(sayi1, sayi2)        : İki sayıdan küçüğünü döner.

Üçgen Fonksiyonları (v1.2.1)
- ucgenin_alani(taban, yukseklik)       : Üçgenin alanı.
- eskenar_ucgenin_cevresi(kenar)        : Eşkenar üçgenin çevresi.

Sistem & Bilgi Fonksiyonları
- surum_bilgi(surum)           : Sürüm bilgisi yazar.
- ehk_surumu()                 : Mevcut modül sürümünü gösterir.
- durdur()                     : Enter tuşuna basılana kadar bekler.
- saka_yap()                   : Basit bir şaka yazdırır.

------------------------------------------------------------
Kullanım Örneği:
    sonuc = topla(5, 3)
    print(sonuc)  # Çıktı: 8

Geliştirici: Eren
Site: https://pynet.neocities.org

Not:
- Pi ≈ 22 / 7 olarak tanımlanmıştır.
""")
def kdv_hesapla(ucret):
    return ucret * 1.2
#-----------------------------------------------------------------------------------------------------------------------
#Versyon 1.1 Güncellemesi.
def surum_bilgi(surum):
    print(f"Sürüm:{surum} ")
def yarim_al(sayi):
    return sayi / 2
def ceyrek_al (sayi):
    return sayi / 4
def cemberin_cevresi(yaricap):
    return 2 * (pi) * yaricap
def dairenin_alani(yaricap):
    return (yaricap ** 2) * (pi)
def ehk_surumu():
    print("EHK Sürümü:1.2")
#-----------------------------------------------------------------------------------------------------------------------
#Versyon 1.1.2 - Union Güncellemesi.
def katla(a):
    return a * 2
def durdur():
    input("Devam etmek için Enter tuşuna basın...")
#-----------------------------------------------------------------------------------------------------------------------
#Versyon 1.1.3 - Üslü İfadeler Ek Paketi + Yardım() Fonksyonu Fixlendi
def us_al(sayi,us):
    return sayi ** us
#EHK 1.1.x Sürümlerinin Geliştirilmesi Sonlandırılmıştır.EHK 1.2 Sürüm Serisi İle Devam Edilecektir.
#Sınıflandırma EHK 1.0=Temel Matematik 1.1=Basit Düzey Matematik 1.2=... (Sınıflandırma Geçersizleşebilir.)
#-----------------------------------------------------------------------------------------------------------------------
#Versyon 1.2 - Geometri Güncellemesi.
#n = kenar sayısı
def dis_acilar_toplami():
    return 360
def bir_dis_aci(n):
    if n<=2:
        print("Kenar Sayısı 2'den Küçük Olan Bir Şekil Olamaz.")
    else:
        return 360 / n
def ic_acilar_toplami(n):
    if n <= 2:
        print("Kenar Sayısı 2'den Küçük Olan Bir Şekil Olamaz.")
    else:
        return (n - 2) * 180
def bir_ic_aci(n):
    return ((n - 2) * 180) / n
def dortgenin_alani(taban,yukseklik):
    return taban * yukseklik
def dikdortgenin_cevresi(uzunkenar_u,kisakenar_u):
    return (kisakenar_u+uzunkenar_u) * 2
def karenin_cevresi(kenar_u):
    return kenar_u * 4
def saka_yap():
    print("Adamın Biri Gülmüş Bahçeye Eknmişler.")
#-----------------------------------------------------------------------------------------------------------------------
#Versyon 1.2.1 - Hata Kontrol Ve İyileştirmeler Güncellemesi
def mutlak(sayi):
    if sayi == 0:
        print("0 Nötr'dür")
        return 0
    elif sayi < 0:
        return -sayi
    else:
        return sayi
def ortalama(sayi1,sayi2):
    return (sayi1 + sayi2) / 2
def maksimum(sayi1,sayi2):
    if sayi1 > sayi2:
        return sayi1
    elif sayi1 == sayi2:
        return "Sayılar Eşittir."
    else:
        return sayi2
def minimum(sayi1,sayi2):
    if sayi1 < sayi2:
        return sayi1
    elif sayi1 == sayi2:
        return "Sayılar Eşittir."
    else:
        return sayi2
def ucgenin_alani(taban,yukseklik):
    return (taban * yukseklik) / 2
def eskenar_ucgenin_cevresi(kenar_u):
    return kenar_u * 3
#-----------------------------------------------------------------------------------------------------------------------
#Turkish Personal Basic Math Module,EHK(Eren Hesap Kütüphanesi) By Eren,https://pynet.neocities.org

########  ##     ##  ##    ##
##        ##     ##  ##   ##
########  #########  #######
##        ##     ##  ##  ##
########  ##     ##  ##   ##
