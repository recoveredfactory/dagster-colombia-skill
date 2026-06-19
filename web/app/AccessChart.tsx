"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Point = { anno: number; accesos: number };

// Client component: Recharts needs the browser. The server page passes it the data.
export default function AccessChart({ data }: { data: Point[] }) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data} margin={{ top: 10, right: 24, bottom: 8, left: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="anno" />
        <YAxis
          width={52}
          tickFormatter={(v) => `${(Number(v) / 1_000_000).toFixed(0)}M`}
        />
        <Tooltip
          formatter={(v) => [Number(v).toLocaleString("es-CO"), "Suscriptores"]}
        />
        <Line
          type="monotone"
          dataKey="accesos"
          stroke="#2563eb"
          strokeWidth={2}
          dot={{ r: 3 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
