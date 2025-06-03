class SceneManager:
    _instance = None

    def __init__(self):
        if SceneManager._instance is not None:
            raise Exception("This class is a singleton!")
        self.scenes = {}
        self.current_scene = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SceneManager()
        return cls._instance
    
    def add(self, name, scene):
        self.scenes[name] = scene
    
    def set(self, name):
        if name in self.scenes:
            if self.current_scene:
                if hasattr(self.current_scene, 'reset'):
                    self.current_scene.reset()
            self.current_scene = self.scenes[name]
    
    def update(self):
        if self.current_scene:
            self.current_scene.update()
    
    def render(self, screen):
        if self.current_scene:
            self.current_scene.render(screen)
    
    def handle_event(self, event):
        if self.current_scene:
            self.current_scene.handle_event(event)