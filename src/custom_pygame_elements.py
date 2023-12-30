import pygame # importerer pygame for å kunne lage sprite 

class Image(pygame.sprite.Sprite): 
    """ 
    klasse for å enkelt vise bilder til skjermen i pygame. Arver pygame.sprite.Sprite klasse slik at vi kan jobbe med klassen som sprite 
    """
    def __init__(self, sprite_group: pygame.sprite.Group, img_path: str, size: float, pos: list[float], alignments: list[str]|None=None) -> None: # initialiserer klassen 
        super().__init__(sprite_group) # initialiserer sprite klasse og legger til sprite til sprite gruppen
        self.alignments = alignments # liste med justeringer for posisjon 
        self.pos = pos # posisjon 
        self.size = size # størrelse på bilde
        self.image = pygame.image.load(img_path).convert_alpha() # loader inn bilde som skal vises 
        self.image = pygame.transform.scale(self.image, (self.size[0], self.size[1])) # transformer bilde til riktig størrelse
        self.init_pos() # initialisere posisjon 
      
    def init_pos(self)  -> None: 
        """
        initialiserer posisjonen til bildet på skjermen 
        """
        self.rect = self.image.get_rect() # får rect som tilhører bildet
        screen = pygame.display.get_surface() # metoden returnerer display surface altså skjermen
        screen_size = screen.get_size() # størrelsen på skjermen
        
        if self.alignments: 
            for alignment in self.alignments: # looper igjennom liste med justeringer for posisjonen 
                if alignment == "centerx": 
                    self.rect.centerx = screen_size[0]/2 # setter center for x i midten av skjermen
                elif alignment == "centery": 
                    self.rect.centery = screen_size[1]/2 # setter center for y i midten av skjermen
                elif alignment == "endx": 
                    self.rect.centerx = screen_size[0] - self.rect.width/2 # setter center for x på slutt av skjermen (lengst til høyre)
                elif alignment == "endy": 
                    self.rect.centery = screen_size[1] - self.rect.height/2 # setter center for y nederst av skjermen
                
        self.rect.x += self.pos[0] # legger til x posisjonen som er gitt
        self.rect.y += self.pos[1] # legger til y posisjonen som er gitt
      
   
class Button(Image): 
    """
    klasse for å lage en knapp. Arver fra Image klasse
    """
    def __init__(self, sprite_group: pygame.sprite.Group, img_path: str, size: float, pos: list[float], alignments: list[str]|None=None): # constructor
        super().__init__(sprite_group, img_path, size, pos, alignments) # initialisere parent class Image
        self.clicked: bool = False # variabel for å avgjøre om en knapp allerede er trykket eller ikke 
        self.clickable: bool = True
    
    def update_image(self, img_path: str, size: float|None=None) -> None: 
        """
        metode for å oppdaterer bildet som vises
        """
        if size: # hvis size er gitt, altså ikke er lik None 
            self.size = size # oppdaterer størrelsen av bildet
            
        self.image = pygame.image.load(img_path).convert_alpha() # loader inn bilde som vil vises som Button
        self.image = pygame.transform.scale(self.image, (self.size[0], self.size[1])) # transformerer nytt bilde til riktig posisjon
        self.init_pos() # initialiserer posisjonen til nytt bilde 
        
    def is_clicked(self) -> bool: 
        """
        metode for å avgjøre om Button er klikket 
        """
        mouse_pos = pygame.mouse.get_pos() # posisjonen til musa 
        
        if self.rect.collidepoint(mouse_pos): # hvis self.rect "kolliderer" med musa, betyr det at musa hovrer Button 
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False and self.clickable == True: # venstre klikk og Button er ikke allerede klikket, og Button er trykkbar 
                self.clicked = True # knapp trykket, setter self.clicked til True slik at ikke flere trykk registreres mens venstreklikk holdes ned
                return True # returnerer True fordi Button er klikket
            
            elif pygame.mouse.get_pressed()[0] == 0: # Button er ikke klikket
                self.clicked = False # sett self.clicked til False slik at knapp kan registrere klikk igjen
        return False # returnerer False fordi Button er ikke klikket
        

class Text(pygame.sprite.Sprite): 
    """ 
    klasse for å enkelt lage og vise tekst i pygame. Arver pygame.sprite.Sprite klasse slik at vi kan jobbe med klassen som sprite
    """
    def __init__(self, sprite_group: pygame.sprite.Group, text: str, pos: tuple[float], alignments=False, color: tuple[float]=(255,255,255), font_family="comicsans", bold=False, italic=False, font_size=20): 
        super().__init__(sprite_group) # init sprite class and adds sprite to sprite group 
        self.text = text # tekst som skal vises
        self.color = color # tekst farge
        self.pos = pos # posisjon 
        self.alignments = alignments # justeringer 
        self.font = pygame.font.SysFont(font_family, font_size, bold=bold, italic=italic) # lager et font objekt fra system fontene 
        self.image = self.font.render(text, False, self.color) # lager ny surface med text og setter til self.image slik at det blir tegnet når draw() blir kalt for gruppen  
        self.init_pos() # initialiserer posisjon
        
    def init_pos(self) -> None: 
        """
        initialiserer posisjonen til bildet med tekst som vises på skjermen
        """
        self.rect = self.image.get_rect() # lager rect fra font 
        
        screen = pygame.display.get_surface() # metoden returnerer display surface altså screen
        screen_size = screen.get_size() # størrelsen på skjermen
        
        if self.alignments: 
            for alignment in self.alignments: # looper igjennom liste med justeringer for posisjonen
                if alignment == "centerx": 
                    self.rect.centerx = screen_size[0]/2 # setter center for x i midten av skjermen
                elif alignment == "centery": 
                    self.rect.centery = screen_size[1]/2 # setter center for y i midten av skjermen
                elif alignment == "endx": 
                    self.rect.centerx = screen_size[0] - self.rect.width/2 # setter center for x på slutt av skjermen (lengst til høyre)
                elif alignment == "endy": 
                    self.rect.centery = screen_size[1] - self.rect.height/2 # setter center for y nederst av skjermen
        self.rect.x += self.pos[0] # legger til x posisjonen som er gitt
        self.rect.y += self.pos[1] # legger til y posisjonen som er gitt
        
    def update_text(self, text: str) -> None: 
        """
        metode for å oppdaterer teksten som vises 
        """
        self.image = self.font.render(text, False, self.color) # lager ny surface med text og setter til self.image slik at det blir tegnet når draw() blir kalt for gruppen  
        self.init_pos() # oppdaterer posisjonen fordi bredde og høyde endres.