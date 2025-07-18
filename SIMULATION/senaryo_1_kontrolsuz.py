import pygame
import random
import sys


def run_simulation(config):
    pygame.init()

    GENISLIK, YUKSEKLIK = 800, 800
    ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
    pygame.display.set_caption("Senaryo 1: Kontrolsüz Kavşak")

    Gri = (50, 50, 50)
    YOL_RENGI = (60, 60, 60)
    CIZGI = (200, 200, 200)
    ARAC_RENKLERI = [(255, 0, 0), (0, 255, 0), (0, 128, 255), (255, 255, 0)]

    saat = pygame.time.Clock()
    YOL_GENISLIGI = 200
    SERIT_GENISLIGI = YOL_GENISLIGI // 2
    ARAC_GENISLIK = 20
    ARAC_YUKSEKLIK = 40
    HIZ = 2.5  # Hızı biraz artıralım

    kavsaktan_gecen_arac_sayisi = 0

    class Arac(pygame.sprite.Sprite):
        def __init__(self, yon):
            super().__init__()
            self.yon = yon
            self.image = pygame.Surface([ARAC_GENISLIK, ARAC_YUKSEKLIK], pygame.SRCALPHA)
            pygame.draw.rect(self.image, random.choice(ARAC_RENKLERI), (0, 0, ARAC_GENISLIK, ARAC_YUKSEKLIK),
                             border_radius=4)
            self.original_image = self.image
            self.rect = self.image.get_rect()
            self.kavsak_gecildi = False

            # Araçları ekranın daha dışından başlat
            if yon == "yukari":
                self.rect.center = (GENISLIK // 2 + SERIT_GENISLIGI // 2, YUKSEKLIK + 60)
                self.image = pygame.transform.rotate(self.original_image, 180)
            elif yon == "asagi":
                self.rect.center = (GENISLIK // 2 - SERIT_GENISLIGI // 2, -60)
            elif yon == "sol":
                self.rect.center = (-60, YUKSEKLIK // 2 + SERIT_GENISLIGI // 2)
                self.image = pygame.transform.rotate(self.original_image, 270)
            elif yon == "sag":
                self.rect.center = (GENISLIK + 60, YUKSEKLIK // 2 - SERIT_GENISLIGI // 2)
                self.image = pygame.transform.rotate(self.original_image, 90)

        def update(self):
            nonlocal kavsaktan_gecen_arac_sayisi

            if self.yon == "yukari":
                self.rect.y -= HIZ
            elif self.yon == "asagi":
                self.rect.y += HIZ
            elif self.yon == "sol":
                self.rect.x += HIZ
            elif self.yon == "sag":
                self.rect.x -= HIZ

            # Kavşağı geçti mi kontrolü
            if not self.kavsak_gecildi:
                if (self.yon == "yukari" and self.rect.bottom < 0) or \
                        (self.yon == "asagi" and self.rect.top > YUKSEKLIK) or \
                        (self.yon == "sol" and self.rect.left > GENISLIK) or \
                        (self.yon == "sag" and self.rect.right < 0):
                    kavsaktan_gecen_arac_sayisi += 1
                    self.kavsak_gecildi = True
                    self.kill()  # Ekrandan çıkınca sil

    araclar = pygame.sprite.Group()
    YENI_ARAC_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(YENI_ARAC_EVENT, config['vehicle_spawn_rate_ms'])

    def kaza_var_mi():
        kavsak_alani = pygame.Rect(GENISLIK // 2 - YOL_GENISLIGI // 2, YUKSEKLIK // 2 - YOL_GENISLIGI // 2,
                                   YOL_GENISLIGI, YOL_GENISLIGI)
        kavsaktaki_araclar = [s for s in araclar if kavsak_alani.colliderect(s.rect)]
        for i, a1 in enumerate(kavsaktaki_araclar):
            for a2 in kavsaktaki_araclar[i + 1:]:
                if a1.rect.colliderect(a2.rect):
                    return True
        return False

    def serit_ve_kavsak_ciz():
        ekran.fill(Gri)
        pygame.draw.rect(ekran, YOL_RENGI, (GENISLIK // 2 - YOL_GENISLIGI // 2, 0, YOL_GENISLIGI, YUKSEKLIK))
        pygame.draw.rect(ekran, YOL_RENGI, (0, YUKSEKLIK // 2 - YOL_GENISLIGI // 2, GENISLIK, YOL_GENISLIGI))
        for y in range(0, YUKSEKLIK, 40): pygame.draw.line(ekran, CIZGI, (GENISLIK // 2, y), (GENISLIK // 2, y + 20), 2)
        for x in range(0, GENISLIK, 40): pygame.draw.line(ekran, CIZGI, (x, YUKSEKLIK // 2), (x + 20, YUKSEKLIK // 2),
                                                          2)

    calisiyor = True
    SIMULATION_DURATION_MS = config['simulation_duration_min'] * 60 * 1000
    simulation_start_time = pygame.time.get_ticks()

    while calisiyor:
        current_time = pygame.time.get_ticks()
        if current_time - simulation_start_time > SIMULATION_DURATION_MS:
            calisiyor = False

        for etkinlik in pygame.event.get():
            if etkinlik.type == pygame.QUIT:
                pygame.quit()
                raise pygame.error("Pencere kapatıldı.")
            elif etkinlik.type == YENI_ARAC_EVENT:
                yeni_yon = random.choice(["yukari", "asagi", "sol", "sag"])
                arac = Arac(yeni_yon)
                araclar.add(arac)

        araclar.update()

        if kaza_var_mi() and calisiyor:  # Çoklu kaza mesajını önle
            print("KAZA MEYDANA GELDİ! Senaryo 1 sonlandırılıyor.")
            calisiyor = False

        serit_ve_kavsak_ciz()
        araclar.draw(ekran)
        pygame.display.flip()
        saat.tick(60)

    pygame.quit()
    return {"total_vehicles_passed": kavsaktan_gecen_arac_sayisi}