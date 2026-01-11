import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { formatDateTime, parseDateTime } from "@web/core/l10n/dates";
import { parseFloat } from "@web/views/fields/parsers";
import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { BackButton } from "@point_of_sale/app/screens/product_screen/action_pad/back_button/back_button";
import { InvoiceButton } from "@point_of_sale/app/screens/ticket_screen/invoice_button/invoice_button";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { CenteredIcon } from "@point_of_sale/app/generic_components/centered_icon/centered_icon";
import { SearchBar } from "@point_of_sale/app/screens/ticket_screen/search_bar/search_bar";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, onMounted, onWillStart, useState } from "@odoo/owl";
import {
    BACKSPACE,
    Numpad,
    getButtons,
    ZERO,
    DECIMAL,
} from "@point_of_sale/app/generic_components/numpad/numpad";
import { PosOrderLineRefund } from "@point_of_sale/app/models/pos_order_line_refund";
import { fuzzyLookup } from "@web/core/utils/search";
import { parseUTCString } from "@point_of_sale/utils";
import { useTrackedAsync } from "@point_of_sale/app/utils/hooks";
import { ConnectionLostError } from "@web/core/network/rpc";

const NBR_BY_PAGE = 30;

export class PickingScreen extends Component {
    static template = "e_pos_mrp.PickingScreen";
    static components = {
        ActionpadWidget,
        InvoiceButton,
        Orderline,
        OrderWidget,
        CenteredIcon,
        SearchBar,
        Numpad,
        BackButton,
    };

    setup() {
        this.pos = usePos();
        this.ui = useState(useService("ui"));
        
        this.state = useState({
            page: 1,
            nbrPage: 1,
            filter: this._defaultFilterDetails(),
            search: this._defaultSearchDetails(),
            selectedPickingId: null,
            filteredPickingList:[]
        });
        this.totalPickingCount = 0

        onMounted(()=>{
            this.onFilterSelected(this.state.filter);
        });
    }

    
    async onFilterSelected(selectedFilter) {
        this.state.filter = selectedFilter;
        await this._fetchPickings();
    }
    getNumpadButtons() {
        return getButtons(
            [{ value: "-", text: "+/-", disabled: true }, ZERO, DECIMAL],
            [
                { value: "quantity", text: _t("Qty"), class: "active border-primary" },
                { value: "discount", text: _t("% Disc"), disabled: true },
                { value: "price", text: _t("Price"), disabled: true },
                BACKSPACE,
            ]
        );
    }
    async onSearch(search) {
        this.state.search = search;
        this.state.page = 1;
        await this._fetchPickings();
    }

    onClickpicking(clickedPicking) {
        this.state.selectedPickingId = clickedPicking.id;
    }

    onClickPickinline(picking_line,picking_id) {
        this.state.selectedPickinglineId = picking_line.id;
    }

    onClickRefundOrderUid(orderUuid) {
        const refundOrder = this.pos.models["pos.picking"].find((picking) => picking.uuid == orderUuid);
        if (refundOrder) {
            this._setOrder(refundOrder);
        }
    }

    _isPickingSelected (picking){
        return picking.id == this.state.selectedPickingId
    }

    getSelectedPickinglineId() {
        return this.state.filteredPickingList.filter((p)=> this._isPickingSelected(p))
    }

    activeOrderFilter(o) {
        const screen = ["ReceiptScreen", "TipScreen"];
        const oScreen = o.get_screen_data();
        return (!o.finalized || screen.includes(oScreen.name)) && o.uiState.displayed;
    }

    switchPane() {
        this.pos.switchPaneTicketScreen();
    }

    GetDate(date) {
        return formatDateTime(parseUTCString(date));
    }

    getPartner(picking) {
        return picking.get_partner_name();
    }
    
    
    isHighlighted(picking) {
        return this._isPickingSelected(picking) ;
    }
    
    closePickingScreen() {
        this.pos.showScreen("ProductScreen");
    }

    GetState(state){
        return{
            'waiting': _t("Waiting"),
            'assigned': _t("Ready"),
            'done': _t("Delivered"),
        
        }[state]
    }

    //#region PAGE
    async onNextPage() {
        if (this.state.page < this.getNbrPages()) {
            this.state.page += 1;
            await this._fetchPickings();
        }
    }

    async onPrevPage() {
        if (this.state.page > 1) {
            this.state.page -= 1;
            await this._fetchPickings();
        }
    }

    getNbrPages() {
        return Math.ceil(this.totalPickingCount / NBR_BY_PAGE);
    }
    getPageNumber() {
        if (!this.totalPickingCount) {
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
            defaultFilter: 'done',
        };
    }

    
    _getFilterOptions() {
        const states = new Map();
        states.set("all", {
            text: _t("All"),
            indented: true,
        });
        states.set("assigned", {
            text: _t("Assigned"),
            indented: true,
        });
        states.set("waiting", {
            text: _t("Waiting"),
            indented: true,
        });
        states.set("done", {
            text: _t("Done"),
            indented: true,
        });
        
        return states;
    }
    

    _getSearchFields() {
        return {
            NAME: {
                displayName: _t("Picking"),
                modelField: "name",
            },
            POS_ORDER_NAME: {
                displayName: _t("Pos Order"),
                modelField: "pos_order_id.name",
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
        return "assigned"
    }

    //#region FETCH
    _computeSyncedPickingsDomain() {
        
        const { fieldName, searchTerm } = this.state.search;
        const searchField = this._getSearchFields()?.[fieldName] ?? undefined;
        let domain = []

        if (searchField && searchTerm && searchField.modelField )
            domain.push([searchField.modelField, "ilike", `%${searchTerm}%`])
        
        if(this.state.filter && this.state.filter != 'all')
            domain.push(['state','=', this.state.filter])
        
        return domain;
        
    }

    async _fetchPickings() {
        const domain = this._computeSyncedPickingsDomain();
        const offset = (this.state.page - 1) * NBR_BY_PAGE
        const { PickingsInfo, totalPickingCount } = await this.pos.data.call(
            "stock.picking",
            "search_assigned_picking_ids",
            [],
            {
                domain,
                limit: 30,
                offset,
            }
        );

        this.totalPickingCount = totalPickingCount;
        this.state.filteredPickingList = PickingsInfo
        this.selectedPickingId = null
    }
}


registry.category("pos_screens").add("PickingScreen", PickingScreen);