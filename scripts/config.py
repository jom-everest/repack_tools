
class Config:
    settings = {
        'max_threads':16,
        # Пути к каталогам
        'paths': {
            'src_dir': '',
            'dst_dir': '',
            'temp_dir': '',
        },
        
        # Настройки архивации
        'archive': {
            'type': '7z',
            'compression_level': 19,
            'threads': 8,
            'buffer_size': 10**8,
            'use_long_mode': True,
        },
        'groups': {
            'all': {
                'archive_params': {
                    'type': '7z',
                    'c_ratio': '9',
                },
            },
            'un': {
                'extensions': {
                    '.pjxl', '.pwebp',
                    '.jpg', '.jpeg', '.png', '.webp', '.gif', '.heic', '.heif', '.jxl', 
                    '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm',
                    '.mp3', '.aac', '.ogg', '.m4a', '.opus', '.flac', '.alac',
                    '.zip', '.rar', '.7z', '.gz', '.bz2', '.xz', '.tar.gz', '.tgz', '.tar.bz2', '.tar.xz',
                    '.enc', '.gpg', '.pgp', '.rnd',
                },
                'archive_params': {
                    'type': '7z',
                    'c_ratio': '3',
                },
            },
        },
        # Расширения файлов
        'extensions': {
            'user': {
                '.pjxl', '.pwebp',
            },
            'uncompressible': {
                '.jpg', '.jpeg', '.png', '.webp', '.gif', '.heic', '.heif', '.jxl', 
                '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm',
                '.mp3', '.aac', '.ogg', '.m4a', '.opus', '.flac', '.alac',
                '.zip', '.rar', '.7z', '.gz', '.bz2', '.xz', '.tar.gz', '.tgz', '.tar.bz2', '.tar.xz',
                '.enc', '.gpg', '.pgp', '.rnd',
            },
            'image': {'.jpg', '.jpeg', '.png', '.webp', '.gif'},
            'video': {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.webm'},
        },

        # Внешние инструменты
        'tools': {
            'oxi_path': 'bin/oxipng.exe',
            'cwebp_path': 'bin/cwebp.exe',
            'dwebp_path': 'bin/dwebp.exe',
            'zstd_path': 'bin/zstd.exe',
            'cjxl_path': 'bin/cjxl.exe',
            'djxl_path': 'bin/djxl.exe',
            '7z_path': 'bin/7z.exe',
            'repak_path': 'bin/repak.exe',
        },
        
        # Упаковщики
        'packers': {
            '.zip': {
                'unpack': 'unzip_file',
                'suffix': '_zip',
            },
            '.rar': {
                'unpack': 'unrar_file',
                'suffix': '_rar',
            },
        },
    }
    
    @classmethod
    def get(cls, key, default=None):
        """
        Получить значение по ключу с поддержкой вложенных ключей через точку.
        Например: Config.get('paths.src_dir')
        """
        if '.' not in key:
            return cls.settings.get(key, default)
        
        parts = key.split('.')
        value = cls.settings
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        return value
    
    @classmethod
    def set(cls, key, value):
        """
        Установить значение по ключу с поддержкой вложенных ключей через точку.
        Например: Config.set('archive.compression_level', 15)
        """
        if '.' not in key:
            cls.settings[key] = value
            return
        
        parts = key.split('.')
        target = cls.settings
        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]
        
        target[parts[-1]] = value
