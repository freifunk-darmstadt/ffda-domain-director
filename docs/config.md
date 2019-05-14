# Config-File
For a sample config-file have a look at `config.yml.example` in the projects root directory

## Generic Configuration
Generic configuration is set on root-level of the config-file.

### host
Defines the address to listen on. Usually this should be set to the IPv6 link-local address `::`.

### port
Defines the port to listen on.

## Geo-Provider
Geo-Provider settings are set in the `geo` key of the config-file.

### provider
This setting refers to the Geo-Provider used. Currently, only the `mozilla` provider is available

## Mozilla Geo-Provider
Configuration for the Mozilla Location Service based Geo-Provider is done in the `mozilla` key within `geo`.

### api_key
Defines the API-key to be used for accessing the Mozilla Location Service API. Mozilla provides the `test` API-key for testing purposes.

## Director
Director settings are set in the `director` key of the config-file.

### enabled
Enables or disables the director. Valid values are `true` or `false`.

### sqlite_path
Defines the path the SQLite database is stored at. Relative and absolute paths are valid. In addition, `:memory:` will create a volatile in-memory database.

### geojson
Defines the path to the GeoJSON containing the polygons of all the domains nodes should be directed to.

### meshviewer_json_url
Defines the URL the `meshviewer.json` file is served at. This is usually located at `https://<map-vhost>/data/meshviewer.json`.

### update_interval:
The interval map-data is refreshed in seconds. `-1` disables automatic updates. Recommendation is a value around 10 to 15 minutes.

### default_domain
This domain is provided to nodes for which a domain decision could not be performed.

### domain_switch_time
UNIX epoch nodes should switch to the domain they are directed to. This value will be ignored in case a custom switch-time is set via the admin endpoints.

### only_migrate_vpn
When set to `true`, only nodes who have no mesh-neighbours will be directed.

### tolerance_distance
Up to this specified distance (in meters), a node will be still assigned to the nearest domain, even when the nodes position is not covered by a domain polygon.

### max_accuracy
Up to this accuracy in meters, a geo-provider acquired position is honored.

## Director-Admin
Director-admin settings are set in the `admin` key of within `director`.

### enabled
Enables or disables the admin endpoints of the director. Valid values are `true` or `false`.

### token
Defines the token required to update nodes and meshes thru the admin endpoints.

## Locator
Locator settings are set in the `locator` key of the config-file.

### enabled
Enables or disables the locator. Valid values are `true` or `false`.
