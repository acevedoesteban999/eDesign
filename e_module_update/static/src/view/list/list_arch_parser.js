import { ListArchParser } from '@web/views/list/list_arch_parser';
import { patch } from "@web/core/utils/patch";
import { exprToBoolean } from "@web/core/utils/strings";
import { visitXML } from "@web/core/utils/xml";

patch(ListArchParser.prototype,{
    parse(xmlDoc, models, modelName) {
        const _parse = super.parse(xmlDoc, models, modelName)  
        visitXML(xmlDoc,(node) => {
            if ("list" === node.tagName && _parse.activeActions)
                _parse.activeActions['link'] = exprToBoolean(xmlDoc.getAttribute("link"), true) 
                _parse.activeActions['unlink'] = exprToBoolean(xmlDoc.getAttribute("unlink"), true) 
            return {..._parse}
        })
        return _parse
    }
})

