function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&#]+([^=&]+)=([^&#]*)/gi, function (m, key, value) {
        vars[key] = decodeURIComponent(value);
    });
    return vars;
}

function make_uri(uri, options) {
    var ops = {};
    $.extend(ops, getUrlVars());
    if (options != null) {
        $.extend(ops, options);
    }
    var str = $.map(ops, function (val, index) {
        return index + "=" + encodeURIComponent(val).toLowerCase();
    }).join("&");

    return (str == "") ? uri : uri + "?" + str;
}

function reload(extra) {
    window.location.search = make_uri ("", extra);
}

function update_url(extra) {
    var ops = {};
    $.extend(ops, getUrlVars ());
    if (extra != null) {
        $.extend(ops, extra);
    }
    window.location.hash = $.map(ops, function (val, index) {
        return val ? (index + "=" + encodeURIComponent(val)) : null;
    }).join("&")
}

function initSingleSelector(selector_id, property, dataSet, update_handler) {
    var values = {};

    for (var i = 0; i < dataSet.length; i++) {
        var element = dataSet[i][property];
	if (element instanceof Array) {
	    for (var key in element)
		values[element[key]] = element[key];
	} else
	    values[element] = element;
    }

    var result = [];
    for (var value in values)
        result.push({"id": value, "text": value});

    $("#" + selector_id).
	val (getUrlVars()[property]).
        on("select2-selecting", function (e) {
            var options = {};
            options[property] = e.val;
            update_url (options);
	    update_handler ();
        }).
        on("select2-removed", function (e) {
            var options = {};
            options[property] = '';
            update_url (options);
	    update_handler ();
        }).
        select2({data: result, allowClear: true});
}

function showInfo (template_id, info) {
    $("#info_container").empty();
    $("#" + template_id).tmpl(info).appendTo("#info_container");
    $("#info_dialog").dialog("open");
}

function setupInfoHandler (table_id, element_id, template_id, info) {
    $("#info_dialog").dialog({
        autoOpen: false,
        width: "70%",
        modal: true,
        buttons: {
            Close: function () {
                $(this).dialog("close");
            }
        },
        close: function () {
        }
    });

    $("#" + table_id).on("click", "#" + element_id, function (event) {
        event.preventDefault();
        event.stopPropagation();

        showInfo (template_id, info);
    });
}

function filterData (tableData, filters) {
    var filteredData = [];

    for (var i = 0; i < tableData.length; i++) {
        var row = tableData[i];
        var filtered = true;

        for (var column in filters) {
	    if (column in row) {
		if (row[column] instanceof Array) {
		    filtered = false;
		    for (var key in row[column])
			if (filters[column] == row[column][key])
			    filtered = true;
		} else {
		    if (filters[column] != row[column])
			filtered = false;
		}
	    }
	    if (filtered == false)
		break;
        }

        if (filtered) {
	    filteredData.push(row);
        }
    }

    return filteredData;
}

function populate_table (table_id, table_column_names, tableData)
{
    var tableColumns = [];
    for (var i = 0; i < table_column_names.length; i++) {
        tableColumns.push({"mData": table_column_names[i]});
    }

    if (table_id) {
        $("#" + table_id).dataTable({
	    "aLengthMenu": [
                [10, 25, 50, -1],
                [10, 25, 50, "All"]
	    ],
	    "bDestroy": true,
	    "iDisplayLength": -1,
	    "bAutoWidth": false,
	    "bPaginate": true,
	    "aaData": tableData,
	    "aoColumns": tableColumns
        });
    }    
}

var glance_images = { images: [] };

function show_glance_images ()
{
    var ops = getUrlVars ();
    var tableData = filterData (glance_images["images"], ops);

    var table_column_names = ["image_name_html", "provided_by_html", "description", "format", "supported_by", "license"];
    var table_id = "glance_images_table";

    for (var i = 0; i < tableData.length; i++) {

        tableData[i].image_name_html = "<a href=\"#\" title=\"Show details\">" + tableData[i].image_name + "</a>";
        tableData[i].image_name_html = "<div id=\"image_" + i + "\">" + tableData[i].image_name_html + "</div>";

        setupInfoHandler (table_id, "image_" + i, "image_info_template", tableData[i]);

        tableData[i].provided_by_html = "<a href=\"" + tableData[i].provided_by.href +
	    "\" title=\"Show details\">" + tableData[i].provided_by.name + "</a> " +
	    "[" + tableData[i].provided_by.company + "]";
    }

    populate_table (table_id, table_column_names, tableData);
}

var heat_templates = { templates: [] };

function show_heat_templates ()
{
    var ops = getUrlVars ();
    var tableData = filterData (heat_templates["templates"], ops);

    var table_column_names = ["template_name_html", "provided_by_html", "description", "release_html", "format", "supported_by", "license"];
    var table_id = "heat_templates_table";

    for (var i = 0; i < tableData.length; i++) {

        tableData[i].template_name_html = "<a href=\"#\" title=\"Show details\">" + tableData[i].template_name + "</a>";
        tableData[i].template_name_html = "<div id=\"template_" + i + "\">" + tableData[i].template_name_html + "</div>";

        setupInfoHandler (table_id, "template_" + i, "template_info_template", tableData[i]);
	
        tableData[i].provided_by_html = "<a href=\"" + tableData[i].provided_by.href +
	    "\" title=\"Show details\">" + tableData[i].provided_by.name + "</a> " +
	    "[" + tableData[i].provided_by.company + "]";
	tableData[i].release_html = tableData[i].release.join (", ");
    }

    populate_table (table_id, table_column_names, tableData);
}

var murano_apps = { applications: [] };

function show_murano_apps ()
{
    var ops = getUrlVars ();
    var tableData = filterData (murano_apps["applications"], ops);

    var table_column_names = ["package_name_html", "provided_by_html", "description", "release_html", "format", "supported_by", "license"];
    var table_id = "murano_apps_table";

    for (var i = 0; i < tableData.length; i++) {

        tableData[i].package_name_html = "<a href=\"#\" title=\"Show details\">" + tableData[i].package_name + "</a>";
        tableData[i].package_name_html = "<div id=\"package_" + i + "\">" + tableData[i].package_name_html + "</div>";

        setupInfoHandler (table_id, "package_" + i, "application_info_template", tableData[i]);

        tableData[i].provided_by_html = "<a href=\"" + tableData[i].provided_by.href +
	    "\" title=\"Show details\">" + tableData[i].provided_by.name + "</a> " +
	    "[" + tableData[i].provided_by.company + "]";
	tableData[i].release_html = tableData[i].release.join (", ");
    }

    populate_table (table_id, table_column_names, tableData);
}

function initMarketPlace ()
{
    var tab_idx = 0;
    var options = getUrlVars ();
    if ("tab" in options) {
        var tabs_list = $("#tabs")[0].children[0].children;
        for (var i = 0; i < tabs_list.length; ++i)
	    if (tabs_list[i].children[0].hash.substring (1) == options["tab"]) {
		tab_idx = i;
		break;
	    }
    }
    
    $( "#tabs" ).tabs({
        activate: function( event, ui ) {
	    update_url ({ tab : ui.newTab.context.hash.substring (1) });
        },
        active: tab_idx,
    });
    
    $.ajax({
        url: make_uri("static/glance_images.json"),
        dataType: "json",

        success: function (data) {
	    glance_images = data;
	    initSingleSelector ("glance_supported_by", "supported_by", glance_images["images"], show_glance_images);
	    show_glance_images ();
        }
    });      

    $.ajax({
        url: make_uri("static/heat_templates.json"),
        dataType: "json",

        success: function (data) {
	    heat_templates = data;
	    initSingleSelector ("heat_supported_by", "supported_by", heat_templates["templates"], show_heat_templates);
	    initSingleSelector ("heat_release", "release", heat_templates["templates"], show_heat_templates);
	    show_heat_templates ();
        }
    });      

    $.ajax({
        url: make_uri("static/murano_apps.json"),
        dataType: "json",

        success: function (data) {
	    murano_apps = data;
	    initSingleSelector ("murano_supported_by", "supported_by", murano_apps["applications"], show_murano_apps);
	    initSingleSelector ("murano_release", "release", murano_apps["applications"], show_murano_apps);
	    show_murano_apps ();
        }
    });      
    
}
