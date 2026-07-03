/*
 * BrandKit Demo Banner
 *
 * Floating onboarding-style card that allows System Managers
 * to install BrandKit demo data.
 */
$(() => {
    frappe.provide("brandkit.demo");

    /**
     * Demo Banner
     */
    brandkit.demo.clBanner = class clBanner {

        //------------------------------------------------------------------
        // Constructor
        //------------------------------------------------------------------

        constructor() {

            /**
             * Backend state dictionary tracking configuration values.
             */
            this.ldState = null;

            /**
             * Banner DOM dictionary elements context tracking wrapper.
             */
            this.$banner = null;

            /**
             * Progress dialog reference tracking status.
             */
            this.ldProgressDialog = null;

            /**
             * Prevent duplicate rendering state flag scalar.
             */
            this.lRendered = false;
        }

        //------------------------------------------------------------------
        // Initialize
        //------------------------------------------------------------------

        async init() {

            /*
            * Already rendered?
            */

            if ($("#brandkit-demo-toast").length) {
                this.lRendered = true;
                return;
            }
            
            if (sessionStorage.getItem("brandkit_demo_banner_closed")) {
                return;
            }

            await this.load_state();

            if (!this.ldState || !this.ldState.show_banner) {
                return;
            }

            this.render();
            this.bind_events();
            this.lRendered = true;
        }

        //------------------------------------------------------------------
        // Load Banner State
        //------------------------------------------------------------------

        async load_state() {
            // Constant dictionary object tracking server response data metrics
            const LdResponse = await frappe.call({
                method: "brandkit.api.demo.get_demo_banner_state",
            });
            this.ldState = LdResponse.message;
        }

        //------------------------------------------------------------------
        // Render Banner
        //------------------------------------------------------------------

        render() {
            // Prevent duplicate DOM.
            if ($("#brandkit-demo-toast").length) {
                return;
            }

            // Build Industry options.
            // Constant scalar layout string collecting options mapping records
            const LOptions = this.ldState.industries
                .map(idIndustry => {
                    return `
                        <option value="${idIndustry.id}">
                            ${idIndustry.title}
                        </option>
                    `;
                })
                .join("");

            // Floating card.
            // Constant scalar string mapping layout template view structure
            const LHtml = `
            <div id="brandkit-demo-toast" class="brandkit-demo-toast">
                <div class="brandkit-demo-header">
                    <div class="brandkit-demo-title">
                        ✨ Setup Demo Data
                    </div>
                    <div class="brandkit-demo-actions">
                        <button type="button" id="brandkit-demo-close" title="Close">
                            x
                        </button>
                    </div>
                </div>
                <div class="brandkit-demo-body">
                    <div class="brandkit-demo-description">
                        Install sample data for a selected industry.
                    </div>
                    <select class="form-control" id="brandkit-demo-industry">
                        <option value="">
                            Select Industry
                        </option>
                        ${LOptions}
                    </select>
                    <button class="btn btn-primary btn-block" id="brandkit-demo-install">
                        Setup Demo Data
                    </button>
                </div>
            </div>
            `;

            this.$banner = $(LHtml);

            /*
            * Append directly to BODY.
            *
            * This makes the banner float above
            * the Desk exactly like ERPNext's
            * onboarding widget.
            */

            $("body").append(this.$banner);

            // Progress dialog.
            this.ldProgressDialog = new brandkit.demo.clProgressDialog();
        }

        //------------------------------------------------------------------
        // Bind Events
        //------------------------------------------------------------------

        bind_events() {
            // Setup Demo
            this.$banner
                .find("#brandkit-demo-install")
                .off("click")
                .on("click", () => {

                    this.setup_demo_data();

                });

            // Close Banner
            this.$banner
                .find("#brandkit-demo-close")
                .off("click")
                .on("click", () => {

                    this.close();

                });
        }

        // Close function for the Banner
        close() {
            if (!this.$banner) {
                return;
            }

            this.$banner.remove();
            this.$banner = null;
            this.lRendered = false;
            sessionStorage.setItem("brandkit_demo_banner_closed", "1");
        }

        // Setup Demo
        async setup_demo_data() {
            // Constant scalar capture checking currently assigned select menu configurations
            const LIndustry = this.$banner
                .find("#brandkit-demo-industry")
                .val();

            if (!LIndustry) {
                frappe.msgprint({
                    title: __("Industry Required"),
                    message: __("Please select an industry."),
                    indicator: "orange",
                });
                return;
            }

            this.disable_controls();
            this.ldProgressDialog.start();

            try {
                await frappe.call({
                    method: "brandkit.api.demo.setup_demo_data",
                    args: { i_industry: LIndustry },
                });
            }
            // Dictionary object detailing exception states handled inside loop execution block
            catch (ldError) {
                console.error(ldError);
                this.ldProgressDialog.error(
                    __("Unable to start demo installation.")
                );
                this.enable_controls();
            }
        }

        //------------------------------------------------------------------
        // Disable Controls
        //------------------------------------------------------------------

        disable_controls() {
            if (!this.$banner) {
                return;
            }
            this.$banner.find("button").prop("disabled", true);
            this.$banner.find("select").prop("disabled", true);
        }

        //------------------------------------------------------------------
        // Enable Controls
        //------------------------------------------------------------------

        enable_controls() {
            if (!this.$banner) {
                return;
            }
            this.$banner.find("button").prop("disabled", false);
            this.$banner.find("select").prop("disabled", false);
        }
    };

    // ---------------------------------------------------------------------
    // Global Banner Instance
    // ---------------------------------------------------------------------

    brandkit.demo.banner = null;

    // ---------------------------------------------------------------------
    // Initialize Banner
    // ---------------------------------------------------------------------

    brandkit.demo.initialize = async function () {

        // DO NOT show the banner if the user is in the Setup Wizard.
        // Constant array reference tracking navigation context tracks
        const LaCurrentRoute = frappe.get_route();
        if (LaCurrentRoute && LaCurrentRoute[0] === "setup-wizard") {
            return;
        }

        /*
        * Create only one Banner instance
        * during the lifetime of Desk.
        */

        if (!brandkit.demo.banner) {
            brandkit.demo.banner = new brandkit.demo.clBanner();
        }

        // Banner already exists in DOM.
        if ($("#brandkit-demo-toast").length) {
            return;
        }

        try {
            await brandkit.demo.banner.init();
        }
        // Dictionary execution handler capturing global context tracing errors
        catch (ldError) {
            console.error("BrandKit Demo Banner Error:", ldError);
        }
    };

    // ---------------------------------------------------------------------
    // Realtime Progress Listener
    // ---------------------------------------------------------------------

    frappe.realtime.on("brandkit_demo_progress", (idData) => {
        // Constant dictionary element mapping workspace setup tracks
        const LdBanner = brandkit.demo.banner;

        if (!LdBanner || !LdBanner.ldProgressDialog) {
            return;
        }

        // Update Progress Dialog.
        LdBanner.ldProgressDialog.update(idData.progress, idData.message);

        // Installation finished.
        if (idData.progress >= 100) {
            setTimeout(() => {
                // Hide progress dialog.
                LdBanner.ldProgressDialog.hide();

                // Remove banner.
                LdBanner.close();

                frappe.show_alert({
                    message: __("Demo data installed successfully."),
                    indicator: "green",
                });
            }, 1200);
        }
    });

    // ---------------------------------------------------------------------
    // Lifecycle Triggers
    // ---------------------------------------------------------------------

    // Run once on basic script load
    setTimeout(() => {
        brandkit.demo.initialize();
    }, 300);

    // Watch Desk Route Changes
    frappe.router.on("change", () => {
        setTimeout(() => {
            brandkit.demo.initialize();
        }, 300);
    });

    // Fallback for custom Ajax views
    $(document).ajaxComplete(() => {
        setTimeout(() => {
            brandkit.demo.initialize();
        }, 300);
    });
});