/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { loadJS, loadCSS } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.TVCatalog = publicWidget.Widget.extend({
    selector: '.tv-catalog-container',
    
    async willStart() {
        await Promise.all([
            loadJS("/e_design_website_tv_catalog/static/src/lib/swiper/swiper-bundle.min.js"),
            loadCSS("/e_design_website_tv_catalog/static/src/lib/swiper/swiper-bundle.min.css"),
        ]);
    },

    async start() {
        this._super(...arguments);
        this.maxItemsPerSlide = 6;
        this.groupsCache = [];
        this.isLoading = false;
        
        const rawConfig = this.$el.attr('data-config');
        this.config = rawConfig ? JSON.parse(rawConfig) : { autoplay: 3000 };
        
        this._startClock();
        await this._fetchFreshData(true);
        this._startAutoRefresh();
    },

    _startClock() {
        const updateTime = () => {
            const now = new Date();
            const timeStr = now.toLocaleTimeString('es-ES', { 
                hour12: false, 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit',
            });
            this.$('#tv-clock').text(timeStr);
        };
        updateTime();
        this.clockInterval = setInterval(updateTime, 1000);
    },

    _startAutoRefresh() {
        const interval = this.config.refresh_interval || 3600000;
        this.refreshInterval = setInterval(async () => {
            await this._fetchFreshData(false);
        }, interval);
    },

    async _fetchFreshData(isInitial = false) {
        if (this.isLoading) return;
        this.isLoading = true;
        
        try {
            const result = await rpc('/tv/catalog/data', {});
            
            if (result && result.groups && result.groups.length > 0) {
                this.groupsCache = result.groups.map((group, index) => ({
                    index: index,
                    name: group.name,
                    type: group.type,
                    allItems: group.items || []
                }));
                
                if (isInitial) {
                    this._buildDOMFromCache();
                    this._initSwiper();
                } else {
                    const currentIdx = this.swiper ? this.swiper.realIndex : 0;
                    if (this.swiper) {
                        this.swiper.destroy();
                        this.swiper = null;
                    }
                    this._buildDOMFromCache();
                    this._initSwiper();
                    if (currentIdx < this.groupsCache.length) {
                        this.swiper.slideTo(currentIdx + 1, 0);
                    }
                }
            }
        } catch (error) {
            console.error('TV Catalog: Failed to fetch data', error);
        } finally {
            this.isLoading = false;
        }
    },

    _buildDOMFromCache() {
        const $wrapper = this.$('.swiper-wrapper');
        $wrapper.empty();
        
        this.groupsCache.forEach(group => {
            $wrapper.append(`
                <div class="swiper-slide p-4" 
                     data-index="${group.index}"
                     data-group-name="${group.name}"
                     data-group-type="${group.type}">
                    <div class="tv-dynamic-grid h-100 d-flex flex-column justify-content-center"></div>
                </div>
            `);
        });
    },

    _getGroupTypeLabel(type) {
        const labels = {
            'category': _t('Category'),
            'product': _t('Product'),
            'design': _t('Design'),
            'designs': _t('Designs')
        };
        return labels[type] || type;
    },

    _renderCurrentSlide() {
        if (!this.swiper || this.groupsCache.length === 0) return;
        
        const realIndex = this.swiper.realIndex;
        if (realIndex >= this.groupsCache.length) return;
        
        const group = this.groupsCache[realIndex];
        
        const selected = this._getRandomItems(group.allItems, this.maxItemsPerSlide);
        
        const activeSlide = this.swiper.slides[this.swiper.activeIndex];
        const $grid = $(activeSlide).find('.tv-dynamic-grid');
        const gridHtml = this._generateDynamicGrid(selected, group.name);
        $grid.html(gridHtml);
        
        this._updateHeader(group);
    },

    _getRandomItems(items, max) {
        if (!items || items.length === 0) return [];
        const shuffled = [...items].sort(() => 0.5 - Math.random());
        return shuffled.slice(0, Math.min(max, shuffled.length));
    },

    _generateDynamicGrid(items, groupName) {
        const total = items.length;
        if (total === 0) {
            return '<div class="text-center text-muted display-4">No items available</div>';
        }

        let rows = [];
        if (total <= 3) {
            rows = [total];
        } else if (total === 4) {
            rows = [2, 2];
        } else if (total === 5) {
            rows = [2, 3];
        } else if (total === 6) {
            rows = [3, 3];
        } else {
            const half = Math.ceil(total / 2);
            rows = [half, total - half];
        }

        let html = '<div class="h-100 d-flex flex-column gap-2">';
        let itemIndex = 0;

        rows.forEach((countInRow) => {

            const colSize = Math.floor(12 / countInRow);
            
            html += `<div class="row g-1 flex-grow-1" style="min-height: 0;">`;
            
            for (let i = 0; i < countInRow; i++) {
                if (itemIndex >= items.length) break;
                
                const item = items[itemIndex++];
                html += `
                    <div class="col-${colSize} h-100">
                        ${this._renderItem(item)}
                    </div>
                `;
            }
            
            html += '</div>';
        });

        html += '</div>';
        
        html += `
            <div class="position-absolute bottom-0 start-0 m-4 px-4 py-2 bg-dark bg-opacity-75 rounded-pill border border-secondary">
                <span class="fw-bold text-warning">${items.length}</span>
                <span class="text-white-50 small"> ${_t('of')} ${groupName}</span>
            </div>
        `;
        
        return html;
    },

    _renderItem(item) {
        const baseUrl = `/web/image/product.edesign/${item.id}/image`;
        const placeholder = '🎨';
        
        return `
            <div class="card h-100 border-0 shadow position-relative overflow-hidden bg-dark">
                <div class="h-100 w-100 bg-secondary position-relative">
                    ${item.image ? 
                        `<img src="${baseUrl}" class="w-100 h-100" style="object-fit: cover;" loading="lazy" alt="${item.name}"/>` :
                        `<div class="w-100 h-100 d-flex align-items-center justify-content-center display-4">${placeholder}</div>`
                    }
                    <!-- Nombre dentro de la imagen, abajo con gradiente -->
                    <div class="position-absolute bottom-0 start-0 end-0 p-3 background-linear">
                        <h4 class="fw-bold text-white text-center mb-0 text-truncate w-100" 
                            style="font-size: 1.2rem; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">
                            ${item.name}
                        </h4>
                    </div>
                </div>
            </div>
        `;
    },

    _updateHeader(group) {
        if (!group) return;
        
        const total = this.groupsCache.length;
        const current = this.swiper ? (this.swiper.realIndex + 1) : 1;
        const typeLabel = this._getGroupTypeLabel(group.type);
        
        this.$('#group-indicators').html(`
            <span class="badge bg-primary fs-6 me-2">${current} / ${total}</span>
            <span class="badge bg-info text-dark ms-2 fs-6 text-uppercase fw-bold">${typeLabel}</span>
            <span class="mx-2 text-white-50">|</span>
            <span class="text-white fw-bold" style="font-size: 1.2rem; text-transform: uppercase;">${group.name}</span>
        `);
    },

    _initSwiper() {
        const self = this;
        const $progress = this.$('.autoplay-progress');
        const delay = parseInt(this.config.autoplay) || 3000;
        const isSingleSlide = this.groupsCache.length <= 1;
        
        this.swiper = new Swiper('.tv-swiper', {
            direction: 'horizontal',
            loop: !isSingleSlide, 
            speed: 1000,
            autoplay: {
                delay: delay,
                disableOnInteraction: false,
                pauseOnMouseEnter: false,
            },
            effect: 'fade',
            fadeEffect: { crossFade: true },
            allowTouchMove: false,
            keyboard: false,
            
            on: {
                afterInit: function() {
                    if (isSingleSlide && $progress.length) {
                        const animateBar = () => {
                            $progress.css({transition: 'none', width: '0%'});
                            void $progress[0].offsetWidth; 
                            $progress.css({transition: `width ${delay}ms linear`, width: '100%'});
                            self._renderCurrentSlide();
                        };
                        animateBar();
                        setInterval(animateBar, delay);
                    }
                },
                autoplayTimeLeft(swiper, time, progress) {
                    if (!isSingleSlide && $progress.length && progress >= 0 && progress <= 1) {
                        $progress.css('width', `${(1 - progress) * 100}%`);
                    }
                },
                slideChange() {
                    if (!isSingleSlide && $progress.length) {
                        $progress.css('width', '0%');
                    }
                    setTimeout(() => self._renderCurrentSlide(), 50);
                }
            }
        });
        
        if (this.groupsCache.length > 0) {
            setTimeout(() => this._renderCurrentSlide(), 100);
        }
    },

    destroy() {
        if (this.singleSlideInterval) {
            clearInterval(this.singleSlideInterval);
        }

        if (this.swiper) {
            this.swiper.destroy(true, true);
            this.swiper = null;
        }
        if (this.clockInterval) {
            clearInterval(this.clockInterval);
        }
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        this._super(...arguments);
    },
});