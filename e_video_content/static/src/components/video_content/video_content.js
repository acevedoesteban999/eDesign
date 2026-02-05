/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, onMounted, onWillStart, onWillUnmount, onWillUpdateProps, useRef, useState } from "@odoo/owl";
import { FileUploader } from "@web/views/fields/file_handler";
import { loadJS, loadCSS } from "@web/core/assets";

const MAX_INLINE_SIZE = 2 * 1024 * 1024; // 2MB

export class VideoContentField extends Component {
    static template = "e_video_content.VideoContentField";
    static components = { FileUploader };
    static props = {
        ...standardFieldProps,
        filenameField: { type: String, optional: true },
    };

    setup() {
        this.state = useState({
            videoUrl: null,
            
            loading: false,
            libsLoaded: false,
            error: null,
        });
        this.player = null;
        this.playerRef = useRef("player");
        this.objectUrl = null;
        this.lastRecordId = null;

        onWillStart(async()=>{
            await loadCSS("/e_video_content/static/src/library/plyr/plyr.css")
            await loadJS("/e_video_content/static/src/library/plyr/plyr.js")
        })

        onMounted(() => this.loadData());
        
        onWillUnmount(() => this.destroy());
    }

    async loadData() {
        const recordId = this.props.record.resId;
        const resModel = this.props.record.resModel;
        const fieldValue = this.props.record.data[this.props.name];
        
        this.state.error = null;
        
        if (!fieldValue || !resModel || !recordId) {
            this.state.videoUrl = null;
            this.destroyPlayer();
            return;
        }

        this.state.loading = true;

        try {
           
                this.state.isNewUpload = false;
                this.state.videoUrl = `/e_video_content/video/stream/${resModel}/${recordId}`;
                await this.initPlayer();
                this.state.loading = false;
                return;

        } catch (error) {
            console.error("VideoContent init error:", error);
            this.state.error = "Failed to load video player";
            this.state.loading = false;
        }
    }

    async initPlayer() {
        if (!this.playerRef.el || !window.Plyr) return;

        this.destroyPlayer();

        const videoEl = this.playerRef.el;
        
        if (this.state.videoUrl && !videoEl.src) {
            videoEl.src = this.state.videoUrl;
        }

        await new Promise(resolve => setTimeout(resolve, 500));

        this.player = new Plyr(videoEl, {
            controls: [
                'play-large', 'play', 'progress', 'current-time', 'duration',
                'mute', 'volume', 'captions', 'settings', 'pip', 'airplay', 'fullscreen'
            ],
            settings: ['captions', 'quality', 'speed', 'loop'],
            loadSprite: true,
            iconUrl: '/e_video_content/static/src/library/plyr/plyr.svg',
            blankVideo: null,
            autoplay: false,
            preload: 'metadata',
            storage: { enabled: false },
            tooltips: { controls: true, seek: true },
            keyboard: { focused: true, global: false },
            clickToPlay: true,
            hideControls: true,
            resetOnEnd: false,
        });

        this.player.on('ready', () => {
            this.state.loading = false;
        });

        this.player.on('error', () => {
            this.state.error = "Video playback error";
            this.state.loading = false;
        });

        this.player.on('loadedmetadata', () => {
            this.state.loading = false;
        });
    }

    destroyPlayer() {
        if (this.player) {
            try {
                this.player.destroy();
            } catch (e) {
                console.warn("Error destroying player:", e);
            }
            this.player = null;
        }
    }

    destroy() {
        this.destroyPlayer();
    }


    get filename() {
        return this.props.record.data[this.props.filenameField] || "";
    }

    async update({ data, name }) {
        if (!data) {
            return
        }

        
        try {
            await this.props.record.update({ 
                [this.props.name]: data, 
                [this.props.filenameField]: name 
            });
            
            await this.loadData();
            
        } catch (error) {
            console.error("Upload error:", error);
            this.state.error = "Upload failed";
            this.tempBase64 = null;
            this.state.isNewUpload = false;
        }
    }

    async onDelete() {
        this.tempBase64 = null;
        this.state.isNewUpload = false;
        this.destroy();
        this.state.videoUrl = null;
        return this.props.record.update({ 
            [this.props.name]: false, 
            [this.props.filenameField]: false 
        });
    }

    async retry() {
        this.state.error = null;
        await this.loadData();
    }
}

export const videoContentField = {
    component: VideoContentField,
    supportedTypes: ["binary"],
    extractProps: ({ attrs }) => ({ filenameField: attrs.filename }),
};

registry.category("fields").add("video_content", videoContentField);