class SceneManager:
    _instance = None

    def __init__(self):
        self.scenes = {}  
        self.current_scene = None 
        self.previous_scene = None  
        self.last_completed_level = None  # 🆕 Добавили сюда
        self.last_scene_name = None 

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SceneManager()
        return cls._instance
    
    def add(self, name, scene):
        self.scenes[name] = scene
    
    def set(self, name):
        if name in self.scenes:
            self.last_scene_name = (
                self.get_current_scene_name() if self.current_scene else None
            )
            self.previous_scene = self.current_scene

            if self.current_scene and hasattr(self.current_scene, 'reset'):
                self.current_scene.reset()

            self.current_scene = self.scenes[name]
    def get_current_scene_name(self):
        for name, scene in self.scenes.items():
            if scene == self.current_scene:
                return name
        return None


    def set_last_completed_level(self, level_name):  # 🆕 Добавили
        self.last_completed_level = level_name
        
    def get_last_completed_level(self):  # 🆕 Добавили
        return self.last_completed_level
    def update(self):
        if self.current_scene:
            self.current_scene.update()
    
    def render(self, screen):

        if self.current_scene:
            self.current_scene.render(screen)
    
    def handle_event(self, event):
        if self.current_scene:
            self.current_scene.handle_event(event)
    

    def get_current_scene(self):
        return self.current_scene
    
    def get_previous_scene(self):
        return self.previous_scene
    
    def has_scene(self, name):
        return name in self.scenes