from django.utils.translation import pgettext_lazy as _p


DJDTK_DATATABLES_CONFIG = {
    "globalSearchHtmlEscape": True,
    "language": {
        "download": _p("DataTable Download tooltip", "Download"),
        "edit": _p("DataTable Edit tooltip", "Edit"),
        "view": _p("DataTable Edit tooltip", "View"),
        "notMinSearchCharsMessage": _p(
            "DataTable min characters",
            _p("DataTable notMinSearchCharsMessage",
               "Please enter more than _MIN_SEARCH_CHARS_ characters to search")
        ),
    },
    "minSearchChars": 3,
}
