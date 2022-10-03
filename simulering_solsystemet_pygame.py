import sys # importerer modul for å manipulere kjøretidsmiljøet
import pygame # importerer bibliotek for å bruke pygame
import datetime # importerer bibliotek for å bruke datoer i python
from dateutil.relativedelta import relativedelta # bibliotek for å kunne manipulere datetime, som f.eks å legge til en måned til en dato
from custom_pygame_elements import Image, Button, Text # importerer modul med klassene Image, Button og Text for å enkelt lage og vise elementer i pygame
from storage import Storage # importerer modul med klassen Storage for å lagre simuleringstilstand slik at man kan gjenoppta en simulering 
import os
os.chdir(os.path.dirname(os.path.abspath(__file__))) # set cwd

pygame.init() # initaliserer pygame moduler

SCREEN = pygame.display.set_mode((800,700), pygame.RESIZABLE) # initaliserer skjermen. Start 800x700. Er resizable.
pygame.display.set_caption("Simulering solsystemet") # legger til undertittel 
appIcon = pygame.image.load("./app_icon.png") # laster inn app icon
pygame.display.set_icon(appIcon) # legger til app icon

FPS = 60 # max FPS for simulering 

CLOCK = pygame.time.Clock() # lager ny pygame klokke 

CONVERT = 1/4182695000 # et veldig lite tall for å gå fra virkelig avstand til pixler i pygame. 1 pixel tilsvarer altså 4 182 695 000 m i virkeligheten 

grav_const = 6.67430e-11 # gravitasjonskonstanten 

storage = Storage() # storage objekt for å lagre og hente lagret simuleringsstilstand 

def aks(x: float, y: float, mass: float) -> tuple[float, float]: 
    """
    funksjon for å finne akselerasjonsvektor til et objekt når gravitasjonskraften fra et objekt med masse lik parameteren masse, virker på objektet. x er avstanden i x retning i et koordinatsystem, og y er avstanden i y retning i et koordinatsystem. 
    """
    r = (x**2 + y**2)**0.5 # avstanden (rett linje) fra objektet som virker med gravitasjonskraft til okjektet vi kalkulerer akselerasjonen til. Lengde av vektor
    a_x = -grav_const*mass*x/r**3 # kalkulerer akselerasjonen til objektet i x retning ut fra massen til objektet som trekker med gravitasjonskraften, avstanden i x retning og avstanden i rett linje mellom de to objektene
    a_y = -grav_const*mass*y/r**3 # kalkulerer akselerasjonen til objektet i y retning ut fra massen til objektet som trekker med gravitasjonskraften, avstanden i y retning og avstanden i rett linje mellom de to objektene
    return a_x, a_y # returnerer akselerasjonsvektoren som er kalkulert 


class Space_object(pygame.sprite.Sprite): 
    """ 
    Klasse for å vise, flytte og oppdaterer romobjekter. Arver fra pygame sprite klasse noe som gjør at vi kan lage sprite-er (2D bilder) i pygame og gjør det enkelt å flytte og vise objektetene til skjermen 
    """
    def __init__(self, sprite_group: pygame.sprite.Group, name: str, img_path: str, size: float, mass: float, x: float, y: float, v_x: float, v_y: float): # initialsierer klasse
        super().__init__(sprite_group) # initialiserer sprite klasse og legger til objektet til sprite gruppe
        self.size = size # størrelsen på bildet som vises 
        self.img_path = img_path # path til bilde som vises
        self.name = name # navn til objektet
        self.mass = mass # masse til objektet
        self.x = x # virkelig x koordinat 
        self.y = y # virkelig y koordinat
        self.v_x = v_x # x verdi i fartsvektor
        self.v_y = v_y # y verdi i fartsvektor
        self.a_x = 0 # x verdi i akselerasjonsvektor
        self.a_y = 0 # y verdi  akselerasjonsvektor
        self.image = pygame.image.load(self.img_path).convert_alpha() # laster inn bilde som vises til skjermen
        self.image = pygame.transform.scale(self.image, (self.size, self.size)) # skalerer bilde til riktig størrelse
        self.rect = self.image.get_rect() # lager et pygame rect for å endre på posisjonen og manipulere objektet når det vises på skjermen
        self.rect.center = (pygame.display.get_surface().get_width()/2, pygame.display.get_surface().get_height()/2) # setter senter av rect til midten av skjermen
        self.rect.x = self.x * CONVERT  # gjør om fra virkelig x koordinat til posisjonen langs x retning i pygame 
        self.rect.y = -self.y * CONVERT # gjør om fra virkelig y koordinat til posisjonen langs y retning i pygame. Siden at jo større y koordinat i pygame betyr lengre ned på skjermen (altså motsatt av et vanligkoordinatsystem), må vi ta den negative y-koordinaten for å få riktig plassering på skjermen.
           
    def update_aks(self, space_objects): # metode for å oppdaterer akselerasjonsvektoren til objektet
        self.a_x = 0 # nullstiller akselerasjonen
        self.a_y = 0 # nullstiller akselerasjonen 
        for space_object in space_objects: # looper gjennom alle romobjekter
            if space_object is not self: # så lenge at romobjektet ikke er den selv, kalkuler akselerasjonen objektet (self) får ut fra gravitasjonskraften fra det fremmede objektet
                d_x = self.x - space_object.x # avstand mellom objektene i x retning
                d_y = self.y - space_object.y # avstand mellom objektene i y retning
                a_x, a_y = aks(d_x, d_y, space_object.mass) # regner ut akselerasjonen objektet får fra det fremmede objektet 
                self.a_x += a_x # legger til akselerasjon i x retning 
                self.a_y += a_y # legger til akselerasjon i y retning
                  
    def update_pos(self, dt, zoom, half_w, half_h): # metode for å oppdaterer posisjonen til objektet
        self.v_x += self.a_x*dt # oppdaterer fartsvektoren ut fra akselerasjon og tidsendring
        self.v_y += self.a_y*dt  # oppdaterer fartsvektorenut fra akselerasjon og tidsendring
        self.x += self.v_x*dt # oppdaterer x koordinat ut fra fartsvektor og tidsendring
        self.y += self.v_y*dt# oppdaterer y koordinat ut fra fartsvektor og tidsendring
        self.update_rect(zoom, half_w, half_h) # kaller metode for å oppdaterer rect slik at posisjonen til bildet som vises på skjermen også endres
        
    def update_rect(self, zoom, half_w, half_h): # metode for å oppdaterer rect, altså posisjonen til bildet på skjermen ut fra vireklig posisjon
        self.rect.center = (half_w,half_h) # setter senter av rect til midten av skjermen
        self.rect.x += self.x * CONVERT * zoom # gjør om fra virkelig x koordinat til posisjonen langs x retning i pygame ut fra CONVERT og zoom level
        self.rect.y -= self.y * CONVERT * zoom # gjør om fra virkelig y koordinat til posisjonen langs y retning i pygame ut fra CONVERT og zoom level. Siden at jo større y koordinat i pygame betyr lengre ned på skjermen (altså motsatt av et vanligkoordinatsystem), må vi ta den negative y-koordinaten for å få riktig plassering på skjermen.

    def update_image_size(self, zoom, half_w, half_h): # metode for å oppdatete bildestørrelse når zoom endres 
        self.image = pygame.image.load(self.img_path).convert_alpha() # laster inn bilde på nytt
        self.image = pygame.transform.scale(self.image, (self.size * zoom, self.size*zoom)) # skalerer bilde til riktig størrelse
        self.rect = self.image.get_rect() # lager et nytt pygame rect
        self.update_rect(zoom, half_w, half_h) # oppdaterer rect ut fra zoom level 
        
            
class CameraGroup(pygame.sprite.Group): # Klasse som for å manipulere kameraet. Arver fra sprite gruppe, og inneholder alle romobjekter (space_object). 
    def __init__(self): # initialiserer klasse
        super().__init__() # initialiserer sprite group klasse slik at CameraGroup fungerer som sprite gruppe 
        self.display_surface = pygame.display.get_surface() # overflate (skjerm) som CameraGroup tegner på 
        self.offset = pygame.math.Vector2(0,0) # camera offset. Trekker fra camera offset fra alle objekter slik at vi får en motbevegelse og det virker derfor som at kameraet beveger på seg. 
        self.half_w = self.display_surface.get_size()[0] // 2 # halve bredden av skjermen 
        self.half_h = self.display_surface.get_size()[1] // 2 # halve høyden av skjermen 
        self.keyboard_speed = 2 # Hastigheten til kamera bevegelsen når kameraet blir styrt med taster 
        self.target = None # kamera target (target som kamera fokuserer på)
        self.zoom_scale = 1 # zoom 
        self.dt_per_s = 86400 # tidssteg per sekund i simuleringen 
        self.dt = 0 # tidssteg. Blir kalkulert ut fra dt_per_s og FPS slik at tidssteg per sekund blir lik uavhengig av FPS 
        
    def update_display_suface(self): # metode for å oppdatere display når størrelsen på skjermen blir endret
        self.display_surface = pygame.display.get_surface() # overflate (skjerm) som CameraGroup tegner på 
        self.half_w = self.display_surface.get_size()[0] // 2 # halve bredden av skjermen 
        self.half_h = self.display_surface.get_size()[1] // 2 # halve høyden av skjermen 
        for sprite in self.sprites(): # looper igjennom alle romobjekter og oppdaterer rect slik at den blir plassert riktig i skjermen
            sprite.update_rect(self.zoom_scale, self.half_w, self.half_h)
        
    def init_state(self): # metode for å initialsierer tilstand ut fra lagret data slik at en simulering kan gjenopptas   
        storage_data = storage.get() # henter data som er lagret i fil 
        for sprite in self.sprites(): # looper igjennom alle romobjekter (altså alle sprites i gruppa)
            for space_object_json in storage_data["space_objects"]: # looper gjennom lagret data om romobjekter
                if sprite.name == space_object_json["name"]: # hvis navnet til spriten og navnet til romobjektet som er lagret er lik, oppdater informasjon om sprite 
                    sprite.x = space_object_json["x"] # setter x koordinat til lagret x koordinat 
                    sprite.y = space_object_json["y"] # setter y koordinat til lagret y koordinat 
                    sprite.v_x = space_object_json["v_x"] # setter fartsvektor til lagret fartsvektor
                    sprite.v_y = space_object_json["v_y"] # setter fartsvektor til lagret fartsvektor
                    sprite.update_image_size(storage_data["zoom"], self.half_w, self.half_h) # oppdaterer bildestørrelse ut fra lagret zoom
        
        self.zoom_scale = storage_data["zoom"] # setter zoom til lagret zoom
        self.offset = pygame.math.Vector2(storage_data["camera_offset"][0],storage_data["camera_offset"][1]) # oppdaterer offset til kameraet slik at kamera er plassert riktig ut fra kameras lagret posisjon
        self.dt_per_s = storage_data["dt_per_s"] # oppdaterer tidsendring per sekundt til lagret tidsendring per sekund
        
    def update_aks(self): # kalles metoden update_aks for alle romobjekter (space_object), noe som kalkulerer akselerasjonen for alle romobjektene
        for sprite in self.sprites(): # looper gjennom alle sprites
            sprite.update_aks(self.sprites()) # kaller metoden update_aks
            
    def update_pos(self): # kaller metoden update_pos for alle romobjekter (space_object)
        for sprite in self.sprites(): # looper gjennom alle sprites 
            sprite.update_pos(self.dt, self.zoom_scale, self.half_w, self.half_h) # kaller metoden update_pos
            
    def update_image_sizes(self): # metode for å oppdaterer størrelsen på bilene til alle remobjektene i gruppa. Brukes for å gjøre bildene større eller mindre avhengig av zoom_scale 
        for sprite in self.sprites(): # looper gjennom alle spriter (romobjekter)
            sprite.update_image_size(self.zoom_scale, self.half_w, self.half_h) # kaller metoden update_image_size for alle spriter i klassen
            
    def center_target_camera(self): # metode for å gjøre at kameraet forkuserer på et objekt
        self.offset.x = self.target.rect.centerx - self.half_w # setter offset i x retning til target x koordinater - halve bredden av skjermen. Dette vil gjøre at target blir i midten av skjermen når offset blir trekt fra alle objekter
        self.offset.y = self.target.rect.centery - self.half_h # setter offset i y retning til target y koordinater - halve høyden av skjermen. Dette vil gjøre at target blir i midten av skjermen når offset blir trekt fra alle objekter
        
    def keyboard_control(self): # metode for å kontrollere kameraet og tidssteg med taster
        keys = pygame.key.get_pressed() # metode som returnerer alle kanpper som er presset
        ### kamera bevegelse
        if keys[pygame.K_a] and self.target == None: # hvis a er trykket, trekk i fra keyboard_speed fra offset i x retning slik at kameraet beveger seg mot venstre
            self.offset.x -= self.keyboard_speed
        if keys[pygame.K_d] and self.target == None: # hvis d er trykket, legg til keyboard_speed til offset i x retning slik at kameraet beveger seg mot høyre
            self.offset.x += self.keyboard_speed
        if keys[pygame.K_w] and self.target == None: # hvis w er trykket, trekk i fra keyboard_speed fra offset i y retning slik at kameraet beveger seg oppover
            self.offset.y -= self.keyboard_speed
        if keys[pygame.K_s] and self.target == None: # hvis s er trykket, legg til keyboard_speed til offset i y retning slik at kameraet beveger seg nedover
            self.offset.y += self.keyboard_speed
            
        ### zoom
        if keys[pygame.K_LEFT] and self.zoom_scale <= 5: # hvis venstre tast er trykket, og zoom_scale er mindre eller lik 5
            self.zoom_scale += 0.02 # legg til 0.02 til zoom_scale slik at kameraet zoomer inn  
            self.update_image_sizes() # oppdater alle bildestørrelsene til romobjektene
        if keys[pygame.K_RIGHT] and self.zoom_scale >= 0.3: # hvis høyre tast er trykket, og zoom_scale er større eller lik 0.3 
            self.zoom_scale -= 0.02 # trekk i fra 0.02 fra zoom_scale slik at kameraet zoomer ut 
            self.update_image_sizes() # oppdater alle bildestørrelsene til romobjektene
            
        ### tidssteg
        if keys[pygame.K_UP]: # hvis opp tast er trykket
            self.dt_per_s += 1000 + self.dt_per_s*0.001 # legger til 1000 og i tudendel av dt_per_s slik at tidsendring per sekund øker eksponentielt 
        if keys[pygame.K_DOWN]: # hvis ned tast er trykket
            self.dt_per_s -= 1000 + self.dt_per_s*0.001 # trekker fra 1000 og en tudendel av dt_per_s slik at tidsendring per sekund synker eksponentielt 
            
    def check_mouse_click(self, mx, my): # metode som sjekker om et romobjekt er klikket 
        for sprite in self.sprites(): # loops gjennom alle spriter (romobjekter) i gruppa
            rect = sprite.rect # setter rect lik rect til sprite
            if rect.collidepoint(mx+self.offset.x, my+self.offset.y): # ser om mus posisjonen + offset har samme posisjon som en av elementene, fordi da trykker musa på en av objektene
                self.target = sprite # setter target til spriten (romobjektet) som ble klikket
                break # stopper for-loopen 
            else: # objektet er ikke klikket
                self.target = None # nullstiller target
        
    def custom_draw(self): # metode som tegner romobjektene til skjermen
        self.keyboard_control() # kaller metoden keyboard_control for å kontrollere kameraet og tidssteg med taster
        
        if self.target != None: # hvis et target er satt, kall metoden center_target_camera slik at kameraet fokuserer på objektet
            self.center_target_camera() 
          
        for sprite in self.sprites(): # looper gjennom alle spriter (romobjekter)
            offset_position = sprite.rect.topleft - self.offset # kalkulerer posisjonen til bildet ut fra posisjonen til rect minus offset slik at vi får en motbevegelse til kameraet slik at det virker som at kameraet flytter på seg
            self.display_surface.blit(sprite.image, offset_position) # viser bildet med kalkulert posisjon til skjermen  
    
        return self.target # returnerer kamera target
 

default_date = datetime.date(2022, 1, 1) # startdato for simulering. Startposisjonen til alle objekter er hentet fra denne datoen

def init_camera_group(): # funksjon som initialiserer kamera gruppen med alle romobjektene 
    camera_group = CameraGroup() # lager en kamera gruppe som skal inneholde alle romobjektene som skal vises til skjermen
    ### Avstand er gitt fra solsystemets barycenter
    ### basert på 1 januar 2022 
    ### https://ssd.jpl.nasa.gov/horizons/app.html#/ (tallene står i km, så må endres til m)
    ### Parametere til space_object (alle tall er oppgitt ut fra SI-enheter)
    ### sprite gruppe, navn, path til bilde, bildestørrelse, masse, x koordinat, y koordinat, x fartsvektor, y fartsvektor
    Space_object(camera_group, "Sola", "sun.jpeg", 15, 1.98847e30, -1.283674643550172e9, 5.007104996950605e8, -5.809369653802155, -1.461959576560110e1)
    Space_object(camera_group, "Merkur", "mercury.jpeg", 3, 0.30104e24, 5.242617205495467e10, -5.596063357617276e9, -3.931719860392732e3, 5.056613955108243e4) 
    Space_object(camera_group, "Venus", "venus.jpeg", 5, 4.8673e24, -1.143612889654620e10, 1.076180391552140e11, -3.498958532524220e4, -3.509011592387367e3) 
    Space_object(camera_group, "Jorda", "earth.jpeg", 6, 5.9722e24, -2.741147560901964e10, 1.452697499646169e11, -2.981801522121922e4, -5.415519940416356e3) 
    Space_object(camera_group, "Mars", "mars.jpeg", 4, 0.64169e24, -1.309510737126251e11, -1.893127398896606e11, 2.090994471204196e4, -1.160503586188451e4) 
    Space_object(camera_group, "Jupiter", "jupiter.jpeg", 13, 1898.13e24, 6.955554713494443e11, -2.679620040967891e11, 4.539612624165795e3, 1.280513202430234e4) 
    Space_object(camera_group, "Saturn", "saturn.png", 20, 568.32e24, 1.039929082221698e12, -1.056650148100382e12, 6.345150014839902e3, 6.756117343710409e3) 
    Space_object(camera_group, "Uranus", "uranus.jpeg", 12, 86.811e24, 2.152570437700128e12, 2.016888245555490e12, -4.705853565766252e3, 4.652144641704226e3) 
    Space_object(camera_group, "Neptun", "neptune.jpeg", 12, 102.409e24, 4.431790029686977e12, -6.114486878028781e11, 7.066237951457524e2, 5.417076605926207e3)
    return camera_group  # returnerer kamera gruppe 
    
def update_display(width, height):# funksjon for å oppdatere størrelsen på skjermen
    if width < 800: # hvis with er mindre enn 800
        width = 800 # sett width til 800
    if height < 600: # hvis height er mindre enn 600
        height = 600 # sett height til 600
        
    global SCREEN # for å kunne oppdatere en global variabel       
    SCREEN = pygame.display.set_mode((width, height),pygame.RESIZABLE) # oppdaterer SCREEN til ny størrelse
    return width, height # returnerer width og height 

def welcome_screen(): # funksjon som viser welcome screen
    run = True # variabel for å avgjøre om screen loop skal fortsette (hvis den blir satt til False slutter denne skjermen å oppdateres)
    welcome_screen_group = pygame.sprite.Group() # sprite gruppe for alle elementer i welcome screen
    
    if storage.get() == None:  # hvis storage er tum
        start_button = Button(welcome_screen_group, "snsbtn.png", (70*3.2125, 70), (0, -30), alignments=["centerx", "endy"]) # lager kanpp for å starte simulering 
        continue_button = Button(welcome_screen_group, "gsbtn.png", (0, 0), (0, 0)) # lager knapp men skal ikke vises fordi man kan ikke gjenoppta en simulering da data ikke eksisterer
        welcome_screen_group.remove(continue_button) # fjerner fra sprite gruppe fordi knapp skal ikke vises
        continue_button.is_clickable = False # gjør at knappen ikke kan trykkes  
    else: # storage er ikke tum 
        start_button = Button(welcome_screen_group, "snsbtn.png", (70*3.2125, 70), (150, -30), alignments=["centerx", "endy"]) # lager knapp for å starte simulering
        continue_button = Button(welcome_screen_group, "gsbtn.png", (70*3.2125, 70), (-150, -30), alignments=["centerx", "endy"]) # lager knapp for å gjenoppta simulering

    Text(welcome_screen_group, "Simulering solsystemet", (0,30), alignments=["centerx"], font_size=40) # lager tekst som vises til skjermen
    left_button = Button(welcome_screen_group, "arrow-left.png", (40,40), (15,0), alignments=["centery"]) # lager kanpp for å gå til forrige slide
    right_button = Button(welcome_screen_group, "arrow-right.png", (40,40), (-15,0), alignments=["centery", "endx"]) # lager kanpp for å gå til neste slide
    welcome_screen_group.remove(left_button) # viser ikke left knapp i starten fordi det ikke går an å gå til venstre da slide er på index 0
    left_button.clickable = False # gjør at ikke left knapp registrerer klikk i starten 
    
    current_text = Text(welcome_screen_group, "Bruk wasd for å bevege på kameraet", (0,-50), alignments=["centerx", "centery"]) # tekst som vises
    current_img = Image(welcome_screen_group, "wasd.png",(200,120), (0,50), alignments=["centerx", "centery"] ) # bilde som vises
    
    current_slider_page = 0 # hvilken slide som skal vises
    background_image = pygame.image.load("background.jpeg").convert_alpha() # laster inn bakgrunnsbilde som vises
    background_image = pygame.transform.scale(background_image, pygame.display.get_surface().get_size()) # scaler til størrelsen av skjermen

    def slider_change(index, sprite_group, text, img, right_button, left_button): # funksjon som oppdater hvilken slide som vises til skjermen
        sprite_group.remove(text) # fjerner text fra sprite gruppe 
        sprite_group.remove(img) # fjerner bilde fra sprite gruppe
        alignments = ["centerx", "centery"] # posisjonsjusteringer for bilde og tekst 
        if index == 0: 
            text = Text(sprite_group, "Bruk wdsa for å bevege på kameraet", (0,-50), alignments=alignments) # lager ny text og legger til i sprite gruppe slik at den vises på skjermen
            img =  Image(sprite_group, "wasd.png",(220,120), (0,50), alignments=alignments ) # lager nytt bilde og legger til i sprite gruppe slik at den vises på skjerm
        elif index == 1: 
            text = Text(sprite_group, "Venstreklikk på en planet for å følge og se informasjon om planeten", (0,-50), alignments=alignments) # lager ny text og legger til i sprite gruppe slik at den vises på skjermen
            img = Image(sprite_group, "mouse1.jpeg", (100,100), (0,50), alignments=alignments) # lager nytt bilde og legger til i sprite gruppe slik at den vises på skjerm
        elif index == 2: 
            text = Text(sprite_group, "Bruk venstre og høyre tast for å zoome", (0,-50), alignments=alignments) # lager ny text og legger til i sprite gruppe slik at den vises på skjermen
            img = Image(sprite_group, "leftrightkeys.png", (220,100), (0,50), alignments=alignments) # lager nytt bilde og legger til i sprite gruppe slik at den vises på skjerm
        elif index == 3: 
            text = Text(sprite_group, "Bruk opp og ned tast for å øke/senke tidsendringen i simuleringen", (0,-50), alignments=alignments) # lager ny text og legger til i sprite gruppe slik at den vises på skjermen
            img = Image(sprite_group, "updownkeys.png", (220,100), (0,50), alignments=alignments) # lager nytt bilde og legger til i sprite gruppe slik at den vises på skjerm
        elif index == 4: 
            text = Text(sprite_group, "Trykk mellomrom for å pause simuleringen eller på pause knappen", (0,-50), alignments=["centerx", "centery"]) # lager ny text og legger til i sprite gruppe slik at den vises på skjermen
            img = Image(sprite_group, "spacekey.png", (310,100), (0,50), alignments=alignments) # lager nytt bilde og legger til i sprite gruppe slik at den vises på skjerm
        elif index == 5: 
            text = Text(sprite_group, "Trykk på r tasten eller på replay knappen for å starte simuleringen på nytt", (0,-50), alignments=["centerx", "centery"]) # lager ny text og legger til i sprite gruppe slik at den vises på skjermen
            img = Image(sprite_group, "rkey.png", (220,100), (0,50), alignments=alignments) # lager nytt bilde og legger til i sprite gruppe slik at den vises på skjerm
        elif index == 6: 
            text = Text(sprite_group, "Trykk på h for å gjemme bort tall fra skjermen og bare vise simulering", (0,-50), alignments=["centerx", "centery"]) # lager ny text og legger til i sprite gruppe slik at den vises på skjermen
            img = Image(sprite_group, "hkey.png", (220,100), (0,50), alignments=alignments) # lager nytt bilde og legger til i sprite gruppe slik at den vises på skjerm
        elif index == 7: 
            text = Text(sprite_group, "Trykk på c eller på center camera knappen for å nullstille kameraet", (0,-50), alignments=["centerx", "centery"]) # lager ny text og legger til sprite i gruppe slik at den vises på skjermen
            img = Image(sprite_group, "ckey.png", (220,120), (0,50), alignments=alignments) # lager nytt bilde og legger til i sprite gruppe slik at den vises på skjerm
        elif index == 8: 
            text = Text(sprite_group, "Trykk på i eller på hjem knappen for å gå til start siden", (0,-50), alignments=["centerx", "centery"]) # lager ny text og legger til i sprite gruppe slik at den vises på skjermen
            img = Image(sprite_group, "ikey.png", (220,120), (0,50), alignments=alignments) # lager nytt bilde og legger til i sprite gruppe slik at den vises på skjerm
        elif index == 9: 
            text = Text(sprite_group, "Trykk på k eller på kalender knappen for å gå til velg startdato for simulering siden", (0,-50), alignments=["centerx", "centery"]) # lager ny text og legger til i sprite gruppe slik at den vises på skjermen
            img = Image(sprite_group, "kkey.png", (220,120), (0,50), alignments=alignments) # lager nytt bilde og legger til i sprite gruppe slik at den vises på skjerm
            
        if index == 0: # fjerner left button siden slide index er 0 og da kan man ikke gå mer tilbake
            sprite_group.remove(left_button) # fjerner left_button fra sprite gruppe slik at den ikke vises mer
            left_button.clickable = False # gjør at det den ikke kan registrere klikk  

        elif left_button not in sprite_group.sprites(): # hvis index slide index ikke er 0 og left_button ikke er i sprite gruppe 
            sprite_group.add(left_button) # legger til left_button til sprite gruppe
            left_button.clickable = True # gjør at knappen trykkbar igjen 
            
        if index == 9: # hvis slide index er 9 fjern right_button fordi man er på siste slide og kan ikke gå til neste slide
            sprite_group.remove(right_button) # fjerner right_button fra sprite gruppe slik at den ikke vises mer
            right_button.clickable = False # gjør at right_button ikke kan registrere klikk 
        
        elif right_button not in sprite_group.sprites(): # hvis slide index ikke er 9 og right_button ikke er i sprite gruppe 
            sprite_group.add(right_button) # legger til right_button til sprite gruppe 
            right_button.clickable = True # gjør at knappen er trykkbar igjen
            
        return text, img # returnerer tekst og bilde som skal vises
    
    while run: # pygame screen loop for welcome_screen
        CLOCK.tick(FPS) # oppdaterer klokka og gjør at max FPS ikke overstiges
        for event in pygame.event.get(): # looper igjennom pygame eventer
            if event.type == pygame.QUIT: # hvis event er lik pygame.QUIT, bruker ber om å lukke spillet 
                run = False # avslutter welcome_screen loop  
                quit_game() # avslutter spillet 
                
            if event.type == pygame.VIDEORESIZE: # window blir resize-et
                width, height = event.size # setter bredde og høyde til størrelsen på vindu når det blir resize-et
                width, height = update_display(width, height) # oppdaterer størrelsen på skjermen 
                background_image = pygame.image.load("background.jpeg").convert_alpha() # laster inn bakgrunnsbilde som vises på nytt
                background_image = pygame.transform.scale(background_image, (width, height))
                for sprite in welcome_screen_group: # looper igjennom alle spriter i welcome_screen_group og initialiserer posisjonen slik at posisjonen blir rett med alignments og ny screen størrelse
                    sprite.init_pos()
                if left_button not in welcome_screen_group.sprites(): # hvis left_button ikke er i welcome_screen_group 
                    left_button.init_pos() # initialiser posisjonen
                if right_button not in welcome_screen_group.sprites(): # hvis right_button ikke er i welcome_screen_group     
                    right_button.init_pos() # initialiser posisjonen
                
              
        ### sjekk om kanapper er klikket        
        if start_button.is_clicked(): # start_button er klikket, start nytt spill 
            run = False # avslutt welcome_screen loop 
            choose_date_screen("welcome_screen", datetime.date.today()) # bytter til choose_date_screen
          
        if continue_button.is_clicked(): # continue_button er klikket, gjenoppta simulering
            run = False # avslutt welcome_screen loop 
            camera_group = init_camera_group() # initialiserer og returnerer camera_group med romobjekter
            camera_group.init_state() # initialiserer camera_group tilstand basert på lagret data 
            simulation_screen(camera_group, storage.get()["time"]) # bytter til simulation_screen slik at simulering vises

        if right_button.is_clicked(): # right_button er klikket, vis neste slide 
            current_slider_page += 1 # legger til 1 til current_slider_page
            current_text, current_img = slider_change(current_slider_page, welcome_screen_group, current_text, current_img, right_button, left_button) # oppdaterer slider
        
        if left_button.is_clicked(): # right_button er klikket, vis forrige slide 
            current_slider_page -= 1 # trekker fra 1 fra current_slider_page
            current_text, current_img = slider_change(current_slider_page, welcome_screen_group, current_text, current_img, right_button, left_button) # oppdaterer slider
        
        ### tegn elementer til skjerm
        SCREEN.blit(background_image, (0,0)) # tegner bakgrunnsbilde
        welcome_screen_group.draw(SCREEN) # tegner alle elementer i gruppa til skjermen
        pygame.display.update() # oppdaterer display 
   

def choose_date_screen(prev_screen, selected_date): # funksjon som viser choos_date_screen
    run = True # variabel for å avgjøre om screen loop skal fortsette (hvis den blir satt til False slutter denne skjermen å oppdateres)
    choose_date_screen_group = pygame.sprite.Group() # sprite gruppe for alle elementer i choose_date_screen

    Text(choose_date_screen_group, "Velg startdato for simulering", (0,-200), alignments=["centerx", "centery"]) # tekst som vises til skjermen

    year_text = Text(choose_date_screen_group, str(selected_date.year), (-100,0), alignments=["centery", "centerx"]) # tekst som viser hvilket år som er valgt
    year_up_btn = Button(choose_date_screen_group, "up_btn.png", (20, 20), (-100,-30), alignments=["centerx", "centery"]) # knapp for å gå ett år opp
    year_down_btn = Button(choose_date_screen_group, "down_btn.png", (20, 20), (-100,30), alignments=["centerx", "centery"]) # knapp for å gå ett år ned
    Text(choose_date_screen_group, "år", (-100, -60), font_size=15, alignments=["centery", "centerx"]) # tekst hvor det står "år" 
    
    month_text = Text(choose_date_screen_group, str(selected_date.month), (0,0), alignments=["centery", "centerx"]) # tekst som viser hvilken måned som er valgt
    month_up_btn = Button(choose_date_screen_group, "up_btn.png", (20, 20), (0,-30), alignments=["centerx", "centery"]) # knapp for å gå en måned opp
    month_down_btn = Button(choose_date_screen_group, "down_btn.png", (20, 20), (0,30), alignments=["centerx", "centery"]) # knapp for å gå en måned ned
    Text(choose_date_screen_group, "måned", (0, -60), font_size=15, alignments=["centery", "centerx"]) # tekst hvor det står "måned"
    
    day_text = Text(choose_date_screen_group, str(selected_date.day), (100,0), alignments=["centery", "centerx"]) # viser hvilken dag som er valgt 
    day_up_btn = Button(choose_date_screen_group, "up_btn.png", (20, 20), (100,-30), alignments=["centerx", "centery"]) # knapp for å gå en dag opp
    day_down_btn = Button(choose_date_screen_group, "down_btn.png", (20, 20), (100,30), alignments=["centerx", "centery"]) # knapp for å gå en dag ned
    Text(choose_date_screen_group, "dag", (100, -60), font_size=15, alignments=["centery", "centerx"]) # tekst hvor det står "dag" 
    
    initdate_btn = Button(choose_date_screen_group, "initdate_btn.png", (602*0.31, 121*0.31), (0,200), alignments=["centerx", "centery"]) # initialiser dato knapp 
    go_back_btn = Button(choose_date_screen_group, "arrow-left.png", (25,25), (5,10)) # gå tilbake knapp 

    while run: # pygame screen loop for choose_date_screen
        CLOCK.tick(FPS) # oppdaterer klokka og gjør at max FPS ikke overstiges
        for event in pygame.event.get():  # looper igjennom pygame eventer
            if event.type == pygame.QUIT: # hvis event er lik pygame.QUIT, bruker ber om å lukke spillet 
                run = False # avslutter choose_date_screen loop   
                quit_game() # avslutter spillet
            if event.type == pygame.VIDEORESIZE: # window blir resize-et
                width, height = event.size # setter bredde og høyde til størrelsen på vindu når det blir resize-et
                update_display(width, height) # oppdaterer størrelsen på skjermen 
                for sprite in choose_date_screen_group: # looper igjennom alle spriter i choose_date_screen_group og initialiserer posisjonen slik at posisjonen blir rett med alignments og ny screen størrelse
                    sprite.init_pos()
                
        ### sjekk om knapper er klikket   
        if initdate_btn.is_clicked(): # hvis initdate_btn er klikket
            run = False # avslutter choose_date_screen loop
            init_simulation(selected_date) # initialiser simulering ut fra gitt dato 
        
        if go_back_btn.is_clicked(): # hvis go_back_btn er klikket
            run = False # avslutter choose_date_screen loop
            if prev_screen == "game_screen": # hvis prev_screen er lik game_screen
                camera_group = init_camera_group() # initialiserer og returnerer camera_group med romobjekter
                camera_group.init_state() # initialiserer camera_group tilstand basert på lagret data 
                simulation_screen(camera_group, storage.get()["time"]) # bytter til simulation_screen slik at simulering vises
            else: # hvis ikke prev_screen er lik game_screen
                welcome_screen() # bytt til welcome_screen
        
        if year_up_btn.is_clicked(): # hvis year_up_btn er klikket, legg til ett år til selected_date
            selected_date = selected_date + relativedelta(years=1) # legger til ett år til selected_date
            
        if year_down_btn.is_clicked(): # hvis year_down_btn er klikket, trekk fra ett år fra selected_date
            selected_date = selected_date - relativedelta(years=1) # trekker fra ett år fra selected_date
        
        if month_up_btn.is_clicked(): # hvis month_up_btn er klikket, legg til en måned til selected_date
            selected_date = selected_date + relativedelta(months=1) # legger til en måned til selected_date
        
        if month_down_btn.is_clicked(): # hvis month_down_btn er klikket, trekk fra en måned fra selected_date
            selected_date = selected_date - relativedelta(months=1) # trekker fra en måned fra selected_date
            
        if day_up_btn.is_clicked(): # hvis day_up_btn er klikket, legg til en dag til selected_date
            selected_date = selected_date + relativedelta(days=1) # legger til en dag til selected_date
        
        if day_down_btn.is_clicked(): # hvis year_down_btn er klikket, trekk fra en dag fra selected_date
            selected_date = selected_date - relativedelta(days=1) # trekker fra en dag fra selected_date
        
        ### opptater tekst
        year_text.update_text(str(selected_date.year))
        month_text.update_text(str(selected_date.month)) 
        day_text.update_text(str(selected_date.day))
        
        ### tegner elementer til skjerm
        SCREEN.fill(0) # tegner en svart bakgrunn til skjermen
        choose_date_screen_group.draw(SCREEN) # tegner alle elementer i gruppa til skjermen
        pygame.display.update() # oppdaterer display


def init_simulation(start_simulation_date): # funksjon for å initialisere simuleringen til gitt simuleringsdato ut fra data hentet fra 1 januar 2022
    camera_group = init_camera_group() # initialiserer og returnerer camera_group med romobjekter
    storage.clear() # fjerner all data fra den forrige simuleringen
    
    ### innhold som vises til skjerm mens simulering blir initialiser til rett dato
    init_simulation_group = pygame.sprite.Group()  # sprite gruppe for å vise tekst til skjer
    Text(init_simulation_group, "Laster inn...", (0,0), alignments=["centerx", "centery"]) # lager teksten "Laster inn..." som vises til skjermen mens simulering initialiseres
    SCREEN.fill(0) # tegner en svart bakgrunn til skjermen
    init_simulation_group.draw(SCREEN) # tegner gruppen med teksten "Laster inn..." til skjerm
    pygame.display.update() # oppdaterer display 
    
    ### initialiserer simulering 
    simulation_time = 0 # simuleringstid fra 1 januar 2022
    current_date = default_date # dato som simulering er på 
    
    if start_simulation_date > default_date: # hvis datoen som simuleringen skal starte på er større enn default_date (1 jan. 2020) som er den dagen startverdier for romobjektene  er hentet fra  
        camera_group.dt = 1000 # sett tidssteg til 1000
    else: # hvis ikke (da er datoen som simuleringen skal starte på mindre enn default_date (1. jan 2022))
        camera_group.dt = -1000 # sett tidssteg til -1000
        
    while current_date != start_simulation_date: # looper gjennom så lenge at current_date ikke er lik start_simulation_date fordi vi ikke er på den datoen hvor bruker ønsker at simuleringen skal vises  
        simulation_time += camera_group.dt # legger til tidssteg til simuleringstid 
        current_date = default_date + datetime.timedelta(seconds=simulation_time) # oppdaterer hvilken dato vi er på i simuleringen
        camera_group.update_aks() # kaller update_aks for alle sprite i gruppen, kalkulerer akselerasjonen basert på gravitasjonskreaften fra alle legemer 
        camera_group.update_pos() # kaller update_pos for alle sprite i gruppen, oppdaterer posisjonen basert på kalkulert akselerasjon 
            
    simulation_screen(camera_group,simulation_time) # viser simulation_screen slik at simuleringen vises når current_date er lik start_simulation_date slik at simuleringen vises fra den datoen bruker har oppgitt 


def simulation_screen(camera_group, simulation_time): # funksjon for å vise simulering 
    run = True # variabel for å avgjøre om screen loop skal fortsette (hvis den blir satt til False slutter denne skjermen å oppdateres)
    current_date = default_date + datetime.timedelta(seconds=simulation_time) # dato vi er på i simuleringen. 1 jan. 2022 + simuleringstiden
    simulation_paused = False # boolean for å avgjøre om simulering er pauset
    only_simulation_shown = False # boolean for å avgjøre om bare simuleringen skal vises og ikke noe tekst eller knapper 
    
    ### knapper
    button_group = pygame.sprite.Group() # lager sprite gruppe for knapper 
    play_pause_button = Button(button_group, "pause.png", (25,25), (-125,5), alignments=["endx"]) # kanpp for å pause simulering
    replay_button = Button(button_group, "replay.png", (25,25), (-95,5), alignments=["endx"]) # knapp for å restarte simulering 
    reset_camera_button = Button(button_group, "focus.png", (25,25), (-65, 5), alignments=["endx"]) # knapp for å nullstille kameraet
    choose_date_button = Button(button_group, "date.png", (25, 25), (-35, 5), alignments=["endx"]) # knapp for å gå til choose_date_screen slik at bruker kan velge en ny dato 
    home_button = Button(button_group, "home.png", (25,25), (-5,5), alignments=["endx"]) # knapp for å gå til start igjen (welcome_screen)
    
    ### tekst med informasjon om simuleringen
    info_group = pygame.sprite.Group() # lager sprite gruppe for tekst med informasjon om simuleringen
    info1_text = Text(info_group, "", (5,5), font_size= 15) # lager tekst for å vise tidssteg per sekund 
    info2_text = Text(info_group, "", (5,30), font_size=15) # lager tekst for å vise zoom
    info3_text = Text(info_group, "", (5,55), font_size=15) # lager tekst for å vise dato i simulering
    
    ### tekst med informasjon om romobjektet kameraet følger
    objectinfo_group = pygame.sprite.Group() # lager sprite gruppe for tekst med informasjon om romobjektet kameraet følger 
    objectinfo1_text = Text(objectinfo_group, "", (5, -155), font_size=15, alignments=["endy"]) # lager tekst for å vise navnet til romobjektet kamera følger
    objectinfo2_text = Text(objectinfo_group, "", (5, -130), font_size=15, alignments=["endy"]) # lager tekst for å vise massen av romobjektet kamera følger
    objectinfo3_text = Text(objectinfo_group, "", (5, -105), font_size=15, alignments=["endy"]) # lager tekst for å vise posisjonen til romobjektet kamera følger
    objectinfo4_text = Text(objectinfo_group, "", (5, -80), font_size=15, alignments=["endy"]) # lager tekst for å vise fartsvektoren til romobjektetkamera følger
    objectinfo5_text = Text(objectinfo_group, "", (5, -55), font_size=15, alignments=["endy"]) # lager tekst for å vise banefarten til romobjektet kamera følger
    objectinfo6_text = Text(objectinfo_group, "", (5, -30), font_size=15, alignments=["endy"]) # lager tekst for å vise akselerasjonsvektoren til romobjektet kamera følger
    objectinfo7_text = Text(objectinfo_group, "", (5, -5), font_size=15, alignments=["endy"]) # lager tekst for å vise baneakselerasjonen til romobjektet kamera følger
    
    def seconds_to_days_and_seconds(seconds): # funkjson som gjør om fra sekunder til string med antall dager og sekunder
        days_and_seconds = "" # string for antall dager og sekunder
        
        if seconds < 0: # hvis vi har negativt sekunder
            seconds = -seconds # gør sekunder om til positivt
            if seconds//86400 != 0: # 86400 sekunder i en dag, så så lenge heldivisjon er større enn null, bruk dager 
                days_and_seconds += "-" + str(seconds//86400) + " dager og " # legger til string for dager (med negativt fortegn siden seconds opprinnelig var negativt)
                
            days_and_seconds += "-" + str(seconds%86400) + " sekunder" # legger til string for sekunder (med negativt fortegn siden seconds opprinnelig var negativt)
                
        else: # hvis vi har positivt sekunder 
            if seconds//86400 != 0: # 86400 sekunder i en dag, så så lenge heldivisjon er større enn null, bruk dager 
                days_and_seconds += str(seconds//86400) + " dager og " # legger til string for dager
            
            days_and_seconds += str(seconds%86400) + " sekunder" # legger til string for sekunder
        return days_and_seconds # returnerer string med dager og sekunder
    
    def update_info_text(time, date): # funksjon for å oppdatere tekst med informasjon om simuleringen
        if CLOCK.get_fps() < 30: # hvis FPS er mindre enn 30, vis tekst for kalkulert tidssteg per sekund, da tidssteg ikke kalkulerer ut fra FPS siden den er for lav     
            info1 = f"Tidsendring per sekund: {seconds_to_days_and_seconds(int(camera_group.dt*CLOCK.get_fps()))}"
        else: # FPS er større enn 20, hvis tekst med gjennomsnittlig tidssteg per sekund 
            info1 = f"Tidsendring per sekund: {seconds_to_days_and_seconds(int(camera_group.dt_per_s))}" 
        info1_text.update_text(info1) # oppdatterer tekst for tidssteg per sekund
        info2_text.update_text(f"Zoom: {int(camera_group.zoom_scale*100)}%") # oppdatterer tekst for zoom 
        info3_text.update_text(f"Dato: {date}") # oppdaterer tekst for dato i simulering
        
    def update_object_info_text(space_object): # funksjon for å oppdatere tekst med informasjon om romobjektet kamera følger
        objectinfo1_text.update_text(f"Kamera følger: {space_object.name}") # oppdaterer tekst med hvilket romobjekt kamera følger
        objectinfo2_text.update_text(f"Masse: {space_object.mass} kg") # oppdaterer tekst med massen av romobjektet kamera følger
        objectinfo3_text.update_text(f"Posisjon: ({int(space_object.x)}, {int(space_object.y)})") # oppdaterer tekst med posisjonen til romobjektet kamera følger
        objectinfo4_text.update_text(f"Fartsvektor: ({int(space_object.v_x)}, {int(space_object.v_y)})") # oppdaterer tekst med fartsvektoren til romobjektet kamera følger
        objectinfo5_text.update_text("Banefart: " + str(int((space_object.v_x**2 + space_object.v_y**2)**0.5)) + " m/s") # oppdaterer tekst med banefarten til romobjektet kamera følger
        objectinfo6_text.update_text(f"Akselerasjonsvektor: ({round(space_object.a_x, 7)}, {round(space_object.a_y, 7)})") # oppdaterer tekst med akselerasjonsvektoren til romobjektet kamera følger
        objectinfo7_text.update_text(f"Baneakselerasjon: {round((space_object.a_x**2 + space_object.a_y**2)**0.5, 5)} m/s^2") # oppdaterer tekst med baneakselerasjonen til romobjektet kamera følger

    def update_play_pause_button(simulation_paused): # funksjon for å oppdatere play_pause_button når den blir klikket 
        if simulation_paused == False: # hvis simulering ikke er pauset
            play_pause_button.update_image("play.png") # oppdaterer bilde som vises som knapp
            return True # setter simulering på pause
        
        else: # simulering er pauset
            play_pause_button.update_image("pause.png") # oppdaterer bilde som vises som knapp
            return False # starter simulering igjen
        
    def reset_camera(): # funksjon for å nullstille kamera 
        camera_group.zoom_scale = 1 # nullstill zoom
        camera_group.offset = pygame.math.Vector2(0,0) # nullstill kamera offset
        camera_group.target = None # sett kamera target til ingen
        camera_group.update_image_sizes() # oppdater bilde størrelse til romobjektene
        
    def reset_simulation(): # funksjon for å nullstille simulering
        storage.clear() # sletter all lagret data om simulering
        init_simulation(datetime.date.today()) # restart simulering til datoen når programmet kjøres
        
    def go_to_welcome_screen(): 
        save_simulation() # lagre simuleringstilstand slik at simulering kan gjenopptas 
        welcome_screen() # bytt til welcome_screen
     
    def go_to_choose_date_screen(date): 
        save_simulation() # lagre simuleringstilstand slik at simulering kan gjenopptas 
        choose_date_screen("game_screen", date)
            
    def save_simulation(): # funksjon for å lagre simuleringsstatus til json fil 
        storage.update(camera_group.sprites(), simulation_time, camera_group.dt_per_s, camera_group.zoom_scale, camera_group.offset) # lagrer data til storage før simulering avsluttes slik at simulering kan gjenopptas på nytt
            
    while run: # pygame screen loop for simulation_screen
        CLOCK.tick(FPS) # oppdaterer klokka og gjør at max FPS ikke overstiges
        
        if CLOCK.get_fps() < 30: # hvis FPS er under 30, bruk tidssteg som er tilsvarer en konstant FPS på 30, siden en FPS på under 30 vil gjøre at tidssteg blir så stort for å gi likt tidsendring per sekund sammenlignet med f.eks 60 FPS 
            camera_group.dt = camera_group.dt_per_s/30 # kalkulerer konstant tidssteg
        else: # FPS er over 30, og kalkuler tidssteg for frame som vanlig
            camera_group.dt = camera_group.dt_per_s/CLOCK.get_fps() # kalkulerer tidssteg for frame ut fra gitt tidsendring per sekund

        for event in pygame.event.get(): # looper igjennom pygame eventer
            if event.type == pygame.QUIT: # hvis event er lik pygame.QUIT, bruker ber om å lukke spillet 
                save_simulation() # lagre simuleringstildtand slik at simulering kan gjenopptas når spillet åpnes igjen
                run = False # avslutter simulation_screen loop 
                quit_game() # avslutter spillet
                
            if event.type == pygame.VIDEORESIZE: # window blir resize-et
                width, height = event.size # setter bredde og høyde til størrelsen på vindu når det blir resize-et
                update_display(width, height) # oppdaterer størrelsen på skjermen 
                camera_group.update_display_suface() # oppdater disply for camera_group 
                for button in button_group.sprites(): # looper gjennom buttons i buttons group for å finne ny riktig posisjon med alignments 
                    button.init_pos() # initialsierer posisjon på nytt 
                
                    
            if event.type == pygame.KEYDOWN: # hvis en tast på tastaturet blir presset
                if event.key == pygame.K_SPACE: # hvis mellomrom blir presset
                    simulation_paused = update_play_pause_button(simulation_paused) # oppdater om simulering er pauset eller ikke
                    
                if event.key == pygame.K_h: # hvis h knapp er presset
                    only_simulation_shown = not only_simulation_shown # toggle om tekst og knapper skal vises eller ikke
                    
                if event.key == pygame.K_r: # hvis r knapp er presset
                    run = False # avslutter simulation_screen loop
                    reset_simulation() # nullstiller simulering til dato programmet kjøres
                
                if event.key == pygame.K_i: # hvis i knapp er presset 
                    run = False # avslutter simulation_screen loop
                    go_to_welcome_screen() # bytter til welcome_screen
                
                if event.key == pygame.K_c: # hvis c knapp er presset 
                    reset_camera() # nullstiller kamera
                    
                if event.key == pygame.K_k: # hvis k knapp er presset 
                    run = False # avslutter simulation_screen loop
                    go_to_choose_date_screen(current_date) # bytter til choose_date_screen
                    
            if event.type == pygame.MOUSEBUTTONUP: # hvis en tast på musa som er trykket ned blir released 
                if event.button == 1: # left click
                    mx, my = pygame.mouse.get_pos() # posisjonen til musa 
                    camera_group.check_mouse_click(mx,my) # sjekker om et romobjekt er trykket, og hvis et romobjekt er trykket blir det satt som target 
            
        ### sjekker om knappper er klikket
        if play_pause_button.is_clicked(): # play_pause_button er klikket
            simulation_paused = update_play_pause_button(simulation_paused) # oppdater om simulering er pauset eller ikke
        
        if replay_button.is_clicked(): # hvis replay_button er klikket
           run = False # avslutter simulation_screen loop
           reset_simulation() # nullstiller simulering til dato programmet kjøres
        
        if reset_camera_button.is_clicked(): # hvis reset_camera_button er klikket 
            reset_camera() # nullstiller kamera
            
        if choose_date_button.is_clicked():
            run = False # avslutter simulation_screen loop
            go_to_choose_date_screen(current_date) # bytter til choose_date_screen
            
        if home_button.is_clicked(): # viser welcome screen 
            run = False # avslutter simulation_screen loop
            go_to_welcome_screen() # bytter til welcome_screen
        
        ### tegner elementer til skjerm
        SCREEN.fill(0)# tegner en svart bakgrunn til skjermen
        
        if simulation_paused == False: # hvis spillet ikke er pauset
            simulation_time += camera_group.dt # legg til tidssteg til simuleringstiden 
            current_date = default_date + datetime.timedelta(seconds=simulation_time) # oppdater datoen i simuleringen
            camera_group.update_aks() # kaller update_aks for alle sprite i gruppen, kalkulerer akselerasjonen basert på gravitasjonskreaften fra alle legemer 
            camera_group.update_pos() # kaller update_pos for alle sprite i gruppen, oppdaterer posisjonen basert på kalkulert akselerasjon 
    
        camera_target = camera_group.custom_draw() # tegner alle romobjekter til skjermen og returnerer kamera target
        if camera_target: # hvis kamera target er gitt
            if only_simulation_shown == False: # bare hvis tekst og knapper skal vises
                update_object_info_text(camera_target) # oppdater informasjon om romobjektet
                objectinfo_group.draw(SCREEN) # viser info tekst om objektet til skjermen

        if only_simulation_shown == False: # viser bare hvis tekst og knapper skal vises
            update_info_text(simulation_time, current_date.strftime("%d.%m.%Y")) # oppdaterer tekst med informasjom om simuleringen
            info_group.draw(SCREEN) # viser all informasjon om simuleringen til skjerm 
            button_group.draw(SCREEN) # viser alle knapper til skjerm
        
        pygame.display.update() # oppdaterer display  
     
def quit_game(): # funksjon for å avslutte hele simuleringen
    pygame.quit() # avslutter pygame
    sys.exit() # exits program 

if __name__ == '__main__': # hvis scriptet ikke er importert 
    welcome_screen() # vis welcome_screen

else: # hvis scriptet er importert, ikke start simulering 
    print("File " + __file__ + " cannot be imported") 