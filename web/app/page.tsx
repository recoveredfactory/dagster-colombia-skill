import AccessChart from "./AccessChart";
import byDepartment from "@/public/data/by_department.json";
import byYear from "@/public/data/by_year.json";
import meta from "@/public/data/meta.json";

// This page reads ONLY the JSON that the Dagster pipeline wrote into
// web/public/data/. Change the data (re-run the pipeline) → the dashboard changes.
export default function Home() {
  const nf = new Intl.NumberFormat("es-CO");

  return (
    <main className="container">
      <header>
        <h1>Internet fijo en Colombia</h1>
        <p className="sub">{meta.dataset_name}</p>
        <p className="meta">
          Periodo {meta.period} · {byDepartment.length} departamentos ·{" "}
          {nf.format(meta.total_accesos)} accesos (acumulado)
        </p>
      </header>

      <section>
        <h2>Accesos por año</h2>
        <AccessChart data={byYear} />
      </section>

      <section>
        <h2>Accesos por departamento</h2>
        {/* 🗺️ Reto (issue "mapa"): by_department.json incluye cod_departamento
            (DIVIPOLA). Únelo con un GeoJSON de departamentos de Colombia para
            pintar aquí un mapa coroplético en lugar de (o además de) la tabla. */}
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Departamento</th>
              <th>Código</th>
              <th className="num">Accesos</th>
            </tr>
          </thead>
          <tbody>
            {byDepartment.map((d, i) => (
              <tr key={d.cod_departamento}>
                <td>{i + 1}</td>
                <td>{d.departamento}</td>
                <td className="code">{d.cod_departamento}</td>
                <td className="num">{nf.format(d.accesos)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <footer>
        <p>
          Fuente:{" "}
          <a href={meta.source_url} target="_blank" rel="noopener noreferrer">
            datos.gov.co / {meta.dataset_id}
          </a>{" "}
          · {meta.note}
        </p>
      </footer>
    </main>
  );
}
