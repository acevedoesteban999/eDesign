import { patch } from "@web/core/utils/patch";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { _t } from "@web/core/l10n/translation";


patch(Orderline, {
    props: {
        ...Orderline.props,
        line: {
            ...Orderline.props.line,
            shape: {
                ...Orderline.props.line.shape,
                has_create_pos_mrp: { type: Boolean, optional: true },
            },
        },
    }
})




        