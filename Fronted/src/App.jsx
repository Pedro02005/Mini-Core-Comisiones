
import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const fechaLocal = (fecha) => `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}-${String(fecha.getDate()).padStart(2, '0')}`

function App() {
  const [pagina, setPagina] = useState('ventas')
  const [vendedores, setVendedores] = useState([])
  const [ventas, setVentas] = useState([])
  const [reporte, setReporte] = useState(null)
  const [expandido, setExpandido] = useState(null)
  const [cargando, setCargando] = useState(false)
  const [mensaje, setMensaje] = useState('')

  const [form, setForm] = useState({
    vendedor: '',
    fecha_venta: '',
    monto: ''
  })

  const [fechas, setFechas] = useState({
    inicio: fechaLocal(new Date(new Date().getFullYear(), new Date().getMonth() - 5, 1)),
    fin: fechaLocal(new Date())
  })

  // Formatear valores
  const dinero = (valor) => '$' + Number(valor || 0).toFixed(2)
  const porcentaje = (valor) => (Number(valor || 0) * 100).toFixed(2) + '%'

  // Consultar vendedores y ventas
  const cargarDatos = async () => {
    const [resVendedores, resVentas] = await Promise.all([
      axios.get('/api/vendedores/'),
      axios.get('/api/ventas/')
    ])

    setVendedores(resVendedores.data)
    setVentas(resVentas.data)
  }

  useEffect(() => {
    cargarDatos().catch(error => {
      console.error(error)
      setMensaje('Error al conectar con Django')
    })
  }, [])

  // Guardar venta
  const guardarVenta = async (e) => {
    e.preventDefault()
    setCargando(true)
    setMensaje('')

    try {
      await axios.post('/api/ventas/', form)
      await cargarDatos()

      setForm({ vendedor: '', fecha_venta: '', monto: '' })
      setReporte(null)
      setMensaje('Venta registrada correctamente')
    } catch (error) {
      console.error(error)
      setMensaje('Error al guardar la venta')
    } finally {
      setCargando(false)
    }
  }

  // Eliminar venta
  const eliminarVenta = async (id) => {
    if (!window.confirm('¿Eliminar esta venta?')) return

    setCargando(true)
    setMensaje('')

    try {
      await axios.delete(`/api/ventas/${id}/`)
      await cargarDatos()

      setReporte(null)
      setMensaje('Venta eliminada correctamente')
    } catch (error) {
      console.error(error)
      setMensaje('Error al eliminar la venta')
    } finally {
      setCargando(false)
    }
  }

  // Calcular comisiones por fechas
  const calcularComisiones = async () => {
    if (!fechas.inicio || !fechas.fin) {
      setMensaje('Selecciona las dos fechas')
      return
    }

    setCargando(true)
    setMensaje('')

    try {
      const respuesta = await axios.post(
        '/api/comisiones/calcular/',
        {
          fecha_inicio: fechas.inicio,
          fecha_fin: fechas.fin
        }
      )

      setReporte(respuesta.data)
      setExpandido(null)
      setMensaje('Comisiones calculadas correctamente')
    } catch (error) {
      console.error(error)
      setMensaje('Error al calcular las comisiones')
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="contenedor">

      <header>
        <h1>Sistema de Comisiones - Mini Core MVC</h1>

        <nav>
          <button
            className={pagina === 'ventas' ? 'activo' : ''}
            onClick={() => { setPagina('ventas'); setMensaje('') }}
          >
            Gestión de Ventas
          </button>

          <button
            className={pagina === 'comisiones' ? 'activo' : ''}
            onClick={() => { setPagina('comisiones'); setMensaje('') }}
          >
            Cálculo de Comisiones
          </button>
        </nav>
      </header>

      {mensaje && <p className="mensaje">{mensaje}</p>}

      {/* PESTAÑA VENTAS */}
      {pagina === 'ventas' && (
        <>
          <section>
            <h2>Agregar Nueva Venta</h2>

            <form onSubmit={guardarVenta}>
              <select
                value={form.vendedor}
                onChange={e => setForm({
                  ...form, vendedor: e.target.value
                })}
                required
              >
                <option value="">Seleccionar vendedor</option>
                {vendedores.map(v => (
                  <option key={v.id} value={v.id}>
                    {v.nombre}
                  </option>
                ))}
              </select>

              <input
                type="date"
                value={form.fecha_venta}
                onChange={e => setForm({
                  ...form, fecha_venta: e.target.value
                })}
                required
              />

              <input
                type="number"
                placeholder="Monto"
                step="0.01"
                min="0.01"
                value={form.monto}
                onChange={e => setForm({
                  ...form, monto: e.target.value
                })}
                required
              />

              <button type="submit" disabled={cargando}>
                Guardar Venta
              </button>
            </form>
          </section>

          <section>
            <h2>Lista de Ventas</h2>

            <div className="tabla-contenedor">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Vendedor</th>
                    <th>Fecha</th>
                    <th>Monto</th>
                    <th>Comisión</th>
                    <th>Acciones</th>
                  </tr>
                </thead>

                <tbody>
                  {ventas.map(venta => (
                    <tr key={venta.id}>
                      <td>{venta.id}</td>
                      <td>{venta.vendedor_nombre}</td>
                      <td>{venta.fecha_venta}</td>
                      <td>{dinero(venta.monto)}</td>
                      <td>
                        {dinero(venta.comision_calculada.monto)}
                        {' '}
                        ({porcentaje(venta.comision_calculada.porcentaje)})
                      </td>
                      <td>
                        <button
                          className="eliminar"
                          disabled={cargando}
                          onClick={() => eliminarVenta(venta.id)}
                        >
                          Eliminar
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {ventas.length === 0 && (
                <p>No hay ventas registradas</p>
              )}
            </div>
          </section>
        </>
      )}

      {/* PESTAÑA COMISIONES */}
      {pagina === 'comisiones' && (
        <>
          <section>
            <h2>Calcular Comisiones por Fechas</h2>

            <div className="filtros">
              <div>
                <label>Fecha de inicio</label>
                <input
                  type="date"
                  value={fechas.inicio}
                  onChange={e => {
                    setFechas({ ...fechas, inicio: e.target.value })
                    setReporte(null)
                  }}
                />
              </div>

              <div>
                <label>Fecha de fin</label>
                <input
                  type="date"
                  value={fechas.fin}
                  onChange={e => {
                    setFechas({ ...fechas, fin: e.target.value })
                    setReporte(null)
                  }}
                />
              </div>

              <button onClick={calcularComisiones} disabled={cargando}>
                {cargando ? 'Calculando...' : 'Calcular Comisiones'}
              </button>
            </div>
          </section>

          {reporte && (
            <>
              {/* RESUMEN GENERAL */}
              <section>
                <h2>Resumen de Comisiones</h2>

                <p>
                  Período: {reporte.periodo_info.fecha_inicio_formateada}
                  {' - '}
                  {reporte.periodo_info.fecha_fin_formateada}
                </p>

                <div className="resumen">
                  <div>
                    <h3>{reporte.total_vendedores}</h3>
                    <p>Vendedores</p>
                  </div>

                  <div>
                    <h3>{reporte.total_ventas}</h3>
                    <p>Ventas</p>
                  </div>

                  <div>
                    <h3>{dinero(reporte.total_monto_ventas)}</h3>
                    <p>Total Ventas</p>
                  </div>

                  <div>
                    <h3>{dinero(reporte.total_comisiones)}</h3>
                    <p>Total Comisiones</p>
                  </div>
                </div>
              </section>

              {/* COMISIONES POR VENDEDOR */}
              <section>
                <h2>Comisiones por Vendedor</h2>
                <p>Selecciona un vendedor para ver sus ventas.</p>

                {reporte.vendedores.map(vendedor => (
                  <div className="vendedor" key={vendedor.vendedor_id}>

                    <button
                      className="vendedor-boton"
                      onClick={() => setExpandido(
                        expandido === vendedor.vendedor_id
                          ? null
                          : vendedor.vendedor_id
                      )}
                    >
                      <span>
                        {expandido === vendedor.vendedor_id ? '▼' : '▶'}
                        {' '}
                        {vendedor.vendedor_nombre}
                      </span>

                      <span>
                        {vendedor.total_ventas} ventas
                        {' | '}
                        {dinero(vendedor.total_comisiones)}
                      </span>
                    </button>

                    {expandido === vendedor.vendedor_id && (
                      <div className="detalle">
                        <p>
                          Total vendido:
                          {' '}
                          <strong>{dinero(vendedor.total_monto_ventas)}</strong>
                        </p>

                        <p>
                          Porcentaje promedio:
                          {' '}
                          <strong>{porcentaje(vendedor.porcentaje_promedio)}</strong>
                        </p>

                        <div className="tabla-contenedor">
                          <table>
                            <thead>
                              <tr>
                                <th>ID</th>
                                <th>Fecha</th>
                                <th>Venta</th>
                                <th>Porcentaje</th>
                                <th>Comisión</th>
                                <th>Regla</th>
                              </tr>
                            </thead>

                            <tbody>
                              {vendedor.comisiones_individuales.map(c => (
                                <tr key={c.id}>
                                  <td>{c.id}</td>
                                  <td>{c.fecha}</td>
                                  <td>{dinero(c.monto_venta)}</td>
                                  <td>{porcentaje(c.porcentaje_aplicado)}</td>
                                  <td>{dinero(c.monto_comision)}</td>
                                  <td>{c.regla_aplicada.descripcion}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                {reporte.vendedores.length === 0 && (
                  <p>No existen ventas en el período seleccionado.</p>
                )}
              </section>
            </>
          )}
        </>
      )}
    </div>
  )
}

export default App
