
# data base das poções

POTION_DATA = {
    'potion_1.png': {
        'type': 'good',
        'effect': 'aumenta score'
    },
    'potion_2.png': {
        'type': 'good',
        'effect': 'aumenta score'
    },
    'potion_4.png': {
        'type': 'good',
        'effect': 'bônus especial (score extra ou vida)'
    },
    'potion_5.png': {
        'type': 'bad',
        'effect': 'causa dano ou efeito negativo'
    },
    'potion_7.png': {
        'type': 'bad',
        'effect': 'efeito venenoso ou perda de pontos'
    },
    'potion_10.png': {
        'type': 'good',
        'effect': 'bônus especial'
    },
    'potions (3).png': {
        'type': 'good',
        'effect': 'score médio'
    },
    'potions (6).png': {
        'type': 'good',
        'effect': 'bônus leve'
    },
    'potions (8).png': {
        'type': 'bad',
        'effect': 'dano ou efeito ruim'
    },
    'potion (9).png': {
        'type': 'bad',
        'effect': 'tipo bomba ou efeito negativo'
    },
}

# Constantes para facilitar o acesso aos tipos
good_potions = [k for k, v in POTION_DATA.items() if v['type'] == 'good']
bad_potions = [k for k, v in POTION_DATA.items() if v['type'] == 'bad']
