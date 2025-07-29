.. |pypi-version| image:: https://img.shields.io/pypi/v/django-datatables-kit?label=PyPI%20Version&color=4BC51D
   :alt: PyPI Version
   :target: https://pypi.org/projects/django-datatables-kit/

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/django-datatables-kit?label=PyPI%20Downloads&color=037585
   :alt: PyPI Downloads
   :target: https://pypi.org/projects/django-datatables-kit/

django-datatables-kit
#####################

|pypi-version| |pypi-downloads|

Description
***********

Provides powerful backend for DataTables.

Installation
************

Install DataTables Node packages
================================

Manual Installation
-------------------

Install DataTables JavaScript library in your Django project. Optionally install additional DataTables NPM packages depending on CSS framework you use (i.e. BootStrap5 and Responsive Bootstrap5). DataTables requires jQuery and is automatically installed, however if you wish to use a specific version of jQuery, you can install that too.

Standard Installation
---------------------

If you do not already have a directory convention on where to install JS packages, you can create a `vendor` directory in the root directory of Django, then create a sub-directory `node_packages`, and create `package.json` with following content.

.. code-block:: json

   {
     "name": "custom-libraries",
     "description": "Node packages used in the project",
     "version": "1.0.0",
     "scripts": {
       "build": "npm-run-all copy",
       "copy": "npm-run-all make_vendor copy_vendor",
       "make_vendor": "npm-run-all --parallel make-*",
       "make-css": "if not exist \"../../public/static/vendor/css\" mkdir \"../../public/static/vendor/css\"",
       "make-js": "if not exist \"../../public/static/vendor/js\" mkdir \"../../public/static/vendor/js\"",
       "copy_vendor": "npm-run-all --parallel copy-*",
       "copy-datatablesnet-js": "cp -r node_modules/datatables.net/js/*.min.js ../../public/static/vendor/js",
       "copy-datatablesbs5-css": "cp -r node_modules/datatables.net-bs5/css/*.min.css  ../../public/static/vendor/css",
       "copy-datatablesbs5-js": "cp -r node_modules/datatables.net-bs5/js/*.min.js ../../public/static/vendor/js",
       "copy-datatablesrespoonsive-js": "cp -r node_modules/datatables.net-responsive/js/*.min.js ../../public/static/vendor/js",
       "copy-datatablesresponsive-css": "cp -r node_modules/datatables.net-responsive-bs5/css/*.min.css ../../public/static/vendor/css",
       "copy-datatablesrespoonsive-bs5-js": "cp -r node_modules/datatables.net-responsive-bs5/js/*.min.js ../../public/static/vendor/js",
       "copy-jquery-js": "cp -r node_modules/jquery/dist/*.js ../../public/static/vendor/js"
     },
     "license": "SEE LICENSE IN LICENSE",
     "private": true,
     "dependencies": {
       "datatables.net": "^2.3.2",
       "datatables.net-bs5": "^2.3.2",
       "datatables.net-responsive-bs5": "^3.0.4",
       "jquery": "^3.7.1",
       "npm-run-all2": "^8.0.4"
     }
   }

Now run the following commands:

.. code-block:: shell

   cd vendor/node_packages
   npm install
   npm run build

This will install DataTables packages, create `public/static/vendor/css` and `public/static/vendor/js` directories in the Django root directory, and copy the necessary `*.min.css` and `*.min.js` files. These files need to be included in the templates of views which use DataTables (we will discuss this later).

Install DataTables Python packages
==================================

.. code-block:: shell

   pip install django-datatables-kit

If you use `PDM <https://pdm-project.org>`__:

.. code-block:: shell

   pdm add django-datatables-kit

Note that `django-helper-kit` is a dependency and is automatically installed.

Setup Django
************

Edit Django `settings.py`:

1. Import DataTables settings provided by this package. There are two settings dictionaries: `DJDTK_DATATABLES_CONFIG` and `DJDTK_DATATABLES_DEFAULTS`. If you want to override these settings, copy them into separate file(s) and import them here (modify your `import` likewise). Caution: Do not change the names of the settings variables.

.. code-block:: python

   from django_datatables_kit.settings import *

2. Add packages to `INSTALLED_APPS`. Note that `django_helper_kit` is required to be added, and it must appear before `django_datatables_kit`.

.. code-block:: python

   INSTALLED_APPS = [
       # ...
       "django_helper_kit",
       "django_datatables_kit",
       # ...
   ]

Note: This is an alpha version, and things may change quite a bit.

Usage
*****

In Template
===========

In the template using DataTables, include the following:

.. code-block:: django-template

   {% include "django_datatables_kit/datatables-config.html" %}

Depending on what DataTables related-packages you have installed and where you have copied DataTables and jQuery `*.min.css` and `*.min.js`, modify the following and create a partial template, then include it in the template using DataTables:

.. code-block:: django-template

   {% load static %}
   <link rel="stylesheet" href="{% static 'vendor/css/dataTables.bootstrap5.min.css' %}">
   <link rel="stylesheet" href="{% static 'vendor/css/responsive.bootstrap5.min.css' %}">
   <script src="{% static 'vendor/js/jquery.min.js' %}"></script>
   <script src="{% static 'vendor/js/dataTables.min.js' %}"></script>
   <script src="{% static 'vendor/js/dataTables.bootstrap5.min.js' %}"></script>
   <script src="{% static 'vendor/js/dataTables.responsive.min.js' %}"></script>
   <script src="{% static 'vendor/js/responsive.bootstrap5.min.js' %}"></script>

Create a JavaScript file for DataTables and include this in the template. In the following example, `state` is a TextChoices field, and so the `human_readable` value is chosen to be displayed, the stored value can is available as `raw`.

.. code-block:: javascript

   document.addEventListener("DOMContentLoaded", function (event) {
       const dtTableId = "example-dt";
       const dtParms = readDtParms(dtTableId);
       initDataTable(
           tableId=dtTableId,
           columns=[
               {
                   data: "id",
                   responsivePriority: 1,
                   searchable: false,
                   orderable: false,
                   name: "action",
                   render: function (data, type, row, meta) {
                       return `<a href="${dtParms.viewExampleUrl.replace(':site_id:', data)}" title="${DJDTK_DATATABLES_CONFIG.language.view}"><i class="bi bi-eye"></i></a>`;
                   },
               },
               {
                   data: "id",
                   responsivePriority: 2,
                   searchable: false,
                   orderable: false,
               },
               {
                   data: "name",
                   responsivePriority: 3,
                   searchable: true,
                   orderable: true,
               },
               {
                   data: "state",
                   responsivePriority: 6,
                   searchable: false,
                   orderable: false,
                   render: function (data, type, row, meta) { return data.human_readable; },
               },
               {
                   data: "example_count",
                   responsivePriority: 4,
                   searchable: false,
                   orderable: false,
               },
           ],
           order=[[2, "asc"]],
       );
   });


.. code-block:: django-template

   <script src="{% static 'app_example/js/datatables/example/dt-example-list.js' %}"></script>

In the template table HTML tag, define `id` (value must match `dtTableId` above, this links the DataTable to HTML table) and `data-dt-parms` attributes. You can pass any parameter in `data-dt-parms` which will be made available to DataTables JavaScript (see later).

.. code-block:: django-template

   <table id="example-dt" class="table table-hover display nowrap" data-dt-parms='{"apiUrl": "{% url 'app_example:filter_example' %}", "viewExampleUrl": "{% url 'app_example:view_example' ':example_id:' %}"}'>
    <thead>
     <tr>
      <th class="fw-bold">{% translate 'Action' %}</th>
      <th class="fw-bold">{% translate 'Example Code' %}</th>
      <th class="fw-bold">{% translate 'Example Name' %}</th>
      <th class="fw-bold">{% translate 'State' %}</th>
      <th class="fw-bold">{% translate 'Example Count' %}</th>
     </tr>
    </thead>
    <tbody></tbody>
   </table>
