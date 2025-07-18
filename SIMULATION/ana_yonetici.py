import pygame
import matplotlib.pyplot as plt
import numpy as np
import sys  # Eksik import eklendi

# Senaryo modüllerini içe aktar
import senaryo_1_kontrolsuz
import senaryo_2_sirali_adaptif
import senaryo_3_yogunluk_adaptif
import senaryo_4_sabit_sureli

def kullanici_ayarlarini_al():
    """Kullanıcıdan simülasyon için temel yapılandırma ayarlarını alır."""
    print("--- Trafik Simülasyonu Ayarları ---")
    print("Lütfen aşağıdaki değerleri girin (Tavsiye edilen değerler parantez içindedir).")

    config = {}
    try:
        config['simulation_duration_min'] = float(input("Her senaryo için simülasyon süresi (dakika) [Örn: 0.7]: ") or "0.7")
        config['vehicle_spawn_rate_ms'] = int(input("Yeni araç oluşturma sıklığı (milisaniye) [Örn: 800]: ") or "800")
        config['base_green_time_sec'] = int(input("Adaptif senaryolar için min. yeşil süre (sn) [Örn: 5]: ") or "5")
        config['max_green_time_sec'] = int(input("Adaptif senaryolar için maks. yeşil süre (sn) [Örn: 15]: ") or "15")
        config['sabit_yesil_sure_sn'] = int(input("Sabit süreli senaryo için yeşil ışık süresi (sn) [Örn: 10]: ") or "10")
        print("Ayarlar başarıyla alındı.\n")
    except ValueError:
        print("Geçersiz giriş. Lütfen sayısal değerler girin. Varsayılan ayarlar kullanılıyor.")
        config = {
            'simulation_duration_min': 0.7,
            'vehicle_spawn_rate_ms': 800,
            'base_green_time_sec': 5,
            'max_green_time_sec': 15,
            'sabit_yesil_sure_sn': 10
        }
    return config

def karsilastirma_grafigi_ciz(sonuclar):
    """Tüm senaryolardan elde edilen sonuçları karşılaştıran grafikleri çizer."""
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 7))
    fig.suptitle('Simülasyon Senaryolarının Performans Karşılaştırması', fontsize=20, y=0.98)

    senaryo_adlari = list(sonuclar.keys())
    renkler = ['#4c72b0', '#55a868', '#c44e52', '#8172b2']

    # Grafik 1: Toplam Geçen Araç Sayısı
    toplam_gecen_arac = [res.get('total_vehicles_passed', 0) for res in sonuclar.values()]

    bars1 = ax1.bar(senaryo_adlari, toplam_gecen_arac, color=renkler)
    ax1.set_title('Kavşaktan Geçen Toplam Araç Sayısı', fontsize=14)
    ax1.set_ylabel('Araç Sayısı', fontsize=12)
    ax1.tick_params(axis='x', rotation=10)
    ax1.set_ylim(top=max(toplam_gecen_arac) * 1.15 if toplam_gecen_arac else 1)
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, yval + 3, int(yval), ha='center', va='bottom')

    # Grafik 2: Ortalama Bekleme Süresi
    ort_bekleme_sureleri = []
    for senaryo in senaryo_adlari:
        if senaryo == '1. Kontrolsüz Kavşak':
            ort_bekleme_sureleri.append(0)
            continue

        wait_times = sonuclar[senaryo].get('waiting_times', {}).get('overall', [])
        ort_bekleme_sureleri.append(np.mean(wait_times) if wait_times else 0)

    bars2 = ax2.bar(senaryo_adlari, ort_bekleme_sureleri, color=renkler)
    ax2.set_title('Araç Başına Ortalama Bekleme Süresi', fontsize=14)
    ax2.set_ylabel('Süre (saniye)', fontsize=12)
    ax2.tick_params(axis='x', rotation=10)
    ax2.set_ylim(top=max(ort_bekleme_sureleri) * 1.15 if ort_bekleme_sureleri else 1)
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.1, f'{yval:.2f} s', ha='center', va='bottom')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

def main():
    """Ana program akışı."""
    config = kullanici_ayarlarini_al()

    tum_sonuclar = {}

    try:
        print("\n--- SENARYO 1: KONTROLSÜZ KAVŞAK (KAZA TESPİTLİ) BAŞLATILIYOR ---")
        sonuc1 = senaryo_1_kontrolsuz.run_simulation(config)
        tum_sonuclar['1. Kontrolsüz Kavşak'] = sonuc1
        print("Senaryo 1 Tamamlandı.\n")

        print("--- SENARYO 2: SIRALI ADAPTİF TRAFİK IŞIĞI BAŞLATILIYOR ---")
        sonuc2 = senaryo_2_sirali_adaptif.run_simulation(config)
        tum_sonuclar['2. Sıralı Adaptif'] = sonuc2
        print("Senaryo 2 Tamamlandı.\n")

        print("--- SENARYO 3: YOĞUNLUK ODAKLI ADAPTİF TRAFİK IŞIĞI BAŞLATILIYOR ---")
        sonuc3 = senaryo_3_yogunluk_adaptif.run_simulation(config)
        tum_sonuclar['3. Yoğunluk Odaklı'] = sonuc3
        print("Senaryo 3 Tamamlandı.\n")

        print("--- SENARYO 4: SABİT SÜRELİ TRAFİK IŞIĞI BAŞLATILIYOR ---")
        sonuc4 = senaryo_4_sabit_sureli.run_simulation(config)
        tum_sonuclar['4. Sabit Süreli'] = sonuc4
        print("Senaryo 4 Tamamlandı.\n")

    except pygame.error as e:
        print(f"\npygame hatası oluştu: {e}")
        print("Simülasyon penceresi kullanıcı tarafından kapatılmış olabilir. Program sonlandırılıyor.")
        sys.exit()

    print("Tüm simülasyonlar tamamlandı. Sonuç grafikleri oluşturuluyor...")
    karsilastirma_grafigi_ciz(tum_sonuclar)

    print("\nProgram başarıyla tamamlandı.")

if __name__ == '__main__':
    main()