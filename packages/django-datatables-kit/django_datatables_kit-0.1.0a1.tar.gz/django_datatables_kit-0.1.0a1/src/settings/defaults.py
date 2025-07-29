from django.utils.translation import pgettext_lazy as _p


DJDTK_DATATABLES_DEFAULTS = {
    # As of April 2025, there seems to be a bug in DataTables where
    # choosing "All" shows "Showing 1 to NaN of X entries"
    # "lengthMenu": [5, 10, 20, 50, {label: 'All', value: -1}],
    "filter": True,        # hides search input box if false
    "lengthMenu": [5, 10, 20, 50],
    "lengthChange": True,  # hides page length dropdown if false
    "ordering": True,
    "paging": True,
    "scrollY": "30rem",    # constrains table in this height and enables scrolling
    "scrollCollapse": True,
    "processing": False,
    "searching": True,
    "serverSide": True,
    "searchDelay": 400,   # milliseconds
    "search": {"caseInsensitive": False},
    "language": {
        "decimal": _p("DataTable options.language.decimal", ""),
        "emptyTable": _p("DataTable options.language.emptyTable",
                         "No results found"),
        "info": _p("DataTable options.language.info, keep _*_ "
                   "placeholders", "Showing _START_ to _END_ of _TOTAL_ items"),
        "infoEmpty": _p("DataTable options.language.infoEmpty",
                        "Showing 0 to 0 of 0 items"),
        "infoFiltered": _p("DataTable options.language.infoFiltered",
                           "(filtered from _MAX_ total entries)"),
        "infoPostFix": _p("DataTable infoPostfix", ""),
        "thousands": _p("DataTable options.language.thousands", ","),
        "lengthMenu": _p("DataTable options.language.lengthMenu",
                         "_MENU_ per page"),
        "loadingRecords":
            _p("DataTable options.language.loadingRecords",
               "Loading..."),
        "processing": _p("DataTable options.language.processing", ""),
        "search": _p("DataTable options.language.search", "_INPUT_"),
        "searchPlaceholder":
            _p("DataTable options.language.searchPlaceholder",
               "Search..."),
        "zeroRecords": _p("DataTable options.language.zeroRecords",
                          "No results found"),
        "paginate": {
            "first": _p("DataTable options.language.paginate.first",
                        "« First"),
            "last": _p("DataTable options.language.paginate.last",
                       "Last »"),
            "next": _p("DataTable options.language.paginate.next",
                       "Next ›"),
            "previous":
                _p("DataTable options.language.paginate.previous",
                   "‹ Previous"),
        },
        "aria": {
            "orderable": _p("DataTable options.language.aria.orderable",
                            "Order by this column"),
            "orderableReverse":
                _p("DataTable options.language.aria.orderableReverse",
                   "Reverse order this column"),
        },
    },
}
