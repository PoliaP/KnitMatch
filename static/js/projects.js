// static/js/projects.js

// Глобальные переменные
let csrfToken = null;

// 1. Функция применения фильтров
function applyFilters() {
    console.log('Применение фильтров...');
    
    const difficulty = document.getElementById('difficultyFilter').value;
    const yarnWeight = document.getElementById('yarnWeightFilter').value;
    const searchQuery = document.getElementById('searchInput').value.trim();
    
    // Чекбоксы
    const freeOnly = document.getElementById('freeOnly').checked;
    const withPhotos = document.getElementById('withPhotos').checked;
    const highRated = document.getElementById('highRated').checked;
    
    // Формируем URL с параметрами
    let url = window.location.pathname + '?';
    const params = [];
    
    if (difficulty) params.push(`difficulty=${difficulty}`);
    if (yarnWeight) params.push(`yarn_weight=${encodeURIComponent(yarnWeight)}`);
    if (searchQuery) params.push(`search=${encodeURIComponent(searchQuery)}`);
    if (freeOnly) params.push(`free_only=true`);
    if (withPhotos) params.push(`with_photos=true`);
    if (highRated) params.push(`high_rated=true`);
    
    if (params.length > 0) {
        url += params.join('&');
        console.log('Переход по URL:', url);
        window.location.href = url;
    } else {
        console.log('Сброс фильтров');
        window.location.href = window.location.pathname;
    }
}

// 2. Функция сброса фильтров
function resetFilters() {
    console.log('Сброс всех фильтров...');
    window.location.href = window.location.pathname;
}

// 3. Функция удаления фильтра
function removeFilter(filterType) {
    console.log('Удаление фильтра:', filterType);
    
    // Создаем URLSearchParams из текущего URL
    const url = new URL(window.location.href);
    const params = url.searchParams;
    
    // Удаляем указанный параметр
    params.delete(filterType);
    
    // Если параметр page существует, удаляем его (чтобы вернуться на первую страницу)
    if (params.has('page')) {
        params.delete('page');
    }
    
    // Обновляем URL
    url.search = params.toString();
    console.log('Новый URL:', url.toString());
    window.location.href = url.toString();
}

// 4. Функция избранного
function toggleFavorite(patternId, button) {
    console.log('Избранное для patternId:', patternId);
    
    // Получаем CSRF токен
    if (!csrfToken) {
        csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    }
    
    fetch(`/patterns/favorite/${patternId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `csrfmiddlewaretoken=${csrfToken}`
    })
    .then(response => response.json())
    .then(data => {
        console.log('Ответ сервера:', data);
        
        if (data.status === 'success') {
            // Обновляем кнопку
            const heartIcon = button.querySelector('i');
            const spanText = button.querySelector('span');
            
            if (data.is_favorite) {
                // Добавлено в избранное
                button.classList.remove('btn-outline-danger');
                button.classList.add('btn-danger');
                heartIcon.classList.remove('far');
                heartIcon.classList.add('fas');
                button.title = 'Удалить из избранного';
                if (spanText) {
                    spanText.textContent = 'Удалить';
                }
            } else {
                // Удалено из избранного
                button.classList.remove('btn-danger');
                button.classList.add('btn-outline-danger');
                heartIcon.classList.remove('fas');
                heartIcon.classList.add('far');
                button.title = 'Добавить в избранное';
                if (spanText) {
                    spanText.textContent = 'В избранное';
                }
            }
            
            // Обновляем счетчик
            const favoritesCountElement = document.getElementById('favoritesCount');
            if (favoritesCountElement) {
                let currentCount = parseInt(favoritesCountElement.textContent) || 0;
                if (data.is_favorite) {
                    currentCount++;
                } else {
                    currentCount = Math.max(0, currentCount - 1);
                }
                favoritesCountElement.textContent = currentCount;
            }
            
            // Показываем уведомление
            showNotification(data.message, 'success');
        } else {
            showNotification(data.message || 'Ошибка', 'danger');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showNotification('Ошибка при обновлении избранного', 'danger');
    });
}

// 5. Функция обновления схем
function loadPatternsFromAPI() {
    console.log('Загрузка новых схем...');
    
    // Получаем CSRF токен
    if (!csrfToken) {
        csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    }
    
    fetch('/patterns/refresh/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `csrfmiddlewaretoken=${csrfToken}&count=20`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showNotification(data.error || 'Ошибка загрузки', 'danger');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showNotification('Ошибка загрузки схем', 'danger');
    });
}

// 6. Функция показа уведомления
function showNotification(message, type = 'success') {
    // Проверяем, есть ли уже уведомление
    let notification = document.getElementById('custom-notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'custom-notification';
        notification.className = 'custom-notification';
        document.body.appendChild(notification);
    }
    
    notification.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Автоматическое скрытие через 3 секунды
    setTimeout(() => {
        const alert = notification.querySelector('.alert');
        if (alert) {
            alert.remove();
        }
    }, 3000);
}

// 7. Инициализация после загрузки страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен, инициализация...');
    
    // Получаем CSRF токен
    csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    
    // Назначаем обработчики событий
    if (document.getElementById('applyFiltersBtn')) {
        document.getElementById('applyFiltersBtn').addEventListener('click', applyFilters);
    }
    
    if (document.getElementById('resetFiltersBtn')) {
        document.getElementById('resetFiltersBtn').addEventListener('click', resetFilters);
    }
    
    if (document.getElementById('searchBtn')) {
        document.getElementById('searchBtn').addEventListener('click', applyFilters);
    }
    
    if (document.getElementById('refreshBtn')) {
        document.getElementById('refreshBtn').addEventListener('click', loadPatternsFromAPI);
    }
    
    if (document.getElementById('refreshEmptyBtn')) {
        document.getElementById('refreshEmptyBtn').addEventListener('click', loadPatternsFromAPI);
    }
    
    // Удаление фильтров
    document.querySelectorAll('.remove').forEach(button => {
        button.addEventListener('click', function() {
            const filterType = this.getAttribute('data-filter');
            removeFilter(filterType);
        });
    });
    
    // Кнопки избранного
    document.querySelectorAll('.card-footer button[data-pattern-id]').forEach(button => {
        button.addEventListener('click', function() {
            const patternId = this.getAttribute('data-pattern-id');
            toggleFavorite(patternId, this);
        });
    });
    
    // Enter в поле поиска
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                applyFilters();
            }
        });
    }
    
    // Анимация карточек
    setTimeout(() => {
        document.querySelectorAll('.pattern-card').forEach((card, index) => {
            card.style.opacity = '1';
        });
    }, 100);
    
    console.log('Инициализация завершена');
});

// Экспортируем функции в глобальную область видимости (если нужно вызывать из HTML)
window.applyFilters = applyFilters;
window.resetFilters = resetFilters;
window.toggleFavorite = toggleFavorite;
window.loadPatternsFromAPI = loadPatternsFromAPI;
window.showNotification = showNotification;