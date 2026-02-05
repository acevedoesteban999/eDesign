/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, onMounted, onWillStart, onWillUnmount, useRef, useState  } from "@odoo/owl";
import { FileUploader } from "@web/views/fields/file_handler";
import { loadJS, loadCSS } from "@web/core/assets";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

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
            error: null,
            recordIsSaved: false,
        });
        
        this.player = null;
        this.playerRef = useRef("player");
        this._listeners = []; 

        onWillStart(async () => {
            await Promise.all([
                loadCSS("/e_video_content/static/src/library/plyr/plyr.css"),
                loadJS("/e_video_content/static/src/library/plyr/plyr.js")
            ]);
        });

        onMounted(() => this.loadData());
        onWillUnmount(() => this.destroy());
    }

    get hasVideo() {
        return Boolean(this.state.videoUrl);
    }

    get isReadonly() {
        return this.props.readonly;
    }

    async loadData() {
        await this.props.record.load();
        const { resId, resModel } = this.props.record;
        const fieldValue = this.props.record.data[this.props.name];
        
        this.clearError();
        
        if (!fieldValue || !resModel || !resId) {
            this.clearVideo();
            return;
        }

        this.setLoading(true);

        try {
            this.state.videoUrl = `/e_video_content/video/stream/${resModel}/${resId}`;
            await this.initPlayer();
        } catch (error) {
            console.error("VideoContent init error:", error);
            this.setError("Failed to load video player");
        } finally {
            this.setLoading(false);
        }
    }

    async initPlayer() {
        if (!this.playerRef.el || !window.Plyr) return;

        this.destroyPlayer();

        await new Promise(resolve => setTimeout(resolve, 100));

        try {
            this.player = new Plyr(this.playerRef.el, {
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

            // Bind events con tracking para cleanup
            const events = ['ready', 'error', 'loadedmetadata'];
            events.forEach(event => {
                const handler = this.handlePlayerEvent.bind(this, event);
                this.player.on(event, handler);
                this._listeners.push({ event, handler });
            });

        } catch (error) {
            console.error("Plyr initialization failed:", error);
            throw error;
        }
    }

    handlePlayerEvent(event) {
        switch(event) {
            case 'ready':
            case 'loadedmetadata':
                this.setLoading(false);
                break;
            case 'error':
                this.setError("Video playback error");
                break;
        }
    }

    destroyPlayer() {
        if (!this.player) return;
        
        try {
            // Remove tracked listeners first
            this._listeners.forEach(({ event, handler }) => {
                this.player.off(event, handler);
            });
            this._listeners = [];
            
            this.player.destroy();
        } catch (e) {
            console.warn("Error destroying player:", e);
        } finally {
            this.player = null;
        }
    }

    destroy() {
        this.destroyPlayer();
        this.clearVideo();
    }

    clearVideo() {
        if (this.state.videoUrl?.startsWith('blob:')) {
            URL.revokeObjectURL(this.state.videoUrl);
        }
        this.state.videoUrl = null;
    }

    setLoading(value) {
        this.state.loading = value;
    }

    setError(message) {
        this.state.error = message;
        this.setLoading(false);
    }

    clearError() {
        this.state.error = null;
    }

    get filename() {
        return this.props.record.data[this.props.filenameField] || "";
    }

    async _force_write(data){
        if(this.props.record.resId)
            await this.props.record.model.orm.write(
                this.props.record.resModel,
                [this.props.record.resId],
                data,
            )
    }

    async update({ data, name }) {
        if (!data) 
            return;

        this.setLoading(true);
        this.clearError();
        this.clearVideo();

        try {
            
            await this._force_write({ 
                [this.props.name]: data, 
                [this.props.filenameField]: name 
            })
            await this.loadData();
            
        } catch (error) {
            console.error("Upload error:", error);
            this.setError("Upload failed");
        }
    }

    async onDelete() {
        await this.props.record.model.dialog.add(ConfirmationDialog, {
            title: "Confirm",
            body: `Are you sure you want to delete the video?`,
            confirm: async () => {
                this.destroy();
                await this._force_write({ 
                    [this.props.name]: false, 
                    [this.props.filenameField]: false 
                });
                await this.loadData()
            },
            cancel: () => {},
        });
        
    }

    async retry() {
        this.clearError();
        await this.loadData();
    }
}

export const videoContentField = {
    component: VideoContentField,
    supportedTypes: ["binary"],
    extractProps: ({ attrs }) => ({ filenameField: attrs.filename }),
};

registry.category("fields").add("video_content", videoContentField);