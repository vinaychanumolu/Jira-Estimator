import streamlit as st
from estimate_story_points_vector import estimate_story_points

st.set_page_config(
    page_title="Jira Story Estimator (AI-powered)",
    page_icon="favicon.svg",
    layout="wide"
)

# --- Jira-like styling and header ---
st.markdown(
    """
<style>
/* Topbar base */
.jira-topbar{background:#1868db !important;color:#fff !important;padding:12px 20px;display:flex;align-items:center;gap:12px;font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;box-shadow:0 2px 6px rgba(0,0,0,0.12)}
.jira-logo{font-weight:700;font-size:18px;display:flex;align-items:center;gap:8px}
.jira-icon svg{display:block}
.jira-actions{opacity:0.95}

/* Page typography and spacing */
/* Page typography and spacing */
html, body {margin:0;padding:0;overflow-x:hidden;background:#F4F5F7;font-family:'Inter','Roboto','Helvetica Neue',Arial,sans-serif;color:#172B4D}
body, .main, .block-container{font-size:16px !important;line-height:1.65 !important}
label{ !important;margin-bottom:0.55rem !important;letter-spacing:0.02em !important;}
label span{!important;text-transform:none !important}
/* Force Streamlit control labels and section titles to Jira blue with higher specificity */
.stTextInput label, .stTextInput>label, .stTextInput>div>label,
.stTextArea label, .stTextArea>label, .stTextArea>div>label,
.stNumberInput label, .stNumberInput>label, .stNumberInput>div>label,
.stSelectbox label, .stSelectbox>label, .stSelectbox>div>label,
.stCheckbox label, .stCheckbox>label, .stCheckbox>div>label,
.stRadio label, .stRadio>label, .stRadio>div>label,
.stMultiSelect label, .stSlider label,
.field-section-title, .pp-card-title-text {color: var(--jira-blue) !important}
input, textarea, select{font-family:inherit !important;font-size:16px !important;padding:14px 18px !important;border:2px solid rgba(9,30,66,0.12) !important;border-radius:12px !important;background:#fff !important;transition:all 0.2s ease !important;box-shadow:none !important;background-clip:padding-box !important}
input[role="combobox"]{appearance:menulist-button !important;-webkit-appearance:menulist-button !important;cursor:pointer !important;background:#fff !important;caret-color:transparent !important;box-shadow:none !important}
input[role="combobox"]::-webkit-search-decoration, input[role="combobox"]::-webkit-clear-button, input[role="combobox"]::-webkit-inner-spin-button, input[role="combobox"]::-webkit-outer-spin-button{display:none !important}
input:focus, textarea:focus, select:focus{border-color:#1868db !important;box-shadow:0 0 0 4px rgba(24,104,219,0.12) !important;outline:none !important}
textarea{resize:vertical !important;min-height:180px !important}

/* Input containers */
.stTextInput, .stTextArea, .stNumberInput, .stSelectbox{margin-bottom:1.9rem !important}
.stTextInput>div, .stTextInput>div>div,
.stNumberInput>div, .stNumberInput>div>div,
.stSelectbox>div, .stSelectbox>div>div {
  height: auto !important;
  min-height: 44px !important;
  border:none !important;
  background:transparent !important;
}
.stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select,
.stSelectbox input[role="combobox"] {
  padding:12px 16px !important;
  font-size:16px !important;
  min-height:44px !important;
  height:44px !important;
  width:100% !important;
  box-sizing:border-box !important;
  line-height:22px !important;
}
/* Minimal select styling - preserve BaseWeb dropdown functionality */
.stSelectbox{
    box-sizing:border-box !important;
    padding:0 !important;
}
.stSelectbox [data-baseweb="select"]{
    width:100% !important;
}
.stSelectbox [data-baseweb="select"] > div{
    border:2px solid rgba(9,30,66,0.12) !important;
    border-radius:12px !important;
    background:#fff !important;
    box-sizing:border-box !important;
    height:44px !important;
    min-height:44px !important;
    max-height:44px !important;
}
/* Remove extra padding from BaseWeb nested divs */
.stSelectbox [data-baseweb="select"] > div > div,
.stSelectbox [data-baseweb="select"] > div > div > div {
    padding:0 !important;
    margin:0 !important;
    height:100% !important;
}
.stSelectbox input[role="combobox"]{
    padding:12px 16px !important;
    font-size:16px !important;
    color: rgb(49,51,63) !important;
    background:transparent !important;
    border:none !important;
    height:100% !important;
}
.stSelectbox [data-baseweb="select"] [value]{
    padding:12px 16px !important;
    font-size:16px !important;
    color: rgb(49,51,63) !important;
    height:100% !important;
    display:flex !important;
    align-items:center !important;
}
.stNumberInput input[type="number"] {
    min-height:44px !important;
    height:44px !important;
    padding:12px 16px !important;
}

/* Make select label behave like other control labels (above the box) */
.stSelectbox > label[data-testid="stWidgetLabel"], .stSelectbox > label{
    display:block !important;
    margin-bottom:8px !important;
    font-weight:600 !important;
    color: #42526E !important;
}

/* Reduce extra vertical spacing so overall control height matches text input */
.stSelectbox, .stSelectbox *{box-sizing:border-box !important}
.stSelectbox{padding-top:0 !important; padding-bottom:0 !important; margin-bottom:1.9rem !important}
.stTextArea>div>div>textarea{padding:18px 20px !important;font-size:16px !important;line-height:1.7 !important;min-height:190px !important;width:100% !important;box-sizing:border-box !important}

/* Column alignment */
.stColumns>div>div{display:flex !important;align-items:flex-end !important}

/* Button styling */
button{border-radius:10px !important;padding:10px 18px !important;letter-spacing:0.01em !important;font-weight:600 !important;border:none !important;background:#1868db !important;color:#fff !important;font-size:15px !important;transition:all 0.2s ease !important;box-shadow:0 2px 6px rgba(24,104,219,0.15) !important}
button:hover{background:#1558b9 !important;box-shadow:0 4px 12px rgba(24,104,219,0.25) !important}
.stButton>button{width:100%;padding:10px 16px !important;min-height:44px !important;height:44px !important;display:flex !important;align-items:center !important;justify-content:center !important}
.stButton>button:first-child{padding:0 16px !important}
.small-button .stButton>button{width:auto;padding:10px 14px !important;min-height:34px !important;height:34px !important;font-size:14px !important}

/* Subheader styling */
.stSubheader{font-size:1.3rem !important;font-weight:700 !important;color:#172B4D !important;margin-top:1.8rem !important;margin-bottom:0.8rem !important}

/* Caption styling */
.field-section-title{font-size:26px !important;font-weight:700 !important;color:#1868db !important;margin-bottom:6px !important}
.field-section-subtitle{font-size:14px !important;color:#5E6C84 !important;margin-bottom:20px !important}
.stCaption{font-size:13px !important;color:#626F86 !important;margin-bottom:1rem !important;font-style:italic}

/* Info/Warning/Success boxes */
.stInfo, .stWarning, .stSuccess{padding:14px 16px !important;border-radius:10px !important;font-size:14px !important;line-height:1.5 !important}

/* Topbar style */
.jira-topbar{position:fixed;top:0;left:0;right:0;width:100%;background:#1868db !important;color:#fff !important;border-radius:0;margin:0;padding:16px 28px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 6px rgba(0,0,0,0.12);z-index:99999;font-family:'Inter','Roboto','Helvetica Neue',Arial,sans-serif;letter-spacing:0.03em}
.jira-logo{font-weight:700;font-size:18px;display:flex;align-items:center;gap:10px;color:#fff}
.jira-icon{display:flex;align-items:center;justify-content:center;solid rgba(255,255,255,0.72);border-radius:9px;background:#fff;}
.jira-icon svg{display:block}
.jira-logo span{font-family:'Inter','Roboto','Helvetica Neue',Arial,sans-serif;font-size:1rem}
.jira-actions{display:none}

/* Hide Streamlit default footer controls */
footer{display:none !important}

/* Keep Streamlit toolbar visible and place it inside the custom header area */
header{position:absolute;top:0;right:24px;left:auto;width:auto;z-index:99998;background:transparent !important;box-shadow:none !important;color:#fff !important}
header > div{display:flex !important;align-items:center !important;justify-content:flex-end !important;background:transparent !important;border:none !important;color:#fff !important}
header > div[data-testid="stToolbar"]{display:flex !important;align-items:center !important;justify-content:flex-end !important;background:transparent !important;border:none !important;color:#fff !important}
header, header *{color:#fff !important;background:transparent !important}
header svg, header svg *{fill:currentColor !important;stroke:currentColor !important;}
header button, header button *{background:transparent !important;color:#fff !important;border-color:rgba(255,255,255,0.2) !important;box-shadow:none !important}
header [data-testid="stToolbar"], header [data-testid="stToolbar"] *{background:transparent !important}
header > div[data-testid="stToolbar"] svg{display:none !important}
header > div[data-testid="stToolbar"]::before{content:'⋯';margin-right:10px;font-size:20px;color:#fff;line-height:1;}

/* Add top padding to page content */
.block-container, .main, main{padding-top:64px !important}

/* Board layout */
.jira-board{display:flex;gap:16px;margin-top:18px}
.jira-column{background:#F4F5F7;padding:12px;border-radius:6px;width:320px;min-height:220px}
.jira-column h4{margin:0 0 8px 0;color:#172B4D}
.jira-card{background:#fff;padding:10px;border-radius:6px;margin-bottom:10px;box-shadow:0 1px 2px rgba(9,30,66,0.08);border:1px solid rgba(9,30,66,0.04)}
.story-details-card,
.planning-poker-card,
.estimate-card {
    background:transparent;
    padding:0;
    border:none;
    box-shadow:none;
    margin:0;
}
.stVerticalBlock:has(> .stElementContainer .story-details-card),
.stVerticalBlock:has(> .stElementContainer .planning-poker-card),
.stVerticalBlock:has(> .stElementContainer .estimate-card) {
    background:#fff;
    padding:24px;
    border-radius:16px;
    box-shadow:0 4px 12px rgba(9,30,66,0.08);
    border:1px solid rgba(9,30,66,0.1);
    margin:0 auto 16px;
}
.stVerticalBlock:has(> .stElementContainer .story-details-card) .field-section-title,
.stVerticalBlock:has(> .stElementContainer .planning-poker-card) .field-section-title,
.stVerticalBlock:has(> .stElementContainer .estimate-card) .field-section-title {margin-top:0}
.stVerticalBlock:has(> .stElementContainer .story-details-card) .field-section-subtitle,
.stVerticalBlock:has(> .stElementContainer .planning-poker-card) .field-section-subtitle,
.stVerticalBlock:has(> .stElementContainer .estimate-card) .field-section-subtitle {margin-bottom:20px}
.pp-card{background:#F7F9FF;padding:28px;border-radius:18px;box-shadow:0 12px 34px rgba(63,81,181,0.08);border:1px solid rgba(55,84,183,0.12);max-width:980px;margin:0 auto 24px}
.pp-card-title{display:flex;flex-direction:column;align-items:flex-start;justify-content:flex-start;gap:8px;padding-bottom:18px;margin-bottom:22px;border-bottom:1px solid rgba(9,30,66,0.08);color:#172B4D}
.pp-card-title-text{font-size:18px;font-weight:700;letter-spacing:0.01em;color:#172B4D}
.pp-card-title-sub{font-size:14px;color:#42526E;margin-top:0}

/* Reveal Board Styles */
.reveal-board{display:grid;gap:12px;margin:20px 0}
.reveal-cards-row{display:flex;flex-wrap:wrap;gap:12px;justify-content:flex-start;margin-bottom:18px}
.reveal-estimate-card{background:#fff;border:2px solid rgba(9,30,66,0.08);border-radius:12px;padding:16px 20px;min-width:120px;text-align:center;transition:all 0.2s ease;box-shadow:0 2px 8px rgba(9,30,66,0.04)}
.reveal-estimate-card .member-name{font-size:0.85rem;font-weight:600;color:#42526E;margin-bottom:8px;display:block}
.reveal-estimate-card .estimate-value{font-size:1.6rem;font-weight:700;color:#1868db;font-family:monospace}
.reveal-estimate-card.ai-card{background:#4688EC;border-color:#4688EC;box-shadow:0 8px 20px rgba(24,104,219,0.16)}
.reveal-estimate-card.ai-card .member-name{color:#fff}
.reveal-estimate-card.ai-card .estimate-value{color:#fff}
.reveal-estimate-card.not-submitted{opacity:0.5;border-style:dashed}
.reveal-estimate-card.not-submitted .estimate-value{color:#ccc}

/* Small responsive tweaks */
@media (max-width: 900px){.jira-board{flex-direction:column}.jira-column{width:100%}}
</style>
<script>
    (function(){
        const apply = ()=>{
            document.querySelectorAll('input[role="combobox"]').forEach(i=>{
                try{
                    i.style.setProperty('position','absolute','important');
                    i.style.setProperty('left','0px','important');
                    i.style.setProperty('top','0px','important');
                    i.style.setProperty('bottom','0px','important');
                    i.style.setProperty('right','36px','important');
                    i.style.setProperty('width','calc(100% - 36px)','important');
                    i.style.setProperty('box-sizing','border-box','important');
                    i.style.setProperty('height','100%','important');
                    i.style.setProperty('opacity','1','important');
                    i.style.setProperty('pointer-events','auto','important');
                }catch(e){}
            });
        };
        apply();
        const obs = new MutationObserver(()=>apply());
        obs.observe(document.body,{childList:true,subtree:true});
    })();
</script>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="jira-topbar">
    <div class="jira-logo">
        <span class="jira-icon">
            <svg width="32" height="32" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Jira icon">
                <path d="M0 128C0 57.312 57.312 0 128 0h256.001c70.688 0 128 57.312 128 128v256.001c0 70.688-57.312 128-128 128h-256C57.311 512.002 0 454.69 0 384.002v-256z" fill="#1868db" fill-rule="nonzero"/>
                <path d="M189.544 324.041H160.69c-43.51 0-74.72-24.483-74.72-60.321h155.115c8.043 0 13.248 5.241 13.248 12.677V419.77c-38.784 0-64.79-28.853-64.79-69.07V324.04zm76.608-71.245h-28.843c-43.51 0-74.73-24.043-74.73-59.89h155.125c8.043 0 13.718 4.81 13.718 12.236v143.373c-38.785 0-65.27-28.843-65.27-69.061v-26.658zm77.088-70.815h-28.842c-43.51 0-74.731-24.483-74.731-60.321h155.125c8.043 0 13.248 5.241 13.248 12.237v143.372c-38.784 0-64.8-28.853-64.8-69.06V181.98z" fill="#fff" fill-rule="nonzero"/>
            </svg>
        </span>
        <span>Jira Story Estimator (AI-powered)</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)
with st.container():
    st.markdown(
        """
        <div class='story-details-card'>
            <div class='field-section-title'>Story details</div>
            <div class='field-section-subtitle'>Add a clear summary and description for the story before generating AI estimates.</div>
            <div style='margin-top: 16px;'>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<label>Summary <span style='color: #d32f2f; font-weight: 700;'>*</span></label>", unsafe_allow_html=True)
    summary = st.text_input("Summary", placeholder="Summary", label_visibility="collapsed")

    st.markdown("<label>Description <span style='color: #d32f2f; font-weight: 700;'>*</span></label>", unsafe_allow_html=True)
    description = st.text_area(
        "Description",
        placeholder="Description",
        height=100,
        label_visibility="collapsed",
    )

    st.markdown("<label>Acceptance criteria <span style='color: #d32f2f; font-weight: 700;'>*</span></label>", unsafe_allow_html=True)
    acceptance_criteria = st.text_area(
        "Acceptance criteria",
        placeholder="Acceptance criteria",
        height=160,
        label_visibility="collapsed",
    )

    st.markdown(
        """
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Wrap Planning Poker in a styled card container
with st.container():
    st.markdown(
        '''
        <div class="planning-poker-card">
            <div class="field-section-title">Planning Poker</div>
            <div class="field-section-subtitle">Team estimates and AI recommendation</div>
        ''',
        unsafe_allow_html=True,
    )

    DEFAULT_TOP_K = 5

    # Always use similar stories
    use_similar = True

    # ----------------------------
    # Planning Poker Section
    # ----------------------------

    if "pp_ai_result" not in st.session_state:
        st.session_state.pp_ai_result = None

    if "pp_team_estimates" not in st.session_state:
        st.session_state.pp_team_estimates = {}

    if "pp_story_fingerprint" not in st.session_state:
        st.session_state.pp_story_fingerprint = ""


    def _story_fingerprint(s: str, d: str, a: str) -> str:
        return f"{(s or '').strip()}||{(d or '').strip()}||{(a or '').strip()}"


    def _reset_poker_round():
        st.session_state.pp_ai_result = None
        st.session_state.pp_team_estimates = {}
        st.session_state.pp_story_fingerprint = _story_fingerprint(summary, description, acceptance_criteria)


    _current_fp = _story_fingerprint(summary, description, acceptance_criteria)

    if st.session_state.pp_story_fingerprint and _current_fp != st.session_state.pp_story_fingerprint:
        _reset_poker_round()
    elif not st.session_state.pp_story_fingerprint:
        st.session_state.pp_story_fingerprint = _current_fp

    _ALLOWED_POINTS = [1, 2, 3, 5, 8, 13]

    _col1, _col2 = st.columns([1, 3])

    with _col1:
        _team_size = st.number_input(
            "Team size",
            min_value=1,
            max_value=15,
            value=4,
            step=1,
            key="pp_team_size"
        )

    with _col2:
        st.empty()

    st.caption("Each member enters their estimate. Click **Generate AI estimate** to show AI results.")

    # Create two columns: left for members, right for planning poker image
    _members_col, _image_col = st.columns([2, 1.4])

    with _members_col:
        _team_names = []

        for _i in range(int(_team_size)):
            _name_col, _estimate_col, _spacer_col = st.columns([1, 1, 0.2])

            with _name_col:
                _name = st.text_input(
                    f"Member {_i+1} name",
                    value=f"Member {_i+1}",
                    key=f"pp_name_{_i}"
                )

            with _estimate_col:
                _choice = st.selectbox(
                    "Estimate",
                    options=["—"] + [str(x) for x in _ALLOWED_POINTS],
                    key=f"pp_estimate_{_i}",
                )

            _member_name = _name.strip() if _name else f"Member {_i+1}"
            _team_names.append(_member_name)

            st.session_state.pp_team_estimates[_member_name] = (
                None if _choice == "—" else int(_choice)
            )

    with _image_col:
        st.markdown(
            """<div style='display:flex;justify-content:center;align-items:center;width:100%;'>
<div style='width:100%;max-width:360px;height:500px;padding:16px;background:#fff;border-radius:22px;display:flex;justify-content:center;align-items:center;'>
<svg viewBox="0 0 200 180" style="width:100%;height:100%;">
<!-- Table -->
<ellipse cx="100" cy="110" rx="80" ry="35" fill="none" stroke="#666" stroke-width="2"/>
<path d="M 30 110 Q 30 140, 50 150" fill="none" stroke="#666" stroke-width="2"/>
<path d="M 170 110 Q 170 140, 150 150" fill="none" stroke="#666" stroke-width="2"/>
<!-- Cards on table -->
<rect x="60" y="95" width="18" height="25" fill="#A8E6CF" stroke="#333" stroke-width="1" rx="2"/>
<text x="69" y="113" text-anchor="middle" font-size="14" font-weight="bold">3</text>
<rect x="82" y="100" width="18" height="25" fill="#FFD3B6" stroke="#333" stroke-width="1" rx="2"/>
<text x="91" y="118" text-anchor="middle" font-size="14" font-weight="bold">5</text>
<rect x="100" y="98" width="18" height="25" fill="#FFAAA5" stroke="#333" stroke-width="1" rx="2"/>
<text x="109" y="116" text-anchor="middle" font-size="14" font-weight="bold">8</text>
<rect x="120" y="100" width="18" height="25" fill="#A8E6CF" stroke="#333" stroke-width="1" rx="2"/>
<text x="129" y="118" text-anchor="middle" font-size="14" font-weight="bold">2</text>
<!-- Top left person -->
<circle cx="25" cy="50" r="8" fill="none" stroke="#333" stroke-width="2"/>
<line x1="25" y1="58" x2="25" y2="75" stroke="#333" stroke-width="2"/>
<line x1="25" y1="62" x2="15" y2="68" stroke="#333" stroke-width="2"/>
<line x1="25" y1="62" x2="35" y2="68" stroke="#333" stroke-width="2"/>
<circle cx="22" cy="47" r="2" fill="#333"/>
<circle cx="28" cy="47" r="2" fill="#333"/>
<!-- Top center-left -->
<circle cx="60" cy="35" r="8" fill="none" stroke="#333" stroke-width="2"/>
<line x1="60" y1="43" x2="60" y2="60" stroke="#333" stroke-width="2"/>
<line x1="60" y1="47" x2="50" y2="53" stroke="#333" stroke-width="2"/>
<line x1="60" y1="47" x2="70" y2="53" stroke="#333" stroke-width="2"/>
<circle cx="57" cy="32" r="2" fill="#333"/>
<circle cx="63" cy="32" r="2" fill="#333"/>
<!-- Top center -->
<circle cx="100" cy="25" r="8" fill="none" stroke="#333" stroke-width="2"/>
<line x1="100" y1="33" x2="100" y2="50" stroke="#333" stroke-width="2"/>
<line x1="100" y1="37" x2="90" y2="43" stroke="#333" stroke-width="2"/>
<line x1="100" y1="37" x2="110" y2="43" stroke="#333" stroke-width="2"/>
<circle cx="97" cy="22" r="2" fill="#333"/>
<circle cx="103" cy="22" r="2" fill="#333"/>
<!-- Top right -->
<circle cx="140" cy="35" r="8" fill="none" stroke="#333" stroke-width="2"/>
<line x1="140" y1="43" x2="140" y2="60" stroke="#333" stroke-width="2"/>
<line x1="140" y1="47" x2="130" y2="53" stroke="#333" stroke-width="2"/>
<line x1="140" y1="47" x2="150" y2="53" stroke="#333" stroke-width="2"/>
<circle cx="137" cy="32" r="2" fill="#333"/>
<circle cx="143" cy="32" r="2" fill="#333"/>
<!-- Right person -->
<circle cx="175" cy="50" r="8" fill="none" stroke="#333" stroke-width="2"/>
<line x1="175" y1="58" x2="175" y2="75" stroke="#333" stroke-width="2"/>
<line x1="175" y1="62" x2="165" y2="68" stroke="#333" stroke-width="2"/>
<line x1="175" y1="62" x2="185" y2="68" stroke="#333" stroke-width="2"/>
<circle cx="172" cy="47" r="2" fill="#333"/>
<circle cx="178" cy="47" r="2" fill="#333"/>
</svg></div></div>""",
            unsafe_allow_html=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    _button_col1, _button_col2, _button_col3 = st.columns([2, 2, 4])

    with _button_col1:
        _get_ai = st.button("🤖 Get AI estimate")

    with _button_col2:
        if st.button("🔄 Reset round"):
            _reset_poker_round()

# ----------------------------
# Generate AI Estimate
# ----------------------------

if _get_ai:
    if not summary.strip() or not description.strip() or not acceptance_criteria.strip():
        st.warning("Please enter a summary, description, and acceptance criteria to generate AI estimate.")
    else:
        try:
            with st.spinner("Generating AI estimate..."):
                merged_description = description.strip()
                if acceptance_criteria and acceptance_criteria.strip():
                    merged_description = (
                        f"{merged_description}\n\nAcceptance criteria:\n{acceptance_criteria.strip()}"
                        if merged_description
                        else acceptance_criteria.strip()
                    )

                _ai_result = estimate_story_points(
                    summary=summary,
                    description=merged_description,
                    top_k=DEFAULT_TOP_K,
                    use_llm=True,
                )

                st.session_state.pp_ai_result = _ai_result

        except Exception as _e:
            st.error(f"Error generating AI estimate: {_e}")

# ----------------------------
# Reveal Board
# ----------------------------

# Show estimate cards and title only after AI estimate button is clicked
if st.session_state.pp_ai_result is not None:
    with st.container():
        _reveal_html = '''
            <div class="estimate-card">
                <div class="field-section-title">📋 Estimates</div>
                <div class="field-section-subtitle">Team reveal and AI recommendation.</div>
                <div class="reveal-board"><div class="reveal-cards-row">
        '''

        for _name in _team_names:
            _val = st.session_state.pp_team_estimates.get(_name)
            _class = "reveal-estimate-card" if _val is not None else "reveal-estimate-card not-submitted"
            _display_val = str(_val) if _val is not None else "—"
            _reveal_html += f'<div class="{_class}"><span class="member-name">{_name}</span><span class="estimate-value">{_display_val}</span></div>'

        _ai = st.session_state.pp_ai_result
        _ai_value = _ai.get('story_points', '?')
        # Handle NA or None values
        if _ai_value is None:
            _ai_value = "—"
        else:
            _ai_value = str(_ai_value)
        _reveal_html += f'<div class="reveal-estimate-card ai-card"><span class="member-name">Story Estimator</span><span class="estimate-value">{_ai_value}</span></div>'

        _reveal_html += '</div>'
        _reveal_html += '<div class="field-section-title">📌 AI Reasoning</div>'
        if _ai.get("llm_raw"):
            _reveal_html += f'<div>{_ai["llm_raw"]}</div>'
        else:
            _reveal_html += f'<div>{_ai.get("reasoning", "No reasoning available")}</div>'

        if _ai.get("similar_stories"):
            _reveal_html += '<div class="field-section-title">🔍 Similar Jira Stories Used (AI Context)</div>'
            for _j, _story in enumerate(_ai.get("similar_stories", []), start=1):
                _reveal_html += (
                    f'<div style="margin-bottom:14px;">'
                    f'<strong>{_j}. {_story["key"]}</strong><br/>'
                    f'Summary: {_story["summary"]}<br/>'
                    f'Story Points: <code>{_story["story_points"]}</code><br/>'
                    f'Similarity: <code>{_story["similarity"]:.2f}</code>'
                    '</div>'
                )
        _reveal_html += '</div>'
        st.markdown(_reveal_html, unsafe_allow_html=True)

