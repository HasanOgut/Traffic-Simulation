import pygame
import random
from collections import deque


def run_simulation(config):
    pygame.init()
    GENISLIK, YUKSEKLIK = 800, 800
    FPS = 60
    HIZ = 2
    TAKIP_MESAFESI = 45

    # Config'den alınan ayarlar
    SIMULATION_DURATION_MS = config['simulation_duration_min'] * 60 * 1000
    YENI_ARAC_GELIS_SURESI_MS = config['vehicle_spawn_rate_ms']
    SABIT_YESIL_SURE_SN = config['sabit_yesil_sure_sn']
    YELLOW_TIME_SEC = 2
    ALL_RED_TIME_SEC = 1

    # Renkler
    SIYAH = (0, 0, 0)
    YOL_RENGI = (60, 60, 60)
    CIZGI = (200, 200, 200)
    YESIL = (0, 255, 0)
    KIRMIZI = (255, 0, 0)
    SARI = (255, 255, 0)
    TRAFIK_ISIK_DIS = (100, 100, 100)

    # Boyutlar
    YOL_GENISLIGI = 200
    SERIT_GENISLIGI = YOL_GENISLIGI // 2
    ARAC_GENISLIK = 20
    ARAC_YUKSEKLIK = 40
    ISIK_KUTUSU_GENISLIK = 20
    ISIK_KUTUSU_YUKSEKLIK = 40
    ISIK_DAIRE_YARI_CAP = 7

    ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
    pygame.display.set_caption("Senaryo 4: Sabit Süreli Trafik Işığı")
    saat = pygame.time.Clock()

    # Işık pozisyonları (diğer senaryolarla uyumlu hale getirildi)
    TRAFIK_ISIK_POS = {
        "yukari": (GENISLIK // 2 + SERIT_GENISLIGI // 2 + 40, YUKSEKLIK // 2 + YOL_GENISLIGI // 2 + 10),
        "asagi": (GENISLIK // 2 - YOL_GENISLIGI // 2 - ISIK_KUTUSU_GENISLIK - 10,
                  YUKSEKLIK // 2 - YOL_GENISLIGI // 2 - ISIK_KUTUSU_YUKSEKLIK - 10),
        "sol": (
            GENISLIK // 2 + YOL_GENISLIGI // 2 + 10, YUKSEKLIK // 2 - YOL_GENISLIGI // 2 - ISIK_KUTUSU_YUKSEKLIK - 10),
        "sag": (
            GENISLIK // 2 - YOL_GENISLIGI // 2 - ISIK_KUTUSU_GENISLIK - 10, YUKSEKLIK // 2 + YOL_GENISLIGI // 2 + 10)
    }

    kuyruklar = {yon: deque() for yon in ["yukari", "asagi", "sol", "sag"]}
    GREEN_LIGHT_ORDER = ["yukari", "sag", "asagi", "sol"]  # Standart ışık sırası

    simulation_data = {
        "waiting_times": {"yukari": [], "asagi": [], "sol": [], "sag": [], "overall": []},
        "total_vehicles_passed": 0
    }

    class TrafikIsigiSabitSureli:
        def __init__(self):
            self.durumlar = {yon: "kirmizi" for yon in GREEN_LIGHT_ORDER}
            self.current_direction_idx = -1
            self.active_direction = None
            self.current_light_state = "INITIALIZING"

            self.sabit_yesil_sure_frames = int(SABIT_YESIL_SURE_SN * FPS)
            self.yellow_duration_frames = int(YELLOW_TIME_SEC * FPS)
            self.all_red_duration_frames = int(ALL_RED_TIME_SEC * FPS)
            self.timer_frames = 0

        def _advance_to_next_direction(self):
            self.current_direction_idx = (self.current_direction_idx + 1) % len(GREEN_LIGHT_ORDER)
            self.active_direction = GREEN_LIGHT_ORDER[self.current_direction_idx]

        def guncelle(self):
            self.timer_frames -= 1

            if self.timer_frames <= 0:
                if self.current_light_state == "INITIALIZING":
                    self._advance_to_next_direction()
                    self.current_light_state = "ALL_RED"
                    self.timer_frames = self.all_red_duration_frames

                elif self.current_light_state == "GREEN":
                    self.current_light_state = "YELLOW"
                    self.timer_frames = self.yellow_duration_frames
                    self.durumlar[self.active_direction] = "sari"

                elif self.current_light_state == "YELLOW":
                    self.durumlar[self.active_direction] = "kirmizi"
                    self._advance_to_next_direction()
                    self.current_light_state = "ALL_RED"
                    self.timer_frames = self.all_red_duration_frames

                elif self.current_light_state == "ALL_RED":
                    self.current_light_state = "GREEN"
                    self.timer_frames = self.sabit_yesil_sure_frames
                    self.durumlar[self.active_direction] = "yesil"

        def durum(self, yon_sorgu):
            return self.durumlar.get(yon_sorgu, "kirmizi")

    class Arac(pygame.sprite.Sprite):
        def __init__(self, yon, kuyruk_ref, spawn_time):
            super().__init__()
            self.yon = yon
            self.kuyruk_ref = kuyruk_ref
            self.image = pygame.Surface((ARAC_GENISLIK, ARAC_YUKSEKLIK))
            self.image.fill((random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
            self.original_image = self.image
            self.rect = self.image.get_rect()
            self.spawn_time = spawn_time
            self.kavsak_gecildi = False

            # Araçları doğru pozisyon ve rotasyonda başlat
            if yon == "yukari":
                self.rect.center = (GENISLIK // 2 + SERIT_GENISLIGI // 2, YUKSEKLIK + ARAC_YUKSEKLIK)
            elif yon == "asagi":
                self.rect.center = (GENISLIK // 2 - SERIT_GENISLIGI // 2, -ARAC_YUKSEKLIK)
                self.image = pygame.transform.rotate(self.original_image, 180)
            elif yon == "sol":
                self.rect.center = (GENISLIK + ARAC_YUKSEKLIK, YUKSEKLIK // 2 + SERIT_GENISLIGI // 2)
                self.image = pygame.transform.rotate(self.original_image, 270)
            elif yon == "sag":
                self.rect.center = (-ARAC_YUKSEKLIK, YUKSEKLIK // 2 - SERIT_GENISLIGI // 2)
                self.image = pygame.transform.rotate(self.original_image, 90)

            self.rect = self.image.get_rect(center=self.rect.center)
            kuyruk_ref.append(self)

        def update(self, trafik_obj):
            # Durma çizgileri
            stop_y_yukari = YUKSEKLIK // 2 + YOL_GENISLIGI // 2
            stop_y_asagi = YUKSEKLIK // 2 - YOL_GENISLIGI // 2
            stop_x_sol = GENISLIK // 2 + YOL_GENISLIGI // 2
            stop_x_sag = GENISLIK // 2 - YOL_GENISLIGI // 2

            hareket_edebilir = True

            # 1. Öndeki aracı kontrol et
            try:
                idx = self.kuyruk_ref.index(self)
                if idx > 0:
                    onumdeki_arac = self.kuyruk_ref[idx - 1]
                    if self.yon == "yukari" and self.rect.top - onumdeki_arac.rect.bottom < TAKIP_MESAFESI:
                        hareket_edebilir = False
                    elif self.yon == "asagi" and onumdeki_arac.rect.top - self.rect.bottom < TAKIP_MESAFESI:
                        hareket_edebilir = False
                    elif self.yon == "sol" and self.rect.left - onumdeki_arac.rect.right < TAKIP_MESAFESI:
                        hareket_edebilir = False
                    elif self.yon == "sag" and onumdeki_arac.rect.left - self.rect.right < TAKIP_MESAFESI:
                        hareket_edebilir = False
            except ValueError:
                hareket_edebilir = True  # Kuyrukta değilse (zaten geçmişse), hareket etsin

            # 2. Trafik ışığını kontrol et
            isik_durumu = trafik_obj.durum(self.yon)
            if hareket_edebilir and not self.kavsak_gecildi and isik_durumu in ["kirmizi", "sari"]:
                if self.yon == "yukari" and self.rect.top <= stop_y_yukari:
                    hareket_edebilir = False
                elif self.yon == "asagi" and self.rect.bottom >= stop_y_asagi:
                    hareket_edebilir = False
                elif self.yon == "sol" and self.rect.left <= stop_x_sol:
                    hareket_edebilir = False
                elif self.yon == "sag" and self.rect.right >= stop_x_sag:
                    hareket_edebilir = False

            # 3. Hareket et
            if hareket_edebilir:
                if self.yon == "yukari":
                    self.rect.y -= HIZ
                elif self.yon == "asagi":
                    self.rect.y += HIZ
                elif self.yon == "sol":
                    self.rect.x -= HIZ
                elif self.yon == "sag":
                    self.rect.x += HIZ

            # Kavşak geçişini ve veri toplamayı yönet
            if not self.kavsak_gecildi:
                gecis_sarti = False
                if self.yon == "yukari" and self.rect.top < stop_y_asagi:
                    gecis_sarti = True
                elif self.yon == "asagi" and self.rect.bottom > stop_y_yukari:
                    gecis_sarti = True
                elif self.yon == "sol" and self.rect.left < stop_x_sag:
                    gecis_sarti = True
                elif self.yon == "sag" and self.rect.right > stop_x_sol:
                    gecis_sarti = True

                if gecis_sarti:
                    self.kavsak_gecildi = True
                    wait_time = (pygame.time.get_ticks() - self.spawn_time) / 1000.0
                    simulation_data["waiting_times"][self.yon].append(wait_time)
                    simulation_data["waiting_times"]["overall"].append(wait_time)
                    simulation_data["total_vehicles_passed"] += 1
                    if self in self.kuyruk_ref:
                        self.kuyruk_ref.remove(self)

            # Ekran dışına çıkanları sil
            if (self.rect.bottom < -50 or self.rect.top > YUKSEKLIK + 50 or
                    self.rect.right < -50 or self.rect.left > GENISLIK + 50):
                self.kill()
                if self in self.kuyruk_ref:
                    self.kuyruk_ref.remove(self)

    def arayuz_ciz():
        ekran.fill((50, 50, 50))
        pygame.draw.rect(ekran, YOL_RENGI, (GENISLIK // 2 - YOL_GENISLIGI // 2, 0, YOL_GENISLIGI, YUKSEKLIK))
        pygame.draw.rect(ekran, YOL_RENGI, (0, YUKSEKLIK // 2 - YOL_GENISLIGI // 2, GENISLIK, YOL_GENISLIGI))
        for y in range(0, YUKSEKLIK, 40):
            if y < YUKSEKLIK // 2 - YOL_GENISLIGI // 2 or y > YUKSEKLIK // 2 + YOL_GENISLIGI // 2 - 20:
                pygame.draw.line(ekran, CIZGI, (GENISLIK // 2, y), (GENISLIK // 2, y + 20), 2)
        for x in range(0, GENISLIK, 40):
            if x < GENISLIK // 2 - YOL_GENISLIGI // 2 or x > GENISLIK // 2 + YOL_GENISLIGI // 2 - 20:
                pygame.draw.line(ekran, CIZGI, (x, YUKSEKLIK // 2), (x + 20, YUKSEKLIK // 2), 2)

    def draw_trafik_isigi(x, y, durum_isik):
        pygame.draw.rect(ekran, TRAFIK_ISIK_DIS, (x, y, ISIK_KUTUSU_GENISLIK, ISIK_KUTUSU_YUKSEKLIK))
        pygame.draw.circle(ekran, KIRMIZI if durum_isik == "kirmizi" else SIYAH, (x + 10, y + 9), ISIK_DAIRE_YARI_CAP)
        pygame.draw.circle(ekran, SARI if durum_isik == "sari" else SIYAH, (x + 10, y + 20), ISIK_DAIRE_YARI_CAP)
        pygame.draw.circle(ekran, YESIL if durum_isik == "yesil" else SIYAH, (x + 10, y + 31), ISIK_DAIRE_YARI_CAP)

    araclar = pygame.sprite.Group()
    trafik_yonetimi = TrafikIsigiSabitSureli()
    YENI_ARAC_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(YENI_ARAC_EVENT, YENI_ARAC_GELIS_SURESI_MS)

    calisiyor = True
    simulation_start_time = pygame.time.get_ticks()

    while calisiyor:
        current_time = pygame.time.get_ticks()
        if current_time - simulation_start_time > SIMULATION_DURATION_MS:
            calisiyor = False

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                calisiyor = False
                pygame.quit()
                return simulation_data  # Pencere kapatılırsa o anki veriyi döndür
            if e.type == YENI_ARAC_EVENT:
                yon = random.choice(["yukari", "asagi", "sol", "sag"])
                if len(kuyruklar[yon]) < 12:  # Kuyruk sınırı
                    arac = Arac(yon, kuyruklar[yon], pygame.time.get_ticks())
                    araclar.add(arac)

        trafik_yonetimi.guncelle()
        araclar.update(trafik_yonetimi)

        arayuz_ciz()
        araclar.draw(ekran)
        for yon_key, pos in TRAFIK_ISIK_POS.items():
            draw_trafik_isigi(pos[0], pos[1], trafik_yonetimi.durum(yon_key))

        pygame.display.flip()
        saat.tick(FPS)

    pygame.quit()
    return simulation_data