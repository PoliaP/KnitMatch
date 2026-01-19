// Функция для обработки анимации кнопки удаления
function setupDeleteButtonAnimation() {
    const deleteButton = document.querySelector('.btn-delete');
    
    if (deleteButton) {
        // Анимация при наведении
        deleteButton.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
            this.style.transition = 'transform 0.2s ease';
        });
        
        // Анимация при уходе курсора
        deleteButton.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
        
        // Анимация при нажатии
        deleteButton.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.95)';
        });
        
        deleteButton.addEventListener('mouseup', function() {
            this.style.transform = 'scale(1.05)';
        });
    }
}

// Функция для подтверждения удаления
function confirmDelete(event) {
    if (!window.confirm('Вы уверены, что хотите удалить эту пряжу? Это действие нельзя отменить.')) {
        event.preventDefault();
        return false;
    }
    
    // Показать индикатор загрузки
    const deleteButton = document.querySelector('.btn-delete');
    if (deleteButton) {
        const originalText = deleteButton.innerHTML;
        deleteButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Удаление...';
        deleteButton.disabled = true;
        
        // Восстановить текст через 5 секунд на всякий случай
        setTimeout(() => {
            deleteButton.innerHTML = originalText;
            deleteButton.disabled = false;
        }, 5000);
    }
    
    return true;
}

// Функция для обработки предупреждения при закрытии страницы
function setupBeforeUnloadWarning() {
    let formSubmitted = false;
    
    // Отслеживаем отправку формы
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function() {
            formSubmitted = true;
        });
    }
    
    // Предупреждение при закрытии страницы
    window.addEventListener('beforeunload', function(e) {
        if (!formSubmitted) {
            e.preventDefault();
            e.returnValue = 'Вы уверены, что хотите покинуть страницу? Изменения могут не сохраниться.';
        }
    });
}

// Функция для анимации появления карточки
function setupCardAnimation() {
    const card = document.querySelector('.delete-yarn-card');
    if (card) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        // Запускаем анимацию после небольшой задержки
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100);
    }
}

// Функция для анимации иконки предупреждения
function setupWarningIconAnimation() {
    const warningIcon = document.querySelector('.warning-icon');
    if (warningIcon) {
        // Начальное состояние
        warningIcon.style.opacity = '0';
        warningIcon.style.transform = 'scale(0.8) rotate(-10deg)';
        warningIcon.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        // Анимация появления
        setTimeout(() => {
            warningIcon.style.opacity = '1';
            warningIcon.style.transform = 'scale(1) rotate(0deg)';
        }, 300);
        
        // Добавляем пульсацию
        setTimeout(() => {
            warningIcon.classList.add('warning-pulse');
        }, 1000);
    }
}

// Функция для добавления CSS анимаций
function addAnimations() {
    // Добавляем CSS для анимации пульсации
    const style = document.createElement('style');
    style.textContent = `
        .warning-pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% {
                transform: scale(1);
                box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.7);
            }
            70% {
                transform: scale(1.05);
                box-shadow: 0 0 0 10px rgba(255, 193, 7, 0);
            }
            100% {
                transform: scale(1);
                box-shadow: 0 0 0 0 rgba(255, 193, 7, 0);
            }
        }
        
        .yarn-info-card {
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .yarn-info-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
        }
    `;
    document.head.appendChild(style);
}

// Инициализация всех функций при загрузке страницы
function initializeDeleteYarnPage() {
    // Добавляем CSS анимации
    addAnimations();
    
    // Настраиваем анимацию карточки
    setupCardAnimation();
    
    // Настраиваем анимацию иконки предупреждения
    setupWarningIconAnimation();
    
    // Настраиваем анимацию кнопки удаления
    setupDeleteButtonAnimation();
    
    // Настраиваем предупреждение при закрытии страницы
    setupBeforeUnloadWarning();
    
    // Добавляем обработчик подтверждения удаления
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', confirmDelete);
    }
    
    // Добавляем обработчик для кнопки отмены
    const cancelButton = document.querySelector('.btn-cancel-delete');
    if (cancelButton) {
        cancelButton.addEventListener('click', function(e) {
            // Плавный переход назад
            e.preventDefault();
            const card = document.querySelector('.delete-yarn-card');
            if (card) {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                
                // Переход после завершения анимации
                setTimeout(() => {
                    window.location.href = this.href;
                }, 300);
            } else {
                window.location.href = this.href;
            }
        });
    }
}

// Запуск инициализации при полной загрузке DOM
document.addEventListener('DOMContentLoaded', initializeDeleteYarnPage);