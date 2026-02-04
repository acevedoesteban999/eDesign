import { patch } from "@web/core/utils/patch";
import { Orderline } from '@point_of_sale/app/generic_components/orderline/orderline';

patch(Orderline,{
    props:{
        ...Orderline.props,
        line:{
            ...Orderline.props.line,
            shape:{
                ...Orderline.props.line.shape,
                design_id: { 
                    type: [Object,Boolean], 
                    optional: true , 
                    shape:{
                        default_code:{ type: String }
                    }
                }
            },
        }
    }
})


