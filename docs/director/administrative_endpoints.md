# Administrative Endpoints
The director component has an optional administrative endpoint which allow to set a meshes domains and switch_time manually.

By setting domain and/or switch-time manually, the automatic decision of the director is overridden forever.

You can use the administrative endpoints, for example, via curl:

```
curl -v \
    -X PATCH \
    "http://<YOUR_LOCATOR_HOST>/mesh/<MESH_ID>/" \
    -H "Content-Type: application/json" \
    --data '{"switch_time": 42424242, "domain": "new_domain", "force": "yes"}'

```

The `force` flag is needed when when the switch-time is set to be in the past. The flag is not needed if the switch-time is set to be in the future.
