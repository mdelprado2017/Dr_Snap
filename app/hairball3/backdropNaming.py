from app.hairball3.plugin import Plugin
import app.consts_drscratch as consts


class BackdropNaming(Plugin):
    """
    Plugin that tracks how often backdrops default names (like Backdrop1, Backdrop2) are used in a scratch project
    """

    def __init__(self, filename, json_project):
        super().__init__(filename, json_project)
        self.total_default = 0
        self.list_default_names = []

    def analyze(self):
        for key, value in self.json_project.items():
            for default in consts.PLUGIN_BACKDROPNAMING_DEFAULT_NAMES:
                if default in key:
                    self.total_default += 1
                    self.list_default_names.append(key)

    def finalize(self) -> str:

        self.analyze()

        result = '{} default backdrop names found:\n'.format(self.total_default)

        for name in self.list_default_names:
            result += name
            result += "\n"

        return result




