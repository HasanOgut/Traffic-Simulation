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
    BASE_GREEN_TIME_SEC = config['base_green_time_sec']
    MAX_GREEN_TIME_SEC = config['max_green_time_sec']
    PER_CAR_EXTENSION_SEC = 0.8
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
    pygame.display.set_caption("Senaryo 3: Yoğunluk Odaklı Adaptif Trafik Işığı")
    saat = pygame.time.Clock()

    # Işık pozisyonları
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

    # Veri toplama
    simulation_data = {
        "waiting_times": {"yukari": [], "asagi": [], "sol": [], "sag": [], "overall": []},
        "total_vehicles_passed": 0
    }

    class TrafikIsigiYogunlukAdaptif:
        def __init__(self):
            self.durumlar = {yon: "kirmizi" for yon in kuyruklar.keys()}
            self.active_direction = None
            self.timer_frames = 0
            self.yellow_duration_frames = int(YELLOW_TIME_SEC * FPS)
            self.intergreen_all_red_duration_frames = int(ALL_RED_TIME_SEC * FPS)
            self.current_light_state = "INTERGREEN_ALL_RED"
            self.timer_frames = self.intergreen_all_red_duration_frames  # Başlangıçta tümü kırmızı

        def _choose_next_direction(self, kuyruklar_dict):
            # En uzun kuyruğu bul
            max_len = -1
            chosen_dir = None
            for yon, kuyruk in kuyruklar_dict.items():
                if kuyruk and len(kuyruk) > max_len:
                    max_len = len(kuyruk)
                    chosen_dir = yon
            return chosen_dir

        def _calculate_adaptive_green_frames(self, yon):
            if yon is None:
                return BASE_GREEN_TIME_SEC * FPS
            queue_len = len(kuyruklar[yon])
            calculated_time_sec = BASE_GREEN_TIME_SEC + (queue_len * PER_CAR_EXTENSION_SEC)
            return min(max(calculated_time_sec, BASE_GREEN_TIME_SEC), MAX_GREEN_TIME_SEC) * FPS

        def guncelle(self, kuyruklar_dict_ref):
            self.timer_frames -= 1

            if self.timer_frames <= 0:
                if self.current_light_state == "INTERGREEN_ALL_RED":
                    next_dir = self._choose_next_direction(kuyruklar_dict_ref)
                    if next_dir:
                        self.active_direction = next_dir
                        self.current_light_state = "GREEN"
                        self.timer_frames = self._calculate_adaptive_green_frames(self.active_direction)
                        self.durumlar = {yon: "kirmizi" for yon in self.durumlar}
                        self.durumlar[self.active_direction] = "yesil"
                    else:
                        # Araç yoksa 1 saniye daha bekle
                        self.timer_frames = FPS

                elif self.current_light_state == "GREEN":
                    self.current_light_state = "YELLOW"
                    self.timer_frames = self.yellow_duration_frames
                    self.durumlar[self.active_direction] = "sari"

                elif self.current_light_state == "YELLOW":
                    self.current_light_state = "INTERGREEN_ALL_RED"
                    self.timer_frames = self.intergreen_all_red_duration_frames
                    self.durumlar[self.active_direction] = "kirmizi"
                    self.active_direction = None

        def durum(self, yon_sorgu):
            return self.durumlar.get(yon_sorgu, "kirmizi")

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

    class Arac(pygame.sprite.Sprite):
        def __init__(self, yon, kuyruk_ref, spawn_time):
            super().__init__()
            self.yon = yon
            self.kuyruk_ref = kuyruk_ref
            self.image = pygame.Surface((ARAC_GENISLIK, ARAC_YUKSEKLIK))
            self.image.fill((random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
            self.rect = self.image.get_rect()
            self.spawn_time = spawn_time
            self.kavsak_gecildi = False

            if yon == "yukari":
                self.rect.center = (GENISLIK // 2 - SERIT_GENISLIGI // 2, YUKSEKLIK + ARAC_YUKSEKLIK // 2)
            elif yon == "asagi":
                self.rect.center = (GENISLIK // 2 + SERIT_GENISLIGI // 2, -ARAC_YUKSEKLIK // 2)
                self.image = pygame.transform.rotate(self.image, 180)
            elif yon == "sol":
                self.rect.center = (GENISLIK + ARAC_GENISLIK // 2, YUKSEKLIK // 2 - SERIT_GENISLIGI // 2)
                self.image = pygame.transform.rotate(self.image, 90)
            elif yon == "sag":
                self.rect.center = (-ARAC_GENISLIK // 2, YUKSEKLIK // 2 + SERIT_GENISLIGI // 2)
                self.image = pygame.transform.rotate(self.image, 270)

            self.rect = self.image.get_rect(center=self.rect.center)
            self.kuyruk_ref.append(self)

        def update(self, trafik_obj):
            dur_y_yukari = YUKSEKLIK // 2 + YOL_GENISLIGI // 2 - ARAC_YUKSEKLIK // 2 + 60
            dur_y_asagi = YUKSEKLIK // 2 - YOL_GENISLIGI // 2 + ARAC_YUKSEKLIK // 2 - 60
            dur_x_sol = GENISLIK // 2 + YOL_GENISLIGI // 2 - ARAC_GENISLIK // 2 + 60
            dur_x_sag = GENISLIK // 2 - YOL_GENISLIGI // 2 + ARAC_GENISLIK // 2 - 60

            hareket_edebilir = True
            isik_durumu = trafik_obj.durum(self.yon)

            # Öndeki aracı kontrol et
            if self.kuyruk_ref and self.kuyruk_ref[0] != self:
                try:
                    idx = list(self.kuyruk_ref).index(self)
                    if idx > 0:
                        onundeki_arac = self.kuyruk_ref[idx - 1]
                        if self.yon == "yukari" and self.rect.top <= onundeki_arac.rect.bottom + TAKIP_MESAFESI:
                            hareket_edebilir = False
                        elif self.yon == "asagi" and self.rect.bottom >= onundeki_arac.rect.top - TAKIP_MESAFESI:
                            hareket_edebilir = False
                        elif self.yon == "sol" and self.rect.left <= onundeki_arac.rect.right + TAKIP_MESAFESI:
                            hareket_edebilir = False
                        elif self.yon == "sag" and self.rect.right >= onundeki_arac.rect.left - TAKIP_MESAFESI:
                            hareket_edebilir = False
                except:
                    pass

            # Işık durumuna göre hareket et
            if hareket_edebilir and not self.kavsak_gecildi:
                if (isik_durumu == "kirmizi" or isik_durumu == "sari"):
                    if self.yon == "yukari" and self.rect.bottom <= dur_y_yukari + 5:
                        hareket_edebilir = False
                    elif self.yon == "asagi" and self.rect.top >= dur_y_asagi - 5:
                        hareket_edebilir = False
                    elif self.yon == "sol" and self.rect.right <= dur_x_sol + 5:
                        hareket_edebilir = False
                    elif self.yon == "sag" and self.rect.left >= dur_x_sag - 5:
                        hareket_edebilir = False

            if hareket_edebilir:
                if self.yon == "yukari":
                    self.rect.y -= HIZ
                elif self.yon == "asagi":
                    self.rect.y += HIZ
                elif self.yon == "sol":
                    self.rect.x -= HIZ
                elif self.yon == "sag":
                    self.rect.x += HIZ

                # Kavşak geçiş kontrolü
                if not self.kavsak_gecildi:
                    if ((self.yon == "yukari" and self.rect.bottom <= dur_y_yukari) or
                            (self.yon == "asagi" and self.rect.top >= dur_y_asagi) or
                            (self.yon == "sol" and self.rect.right <= dur_x_sol) or
                            (self.yon == "sag" and self.rect.left >= dur_x_sag)):
                        self.kavsak_gecildi = True
                        wait_time = pygame.time.get_ticks() - self.spawn_time
                        simulation_data["waiting_times"][self.yon].append(wait_time / 1000.0)
                        simulation_data["waiting_times"]["overall"].append(wait_time / 1000.0)
                        simulation_data["total_vehicles_passed"] += 1

            # Ekran dışına çıkan araçları kaldır
            if (self.rect.bottom < 0 or self.rect.top > YUKSEKLIK or
                    self.rect.right < 0 or self.rect.left > GENISLIK):
                self.kill()
                if self in self.kuyruk_ref:
                    self.kuyruk_ref.remove(self)

    araclar = pygame.sprite.Group()
    trafik_yonetimi = TrafikIsigiYogunlukAdaptif()
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
                return simulation_data
            elif e.type == YENI_ARAC_EVENT:
                yon = random.choice(["yukari", "asagi", "sol", "sag"])
                if len(kuyruklar[yon]) < 15:  # Kuyruk sınırı
                    arac = Arac(yon, kuyruklar[yon], current_time)
                    araclar.add(arac)

        trafik_yonetimi.guncelle(kuyruklar)
        arayuz_ciz()

        for yon_key, pos in TRAFIK_ISIK_POS.items():
            draw_trafik_isigi(pos[0], pos[1], trafik_yonetimi.durum(yon_key))

        araclar.update(trafik_yonetimi)
        araclar.draw(ekran)

        pygame.display.flip()
        saat.tick(FPS)

    pygame.quit()
    return simulation_data