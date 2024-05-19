from roles import Role

class Developer(Role):
    name:str = "Bob"
    profile: str = "Developer"
    goal: str = ""
    constraints: str = ""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Initialize actions specific to the Architect role
        self.set_actions([])
        # Set events or actions the Architect should watch or be aware of
        self._watch([])