import { ListRenderer } from '@web/views/list/list_renderer';
import { patch } from "@web/core/utils/patch";

patch(ListRenderer.prototype,{
    get canUnlink() {
        return "unlink" in this.activeActions ? this.activeActions.unlink : true;
    }
})

