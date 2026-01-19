import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";


patch(ReceiptScreen.prototype,{
    async orderDone() {
        await this.pos._compute_hide_out_stock_data()
        super.orderDone()
    }
})
