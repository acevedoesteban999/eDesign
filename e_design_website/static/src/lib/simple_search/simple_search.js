// Simple Search
(function(global) {
    'use strict';
    
    class SimpleSearch {
        constructor(containerSelector, options = {}) {
            this.container = typeof containerSelector === 'string' 
                ? document.querySelector(containerSelector) 
                : containerSelector;
            
            if (!this.container) return;
            
            this.options = {
                searchInput: options.searchInput || '.search-input',
                markSelector: options.markSelector || '[data-search-mark]',
                containerSelector: options.containerSelector || '[data-search-container]',
                groupSelector: options.groupSelector || '[data-search-group]',
                hiddenClass: options.hiddenClass || 'd-none',
                emptyMessage: options.emptyMessage || 'No results found',
                emptyClass: options.emptyClass || 'search-empty-message',
                minChars: options.minChars || 1,
                caseSensitive: options.caseSensitive || false,
                ...options
            };
            
            this.input = typeof this.options.searchInput === 'string'
                ? document.querySelector(this.options.searchInput)
                : this.options.searchInput;
            
            if (!this.input) return;
            
            this.emptyElement = null;
            this.init();
        }
        
        init() {
            this.input.addEventListener('input', (e) => this.filter(e.target.value));
            this.input.addEventListener('keyup', (e) => {
                if (e.key === 'Escape') {
                    this.input.value = '';
                    this.filter('');
                }
            });
        }
        
        filter(query) {
            const searchTerm = this.options.caseSensitive ? query : query.toLowerCase();
            
            if (searchTerm.length === 0) {
                this.showAll();
                this.hideEmptyMessage();
                return;
            }
            
            if (searchTerm.length < this.options.minChars) return;
            
            const marks = this.container.querySelectorAll(this.options.markSelector);
            const containerMatches = new Map();
            
            marks.forEach(mark => {
                const group = mark.closest(this.options.groupSelector) || mark;
                const container = group.closest(this.options.containerSelector);
                
                if (!container) return;
                
                const text = this.options.caseSensitive 
                    ? mark.textContent 
                    : mark.textContent.toLowerCase();
                
                const match = text.includes(searchTerm);
                const currentStatus = containerMatches.get(container);
                
                if (currentStatus === undefined || !currentStatus) {
                    containerMatches.set(container, match);
                }
            });
            
            let visibleCount = 0;
            
            containerMatches.forEach((hasMatch, container) => {
                if (hasMatch) {
                    container.classList.remove(this.options.hiddenClass);
                    visibleCount++;
                } else {
                    container.classList.add(this.options.hiddenClass);
                }
            });
            
            if (visibleCount === 0) {
                this.showEmptyMessage();
            } else {
                this.hideEmptyMessage();
            }
            
            if (this.options.onFilter) {
                const visible = Array.from(containerMatches.keys())
                    .filter(c => !c.classList.contains(this.options.hiddenClass));
                this.options.onFilter(visible, searchTerm);
            }
        }
        
        showAll() {
            const containers = this.container.querySelectorAll(this.options.containerSelector);
            containers.forEach(container => {
                container.classList.remove(this.options.hiddenClass);
            });
        }
        
        showEmptyMessage() {
            if (this.emptyElement) return;
            
            this.emptyElement = document.createElement('div');
            this.emptyElement.className = this.options.emptyClass;
            this.emptyElement.textContent = this.options.emptyMessage;
            
            const listContainer = this.container.querySelector('.list') || this.container;
            listContainer.appendChild(this.emptyElement);
        }
        
        hideEmptyMessage() {
            if (this.emptyElement && this.emptyElement.parentNode) {
                this.emptyElement.parentNode.removeChild(this.emptyElement);
                this.emptyElement = null;
            }
        }
        
        destroy() {
            this.input.removeEventListener('input', this.filter);
            this.hideEmptyMessage();
            this.showAll();
        }
    }
    
    global.SimpleSearch = SimpleSearch;
    
})(window);