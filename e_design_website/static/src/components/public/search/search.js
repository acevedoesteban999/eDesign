/** @odoo-module **/

import { Component, type, useRef, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class SearchComponent extends Component {
    static template = "e_design_website.SearchComponent";
    static props = {
        'model': String, 
        'domain': { type: Array, optional: true }, 
        'fields': Array, 
        'onSelect': Function, 
        'placeholder': { type: String, optional: true },
        'limit': { type: Number, optional: true },
        'searchQuery':{ type: String , optional: true}
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            searchQuery: this.props.searchQuery || "",
            results: [],
            isSearching: false,
            showDropdown: false,
        });
        this.searchTimeout = null;
        this.inputRef = useRef("searchInput");
        this.dropdownRef = useRef("dropdown")
    }

    async searchRecords(query) {
        var domain;
        domain = [
          ...(this.props.domain || []),
        ];
        if (query){
          domain.push(['name', 'ilike', query])
        }
        
        const limit = this.props.limit || 5;
        
        const records = await this.orm.rpc("/e_design_website/searchRead", {
            model: this.props.model,
            domain: domain,
            fields: this.props.fields,
            limit: limit,
        });
        
        return records;
    }

    onSearchInput(ev) {
        const query = ev.target.value.trim();
        this.state.searchQuery = query;

        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }

        this.state.showDropdown = true;
        this.state.isSearching = true;

        this.searchTimeout = setTimeout(async () => {
            try {
                this.state.results = await this.searchRecords(query);
            } catch (error) {
                console.error("Error en búsqueda:", error);
                this.state.results = [];
            } finally {
                this.state.isSearching = false;
            }
        }, 500);
    }

    onFocusOut(ev){
        if (this.dropdownRef.el && this.dropdownRef.el.contains(ev.relatedTarget)) {
            return;
        }
        this.state.showDropdown = false;
    }
    clearSearch(){
      this.selectOption(false);
    }

    selectOption(record) {
        this.props.onSelect(record);
        this.state.searchQuery = record.display_name;
        this.state.showDropdown = false;
        
    }
}