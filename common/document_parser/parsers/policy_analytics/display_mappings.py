from collections import defaultdict

DISPLAY_TYPE_LOOKUP = defaultdict(lambda: "Document", {
    # This file should not be added too, use properties on the spider to assign these values
    "dod": 'Issuance',
    "dodm": 'Manual',
    "dodi": 'Instruction',
    "dodd": 'Directive',
    "cjcs": 'Notice',
    "cjcsi": 'Instruction',
    "cjcsm": 'Manual',
    "cjcsg": 'Guide',
    "icd": 'Directive',
    "icpg": 'Guide',
    "icpm": 'Manual',
    "title": 'Title',
    "dep": 'Memorandum',
    "sec": 'Memorandum',
    "ai": 'Instruction',
    "dtm": 'Memorandum',
    "eo": 'Order',
    "organization": 'Organization',
    "person": 'Person',
    "ombm": 'Memorandum',
    "opnavnote": 'Notice',
    "secnavnote": 'Notice',
    "opnavinst": 'Instruction',
    "secnavinst": 'Instruction',
    "comnavresforcominst": 'Instruction',
    "comnavresforcomnote": 'Notice',
    "navmed": 'Manual',
    "bumednote": 'Notice',
    "bumedinst": 'Instruction',
    "h.con.res.": 'Legislation',
    "h.j.res.": 'Legislation',
    "h.r.": 'Legislation',
    "h. res.": 'Legislation',
    "s.": 'Legislation',
    "s. con. res.": 'Legislation',
    "s.j. res.": 'Legislation',
    "s. res.": 'Legislation',
    "usar cir": 'Circular',
    "usar pam": 'Pamphlet',
    "usar reg": 'Regulation',
    "memo": "Memorandum",
    "dfar": "Regulation",
    "far": "Regulation",
    "cngbi": "Instruction",
    "cim": "Manual",
    "ci": "Instruction",
    "cn": "Notice",
    "ccn": "Notice",
    "dcmsi": "Instruction",
    "dod coronavirus guidance": "Guidance",
    # "cfr index": "CFR Index",
    # "cfr title": "CFR Title",
    # This file should not be added too, use properties on the spider to assign these values
})


CRAWLER_TO_DISPLAY_ORG_LOOKUP = defaultdict(lambda: "Uncategorized", {
    # This file should not be added too, use properties on the spider to assign these values
    "dod_issuances": "Dept. of Defense",
    "jcs_pubs": 'Joint Chiefs of Staff',
    "jcs_manual_uploads": 'Joint Chiefs of Staff',
    "dod_manual_uploads": 'Dept. of Defense',
    "army_manual_uploads": 'US Army',
    "ic_policies": 'Intelligence Community',
    "us_code": 'United States Code',
    "ex_orders": 'Executive Branch',
    "opm_pubs": "OPM",
    "air_force_pubs": 'Dept. of the Air Force',
    "army_pubs": 'US Army',
    "marine_pubs": 'US Marine Corps',
    "secnav_pubs": 'US Navy',
    "navy_reserves": 'US Navy Reserve',
    "navy_med_pubs": 'US Navy Medicine',
    "Bupers_Crawler": 'US Navy',
    "milpersman_crawler": "US Navy",
    "nato_stanag": "NATO",
    "fmr_pubs": "FMR",
    "legislation_pubs": "Congress",
    "Army_Reserve": "US Army",
    "Memo": "Dept. of Defense",
    "dha_pubs": "Defense Health Agency",
    "jumbo_DFAR": "DFAR",
    "jumbo_FAR": "FAR",
    "National_Guard": "National Guard",
    "Coast_Guard": "Coast Guard",
    "jumbo_DFARS": "DFARS",
    "DOD_Coronavirus_Guidance": "Dept. of Defense",
    "dfar_subpart_regs": "DFAR",
    "far_subpart_regs": "FAR",
    # "code_of_federal_regulations": "Congress",
    # This file should not be added too, use properties on the spider to assign these values
})

CRAWLER_TO_DISPLAY_SOURCE_LOOKUP = defaultdict(lambda: "Unlisted Source", {
    # This file should not be added too, use properties on the spider to assign these values
    "dod_issuances": "WHS DoD Directives Division",
    "army_pubs": "Army Publishing Directorate",
    "jcs_pubs": "Joint Chiefs of Staff Library",
    "jcs_manual_uploads": "Joint Chiefs of Staff",
    "dod_manual_uploads": "Dept. of Defense",
    "army_manual_uploads": "US Army",
    "ic_policies": "Director of National Intelligence",
    "us_code": "Office of the Law Revision Counsel",
    "ex_orders": "Federal Register",
    "opm_pubs": "OMB Publication",
    "air_force_pubs": "Dept. of the Air Force E-Publishing",
    "marine_pubs": "Marine Corps Publications Electronic Library",
    "secnav_pubs": "Dept. of the Navy Issuances",
    "navy_reserves": "U.S. Navy Reserve Publications",
    "navy_med_pubs": "Navy Medicine Directives",
    "Bupers_Crawler": "Bureau of Naval Personnel Instructions",
    "milpersman_crawler": "Navy Personnel Command Instructions",
    "nato_stanag": "NATO Publications",
    "fmr_pubs": "DoD Financial Management Regulation",
    "legislation_pubs": "Congressional Legislation",
    "Army_Reserve": "U.S. Army Reserve Publications",
    "Memo": "OSD Executive Secretary",
    "dha_pubs": "Military Health System",
    "jumbo_FAR": "Federal Acquisition Regulation",
    "jumbo_DFAR": "Defense Federal Acquisition Regulation",
    "jumbo_far_dfar_crawler": "Acquisition Regulation",
    "National_Guard": "National Guard Bureau Publications Library",
    "Coast_Guard": "US Coast Guard Directives",
    "DOD_Coronavirus_Guidance": "Defense Publications",
    "dfar_subpart_regs": "Defense Federal Acquisition Regulation",
    "far_subpart_regs": "Federal Acquisition Regulation",
    # "code_of_federal_regulations": "U.S. Publishing Office",
    # This file should not be added too, use properties on the spider to assign these values
})
