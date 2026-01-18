import requests
import base64
import time
import json
from django.conf import settings
from .models import Pattern

class RavelryAPI:
    """Класс для работы с реальным Ravelry API"""
    
    BASE_URL = 'https://api.ravelry.com'
    
    def __init__(self, use_personal=True):
        """
        Инициализация API
        
        Args:
            use_personal: True - использовать personal доступ, False - read-only
        """
        if use_personal:
            self.username = settings.RAVELRY_USERNAME
            self.access_token = settings.RAVELRY_PERSONAL_ACCESS_TOKEN
            self.access_type = "personal"
        else:
            self.username = getattr(settings, 'RAVELRY_READONLY_USERNAME', '')
            self.access_token = getattr(settings, 'RAVELRY_READONLY_TOKEN', '')
            self.access_type = "read-only"
        
        if not self.username or not self.access_token:
            raise ValueError(f"Не установлены учетные данные для {self.access_type} доступа")
        
        # Basic Auth для Ravelry API
        auth_string = f"{self.username}:{self.access_token}"
        self.auth_header = f"Basic {base64.b64encode(auth_string.encode()).decode()}"
        
        self.headers = {
            'Authorization': self.auth_header,
            'Content-Type': 'application/json',
            'User-Agent': f'KnitMatch/1.0 (PoliaP)'
        }
        
        print(f"🔑 Использую {self.access_type} доступ")
        print(f"   Username: {self.username}")
    
    def test_connection(self):
        """Тестирует подключение к API"""
        print(f"🔌 Тестирую подключение к Ravelry API ({self.access_type})...")
        
        # Простой запрос для проверки
        params = {
            'page_size': 2,
            'sort': 'popularity',
            'craft': 'knitting'
        }
        
        data = self._make_request('patterns/search.json', params)
        
        if data and 'patterns' in data:
            total = data.get('paginator', {}).get('results', 0)
            patterns = data.get('patterns', [])
            
            print(f"✅ Подключение успешно!")
            print(f"   Доступно схем: {total}")
            
            if patterns:
                print("   Примеры схем:")
                for i, pattern in enumerate(patterns[:3], 1):
                    name = pattern.get('name', 'Без названия')[:50]
                    print(f"   {i}. {name}")
            
            return True
        else:
            print("❌ Не удалось подключиться к API")
            return False
    
    def _make_request(self, endpoint, params=None):
        """Делает запрос к Ravelry API с обработкой ошибок"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            print(f"🌐 Запрос: {endpoint}")
            if params:
                print(f"   Параметры: {json.dumps(params, ensure_ascii=False)[:100]}...")
            
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            
            if response.status_code == 200:
                print(f"   ✅ Успешно")
                return response.json()
            elif response.status_code == 401:
                print(f"❌ Ошибка 401: Неверные учетные данные для {self.access_type}")
                return None
            elif response.status_code == 429:
                print("⚠ Ошибка 429: Лимит запросов. Жду 60 секунд...")
                time.sleep(60)
                return self._make_request(endpoint, params)
            else:
                print(f"❌ Ошибка {response.status_code}: {response.reason}")
                print(f"   URL: {url}")
                if response.text:
                    print(f"   Ответ: {response.text[:200]}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ Таймаут запроса")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка сети: {e}")
            return None
    
    def fetch_popular_patterns(count=10):
        """Загрузка популярных схем - ВРЕМЕННАЯ ЗАГЛУШКА"""
        print(f"🛠 DEBUG RavelryAPI.fetch_popular_patterns({count}) - заглушка")
    
    def _convert_difficulty(self, rating):
        """Конвертирует рейтинг сложности"""
        if rating <= 1.5:
            return 'beginner'
        elif rating <= 2.5:
            return 'easy'
        elif rating <= 3.5:
            return 'intermediate'
        else:
            return 'experienced'
    
    def search_patterns(self, query=None, yarn_weight=None, difficulty=None, 
                       free_only=False, count=20):
        """Поиск схем по параметрам"""
        params = {
            'page_size': min(count, 100),
            'craft': 'knitting'
        }
        
        if query:
            params['query'] = query
        if yarn_weight:
            params['weight'] = yarn_weight.lower()
        if free_only:
            params['availability'] = 'free'
        
        print(f"🔍 Поиск схем: {params}")
        
        data = self._make_request('patterns/search.json', params)
        
        if not data or 'patterns' not in data:
            return []
        
        return data['patterns'][:count]

def get_yarn_type_mapping():
    """Возвращает маппинг типов пряжи для фильтрации"""
    return {
        'lace': 'Lace',
        'light fingering': 'Light Fingering',
        'fingering': 'Fingering',
        'sport': 'Sport',
        'dk': 'DK',
        'worsted': 'Worsted',
        'aran': 'Aran',
        'bulky': 'Bulky',
        'super bulky': 'Super Bulky',
        'jumbo': 'Jumbo',
    }

# Синглтон экземпляры для удобства
ravelry_personal = RavelryAPI(use_personal=True)
# ravelry_readonly = RavelryAPI(use_personal=False)