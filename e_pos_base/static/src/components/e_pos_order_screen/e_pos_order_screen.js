import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { formatDateTime } from "@web/core/l10n/dates";
import { _t } from "@web/core/l10n/translation";
import { BackButton } from "@point_of_sale/app/screens/product_screen/action_pad/back_button/back_button";
import { CenteredIcon } from "@point_of_sale/app/generic_components/centered_icon/centered_icon";
import { SearchBar } from "@point_of_sale/app/screens/ticket_screen/search_bar/search_bar";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, onMounted, useState } from "@odoo/owl";
import { parseUTCString } from "@point_of_sale/utils";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";

const NBR_BY_PAGE = 30;

export class ePosOrderScreen extends Component {
    static template = "e_pos_base.ePosOrderScreen";
    static components = {
        CenteredIcon,
        SearchBar,
        BackButton,
        Orderline,
    };

    setup() {
        this.pos = usePos();
        this.ui = useState(useService("ui"));
        this.dialog = useService("dialog");
        this.notification = useService("notification");
        this.state = useState({
            page: 1,
            nbrPage: 1,
            filter: this._defaultFilterDetails(),
            search: this._defaultSearchDetails(),
            selectedPosOrder: null,
            filteredPosOrderList:[],
            posOrderLines:[],
        });

        this.totalPosOrderCount = 0

        onMounted(()=>{
            this.onFilterSelected(this.state.filter);
        });
    }

    
    async onFilterSelected(selectedFilter) {
        this.state.filter = selectedFilter;
        await this._fetchPosOrders();
    }
    
    async onSearch(search) {
        this.state.search = search;
        this.state.page = 1;
        await this._fetchPosOrders();
    }

    async onClickPosOrder(clickedOrder,switchPane=false) {
        this.state.selectedPosOrder = clickedOrder;
        await this._fetchposOrderLines(clickedOrder)
        if (switchPane)
            this.switchPane()
    }

    _isPosOrderSelected (pos_order){
        return pos_order.id == this.state.selectedPosOrder?.id || null
    }

    getSelectedPosOrderlineId() {
        return this.state.filteredPosOrderList.filter((p)=> this._isPosOrderSelected(p))
    }

    activeOrderFilter(o) {
        const screen = ["ReceiptScreen", "TipScreen"];
        const oScreen = o.get_screen_data();
        return (!o.finalized || screen.includes(oScreen.name)) && o.uiState.displayed;
    }

    switchPane() {
        this.pos.switchPaneTicketScreen();
    }

    getDate(date) {
        return formatDateTime(parseUTCString(date));
    }

    getPartner(pos_order) {
        return pos_order.get_partner_name();
    }
    
    
    isHighlighted(pos_order) {
        return this._isPosOrderSelected(pos_order) ;
    }
    
    closePosOrderScreen() {
        this.pos.showScreen("ProductScreen");
    }

    _getStates() {
        return {
            'paid':     { text: _t("Paid"),     decoration: 'badge-success' },
            'invoiced': { text: _t("Invoiced"), decoration: 'badge-info' },
            'done':     { text: _t("Done"),     decoration: 'badge-secondary' },
            'cancel':   { text: _t("Cancel"),   decoration: 'badge-danger' },
        };
    }
    
    getStateData(stateKey) {
        return this._getStates()[stateKey] ?? { 
            text: stateKey, 
            decoration: 'badge-secondary' 
        };
    }
    
    getStateText(stateKey) {
        return this.getStateData(stateKey).text;
    }
    
    getStateDecoration(stateKey) {
        return this.getStateData(stateKey).decoration;
    }

    getPosOrderLineProps() {
        return this.state.posOrderLines.map(line => {
            const { id, ...lineProps } = line;
            return {
                line: lineProps
            };
        });
    }

    //#region PAGE
    async onNextPage() {
        if (this.state.page < this.getNbrPages()) {
            this.state.page += 1;
            await this._fetchPosOrders();
        }
    }
    async onPrevPage() {
        if (this.state.page > 1) {
            this.state.page -= 1;
            await this._fetchPosOrders();
        }
    }

    getNbrPages() {
        return Math.ceil(this.totalPosOrderCount / NBR_BY_PAGE);
    }
    getPageNumber() {
        if (!this.totalPosOrderCount) {
            return `1/1`;
        } else {
            return `${this.state.page}/${this.getNbrPages()}`;
        }
    }

    
    
   

    //#region SEARCH

    getSearchBarConfig() {
        return {
            searchFields: new Map(
                Object.entries(this._getSearchFields()).map(([key, val]) => [key, val.displayName])
            ),
            filter: { show: true, options: this._getFilterOptions() },
            defaultSearchDetails: this.state.search,
            defaultFilter: this.state.filter,
        };
    }

    
    _getFilterOptions() {
        const states = new Map();
        states.set("all", {
            text: _t("All"),
            indented: true,
        });
        const _states = this._getStates();

        Object.entries(_states).forEach(([key, stateData]) => {
            states.set(key, {
                text: stateData.text,
                indented: true,
            });
        });
        return states;
    }
    

    _getSearchFields() {
        return {
            NAME: {
                displayName: _t("Delivery"),
                modelField: "name",
            },
            POS_ORDER_REFERENCE: {
                displayName: _t("Order Number"),
                modelField: "pos_reference",
            },
            POS_TRACKING_NUMBER: {
                displayName: _t("Receipt Number"),
                modelField: "tracking_number",
            },
            PARTNER_NAME: {
                displayName: _t("Partner"),
                modelField: "partner_id.name",
            },
            
            CREATE_DATE: {
                displayName: _t("Create Date"),
                modelField: "create_date",
            },
        };
    }
    
    _defaultSearchDetails(){
        return {fieldName: "name",searchTerm: "",}
    }
    _defaultFilterDetails(){
        return "all"
    }

    //#region FETCH
    _computeSyncedPosOrderDomain() {
        
        const { fieldName, searchTerm } = this.state.search;
        const searchField = this._getSearchFields()?.[fieldName] ?? undefined;
        let domain = []

        if (searchField && searchTerm && searchField.modelField )
            domain.push([searchField.modelField, "ilike", `%${searchTerm}%`])
        
        if(this.state.filter && this.state.filter != 'all')
            domain.push(['state','=', this.state.filter])
        
        return domain;
        
    }

    async _fetchPosOrders() {
        const domain = this._computeSyncedPosOrderDomain();
        const offset = (this.state.page - 1) * NBR_BY_PAGE
        const { data , totalCount } = await this.pos.data.call(
            "pos.order",
            "read_no_draft_pos_order_ids",
            [],
            {
                domain,
                limit: NBR_BY_PAGE,
                offset,
            }
        );

        this.totalPosOrderCount = totalCount;
        this.state.filteredPosOrderList = data
        this.selectedPosOrder = null
    }

    async _fetchposOrderLines(pos_order) {
        this.state.posOrderLines  = await this.pos.data.call(
            "pos.order",
            "read_pos_order_lines",
            [],
            {pos_order_id: pos_order.id}
        ); 
    }

    
}


registry.category("pos_screens").add("ePosOrderScreen", ePosOrderScreen);