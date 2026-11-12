# GraphML 1.0 schema (local copy)

`test-nofi-2-nofo-transformer.sh` validates the transformer's output against the GraphML 1.0 XML schema. The schema is published at <http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd>, but that site has been out of service, which stopped the suite from running. These files are a local copy, so the validation needs no network.

| File | Source |
|---|---|
| `graphml.xsd` | <http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd> |
| `graphml-structure.xsd` | <http://graphml.graphdrawing.org/xmlns/1.0/graphml-structure.xsd> |
| `xlink.xsd` | <http://graphml.graphdrawing.org/xmlns/1.0/xlink.xsd> |

The files were taken from the Internet Archive (`https://web.archive.org/web/2020id_/<source URL>`) on 2026-11-12. SHA-256 of the files as downloaded:

```
c5d04fb93d579712aa375f3ace67fe9243d6aaa9b039576516722af2d9c5af52  graphml.xsd
7809123855d2ef634dea2b678055b6230607efb9addde55a06c4afd67075a04b  graphml-structure.xsd
4f76a2f3c026979b733f92d3f85c815723848b72731a72ef40a1709959b698ed  xlink.xsd
```

One change was made: the `schemaLocation` attributes that point from one file to another use the local file names (`graphml-structure.xsd`, `xlink.xsd`) instead of the `http://graphml.graphdrawing.org/xmlns/1.0/` URLs. `xlink.xsd` is unchanged.
