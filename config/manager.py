from configparser import ConfigParser


class ConfigManager:
    """
    A simple manager created using the configparser module providing some utility functions
    for creating and managing config files.
    """
    def __init__(self, path_to_configfile: str = './config/ini/config.ini') -> None:
        """Creates a configparser and reads the config from the given file."""
        self.path_to_configfile = path_to_configfile
        self.config = ConfigParser()
        self.config.read(path_to_configfile, encoding='utf-8')


class TextureShaderWindowConfig(ConfigManager):
    """
    Child of the ConfigManager class.
    Provides functions for reading, formatting and saving to the windows main config file.
    """
    def __init__(self) -> None:
        """Creates a configparser, reads the config from the given file and formats it."""
        super().__init__(path_to_configfile='./config/ini/texture_shader_window.ini')

        # ----------

        self.most_recent_shader_directory = self.config['compute_shader']['directory']

        self.clr_fg_rgb = (
            float(self.config['color_fg']['red']),
            float(self.config['color_fg']['green']),
            float(self.config['color_fg']['blue'])
        )
        self.clr_bg_rgb = (
            float(self.config['color_bg']['red']),
            float(self.config['color_bg']['green']),
            float(self.config['color_bg']['blue'])
        )

    def save(self) -> None:
        """Reformats the updated config and writes it to the given file."""
        self.config['compute_shader']['directory'] = self.most_recent_shader_directory

        self.config['color_fg']['red'] = str(self.clr_fg_rgb[0])
        self.config['color_fg']['green'] = str(self.clr_fg_rgb[1])
        self.config['color_fg']['blue'] = str(self.clr_fg_rgb[2])

        self.config['color_bg']['red'] = str(self.clr_bg_rgb[0])
        self.config['color_bg']['green'] = str(self.clr_bg_rgb[1])
        self.config['color_bg']['blue'] = str(self.clr_bg_rgb[2])

        with open(self.path_to_configfile, 'w') as configfile:
            self.config.write(configfile)
            configfile.close()


class SlimeMoldWindowConfig(ConfigManager):
    """
    Child of the ConfigManager class.
    Provides functions for reading, formatting and saving to the windows main config file.
    """
    def __init__(self) -> None:
        """Creates a configparser, reads the config from the given file and formats it."""
        super().__init__(path_to_configfile='./config/ini/slime_mold_window.ini')

        # ----------

        self.most_recent_shader_directory = self.config['compute_shader']['directory']

        self.clr_fg_rgb = (
            float(self.config['color_fg']['red']),
            float(self.config['color_fg']['green']),
            float(self.config['color_fg']['blue'])
        )
        self.clr_bg_rgb = (
            float(self.config['color_bg']['red']),
            float(self.config['color_bg']['green']),
            float(self.config['color_bg']['blue'])
        )

    def save(self) -> None:
        """Reformats the updated config and writes it to the given file."""
        self.config['compute_shader']['directory'] = self.most_recent_shader_directory

        self.config['color_fg']['red'] = str(self.clr_fg_rgb[0])
        self.config['color_fg']['green'] = str(self.clr_fg_rgb[1])
        self.config['color_fg']['blue'] = str(self.clr_fg_rgb[2])

        self.config['color_bg']['red'] = str(self.clr_bg_rgb[0])
        self.config['color_bg']['green'] = str(self.clr_bg_rgb[1])
        self.config['color_bg']['blue'] = str(self.clr_bg_rgb[2])

        with open(self.path_to_configfile, 'w') as configfile:
            self.config.write(configfile)
            configfile.close()
