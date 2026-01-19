import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { formatDateTime, parseDateTime } from "@web/core/l10n/dates";
import { _t } from "@web/core/l10n/translation";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { BackButton } from "@point_of_sale/app/screens/product_screen/action_pad/back_button/back_button";
import { CenteredIcon } from "@point_of_sale/app/generic_components/centered_icon/centered_icon";
import { SearchBar } from "@point_of_sale/app/screens/ticket_screen/search_bar/search_bar";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, onMounted, onWillStart, useState } from "@odoo/owl";
import { parseUTCString } from "@point_of_sale/utils";

const NBR_BY_PAGE = 30;

export class PickingScreen extends Component {
    static template = "e_pos_mrp.PickingScreen";
    static components = {
        CenteredIcon,
        SearchBar,
        BackButton,
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
            selectedPicking: null,
            filteredPickingList:[],
            pickingLines:[],
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
    
    async onSearch(search) {
        this.state.search = search;
        this.state.page = 1;
        await this._fetchPickings();
    }

    async onClickpicking(clickedPicking,switchPane=false) {
        this.state.selectedPicking = clickedPicking;
        await this._fetchPickingLines(clickedPicking)
        if (switchPane)
            this.switchPane()
    }

    onClickRefundOrderUid(orderUuid) {
        const refundOrder = this.pos.models["pos.picking"].find((picking) => picking.uuid == orderUuid);
        if (refundOrder) {
            this._setOrder(refundOrder);
        }
    }

    _isPickingSelected (picking){
        return picking.id == this.state.selectedPicking?.id || null
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


    onConfirmPicking(){
        this.dialog.add(ConfirmationDialog, {
            title: _t("Confirm Delivery ?"),
            body: _t("Are you sure that the customer wants to recive the picking?"),
            confirm: () => this.ConfirmPicking(this.state.selectedPicking),
        });
    }
    async ConfirmPicking(pickingLine){
        await this._confirmPicking(pickingLine)
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
            defaultFilter: this.state.filter,
        };
    }

    
    _getFilterOptions() {
        const states = new Map();
        states.set("all", {
            text: _t("All"),
            indented: true,
        });
        states.set("assigned", {
            text: _t("Ready"),
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
                displayName: _t("Delivery"),
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
            "read_assigned_picking_ids",
            [],
            {
                domain,
                limit: NBR_BY_PAGE,
                offset,
            }
        );

        this.totalPickingCount = totalPickingCount;
        this.state.filteredPickingList = PickingsInfo
        this.selectedPicking = null
    }

    async _fetchPickingLines(pickingLine) {
        this.state.pickingLines  = await this.pos.data.call(
            "stock.picking",
            "read_picking_lines",
            [],
            {picking_id: pickingLine.id}
        ); 
    }

    async _confirmPicking(pickingLine) {
        await this.pos.data.call(
            "stock.picking",
            "confirm_picking",
            [],
            {picking_id: pickingLine.id}
        ); 
        this.notification.add(
            _t("Success confirmation for Delivery %s in POS order: %s")
                .replace("%s", pickingLine.name)
                .replace("%s", pickingLine.pos_order_id[1]),
            {
                type: "success",
                title: _t("Success"),
                autocloseDelay: 3000,
            }
        );
        this.closePickingScreen();
    }
}


registry.category("pos_screens").add("PickingScreen", PickingScreen);