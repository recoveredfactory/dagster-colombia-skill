# SoQL cheat sheet (Socrata / datos.gov.co)

SoQL is Socrata's query language. You pass it as URL parameters to
`https://{domain}/resource/{4x4}.json`. The CLI maps each `--flag` to one `$param`.

## Parameters

| CLI flag      | SoQL param | Purpose                                             |
|---------------|------------|-----------------------------------------------------|
| `--select`    | `$select`  | columns / aggregates to return                      |
| `--where`     | `$where`   | row filter (SQL-like predicate)                     |
| `--group`     | `$group`   | group-by columns (for aggregates)                   |
| `--order`     | `$order`   | sort, e.g. `accesos desc`                           |
| `--having`    | `$having`  | filter on aggregates                                |
| `--q`         | `$q`       | full-text search across the row                     |
| `--limit`     | `$limit`   | max rows (single page ≤ 50,000)                      |
| `--offset`    | `$offset`  | skip N rows (pagination)                             |
| `--paginate`  | —          | loop `$offset` to fetch every matching row          |

## Casting (important for datos.gov.co)

Many datasets store numbers as **text**. Cast in SoQL with `::number`:

```
$select=sum(no_de_accesos::number) as accesos
```

Other casts: `::number`, `::text`, `::floating_timestamp`, `::checkbox`.

## Aggregates

`count(*)`, `sum(col)`, `avg(col)`, `min(col)`, `max(col)`. Alias with `as`:

```
$select=departamento, sum(no_de_accesos::number) as accesos
$group=departamento
$order=accesos desc
```

## $where predicates

```
$where=anno = '2022'
$where=no_de_accesos::number > 1000
$where=departamento = 'BOGOTÁ D.C.'          # accents + case matter
$where=anno between '2018' and '2022'
$where=starts_with(departamento, 'ANTIO')
$where=departamento in ('ANTIOQUIA','VALLE DEL CAUCA')
```

Combine with `and` / `or`. String literals use single quotes.

## Pagination past 50k

A single page returns at most 50,000 rows. To pull more, page with `$offset`:

```
$limit=50000 $offset=0
$limit=50000 $offset=50000
...
```

The CLI does this for you with `--paginate`. But prefer aggregating server-side
(`$group`) — for a chart you usually need tens of rows, not millions.

## Handy patterns

```bash
# Row count without pulling data
python3 cli.py query <4x4> --select "count(*) as count"

# Distinct values of a column
python3 cli.py query <4x4> --select "departamento" --group departamento --order departamento

# Time series
python3 cli.py query <4x4> --select "anno, sum(x::number) as total" --group anno --order anno
```

## References

- SODA / SoQL docs: https://dev.socrata.com/docs/queries/
- Discovery API: https://socratadiscovery.docs.apiary.io/
