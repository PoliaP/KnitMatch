// Функция выбора цвета из палитры
function selectColor(hex, name, element) {
    // Обновляем значения полей
    document.getElementById('colorInput').value = hex;
    document.getElementById('colorPicker').value = hex;
    document.getElementById('colorNameInput').value = name;
    
    // Обновляем превью
    document.getElementById('selectedColor').style.backgroundColor = hex;
    document.getElementById('colorPreviewText').textContent = `${name} (${hex})`;
    
    // Убираем активный класс со всех элементов палитры
    document.querySelectorAll('.color-swatch').forEach(swatch => {
        swatch.classList.remove('active');
    });
    
    // Добавляем активный класс к выбранному элементу
    element.classList.add('active');
}

// Функция выбора цвета через пикер
function selectCustomColor(hex) {
    document.getElementById('colorInput').value = hex;
    document.getElementById('colorNameInput').value = '';
    
    // Обновляем превью
    document.getElementById('selectedColor').style.backgroundColor = hex;
    document.getElementById('colorPreviewText').textContent = `Выбранный цвет (${hex})`;
    
    // Убираем активный класс со всех элементов палитры
    document.querySelectorAll('.color-swatch').forEach(swatch => {
        swatch.classList.remove('active');
    });
}

// Функция выбора типа пряжи
function selectYarnType(value, element) {
    // Убираем активный класс со всех кнопок
    document.querySelectorAll('.yarn-type-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Добавляем активный класс к выбранной кнопке
    element.classList.add('active');
    
    // Обновляем выбранный радио-инпут
    const radioInput = element.querySelector('input[type="radio"]');
    if (radioInput) {
        radioInput.checked = true;
    }
}

// Валидация формы
function validateForm(e) {
    const color = document.getElementById('colorInput')?.value.trim();
    const amountInput = document.querySelector('input[name="amount"]');
    const amount = amountInput?.value;
    
    if (!color) {
        alert('Пожалуйста, укажите цвет пряжи');
        e.preventDefault();
        return false;
    }
    
    if (!amount || parseInt(amount) < 1) {
        alert('Пожалуйста, укажите корректное количество мотков');
        e.preventDefault();
        return false;
    }
    
    return true;
}

// Инициализация при загрузке страницы
function initializePage() {
    // Инициализация первого цвета как активного
    const firstColor = document.querySelector('.color-swatch');
    if (firstColor) {
        const hex = firstColor.dataset.hex;
        const name = firstColor.dataset.name;
        selectColor(hex, name, firstColor);
    }
    
    // Инициализация первого типа пряжи как активного
    const firstYarnType = document.querySelector('.yarn-type-btn');
    if (firstYarnType) {
        firstYarnType.classList.add('active');
    }
    
    // Добавление обработчика событий на цветовой пикер
    const colorPicker = document.getElementById('colorPicker');
    if (colorPicker) {
        colorPicker.addEventListener('input', function(e) {
            selectCustomColor(e.target.value);
        });
    }
    
    // Добавление обработчика событий на поле ввода цвета
    const colorInput = document.getElementById('colorInput');
    if (colorInput) {
        colorInput.addEventListener('input', function(e) {
            const hex = e.target.value;
            if (/^#[0-9A-F]{6}$/i.test(hex)) {
                document.getElementById('selectedColor').style.backgroundColor = hex;
                document.getElementById('colorPicker').value = hex;
                document.getElementById('colorPreviewText').textContent = `Выбранный цвет (${hex})`;
                
                // Убираем активный класс со всех элементов палитры
                document.querySelectorAll('.color-swatch').forEach(swatch => {
                    swatch.classList.remove('active');
                });
            }
        });
    }
    
    // Добавление обработчика событий на форму
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', validateForm);
    }
}

// Запуск инициализации при полной загрузке DOM
document.addEventListener('DOMContentLoaded', initializePage);