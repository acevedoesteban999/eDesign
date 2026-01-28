/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { loadJS, loadCSS } from "@web/core/assets";

publicWidget.registry.TVCatalog = publicWidget.Widget.extend({
    selector: '#tv-catalog',
    
    async willStart() {
        await loadJS("/e_design_website_tv_catalog/static/src/lib/swiper/swiper-bundle.min.js");
        await loadCSS("/e_design_website_tv_catalog/static/src/lib/swiper/swiper-bundle.min.css");
    },

    start() {
        // Bloquear interacciones inmediatamente
        this._disableInteractions();
        
        // Iniciar reloj
        this._startClock();
        
        // Parsear datos
        const groupsData = JSON.parse(this.el.dataset.groups || '[]');
        const config = JSON.parse(this.el.dataset.config || '{}');
        
        // Renderizar
        this._renderGroups(groupsData);
        
        // Configuración de Swiper para modo pasivo/TV
        const swiperConfig = {
            autoplay: {
                delay: config.autoplay || 6000,     // 6 segundos por slide
                disableOnInteraction: false,         // No parar nunca
                pauseOnMouseEnter: false,            // No pausar con mouse
            },
            speed: 1200,                             // Transición suave 1.2s
            grabCursor: false,
            allowTouchMove: false,                   // No permitir arrastrar
            keyboard: false,                         // No teclado (a menos que tengas control remoto)
        };
        
        this._initializeSwipers(swiperConfig);
        
        // Iniciar scroll automático vertical después de carga
        setTimeout(() => {
            this._startAutoScroll();
        }, 2000);
        
        return this._super.apply(this, arguments);
    },

    _startClock() {
        const updateClock = () => {
            const now = new Date();
            const timeString = now.toLocaleTimeString('es-ES', { 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit'
            });
            const clockEl = document.getElementById('tv-clock');
            if (clockEl) clockEl.textContent = timeString;
        };
        updateClock();
        setInterval(updateClock, 1000);
    },

    _renderGroups(groups) {
        const container = document.getElementById('tv-groups-container');
        const groupTemplate = document.getElementById('tv-group-template');
        const itemTemplate = document.getElementById('tv-item-template');
        
        if (!groups.length) {
            container.innerHTML = '<div style="text-align:center; padding:5rem;"><h2>No hay contenido disponible</h2></div>';
            return;
        }

        groups.forEach((group, index) => {
            // Si no hay items, saltar este grupo
            if (!group.items || !group.items.length) return;
            
            const groupEl = groupTemplate.firstElementChild.cloneNode(true);
            groupEl.style.animationDelay = `${index * 0.15}s`;
            
            // Configurar título y clase por tipo
            const titleEl = groupEl.querySelector('.tv-group-title');
            titleEl.textContent = group.name;
            
            const headerEl = groupEl.querySelector('.tv-group-header');
            if (group.type === 'product') {
                headerEl.style.borderLeftColor = '#48dbfb';
            }
            
            groupEl.querySelector('.tv-group-count').textContent = 
                `${group.total} diseño${group.total !== 1 ? 's' : ''}`;
            
            const wrapper = groupEl.querySelector('.swiper-wrapper');
            
            // Render items SIN REPETIR (solo los que existen)
            group.items.forEach(item => {
                const itemHtml = itemTemplate.innerHTML
                    .replace(/__ID__/g, item.id)
                    .replace(/__NAME__/g, this._escapeHtml(item.name));
                
                const slide = document.createElement('div');
                slide.className = 'swiper-slide tv-item';
                slide.innerHTML = itemHtml;
                
                wrapper.appendChild(slide);
            });
            
            container.appendChild(groupEl);
        });
    },

    _initializeSwipers(config) {
        const swipers = [];
        const containers = document.querySelectorAll('.tv-swiper');
        
        containers.forEach((container) => {
            const slideCount = container.querySelectorAll('.swiper-slide').length;
            
            // Configuración específica por cantidad de items
            const specificConfig = {
                ...config,
                slidesPerView: 'auto',
                spaceBetween: 30,
                centeredSlides: slideCount <= 3, // Centrar si hay pocos
                loop: slideCount > 4, // Solo loop si hay más de 4 items
                pagination: {
                    el: container.querySelector('.swiper-pagination'),
                    clickable: false,
                    dynamicBullets: slideCount > 5,
                },
                navigation: {
                    enabled: false,
                },
                breakpoints: {
                    320: { slidesPerView: 1.3, spaceBetween: 20 },
                    768: { slidesPerView: 2.5, spaceBetween: 25 },
                    1024: { slidesPerView: 3.5, spaceBetween: 30 },
                    1400: { slidesPerView: 4.5, spaceBetween: 35 },
                    1920: { slidesPerView: 5.5, spaceBetween: 40 },
                },
            };
            
            // Si hay muy pocos items, desactivar autoplay (no tiene sentido girar 1 o 2 items)
            if (slideCount <= 2) {
                specificConfig.autoplay = false;
                specificConfig.loop = false;
            }
            
            const swiper = new Swiper(container, specificConfig);
            swipers.push(swiper);
        });
        
        this.swipers = swipers;
    },

    _startAutoScroll() {
        // Scroll automático vertical suave (sube y baja en loop)
        let direction = 1; // 1 = abajo, -1 = arriba
        const speed = 0.8; // Velocidad de scroll (px por frame)
        const pauseAtEnd = 3000; // Pausa de 3 segundos al llegar arriba/abajo
        
        const scrollLoop = () => {
            const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
            const current = window.pageYOffset;
            
            // Si no hay scroll necesario, no hacer nada
            if (maxScroll <= 0) return;
            
            // Detectar extremos y cambiar dirección
            if (current >= maxScroll - 5 && direction === 1) {
                direction = -1;
                setTimeout(() => requestAnimationFrame(scrollLoop), pauseAtEnd);
                return;
            } else if (current <= 5 && direction === -1) {
                direction = 1;
                setTimeout(() => requestAnimationFrame(scrollLoop), pauseAtEnd);
                return;
            }
            
            window.scrollTo(0, current + (speed * direction));
            requestAnimationFrame(scrollLoop);
        };
        
        requestAnimationFrame(scrollLoop);
    },

    _disableInteractions() {
        // Bloquear todos los eventos de interacción
        this.el.style.pointerEvents = 'none';
        
        // Prevenir menú contextual (click derecho)
        document.addEventListener('contextmenu', (e) => {
            if (e.target.closest('#tv-catalog')) {
                e.preventDefault();
            }
        });
    },

    _escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    destroy() {
        if (this.swipers) {
            this.swipers.forEach(s => s.destroy(true, true));
        }
        return this._super.apply(this, arguments);
    },
});