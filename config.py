"""
Configuration settings for the Brand Name Generator
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
EXPORTS_DIR = BASE_DIR / "exports"
DATABASE_DIR = BASE_DIR / "database"

# Create directories if they don't exist
ASSETS_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)
DATABASE_DIR.mkdir(exist_ok=True)

# Database
DATABASE_PATH = DATABASE_DIR / "brands.db"

# Domain extensions to check
DOMAIN_EXTENSIONS = ['.com', '.io', '.ai', '.co', '.dev', '.app', '.tech', '.cloud']

# Naming styles
NAMING_STYLES = {
    'compound': {
        'prefixes': ['Aero', 'Aqua', 'Astro', 'Bio', 'Cloud', 'Cosmo', 'Data', 'Eco', 'Electro', 'Fusion',
                     'Gen', 'Geo', 'Hydra', 'Infra', 'Juno', 'Kineti', 'Lunar', 'Meta', 'Neon', 'Omni',
                     'Penta', 'Quant', 'Radia', 'Solar', 'Terra', 'Ultra', 'Velo', 'Vortex', 'Zen', 'Zephyr'],
        'suffixes': ['Byte', 'Core', 'Dex', 'Edge', 'Flow', 'Grid', 'Hub', 'Ion', 'Jet', 'Kin',
                     'Lens', 'Mesh', 'Nex', 'Orb', 'Pulse', 'Rift', 'Sync', 'Tron', 'Unity', 'Vault',
                     'Wave', 'X', 'Y', 'Zen', 'Ark', 'Bit', 'Cloud', 'Dynamo', 'Echo', 'Forge']
    },
    'abstract': {
        'syllables': ['A', 'Ac', 'Ad', 'Ag', 'Al', 'Am', 'An', 'Ap', 'Ar', 'As', 'At', 'Av', 'Ax',
                      'Ba', 'Be', 'Bi', 'Bo', 'Bu', 'Ca', 'Ce', 'Ci', 'Co', 'Cu', 'Da', 'De', 'Di',
                      'Do', 'Du', 'E', 'Ec', 'Ed', 'Eg', 'El', 'Em', 'En', 'Ep', 'Er', 'Es', 'Et',
                      'Ev', 'Ex', 'Fa', 'Fe', 'Fi', 'Fo', 'Fu', 'Ga', 'Ge', 'Gi', 'Go', 'Gu', 'Ha',
                      'He', 'Hi', 'Ho', 'Hu', 'I', 'Ic', 'Id', 'Ig', 'Il', 'Im', 'In', 'Ip', 'Ir',
                      'Is', 'It', 'Iv', 'Ix', 'Ja', 'Je', 'Ji', 'Jo', 'Ju', 'Ka', 'Ke', 'Ki', 'Ko',
                      'Ku', 'La', 'Le', 'Li', 'Lo', 'Lu', 'Ma', 'Me', 'Mi', 'Mo', 'Mu', 'Na', 'Ne',
                      'Ni', 'No', 'Nu', 'O', 'Ob', 'Oc', 'Od', 'Og', 'Ol', 'Om', 'On', 'Op', 'Or',
                      'Os', 'Ot', 'Ov', 'Ox', 'Pa', 'Pe', 'Pi', 'Po', 'Pu', 'Qu', 'Ra', 'Re', 'Ri',
                      'Ro', 'Ru', 'Sa', 'Se', 'Si', 'So', 'Su', 'Ta', 'Te', 'Ti', 'To', 'Tu', 'U',
                      'Ul', 'Um', 'Un', 'Up', 'Ur', 'Us', 'Ut', 'Uv', 'Va', 'Ve', 'Vi', 'Vo', 'Vu',
                      'Wa', 'We', 'Wi', 'Wo', 'Wu', 'Xa', 'Xe', 'Xi', 'Xo', 'Xu', 'Ya', 'Ye', 'Yi',
                      'Yo', 'Yu', 'Za', 'Ze', 'Zi', 'Zo', 'Zu']
    },
    'animal': {
        'words': ['Panda', 'Lynx', 'Wolf', 'Eagle', 'Phoenix', 'Dragon', 'Falcon', 'Tiger', 'Cobra',
                  'Raven', 'Apex', 'Viper', 'Orca', 'Hawk', 'Panther', 'Coyote', 'Fox', 'Lion', 'Bear']
    },
    'nature': {
        'words': ['Forest', 'Ocean', 'Mountain', 'River', 'Sky', 'Sun', 'Moon', 'Star', 'Cloud', 'Storm',
                  'Vortex', 'Crystal', 'Ember', 'Aurora', 'Cascade', 'Zenith', 'Quartz', 'Sol', 'Luna']
    }
}

# Blacklist - common/undesirable words
BLACKLIST = [
    'test', 'demo', 'sample', 'temp', 'tmp', 'example',
    'fake', 'dummy', 'null', 'void', 'empty', 'none',
    'admin', 'root', 'system', 'unknown', 'default'
]

# Scoring weights
SCORING_WEIGHTS = {
    'length': 0.15,
    'phonetics': 0.20,
    'memorability': 0.20,
    'domain_availability': 0.25,
    'brand_sound': 0.20
}

# Theme settings
THEMES = {
    'dark': {
        'bg': '#1a1a1a',
        'fg': '#ffffff',
        'accent': '#3b82f6',
        'secondary': '#2d2d2d',
        'text': '#e5e5e5'
    },
    'light': {
        'bg': '#ffffff',
        'fg': '#000000',
        'accent': '#2563eb',
        'secondary': '#f3f4f6',
        'text': '#1f2937'
    }
}