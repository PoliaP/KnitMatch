// Основной объект для управления избранным
const FavoritesManager = {
    // Получение CSRF токена
    getCsrfToken: function() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    },

    // Получение URL для переключения избранного
    getToggleFavoriteUrl: function(patternId) {
        // Используем URL из Django
        return `/patterns/toggle-favorite/${patternId}/`;
    },

    // Удаление схемы из избранного
    toggleFavorite: async function(patternId, button) {
        const csrfToken = this.getCsrfToken();
        if (!csrfToken) {
            this.showNotification('Ошибка безопасности. Пожалуйста, обновите страницу.', 'error');
            return;
        }

        try {
            // Показываем индикатор загрузки
            this.showLoading(button);

            const url = this.getToggleFavoriteUrl(patternId);
            
            console.log('Отправка запроса на:', url);
            console.log('CSRF токен:', csrfToken ? 'Есть' : 'Нет');

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            console.log('Статус ответа:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP ошибка: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Данные ответа:', data);
            
            if (data.status === 'success') {
                if (!data.is_favorite) {
                    // Если удалили из избранного
                    this.removePatternCard(patternId);
                    this.showNotification(data.message, 'success');
                    this.checkEmptyState();
                } else {
                    // Если добавили в избранное (не должно происходить на странице избранного)
                    this.showNotification(data.message, 'success');
                }
            } else {
                this.hideLoading(button);
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            console.error('Ошибка при работе с избранным:', error);
            this.hideLoading(button);
            this.showNotification('Ошибка: ' + error.message, 'error');
        }
    },

    // Анимация удаления карточки
    removePatternCard: function(patternId) {
        // Находим контейнер карточки
        let cardElement = document.querySelector(`[data-pattern-id="${patternId}"]`);
        
        if (!cardElement) {
            // Пробуем другой селектор
            cardElement = document.querySelector(`.pattern-card-container[data-pattern-id="${patternId}"]`);
        }
        
        if (!cardElement) {
            console.warn('Карточка не найдена для удаления:', patternId);
            return;
        }

        // Анимация исчезновения
        cardElement.style.opacity = '0';
        cardElement.style.transform = 'scale(0.9)';
        cardElement.style.transition = 'all 0.3s ease';
        
        setTimeout(() => {
            if (cardElement && cardElement.parentNode) {
                cardElement.remove();
                
                // Пересчитываем сетку для плавности
                this.reflowGrid();
            }
        }, 300);
    },

    // Проверка пустого состояния
    checkEmptyState: function() {
        const container = document.getElementById('patternsContainer');
        if (!container) return;

        const remainingCards = container.querySelectorAll('.pattern-card-container');
        if (remainingCards.length === 0) {
            this.showEmptyState();
        }
    },

    // Показать состояние "пусто"
    showEmptyState: function() {
        const favoritesList = document.getElementById('favoritesList');
        if (!favoritesList) return;

        const emptyStateHTML = `
            <div class="empty-favorites">
                <div class="empty-icon">
                    <i class="fas fa-heart"></i>
                </div>
                <h3 class="mb-3">У вас пока нет избранных схем</h3>
                <p class="text-muted mb-4">Находите интересные схемы и добавляйте их в избранное, чтобы не потерять</p>
                <a href="/projects/" class="btn btn-primary btn-lg">
                    <i class="fas fa-search me-2"></i>Найти схемы
                </a>
            </div>
        `;

        favoritesList.innerHTML = emptyStateHTML;
        
        // Анимация появления пустого состояния
        setTimeout(() => {
            const emptyState = favoritesList.querySelector('.empty-favorites');
            if (emptyState) {
                emptyState.style.opacity = '0';
                emptyState.style.transform = 'translateY(20px)';
                emptyState.style.transition = 'all 0.5s ease';
                
                setTimeout(() => {
                    emptyState.style.opacity = '1';
                    emptyState.style.transform = 'translateY(0)';
                }, 50);
            }
        }, 50);
    },

    // Сортировка избранного (клиентская)
    sortFavorites: function(sortType, button) {
        // Обновляем активную кнопку сортировки
        document.querySelectorAll('.sort-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        if (button) {
            button.classList.add('active');
        }

        // Получаем все карточки
        const container = document.getElementById('patternsContainer');
        if (!container) return;

        const cards = Array.from(container.querySelectorAll('.pattern-card-container'));
        
        // Сортируем карточки
        cards.sort((a, b) => {
            switch (sortType) {
                case 'rating':
                    const ratingA = parseFloat(a.querySelector('.rating-count')?.textContent || 0);
                    const ratingB = parseFloat(b.querySelector('.rating-count')?.textContent || 0);
                    return ratingB - ratingA;
                    
                case 'difficulty':
                    const difficultyOrder = {
                        'Начинающий': 1,
                        'Средний': 2,
                        'Продвинутый': 3
                    };
                    
                    const getDifficulty = (element) => {
                        const difficultyElement = element.querySelector('.difficulty');
                        if (!difficultyElement) return '';
                        
                        const text = difficultyElement.textContent || '';
                        // Убираем иконку и оставляем только текст
                        return text.replace(/[^а-яА-Я]/g, '');
                    };
                    
                    const diffA = getDifficulty(a);
                    const diffB = getDifficulty(b);
                    
                    return (difficultyOrder[diffA] || 0) - (difficultyOrder[diffB] || 0);
                    
                case 'recent':
                default:
                    // Для "новые" оставляем как есть
                    return 0;
            }
        });

        // Анимация перестановки карточек
        this.animateSorting(cards, container);
    },

    // Анимация сортировки
    animateSorting: function(cards, container) {
        if (cards.length === 0) return;

        // Сохраняем текущие позиции
        const originalPositions = cards.map(card => {
            const rect = card.getBoundingClientRect();
            return {
                element: card,
                top: rect.top,
                left: rect.left
            };
        });

        // Перемещаем карточки в DOM
        cards.forEach(card => {
            container.appendChild(card);
        });

        // Получаем новые позиции
        const newPositions = cards.map(card => {
            const rect = card.getBoundingClientRect();
            return {
                element: card,
                top: rect.top,
                left: rect.left
            };
        });

        // Возвращаем на старые позиции для анимации
        originalPositions.forEach((pos, index) => {
            const card = pos.element;
            const newPos = newPositions[index];
            
            const deltaX = pos.left - newPos.left;
            const deltaY = pos.top - newPos.top;
            
            card.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
            card.style.transition = 'transform 0s';
        });

        // Запускаем анимацию
        requestAnimationFrame(() => {
            cards.forEach(card => {
                card.style.transform = '';
                card.style.transition = 'transform 0.5s ease';
            });
        });

        // Сбрасываем трансформацию после анимации
        setTimeout(() => {
            cards.forEach(card => {
                card.style.transition = '';
            });
        }, 500);
    },

    // Перерасчет сетки
    reflowGrid: function() {
        const container = document.getElementById('patternsContainer');
        if (!container) return;

        // Принудительный reflow для анимации
        container.offsetHeight;
    },

    // Показать индикатор загрузки
    showLoading: function(button) {
        if (!button) return;
        
        const originalHTML = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>...';
        button.disabled = true;
        button.dataset.originalHTML = originalHTML;
    },

    // Скрыть индикатор загрузки
    hideLoading: function(button) {
        if (!button) return;
        
        if (button.dataset.originalHTML) {
            button.innerHTML = button.dataset.originalHTML;
            delete button.dataset.originalHTML;
        }
        button.disabled = false;
    },

    // Показать уведомление
    showNotification: function(message, type = 'info') {
        // Удаляем старые уведомления
        const oldNotifications = document.querySelectorAll('.custom-notification');
        oldNotifications.forEach(notification => {
            if (notification.parentNode) {
                notification.remove();
            }
        });

        // Создаем новое уведомление
        const notification = document.createElement('div');
        notification.className = `custom-notification alert alert-${type} alert-dismissible fade show`;
        
        // Иконки для разных типов уведомлений
        const icons = {
            'success': 'fa-check-circle',
            'error': 'fa-exclamation-circle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle'
        };
        
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="flex-grow-1">
                    <i class="fas ${icons[type] || icons.info} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-sm" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;

        document.body.appendChild(notification);

        // Автоматическое удаление через 5 секунд
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.opacity = '0';
                notification.style.transform = 'translateX(100%)';
                notification.style.transition = 'all 0.3s ease';
                
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
    },

    // Инициализация сортировки
    initSortButtons: function() {
        document.querySelectorAll('.sort-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const sortType = button.dataset.sortType || 'recent';
                this.sortFavorites(sortType, button);
            });
        });
    },

    // Инициализация кнопок удаления
    initRemoveButtons: function() {
        // Используем делегирование событий для динамических элементов
        document.addEventListener('click', (e) => {
            // Проверяем, была ли нажата кнопка удаления
            const removeBtn = e.target.closest('.remove-favorite-btn');
            if (removeBtn) {
                e.preventDefault();
                const patternId = removeBtn.dataset.patternId;
                if (patternId) {
                    // Спрашиваем подтверждение
                    if (confirm('Удалить эту схему из избранного?')) {
                        this.toggleFavorite(patternId, removeBtn);
                    }
                }
            }
        });
    },

    // Инициализация анимаций
    initAnimations: function() {
        // Анимация появления карточек
        const cards = document.querySelectorAll('.pattern-card-container');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });

        // Анимация при наведении на карточки
        const patternCards = document.querySelectorAll('.pattern-card');
        patternCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
                this.style.boxShadow = '0 10px 30px rgba(0,0,0,0.15)';
                this.style.transition = 'all 0.3s ease';
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '';
                this.style.transition = 'all 0.3s ease';
            });
        });
    },

    // Инициализация всех функций
    init: function() {
        console.log('Инициализация менеджера избранного...');
        this.initSortButtons();
        this.initRemoveButtons();
        this.initAnimations();
        console.log('Менеджер избранного инициализирован');
    }
};

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен, запускаем инициализацию...');
    FavoritesManager.init();
});