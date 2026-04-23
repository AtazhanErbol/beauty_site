/* Основной JavaScript: навигация, хедер, FAQ, сообщения */
(function () {
    'use strict';

    /* === Header scroll === */
    const header = document.getElementById('site-header');
    if (header) {
        const onScroll = () => {
            if (window.scrollY > 20) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        };
        onScroll();
        window.addEventListener('scroll', onScroll, { passive: true });
    }

    /* === Mobile menu === */
    const menuToggle = document.getElementById('menu-toggle');
    const mainNav = document.getElementById('main-nav');
    if (menuToggle && mainNav) {
        menuToggle.addEventListener('click', () => {
            menuToggle.classList.toggle('active');
            mainNav.classList.toggle('open');
            document.body.classList.toggle('no-scroll');
        });

        // Закрываем меню по клику на ссылку
        mainNav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                menuToggle.classList.remove('active');
                mainNav.classList.remove('open');
                document.body.classList.remove('no-scroll');
            });
        });
    }

    /* === Smooth scroll offset for fixed header === */
    document.querySelectorAll('a[href*="#"]').forEach(anchor => {
        const href = anchor.getAttribute('href');
        // Только для якорей на текущей странице
        const [path, hash] = href.split('#');
        if (!hash) return;
        if (path && path !== window.location.pathname && path !== '') return;

        anchor.addEventListener('click', function (e) {
            const target = document.getElementById(hash);
            if (!target) return;
            e.preventDefault();
            const headerH = header ? header.offsetHeight : 72;
            const top = target.getBoundingClientRect().top + window.scrollY - headerH + 1;
            window.scrollTo({ top, behavior: 'smooth' });
            history.pushState(null, '', '#' + hash);
        });
    });

    /* === FAQ accordion === */
    document.querySelectorAll('.faq-item').forEach(item => {
        const btn = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');
        if (!btn || !answer) return;

        btn.addEventListener('click', () => {
            const isOpen = item.classList.contains('open');

            // Закрываем все остальные
            document.querySelectorAll('.faq-item.open').forEach(other => {
                if (other !== item) {
                    other.classList.remove('open');
                    const otherAnswer = other.querySelector('.faq-answer');
                    const otherBtn = other.querySelector('.faq-question');
                    if (otherAnswer) otherAnswer.style.maxHeight = null;
                    if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
                }
            });

            // Переключаем текущий
            if (isOpen) {
                item.classList.remove('open');
                answer.style.maxHeight = null;
                btn.setAttribute('aria-expanded', 'false');
            } else {
                item.classList.add('open');
                answer.style.maxHeight = answer.scrollHeight + 'px';
                btn.setAttribute('aria-expanded', 'true');
            }
        });
    });

    /* === Messages auto-hide & close === */
    document.querySelectorAll('.message').forEach(msg => {
        const closeBtn = msg.querySelector('.message-close');
        const hide = () => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            setTimeout(() => msg.remove(), 300);
        };
        if (closeBtn) closeBtn.addEventListener('click', hide);
        setTimeout(hide, 6000);
    });

    /* === Простая маска для телефонов === */
    document.querySelectorAll('input[type="tel"], input[name="phone"]').forEach(input => {
        input.addEventListener('input', function () {
            let digits = this.value.replace(/\D/g, '');
            // Заменяем первую 8 на 7 для единообразия
            if (digits.startsWith('8')) digits = '7' + digits.slice(1);

            let formatted = '';
            if (digits.length > 0) formatted = '+' + digits[0];
            if (digits.length > 1) formatted += ' (' + digits.slice(1, 4);
            if (digits.length >= 4) formatted += ') ';
            if (digits.length >= 5) formatted += digits.slice(4, 7);
            if (digits.length >= 7) formatted += '-' + digits.slice(7, 9);
            if (digits.length >= 9) formatted += '-' + digits.slice(9, 11);
            this.value = formatted;
        });
    });
})();
