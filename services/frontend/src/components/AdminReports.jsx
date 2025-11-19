import React, { useState, useEffect, useRef } from 'react';
import adminAPI from '../services/adminAPI';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const StatCard = ({ title, value, extra = '' }) => (
  <div className="bg-white p-4 rounded-lg shadow-md text-center">
    <h2 className="text-lg font-semibold text-gray-600">{title}</h2>
    <p className="text-3xl font-bold text-gray-800">{value}</p>
    {extra && <p className="text-sm text-gray-500">{extra}</p>}
  </div>
);

const AdminReports = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [tramiteStats, setTramiteStats] = useState(null);
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchCriteria, setSearchCriteria] = useState({
    nombre: '',
    rut: '',
    tipo_tramite: '',
    fecha_inicio: '',
    fecha_fin: ''
  });
  const chartRef = useRef(null);

  useEffect(() => {
    const fetchAllData = async () => {
      try {
        setLoading(true);
        const [dashboard, stats] = await Promise.all([
          adminAPI.getDashboardData(),
          adminAPI.getTramiteStats()
        ]);
        setDashboardData(dashboard);
        setTramiteStats(stats);
        setError(null);
      } catch (err) {
        const detail = err.response?.data?.detail || 'No se pudieron cargar los datos. Por favor, intente más tarde.';
        setError(detail);
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, []);

  const handleSearchChange = (e) => {
    setSearchCriteria({ ...searchCriteria, [e.target.name]: e.target.value });
  };

  const handleSearchSubmit = async (e) => {
    e.preventDefault();
    try {
      const results = await adminAPI.buscarReservas(searchCriteria);
      setSearchResults(results.resultados);
    } catch (error) {
      alert('Error al realizar la búsqueda.');
      console.error(error);
    }
  };

  const handleExportExcel = () => {
    const wb = XLSX.utils.book_new();

    if (tramiteStats?.ranking_tramites) {
      const ws1 = XLSX.utils.json_to_sheet(tramiteStats.ranking_tramites);
      XLSX.utils.book_append_sheet(wb, ws1, "Estadísticas de Trámites");
    }

    if (searchResults) {
      const ws2 = XLSX.utils.json_to_sheet(searchResults);
      XLSX.utils.book_append_sheet(wb, ws2, "Resultados de Búsqueda");
    }

    XLSX.writeFile(wb, "ReporteDeReservas.xlsx");
  };

  const handleExportPDF = () => {
    const doc = new jsPDF();
    const chartImage = chartRef.current?.toBase64Image();

    doc.text("Reporte de Administración", 14, 20);

    if (dashboardData) {
        autoTable(doc, {
            startY: 30,
            head: [['Métrica', 'Valor']],
            body: [
            ['Total de Reservas', dashboardData.estadisticas.total_reservas],
            ['Reservas Activas', dashboardData.estadisticas.reservas_activas],
            ['Reservas Completadas', dashboardData.estadisticas.reservas_completadas],
            ['Reservas Anuladas', dashboardData.estadisticas.reservas_anuladas],
            ],
        });
    }

    if (tramiteStats?.ranking_tramites) {
        autoTable(doc, {
            startY: doc.autoTable.previous.finalY + 10,
            head: [['Tipo de Trámite', 'Cantidad']],
            body: tramiteStats.ranking_tramites.map(item => [item.tipo_tramite, item.cantidad]),
        });
    }

    if (chartImage) {
        doc.addPage();
        doc.text("Gráfico de Distribución de Trámites", 14, 20);
        doc.addImage(chartImage, 'PNG', 14, 30, 180, 100);
    }

    if (searchResults) {
        doc.addPage();
        doc.text("Resultados de Búsqueda Avanzada", 14, 20);
        autoTable(doc, {
            startY: 30,
            head: [['ID', 'Nombre', 'Trámite', 'Fecha', 'Estado']],
            body: searchResults.map(res => [res.id, res.usuario_nombre, res.tipo_tramite, res.fecha, res.estado]),
        });
    }

    doc.save("ReporteDeReservas.pdf");
  };

  const chartData = {
    labels: tramiteStats?.ranking_tramites.map(item => item.tipo_tramite) || [],
    datasets: [
      {
        label: 'Cantidad de Reservas',
        data: tramiteStats?.ranking_tramites.map(item => item.cantidad) || [],
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Distribución de Reservas por Tipo de Trámite',
      },
    },
  };

  if (loading) {
    return <div className="text-center p-8">🔄 Cargando reportes...</div>;
  }

  if (error) {
    return <div className="text-center p-8 text-red-500">⚠️ {error}</div>;
  }

  return (
    <div className="container mx-auto p-4 space-y-8">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-3xl font-bold text-gray-800">Panel de Reportes</h1>
        <div className="flex space-x-2">
            <button onClick={handleExportExcel} className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors shadow-sm">
                Exportar a Excel
            </button>
            <button onClick={handleExportPDF} className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors shadow-sm">
                Exportar a PDF
            </button>
        </div>
      </div>

      {/* Dashboard General */}
      {dashboardData && (
        <section>
          <h2 className="text-2xl font-semibold mb-4 text-gray-700">Dashboard General</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard title="Total de Reservas" value={dashboardData.estadisticas.total_reservas} />
            <StatCard title="Reservas Activas" value={dashboardData.estadisticas.reservas_activas} />
            <StatCard title="Reservas Completadas" value={dashboardData.estadisticas.reservas_completadas} />
            <StatCard title="Reservas Anuladas" value={dashboardData.estadisticas.reservas_anuladas} />
          </div>
        </section>
      )}

      {/* Estadísticas de Trámites */}
      {tramiteStats && (
        <section className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4 text-gray-700">Estadísticas de Trámites</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="overflow-x-auto">
              <table className="min-w-full table-auto">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-2 text-left">Tipo de Trámite</th>
                    <th className="px-4 py-2 text-right">Cantidad</th>
                  </tr>
                </thead>
                <tbody>
                  {tramiteStats.ranking_tramites.map((item) => (
                    <tr key={item.tipo_tramite} className="border-t">
                      <td className="px-4 py-2">{item.tipo_tramite}</td>
                      <td className="px-4 py-2 text-right font-mono">{item.cantidad}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="w-full h-full">
              <Bar ref={chartRef} options={chartOptions} data={chartData} />
            </div>
          </div>
        </section>
      )}

      {/* Búsqueda Avanzada */}
      <section className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4 text-gray-700">Búsqueda Avanzada de Reservas</h2>
        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          <input type="text" name="nombre" value={searchCriteria.nombre} onChange={handleSearchChange} placeholder="Nombre" className="p-2 border rounded" />
          <input type="text" name="rut" value={searchCriteria.rut} onChange={handleSearchChange} placeholder="RUT" className="p-2 border rounded" />
          <input type="text" name="tipo_tramite" value={searchCriteria.tipo_tramite} onChange={handleSearchChange} placeholder="Tipo de Trámite" className="p-2 border rounded" />
          <input type="date" name="fecha_inicio" value={searchCriteria.fecha_inicio} onChange={handleSearchChange} className="p-2 border rounded" />
          <input type="date" name="fecha_fin" value={searchCriteria.fecha_fin} onChange={handleSearchChange} className="p-2 border rounded" />
          <button type="submit" className="bg-blue-600 text-white p-2 rounded hover:bg-blue-700">Buscar</button>
        </form>
        {searchResults && (
          <div className="overflow-x-auto">
            <h3 className="text-xl font-semibold mb-2">Resultados ({searchResults.length})</h3>
            <table className="min-w-full table-auto">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-4 py-2 text-left">ID</th>
                  <th className="px-4 py-2 text-left">Nombre</th>
                  <th className="px-4 py-2 text-left">Trámite</th>
                  <th className="px-4 py-2 text-left">Fecha</th>
                  <th className="px-4 py-2 text-left">Estado</th>
                </tr>
              </thead>
              <tbody>
                {searchResults.map((res) => (
                  <tr key={res.id} className="border-t">
                    <td className="px-4 py-2">{res.id}</td>
                    <td className="px-4 py-2">{res.usuario_nombre}</td>
                    <td className="px-4 py-2">{res.tipo_tramite}</td>
                    <td className="px-4 py-2">{res.fecha}</td>
                    <td className="px-4 py-2">{res.estado}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
};

export default AdminReports;
