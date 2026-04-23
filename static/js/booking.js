/* Логика страницы бронирования: календарь + слоты + пошаговая форма */
(function () {
    'use strict';

    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

    const todayStr = calendarEl.dataset.today;
    const maxDateStr = calendarEl.dataset.maxDate;
    const today = parseDate(todayStr);
    const maxDate = parseDate(maxDateStr);

    const dateInput = document.getElementById('id_date');
    const timeInput = document.getElementById('id_time');
    const serviceSelect = document.getElementById('id_service');
    const slotsContainer = document.getElementById('slots-container');
    const timeStep = document.getElementById('time-step');
    const contactStep = document.getElementById('contact-step');
    const summaryEl = document.getElementById('booking-summary');

    const MONTH_NAMES = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ];
    const WEEKDAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

    let currentMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    let selectedDate = null;
    let selectedTime = null;

    function parseDate(str) {
        const [y, m, d] = str.split('-').map(Number);
        return new Date(y, m - 1, d);
    }

    function formatDateISO(date) {
        const y = date.getFullYear();
        const m = String(date.getMonth() + 1).padStart(2, '0');
        const d = String(date.getDate()).padStart(2, '0');
        return `${y}-${m}-${d}`;
    }

    function formatDateHuman(date) {
        return `${String(date.getDate()).padStart(2, '0')}.${String(date.getMonth() + 1).padStart(2, '0')}.${date.getFullYear()}`;
    }

    function isSameDay(a, b) {
        return a.getFullYear() === b.getFullYear() &&
            a.getMonth() === b.getMonth() &&
            a.getDate() === b.getDate();
    }

    function startOfMonth(d) { return new Date(d.getFullYear(), d.getMonth(), 1); }
    function endOfMonth(d) { return new Date(d.getFullYear(), d.getMonth() + 1, 0); }

    function renderCalendar() {
        const monthStart = startOfMonth(currentMonth);
        const monthEnd = endOfMonth(currentMonth);
        // Пн=0 … Вс=6 (в JS Вс=0)
        let startWeekday = monthStart.getDay() - 1;
        if (startWeekday < 0) startWeekday = 6;

        const monthName = MONTH_NAMES[currentMonth.getMonth()];
        const year = currentMonth.getFullYear();

        const prevMonthDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1);
        const nextMonthDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1);

        const prevDisabled = endOfMonth(prevMonthDate) < today;
        const nextDisabled = nextMonthDate > maxDate;

        let html = `
            <div class="calendar-header">
                <button type="button" class="calendar-nav-btn" id="cal-prev" ${prevDisabled ? 'disabled' : ''} aria-label="Предыдущий месяц">
                    <i class="fa-solid fa-chevron-left"></i>
                </button>
                <h4 class="calendar-month-title">${monthName} ${year}</h4>
                <button type="button" class="calendar-nav-btn" id="cal-next" ${nextDisabled ? 'disabled' : ''} aria-label="Следующий месяц">
                    <i class="fa-solid fa-chevron-right"></i>
                </button>
            </div>
            <div class="calendar-weekdays">
                ${WEEKDAYS.map(w => `<div class="calendar-weekday">${w}</div>`).join('')}
            </div>
            <div class="calendar-days">
        `;

        // Пустые клетки до начала месяца
        for (let i = 0; i < startWeekday; i++) {
            html += `<div class="calendar-day empty"></div>`;
        }

        const totalDays = monthEnd.getDate();
        for (let d = 1; d <= totalDays; d++) {
            const dayDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), d);
            const isPast = dayDate < today;
            const isFuture = dayDate > maxDate;
            const isDisabled = isPast || isFuture;
            const isToday = isSameDay(dayDate, today);
            const isSelected = selectedDate && isSameDay(dayDate, selectedDate);

            const classes = ['calendar-day'];
            if (isDisabled) classes.push('disabled');
            if (isToday) classes.push('today');
            if (isSelected) classes.push('selected');

            const dateAttr = formatDateISO(dayDate);
            html += `<button type="button" class="${classes.join(' ')}" data-date="${dateAttr}" ${isDisabled ? 'disabled' : ''}>${d}</button>`;
        }

        html += `</div>`;
        calendarEl.innerHTML = html;

        // Обработчики
        const prevBtn = document.getElementById('cal-prev');
        const nextBtn = document.getElementById('cal-next');
        if (prevBtn && !prevDisabled) {
            prevBtn.addEventListener('click', () => {
                currentMonth = prevMonthDate;
                renderCalendar();
            });
        }
        if (nextBtn && !nextDisabled) {
            nextBtn.addEventListener('click', () => {
                currentMonth = nextMonthDate;
                renderCalendar();
            });
        }

        calendarEl.querySelectorAll('.calendar-day:not(.disabled):not(.empty)').forEach(btn => {
            btn.addEventListener('click', () => {
                const d = btn.dataset.date;
                selectedDate = parseDate(d);
                dateInput.value = d;
                selectedTime = null;
                timeInput.value = '';
                renderCalendar();
                loadSlots(d);
                timeStep.style.display = 'block';
                contactStep.style.display = 'none';
                updateSummary();
            });
        });
    }

    async function loadSlots(dateStr) {
        slotsContainer.innerHTML = '<div class="loading"><i class="fa-solid fa-spinner fa-spin"></i> Загрузка...</div>';
        try {
            const response = await fetch(`/api/slots/?date=${encodeURIComponent(dateStr)}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (!response.ok) throw new Error('Ошибка загрузки');
            const data = await response.json();
            renderSlots(data.slots);
        } catch (err) {
            console.error(err);
            slotsContainer.innerHTML = '<p class="slots-empty">Не удалось загрузить слоты. Попробуйте ещё раз.</p>';
        }
    }

    function renderSlots(slots) {
        if (!slots || slots.length === 0) {
            slotsContainer.innerHTML = '<p class="slots-empty">На эту дату нет доступных слотов.</p>';
            return;
        }

        const hasAvailable = slots.some(s => s.available);

        let html = '<div class="slots-grid">';
        slots.forEach(slot => {
            const disabled = !slot.available;
            html += `<button type="button" class="slot-btn" data-time="${slot.time}" ${disabled ? 'disabled' : ''}>${slot.time}</button>`;
        });
        html += '</div>';

        if (!hasAvailable) {
            html += '<p class="slots-empty" style="margin-top:1rem;">Все слоты на эту дату заняты. Выберите другую дату.</p>';
        }

        slotsContainer.innerHTML = html;

        slotsContainer.querySelectorAll('.slot-btn:not(:disabled)').forEach(btn => {
            btn.addEventListener('click', () => {
                slotsContainer.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                selectedTime = btn.dataset.time;
                timeInput.value = selectedTime;
                contactStep.style.display = 'block';
                updateSummary();
                contactStep.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        });
    }

    function updateSummary() {
        if (!selectedDate || !selectedTime) {
            summaryEl.classList.remove('visible');
            summaryEl.innerHTML = '';
            return;
        }
        const serviceName = serviceSelect && serviceSelect.selectedIndex >= 0
            ? serviceSelect.options[serviceSelect.selectedIndex].text
            : '—';

        summaryEl.classList.add('visible');
        summaryEl.innerHTML = `
            <div class="booking-summary-title">Ваша запись</div>
            <div class="booking-summary-content">
                <span class="booking-summary-label">Услуга:</span>
                <span class="booking-summary-value">${escapeHtml(serviceName)}</span>
                <span class="booking-summary-label">Дата:</span>
                <span class="booking-summary-value">${formatDateHuman(selectedDate)}</span>
                <span class="booking-summary-label">Время:</span>
                <span class="booking-summary-value">${selectedTime}</span>
            </div>
        `;
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // При смене услуги обновляем summary
    if (serviceSelect) {
        serviceSelect.addEventListener('change', updateSummary);
    }

    // Если форма была отправлена с ошибкой — пытаемся восстановить состояние
    if (dateInput.value) {
        try {
            selectedDate = parseDate(dateInput.value);
            currentMonth = startOfMonth(selectedDate);
            timeStep.style.display = 'block';
            if (timeInput.value) {
                selectedTime = timeInput.value;
                contactStep.style.display = 'block';
            }
            loadSlots(dateInput.value).then(() => {
                if (selectedTime) {
                    const btn = slotsContainer.querySelector(`.slot-btn[data-time="${selectedTime}"]`);
                    if (btn) btn.classList.add('selected');
                    updateSummary();
                }
            });
        } catch (e) { /* ignore */ }
    }

    renderCalendar();
})();
