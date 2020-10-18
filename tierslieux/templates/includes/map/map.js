frappe.provide('tierslieux');

tierslieux.SearchBox = class SearchBox extends frappe.ui.FieldGroup {
	constructor(opts) {
		super();
		this.display = false;

		Object.assign(this, opts);
		this.make();
	}

	make() {
		this.$wrapper = $("#tl-map").append(`<div id="searchbox"></div>`)
		this.$body =this.$wrapper.find("#searchbox");
		this.body = this.$body.get(0);

		// make fields (if any)
		super.make();

	}

	hide() {
		this.$body.hide();
	}

	show() {
		this.$body.show();
	}
};

tierslieux.MapSearch = class MapSearch {
	constructor(opts) {
		Object.assign(this, opts);
		this.$wrapper = $(`#${this.wrapperId}`);
		this.data = [];
		this.render()
	}

	render() {
		this.make_wrapper();
		this.bind_leaflet_map();
		this.render_map();
		this.get_marker_icon()
		this.add_dummy_marker();
		this.add_search_tool();
	}

	make_wrapper() {
		this.map_id = frappe.dom.get_unique_id();
		this.map_area = $(
			`<div id=${this.map_id} style="min-height: 92vh; z-index: 1; max-width:100%"></div>`
		);
		this.map_area.appendTo(this.$wrapper);
	}

	bind_leaflet_map() {
		var circleToGeoJSON = L.Circle.prototype.toGeoJSON;
		L.Circle.include({
			toGeoJSON: function() {
				var feature = circleToGeoJSON.call(this);
				feature.properties = {
					point_type: 'circle',
					radius: this.getRadius()
				};
				return feature;
			}
		});

		L.CircleMarker.include({
			toGeoJSON: function() {
				var feature = circleToGeoJSON.call(this);
				feature.properties = {
					point_type: 'circlemarker',
					radius: this.getRadius()
				};
				return feature;
			}
		});

		L.Icon.Default.imagePath = '/assets/frappe/images/leaflet/';
		this.map = L.map(this.map_id).setView([48.85, 2.35], 6);

		L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager_labels_under/{z}/{x}/{y}{r}.png', {
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
			subdomains: 'abcd',
			maxZoom: 19
		}).addTo(this.map);
	}

	render_map() {
		const me = this;
		me.editableLayers = new L.FeatureGroup();
		me.data.forEach(value => {
			const geometry_value = value.map_location
			const data_layers = new L.LayerGroup()
				.addLayer(L.geoJson(JSON.parse(geometry_value),{
					pointToLayer: function(geoJsonPoint, latlng) {
						if (geoJsonPoint.properties.point_type == "circle"){
							return L.circle(latlng, {radius: geoJsonPoint.properties.radius})
								.bindPopup(me.get_popup(value))
								.bindTooltip(me.get_tooltip(value));
						} else if (geoJsonPoint.properties.point_type == "circlemarker") {
							return L.circleMarker(latlng, {radius: geoJsonPoint.properties.radius})
								.bindPopup(me.get_popup(value))
								.bindTooltip(me.get_tooltip(value));
						}
						else {
							return L.marker(latlng)
								.bindPopup(me.get_popup(value))
								.bindTooltip(me.get_tooltip(value));
						}
					}
				}));
			me.add_non_group_layers(data_layers, me.editableLayers);
		})
		try {
			me.map.flyToBounds(me.editableLayers.getBounds(), {
				animate: false,
				padding: [50,50]
			});
		}
		catch(err) {
			// suppress error if layer has a point.
		}
		me.editableLayers.addTo(me.map);

		me.map._onResize();
	}

	add_non_group_layers(source_layer, target_group) {
		// https://gis.stackexchange.com/a/203773
		// Would benefit from https://github.com/Leaflet/Leaflet/issues/4461
		if (source_layer instanceof L.LayerGroup) {
			source_layer.eachLayer((layer)=>{
				this.add_non_group_layers(layer, target_group);
			});
		} else {
			target_group.addLayer(source_layer);
		}
	}

	get_popup(value) {
		const text = Object.keys(this.list_fields).reduce((prev, f) => {
			return `${prev}<p><b>${__(this.list_fields[f])}</b>: ${__(value[f])}</p>`
		}, `<b>${value.name}</b>`)

		return text
	}

	get_tooltip(value) {
		return `<b>${value.name}</b>`
	}

	clickZoom(e) {
		this.map.setView(e.target.getLatLng());
	}

	get_marker_icon() {
		this.markerIcon = L.icon({
			iconUrl: '/assets/tierslieux/images/map-marker.svg',
			iconSize: [38, 95],
			popupAnchor: [0,0]
		});
	}

	add_dummy_marker() {
		const me = this;
		const marker = L.marker([50.633333, 3.066667], {icon: this.markerIcon}).addTo(this.map);
		const popupContent = `<div class="card" style="width: 18rem; z-index: 9999;">
			<img class="card-img-top" src="/assets/tierslieux/images/main_view.jpg" alt="Mon Tiers Lieux">
			<div class="card-body">
			<h5 class="card-title">Mon Tiers Lieux</h5>
			<p class="card-text">16 allée de la filature, 59000 Lille</p>
			<a href="/all-products" class="btn btn-primary">En savoir plus</a>
			</div>
		</div>`
		const layer = marker.bindPopup(popupContent)
		layer.on('popupopen', () => { me.searchtool.hide() });
		layer.on('popupclose', () => { me.searchtool.show() });
		layer.on('click', function(e) { me.clickZoom(e) })
	}

	add_search_tool() {
		this.searchtool = new tierslieux.SearchBox({
			title: __("Search"),
			fields: [
				{
					"fieldtype": "Link",
					"options": "Company",
					"label": __("Tiers Lieux"),
					"fieldname": "company",
					"only_select": 1
				},
				{
					"fieldtype": "Column Break",
					"fielname": "column_break_1"
				},
				{
					"fieldtype": "Data",
					"label": __("Ville"),
					"fieldname": "city"
				},
				{
					"fieldtype": "Column Break",
					"fielname": "column_break_2"
				},
				{
					"fieldtype": "Date",
					"label": __("Date"),
					"fieldname": "date"
				}
			]
		});
	}
};

new tierslieux.MapSearch({wrapperId: "tl-map"});