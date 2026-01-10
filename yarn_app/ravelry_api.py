from .models import Pattern

class RavelryAPI:
    """Класс для работы с Ravelry API (мок версия)"""
    
    MOCK_PATTERNS = [
        {
            'id': 1,
            'name': 'Простой шарф для начинающих',
            'yarn_weight': 'DK',
            'photo_url': 'https://via.placeholder.com/300x200/8A4FFF/FFFFFF?text=Шарф',
            'pattern_url': '#',
            'difficulty_level': 1,
            'craft': 'knitting',
            'free': True,
            'rating': 4.5,
            'rating_count': 123
        },
        {
            'id': 2,
            'name': 'Теплые варежки с узором',
            'yarn_weight': 'Worsted',
            'photo_url': 'https://via.placeholder.com/300x200/FF6B8B/FFFFFF?text=Варежки',
            'pattern_url': '#',
            'difficulty_level': 2,
            'craft': 'knitting',
            'free': True,
            'rating': 4.2,
            'rating_count': 89
        },
        {
            'id': 3,
            'name': 'Уютный плед из квадратов',
            'yarn_weight': 'Bulky',
            'photo_url': 'https://via.placeholder.com/300x200/00D4AA/FFFFFF?text=Плед',
            'pattern_url': '#',
            'difficulty_level': 3,
            'craft': 'knitting',
            'free': False,
            'rating': 4.8,
            'rating_count': 256
        },
        {
            'id': 4,
            'name': 'Ажурная шаль',
            'yarn_weight': 'Fingering',
            'photo_url': 'https://via.placeholder.com/300x200/4FC3F7/FFFFFF?text=Шаль',
            'pattern_url': '#',
            'difficulty_level': 4,
            'craft': 'knitting',
            'free': False,
            'rating': 4.7,
            'rating_count': 187
        },
        {
            'id': 5,
            'name': 'Детская шапочка с помпоном',
            'yarn_weight': 'Sport',
            'photo_url': 'https://via.placeholder.com/300x200/FFA726/FFFFFF?text=Шапочка',
            'pattern_url': '#',
            'difficulty_level': 1,
            'craft': 'knitting',
            'free': True,
            'rating': 4.1,
            'rating_count': 76
        },
        {
            'id': 6,
            'name': 'Носки с косой',
            'yarn_weight': 'Fingering',
            'photo_url': 'https://via.placeholder.com/300x200/66BB6A/FFFFFF?text=Носки',
            'pattern_url': '#',
            'difficulty_level': 3,
            'craft': 'knitting',
            'free': True,
            'rating': 4.6,
            'rating_count': 234
        },
        {
            'id': 7,
            'name': 'Теплый свитер с косами',
            'yarn_weight': 'Worsted',
            'photo_url': 'https://via.placeholder.com/300x200/795548/FFFFFF?text=Свитер',
            'pattern_url': '#',
            'difficulty_level': 4,
            'craft': 'knitting',
            'free': False,
            'rating': 4.9,
            'rating_count': 312
        },
        {
            'id': 8,
            'name': 'Плед из шестиугольников',
            'yarn_weight': 'DK',
            'photo_url': 'https://via.placeholder.com/300x200/9E9E9E/FFFFFF?text=Плед+2',
            'pattern_url': '#',
            'difficulty_level': 3,
            'craft': 'knitting',
            'free': False,
            'rating': 4.3,
            'rating_count': 145
        },
        {
            'id': 9,
            'name': 'Митенки с ажуром',
            'yarn_weight': 'Sport',
            'photo_url': 'https://via.placeholder.com/300x200/8A4FFF/FFFFFF?text=Митенки',
            'pattern_url': '#',
            'difficulty_level': 2,
            'craft': 'knitting',
            'free': True,
            'rating': 4.0,
            'rating_count': 98
        },
        {
            'id': 10,
            'name': 'Пуловер с регланом',
            'yarn_weight': 'Worsted',
            'photo_url': 'https://via.placeholder.com/300x200/FF6B8B/FFFFFF?text=Пуловер',
            'pattern_url': '#',
            'difficulty_level': 4,
            'craft': 'knitting',
            'free': False,
            'rating': 4.8,
            'rating_count': 278
        }
    ]

    @staticmethod
    def get_difficulty_level(level):
        """Конвертирует уровень сложности"""
        if level <= 1:
            return 'beginner'
        elif level == 2:
            return 'easy'
        elif level == 3:
            return 'intermediate'
        else:
            return 'experienced'

    @staticmethod
    def fetch_popular_patterns(count=20):
        """Загружает популярные схемы (мок версия)"""
        try:
            patterns = RavelryAPI.MOCK_PATTERNS[:count]
            
            created_count = 0
            for pattern_data in patterns:
                # Проверяем, есть ли уже такая схема
                if not Pattern.objects.filter(ravelry_id=str(pattern_data['id'])).exists():
                    Pattern.objects.create(
                        ravelry_id=str(pattern_data['id']),
                        name=pattern_data['name'],
                        yarn_weight=pattern_data['yarn_weight'],
                        photo_url=pattern_data['photo_url'],
                        pattern_url=pattern_data['pattern_url'],
                        difficulty=RavelryAPI.get_difficulty_level(pattern_data['difficulty_level']),
                        source='ravelry',
                        craft=pattern_data.get('craft', 'knitting'),
                        is_free=pattern_data.get('free', False),
                        rating=pattern_data.get('rating', 0),
                        rating_count=pattern_data.get('rating_count', 0)
                    )
                    created_count += 1
            
            return created_count, patterns
            
        except Exception as e:
            print(f"Error fetching patterns: {e}")
            return 0, []

def get_yarn_type_mapping():
    """Сопоставление типов пряжи между нашей системой и Ravelry"""
    return {
        'fingering': ['Fingering', 'Lace', 'Super Fine'],
        'sport': ['Sport', 'Light'],
        'dk': ['DK', 'Light Worsted'],
        'worsted': ['Worsted', 'Medium', 'Aran'],
        'bulky': ['Bulky', 'Chunky', 'Super Bulky'],
        'other': ['Any', 'Not Specified']
    }