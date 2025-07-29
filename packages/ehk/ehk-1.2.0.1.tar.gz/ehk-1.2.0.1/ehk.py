
def topla(a, b):
    return a + b #Versyon 1.0
def cikar(a, b):
    return a - b
def carp(a, b):
    return a * b
def bol(a, b):
    return a / b
def yardim():
    print("""
EHK Modülü Yardım Menüsü
------------------------------------------------------------
Versiyon: 1.2

Kullanılabilir Fonksiyonlar ve Açıklamaları:

Temel İşlemler (v1.0)
1. topla(a, b)               : İki sayıyı toplar.
2. cikar(a, b)               : İki sayıyı birbirinden çıkarır.
3. carp(a, b)                : İki sayıyı çarpar.
4. bol(a, b)                 : Bir sayıyı diğerine böler.

Ekonomi İşlemleri (v1.1)
5. kdv_hesapla(ucret)        : Verilen ücrete yüzde 20 KDV ekler.

Basit Dönüşümler (v1.1)
6. yarim_al(sayi)            : Sayının yarısını verir.
7. ceyrek_al(sayi)           : Sayının çeyreğini verir.
8. katla(sayi)               : Sayıyı iki katına çıkarır.
9. us_al(sayi, us)           : Sayının üssünü alır.

Geometri Araçları (v1.2)
10. cemberin_cevresi(yaricap)         : Dairenin çevresini hesaplar (pi ≈ 22/7).
11. dairenin_alani(yaricap)           : Dairenin alanını hesaplar.
12. dis_acilar_toplami()              : Çokgenlerde dış açı toplamı (360 derece).
13. bir_dis_aci(n)                    : n kenarlı düzgün çokgenin bir dış açısı.
14. ic_acilar_toplami(n)             : n kenarlı çokgenin iç açıları toplamı.
15. bir_ic_aci(n)                    : n kenarlı düzgün çokgenin bir iç açısı.
16. dortgenin_alani(taban, yukseklik): Dörtgenin alanını hesaplar.
17. dikdortgenin_cevresi(u, k)       : Dikdörtgenin çevresini hesaplar.
18. karenin_cevresi(kenar)           : Karenin çevresini hesaplar.

Diğer Fonksiyonlar
19. surum_bilgi(surum)       : Belirtilen sürüm bilgisi ekrana yazdırılır.
20. ehk_surumu()             : Mevcut EHK sürümünü gösterir.
21. durdur()                 : Programı Enter tuşuna basılana kadar duraklatır.
22. saka_yap()               : Basit bir şaka yapar.

------------------------------------------------------------
Kullanım Örneği:
    sonuc = topla(5, 3)
    print(sonuc)   # 8

Geliştirme Sitesi:
    https://pynet.neocities.org

Notlar:
- Pi değeri yaklaşık olarak 22/7 alınmıştır.
- İstatistiksel fonksiyonlar 1.3 sürümünde eklenecektir.
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
    return 2 * (22/7) * yaricap
def dairenin_alani(yaricap):
    return (yaricap ** 2) * (22 / 7)
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
    return 360 / n
def ic_acilar_toplami(n):
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
#Turkish Personal Basic Math Module,EHK(Eren Hesap Kütüphanesi) By Eren,https://pynet.neocities.org

########  ##     ##  ##    ##
##        ##     ##  ##   ##
########  #########  #######
##        ##     ##  ##  ##
########  ##     ##  ##   ##
