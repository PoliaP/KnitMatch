// static/js/projects.js

// Глобальные переменные
let favorites = JSON.parse(localStorage.getItem('knitmatch_favorites')) || [];

// Функция показа уведомления
function showNotification(message, type = 'info') {
    // Удаляем старое уведомление
    const oldNotification = document.querySelector('.notification');
    if (oldNotification) oldNotification.remove();
    
    const notification = document.createElement('div');
    notification.className = `notification alert alert-${type}`;
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <div class="flex-grow-1">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-sm" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Автоматическое удаление через 5 секунд
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Обновление схем из API
// static/js/projects.js - исправленная функция loadPatternsFromAPI

async function loadPatternsFromAPI() {
    try {
        showNotification('Загрузка новых схем из Ravelry API...', 'info');
        
        // Создаем FormData для отправки
        const formData = new FormData();
        formData.append('count', '12');
        
        // Получаем CSRF токен
        const csrfToken = getCookie('csrftoken');
        if (csrfToken) {
            formData.append('csrfmiddlewaretoken', csrfToken);
        }
        
        // Отправляем запрос
        const response = await fetch('/patterns/refresh/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        });
        
        console.log("📤 Отправлен запрос на обновление схем");
        
        // Проверяем статус ответа
        if (!response.ok) {
            const errorText = await response.text();
            console.error("❌ Ошибка сервера:", errorText);
            throw new Error(`Ошибка сервера ${response.status}`);
        }
        
        // Парсим JSON
        const data = await response.json();
        console.log("📦 Получен ответ:", data);
        
        if (data.success) {
            showNotification(data.message, 'success');
            
            // Если есть новые схемы, добавляем их на страницу
            if (data.patterns && data.patterns.length > 0) {
                displayNewPatterns(data.patterns);
                
                // Обновляем статистику
                updateStats(data.patterns.length);
            } else {
                showNotification('Нет новых схем для загрузки', 'warning');
            }
            
            // НЕ перезагружаем страницу автоматически!
            // Страница остается, новые схемы добавляются динамически
            
        } else {
            showNotification('Ошибка: ' + (data.error || data.message || 'Неизвестная ошибка'), 'error');
        }
        
    } catch (error) {
        console.error('Ошибка загрузки:', error);
        showNotification('Ошибка загрузки: ' + error.message, 'error');
    }
}

// Функция обновления статистики
function updateStats(newPatternsCount) {
    // Обновляем счетчик "Показано"
    const shownElement = document.querySelector('.stat-card:nth-child(2) .stat-number');
    if (shownElement) {
        const current = parseInt(shownElement.textContent) || 0;
        shownElement.textContent = current + newPatternsCount;
    }
    
    // Обновляем время обновления
    const timeElement = document.querySelector('.stat-card:nth-child(4) .stat-number');
    if (timeElement) {
        const now = new Date();
        timeElement.textContent = now.getHours().toString().padStart(2, '0') + ':' + 
                                  now.getMinutes().toString().padStart(2, '0');
    }
}

// Остальные функции остаются как были...

// Отображение новых схем
function displayNewPatterns(patterns) {
    const container = document.getElementById('patternsContainer');
    if (!container) return;
    
    // Создаем HTML для новых схем
    let newPatternsHTML = '';
    
    patterns.forEach((pattern, index) => {
        newPatternsHTML += `
        <div class="col pattern-new" style="animation-delay: ${index * 0.1}s;">
            <div class="card h-100 shadow-sm pattern-card">
                ${pattern.photo_url ? 
                    `<img src="${pattern.photo_url}" class="card-img-top" alt="${pattern.name}" style="height: 200px; object-fit: cover;">` : 
                    `<div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 200px;">
                        <i class="fas fa-image fa-3x text-muted"></i>
                    </div>`
                }
                <div class="card-body">
                    <h5 class="card-title">${pattern.name}</h5>
                    
                    <div class="pattern-meta mb-3">
                        ${pattern.yarn_weight ? 
                            `<span class="badge bg-info me-1">
                                <i class="fas fa-yarn me-1"></i>${pattern.yarn_weight}
                            </span>` : ''
                        }
                        
                        <span class="badge bg-secondary me-1">
                            ${pattern.difficulty || 'Не указано'}
                        </span>
                        
                        ${pattern.is_free ? 
                            '<span class="badge bg-success">Бесплатно</span>' : 
                            '<span class="badge bg-warning">Платно</span>'
                        }
                    </div>
                    
                    ${pattern.designer && pattern.designer !== 'Неизвестно' ? 
                        `<p class="card-text small text-muted">
                            <i class="fas fa-user me-1"></i> ${pattern.designer}
                        </p>` : ''
                    }
                    
                    ${pattern.rating && pattern.rating > 0 ? 
                        `<div class="rating mb-2">
                            ${getStarRatingHTML(pattern.rating)}
                            <small class="text-muted ms-2">${pattern.rating.toFixed(1)}</small>
                        </div>` : ''
                    }
                </div>
                
                <div class="card-footer bg-white border-top-0">
                    <div class="d-flex justify-content-between align-items-center">
                        <button class="btn btn-sm btn-outline-danger"
                                onclick="toggleFavorite(${pattern.id}, this)"
                                title="Добавить в избранное">
                            <i class="far fa-heart"></i>
                        </button>
                        
                        ${pattern.pattern_url && pattern.pattern_url !== '#' ? 
                            `<a href="${pattern.pattern_url}" target="_blank" class="btn btn-primary btn-sm">
                                <i class="fas fa-external-link-alt me-1"></i>Схема
                            </a>` : 
                            `<span class="text-muted small">
                                <i class="fas fa-lock me-1"></i>Требуется покупка
                            </span>`
                        }
                    </div>
                </div>
            </div>
        </div>`;
    });
    
    // Добавляем новые карточки в начало
    const newRow = document.createElement('div');
    newRow.className = 'row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4 mb-4';
    newRow.id = 'newPatternsRow';
    newRow.innerHTML = `<div class="col-12"><h4><i class="fas fa-star me-2"></i>Новые схемы</h4></div>` + newPatternsHTML;
    
    const existingContainer = container.parentElement;
    existingContainer.insertBefore(newRow, container);
    
    // Анимация появления
    animateNewPatterns();
}

// HTML для звезд рейтинга
function getStarRatingHTML(rating) {
    let html = '';
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    
    for (let i = 0; i < 5; i++) {
        if (i < fullStars) {
            html += '<i class="fas fa-star text-warning"></i>';
        } else if (i === fullStars && hasHalfStar) {
            html += '<i class="fas fa-star-half-alt text-warning"></i>';
        } else {
            html += '<i class="far fa-star text-warning"></i>';
        }
    }
    
    return html;
}

// Анимация новых схем
function animateNewPatterns() {
    const newCards = document.querySelectorAll('.pattern-new');
    newCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.5s ease';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 + (index * 100));
    });
}

// Применение фильтров
function applyFilters() {
    const difficulty = document.getElementById('difficultyFilter')?.value;
    const yarnWeight = document.getElementById('yarnWeightFilter')?.value;
    const searchQuery = document.getElementById('searchInput')?.value?.trim();
    
    // Формируем URL с параметрами
    let url = window.location.pathname + '?';
    const params = [];
    
    if (difficulty) params.push(`difficulty=${difficulty}`);
    if (yarnWeight) params.push(`yarn_weight=${encodeURIComponent(yarnWeight)}`);
    if (searchQuery) params.push(`search=${encodeURIComponent(searchQuery)}`);
    
    // Фильтры чекбоксов
    const freeOnly = document.getElementById('freeOnly')?.checked;
    const withPhotos = document.getElementById('withPhotos')?.checked;
    const highRated = document.getElementById('highRated')?.checked;
    
    if (freeOnly || withPhotos || highRated) {
        // Клиентская фильтрация
        filterClientSide(freeOnly, withPhotos, highRated);
        return;
    }
    
    if (params.length > 0) {
        url += params.join('&');
        window.location.href = url;
    } else {
        window.location.href = window.location.pathname;
    }
}

// Клиентская фильтрация
function filterClientSide(freeOnly, withPhotos, highRated) {
    const cards = document.querySelectorAll('.pattern-card');
    let visibleCount = 0;
    
    cards.forEach(card => {
        let shouldShow = true;
        
        if (freeOnly) {
            const hasFreeBadge = card.querySelector('.badge.bg-success');
            if (!hasFreeBadge) shouldShow = false;
        }
        
        if (withPhotos) {
            const hasPlaceholder = card.querySelector('.fa-image');
            if (hasPlaceholder) shouldShow = false;
        }
        
        if (highRated) {
            const ratingElement = card.querySelector('.rating');
            if (ratingElement) {
                const stars = ratingElement.querySelectorAll('.fa-star').length;
                const halfStars = ratingElement.querySelectorAll('.fa-star-half-alt').length;
                const rating = stars + (halfStars * 0.5);
                if (rating < 4) shouldShow = false;
            } else {
                shouldShow = false;
            }
        }
        
        const parentCol = card.closest('.col');
        if (parentCol) {
            if (shouldShow) {
                parentCol.style.display = 'block';
                visibleCount++;
            } else {
                parentCol.style.display = 'none';
            }
        }
    });
    
    // Показываем сообщение если ничего не найдено
    const container = document.querySelector('#patternsContainer')?.parentElement;
    const emptyState = document.querySelector('.empty-state');
    
    if (visibleCount === 0) {
        if (!emptyState && container) {
            const emptyHtml = `
                <div class="empty-state text-center py-5">
                    <div class="empty-icon mb-4">
                        <i class="fas fa-filter fa-3x text-muted"></i>
                    </div>
                    <h3 class="mb-3">Схемы не найдены</h3>
                    <p class="text-muted mb-4">Ни одна схема не соответствует выбранным фильтрам</p>
                    <button class="btn btn-primary" onclick="resetFilters()">
                        <i class="fas fa-redo me-2"></i>Сбросить фильтры
                    </button>
                </div>
            `;
            container.innerHTML = emptyHtml;
        }
    } else if (emptyState) {
        emptyState.remove();
    }
    
    showNotification(`Найдено ${visibleCount} схем`, 'info');
}

// Сброс фильтров
function resetFilters() {
    window.location.href = window.location.pathname;
}

// AJAX запрос для избранного
async function toggleFavorite(patternId, button) {
    try {
        // Создаем FormData
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
        
        const response = await fetch(`/patterns/favorite/${patternId}/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ошибка: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification(data.message, 'success');
            
            // Обновляем иконку
            if (button) {
                const icon = button.querySelector('i');
                if (data.is_favorite) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    button.classList.remove('btn-outline-danger');
                    button.classList.add('btn-danger');
                } else {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    button.classList.remove('btn-danger');
                    button.classList.add('btn-outline-danger');
                }
            }
        } else {
            showNotification('Ошибка: ' + data.message, 'error');
        }
        
    } catch (error) {
        console.error('Ошибка избранного:', error);
        showNotification('Ошибка: ' + error.message, 'error');
    }
}

// Вспомогательная функция для получения CSRF токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue || '';
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Активируем анимацию карточек
    setTimeout(() => {
        const patternCards = document.querySelectorAll('.pattern-card');
        patternCards.forEach((card, index) => {
            card.style.opacity = '1';
        });
    }, 100);
});

// Функция для добавления/удаления из избранного
function toggleFavorite(patternId, button) {
    fetch(`/toggle_favorite/${patternId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Меняем внешний вид кнопки
            const heartIcon = button.querySelector('i');
            if (data.is_favorite) {
                button.classList.remove('btn-outline-danger');
                button.classList.add('btn-danger');
                heartIcon.classList.remove('far');
                heartIcon.classList.add('fas');
                button.querySelector('span').textContent = 'В избранном';
            } else {
                button.classList.remove('btn-danger');
                button.classList.add('btn-outline-danger');
                heartIcon.classList.remove('fas');
                heartIcon.classList.add('far');
                button.querySelector('span').textContent = 'В избранное';
            }
            
            // Обновляем счетчик в статистике
            updateFavoriteCount();
        }
    })
    .catch(error => console.error('Error:', error));
}

// Обновление счетчика избранного
function updateFavoriteCount() {
    const favoriteCountElement = document.querySelector('.stat-card:nth-child(3) .stat-number');
    const currentCount = parseInt(favoriteCountElement.textContent);
    
    // Можно сделать запрос на сервер для получения точного количества,
    // или просто инкрементировать/декрементировать
    // Для простоты обновим страницу
    setTimeout(() => {
        window.location.reload();
    }, 500);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Анимация появления карточек
    const cards = document.querySelectorAll('.pattern-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${(index % 3) * 0.1}s`;
    });
});