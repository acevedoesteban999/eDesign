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
            loadJS("/e_video_content/static/src/library/plyr/plyr.js"),
            loadCSS("/e_video_content/static/src/library/plyr/plyr.css"),
        ]);
    },

    async start() {
        this._super(...arguments);
        this.groupsCache = [];
        this.isLoading = false;
        this.videoPlayer = null;
        this.isVideoPlaying = false;
        this.videoTimeout = null;
        
        this.videoShuffleState = {
            availableIndices: [], 
            usedIndices: [],      
            currentVideo: null,    
        };
        
        const rawConfig = this.$el.attr('data-config');
        this.config = rawConfig ? JSON.parse(rawConfig) : {};
        this.maxItemsPerSlide = this.config.maxItemsPerSlide ?? 8;
        this.videoDelay = this.config.videoAutoplayDelay ?? 3000;
        
        this._startClock();
        await this._fetchFreshData(true);
        this._startAutoRefresh();
        this.$('#tvNextBtn').on('click', () => {
            this._goToNextSlide();
        });
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
                    allItems: group.items || [],
                    
                    shuffleState: group.type === 'videos' ? {
                        available: [...Array(group.items.length).keys()], // [0,1,2,3...]
                        used: [],
                    } : null,
                }));
                
                this._initVideoShuffle();
                
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

    _initVideoShuffle() {
        const videoGroup = this.groupsCache.find(g => g.type === 'videos');
        if (videoGroup && videoGroup.shuffleState) {
            this._shuffleArray(videoGroup.shuffleState.available);
            console.log('Video shuffle initialized:', videoGroup.shuffleState.available);
        }
    },

    _shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    },

    _getNextVideo(group) {
        if (!group.shuffleState || group.allItems.length === 0) {
            return null;
        }

        const state = group.shuffleState;

        if (state.available.length === 0) {
            console.log('All videos seen, reshuffling...');
            state.available = [...state.used];
            state.used = [];
            this._shuffleArray(state.available);
        }

        const nextIndex = state.available.shift();
        state.used.push(nextIndex);
        
        const video = group.allItems[nextIndex];
        console.log(`Playing video ${nextIndex + 1}/${group.allItems.length}: ${video.name}`);
        
        return video;
    },

    _buildDOMFromCache() {
        const $wrapper = this.$('.swiper-wrapper');
        $wrapper.empty();
        
        this.groupsCache.forEach(group => {
            const isVideoGroup = group.type === 'videos';
            
            $wrapper.append(`
                <div class="swiper-slide ${isVideoGroup ? 'video-slide' : ''}" 
                     data-index="${group.index}"
                     data-group-name="${group.name}"
                     data-group-type="${group.type}">
                    <div class="tv-dynamic-grid h-100 d-flex flex-column justify-content-center ${isVideoGroup ? 'video-container-wrapper' : ''}">
                    </div>
                </div>
            `);
        });
    },

    _getGroupTypeLabel(type) {
        const labels = {
            'category': _t('Category'),
            'product': _t('Product'),
            'design': _t('Design'),
            'videos': _t('Video'),
        };
        return labels[type] || type;
    },

    _renderCurrentSlide() {
        if (!this.swiper || this.groupsCache.length === 0) return;
        
        const realIndex = this.swiper.realIndex;
        if (realIndex >= this.groupsCache.length) return;
        
        const group = this.groupsCache[realIndex];
        const activeSlide = this.swiper.slides[this.swiper.activeIndex];
        const $grid = $(activeSlide).find('.tv-dynamic-grid');
        
        this._cleanupVideo();
        
        if (group.type === 'videos') {
            this._renderVideoSlide(group, $grid);
        } else {
            const selected = this._getRandomItems(group.allItems, this.maxItemsPerSlide);
            const gridHtml = this._generateDynamicGrid(selected, group.name);
            $grid.html(gridHtml);
        }
        
        this._updateHeader(group);
    },

    _renderVideoSlide(group, $container) {
        const video = this._getNextVideo(group);
        
        if (!video) {
            $container.html('<div class="text-center text-muted">No videos available</div>');
            return;
        }

        const html = `
           <div class="video-player-container w-100 h-100 d-flex align-items-center justify-content-center">
                <div style="width: 100%; height: 100%; max-height: calc(100vh - 140px);">
                    <video id="tv-video-player" class="plyr" playsinline controls data-video-id="${video.id}">
                        <source src="${video.url}" type="video/mp4"/>
                    </video>
                </div>
                <div class="video-info position-absolute bottom-0 start-0 m-4 px-4 py-2 bg-dark bg-opacity-75 rounded">
                    <span class="fw-bold text-warning">▶ ${video.name}</span>
                    <span class="text-white-50 ms-2">(${group.shuffleState.used.length}/${group.allItems.length})</span>
                </div>
            </div>
        `;
        
        $container.html(html);
        setTimeout(() => this._initVideoPlayer(), 100);
    },

    _initVideoPlayer() {
        const videoEl = document.getElementById('tv-video-player');
        if (!videoEl || !window.Plyr) return;
        
        this.isVideoPlaying = true;
        
        if (this.swiper && this.swiper.autoplay) {
            this.swiper.autoplay.stop();
        }
        
        this.videoPlayer = new Plyr(videoEl, {
            controls: [],
            autoplay: true,
            muted: true, 
        });
        
        this.videoPlayer.on('ended', () => {
            console.log('Video ended, waiting before next slide...');
            this._scheduleNextSlide();
        });
        
        this.videoPlayer.on('error', () => {
            console.error('Video error, skipping...');
            this._scheduleNextSlide();
        });
        
        this.videoMaxDuration = setTimeout(() => {
            if (this.isVideoPlaying) {
                console.log('Video timeout, forcing next slide...');
                this._scheduleNextSlide();
            }
        }, 180000);
    },

    _scheduleNextSlide() {
        if (!this.isVideoPlaying) return;
        
        console.log(`Waiting ${this.videoDelay}ms before next slide...`);
        
        this.videoTimeout = setTimeout(() => {
            this._goToNextSlide();
        }, this.videoDelay);
    },

    _goToNextSlide() {
        this._cleanupVideo();
        
        if (this.swiper) {
            this.swiper.autoplay.start();
            this.swiper.slideNext();
        }
    },

    _cleanupVideo() {
        this.isVideoPlaying = false;
        
        if (this.videoTimeout) {
            clearTimeout(this.videoTimeout);
            this.videoTimeout = null;
        }
        if (this.videoMaxDuration) {
            clearTimeout(this.videoMaxDuration);
            this.videoMaxDuration = null;
        }
        
        if (this.videoPlayer) {
            try {
                this.videoPlayer.destroy();
            } catch (e) {
                console.warn('Error destroying video player:', e);
            }
            this.videoPlayer = null;
        }
        
        const videoEl = document.getElementById('tv-video-player');
        if (videoEl) {
            videoEl.pause();
            videoEl.src = '';
            videoEl.load();
        }
    },

    _getRandomItems(items, max) {
        if (!items || items.length === 0) return [];
        const shuffled = [...items].sort(() => 0.5 - Math.random());
        return shuffled.slice(0, Math.min(max, shuffled.length));
    },

    _getRandomRows(total) {
        return (total >= 6 && total % 2 == 0 && Math.random() > 0.5) ? 1 : 0;
    },

    _generateDynamicGrid(items, groupName) {
        const total = items.length;
        if (total === 0) {
            return '<div class="text-center text-muted display-4">No items available</div>';
        }

        let rows = [];
        if (total <= 3)
            rows = [total];
        else {
            const half = Math.ceil(total / 2);
            rows = [half - this._getRandomRows(total), total - half - this._getRandomRows(total)];
        }

        let html = '<div class="h-100 d-flex flex-column gap-2" style="padding-bottom: 60px;">';
        let itemIndex = 0;

        rows.forEach((countInRow) => {
            const colSize = Math.floor(12 / countInRow);
            
            html += `<div class="row g-2 flex-grow-1" style="min-height: 0;">`;
            
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
            <div class="tv-counter position-absolute bottom-0 start-0 m-4 px-4 py-2 background-linear rounded-pill">
                <span class="fw-bold text-warning">${items.length}</span>
                <span class="text-white-50 small"> ${_t('of')} ${groupName}</span>
            </div>
        `;
        
        return html;
    },

    _renderItem(item) {
        const baseUrl = `/web/image/product.edesign/${item.id}/image`;
        
        return `
            <div class="card h-100 border-0 shadow position-relative overflow-hidden bg-dark">
                <div class="h-100 w-100 bg-secondary position-relative">
                    ${item.image ? 
                        `<img src="${baseUrl}" class="w-100 h-100" style="object-fit: cover;" loading="lazy" alt="${item.name}"/>` :
                        `<div class="w-100 h-100 d-flex align-items-center justify-content-center display-4">🎨</div>`
                    }
                    <div class="background-linear position-absolute bottom-0 start-0 end-0 p-3">
                        <h4 class="fw-bold text-white text-center mb-0 w-100" 
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
        
        let extraInfo = '';
        if (group.type === 'videos' && group.shuffleState) {
            const seen = group.shuffleState.used.length;
            const totalVideos = group.allItems.length;
            extraInfo = `<span class="badge bg-warning text-dark ms-2">${seen}/${totalVideos}</span>`;
        }
        
        this.$('#group-indicators').html(`
            <span class="badge bg-info text-dark fs-6 text-uppercase fw-bold">${typeLabel}</span>
            <span class="mx-2 text-white-50">|</span>
            <span class="text-white fw-bold text-uppercase">${group.name}</span>
            ${extraInfo}
            <span class="badge bg-primary fs-6 ms-2">${current} / ${total}</span>
        `);
    },

    _initSwiper() {
        const self = this;
        const $progress = this.$('.autoplay-progress');
        const delay = parseInt(this.config.autoplay) || 5000;
        const isSingleSlide = this.groupsCache.length <= 1;
        
        this.swiper = new Swiper('.tv-swiper', {
            direction: 'horizontal',
            loop: !isSingleSlide, 
            speed: 1500,
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
                        self.singleSlideInterval = setInterval(animateBar, delay);
                    }
                },
                autoplayTimeLeft(swiper, time, progress) {
                    if (!isSingleSlide && !self.isVideoPlaying && $progress.length) {
                        $progress.css('width', `${(1 - progress) * 100}%`);
                    }
                },
                slideChange() {
                    self._cleanupVideo();
                    
                    if (!isSingleSlide && $progress.length) {
                        $progress.css('width', '0%');
                    }
                    setTimeout(() => self._renderCurrentSlide(), 100);
                }
            }
        });
        
        if (this.groupsCache.length > 0) {
            setTimeout(() => this._renderCurrentSlide(), 150);
        }
    },

    destroy() {
        this._cleanupVideo();
        
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